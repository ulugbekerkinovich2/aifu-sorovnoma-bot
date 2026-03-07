import logging
import re
import uuid
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

from config import ADMIN_IDS, APP_TITLE, BOT_TOKEN, DEFAULT_LANG, EXPORTS_DIR, I18N, PROGRESS_DIR, QUESTIONNAIRE_XLSX, RESPONSES_DIR
from exporter import export_responses_to_excel
from sheets import append_response, init_sheet
from keyboards import language_keyboard, multi_choice_keyboard, remove_keyboard, single_choice_keyboard, survey_keyboard
from states import SurveyStates
from storage import JsonRepository
from survey_loader import load_questionnaire

logging.basicConfig(level=logging.INFO)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan.")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

surveys = load_questionnaire(QUESTIONNAIRE_XLSX)
repo = JsonRepository(PROGRESS_DIR, RESPONSES_DIR)
init_sheet(surveys)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def tr(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in I18N else DEFAULT_LANG
    text = I18N[lang].get(key) or I18N[DEFAULT_LANG].get(key) or key
    return text.format(**kwargs) if kwargs else text


def build_user_dict(user: types.User):
    return {
        "telegram_user_id": user.id,
        "username": user.username or "",
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "full_name": user.full_name,
    }


async def get_user_lang(state: FSMContext, user_id: int) -> str:
    data = await state.get_data()
    session = data.get("session")
    if session and session.get("lang"):
        return session["lang"]
    if data.get("lang"):
        return data["lang"]
    progress = repo.load_progress(user_id)
    if progress and progress.get("lang"):
        await state.update_data(lang=progress["lang"])
        return progress["lang"]
    return DEFAULT_LANG


def get_current_question(session):
    return surveys[session["survey_code"]].questions[session["question_index"]]


def build_question_text(session):
    lang = session.get("lang", DEFAULT_LANG)
    survey = surveys[session["survey_code"]]
    question = get_current_question(session)

    q_num = session["question_index"] + 1
    q_total = len(survey.questions)
    lines = [
        f"<b>{q_num}/{q_total}</b>",
        "",
        f"<b>{question.get_text(lang)}</b>",
    ]
    help_text = question.get_help_text(lang)
    if help_text:
        lines += ["", f"ℹ️ {help_text}"]

    if question.question_type == "multi_choice":
        lines += ["", tr(lang, "multi_help")]
    elif question.question_type in {"long_text", "integer", "phone", "text"}:
        lines += ["", tr(lang, "text_help")]

    return "\n".join(lines)


async def show_language_menu(message: types.Message, state: FSMContext):
    lang = await get_user_lang(state, message.from_user.id)
    await message.answer(tr(lang, "welcome", app_title=APP_TITLE), reply_markup=language_keyboard())


async def show_survey_menu(message: types.Message, state: FSMContext):
    lang = await get_user_lang(state, message.from_user.id)
    active_surveys = [survey for survey in surveys.values() if survey.is_active]
    progress = repo.load_progress(message.from_user.id)
    extra = tr(lang, "continue_hint") if progress else ""
    await message.answer(
        tr(lang, "menu_title", app_title=APP_TITLE, extra=extra),
        reply_markup=survey_keyboard(active_surveys, lang),
    )


async def show_current_question(target, state: FSMContext):
    data = await state.get_data()
    session = data.get("session")
    if not session:
        return

    prev_msg_id = session.get("last_question_message_id")
    if prev_msg_id:
        try:
            await bot.delete_message(target, prev_msg_id)
        except Exception:
            pass

    lang = session.get("lang", DEFAULT_LANG)
    question = get_current_question(session)
    text = build_question_text(session)
    if question.question_type == "single_choice":
        msg = await bot.send_message(target, text, reply_markup=single_choice_keyboard(question, lang))
    elif question.question_type == "multi_choice":
        msg = await bot.send_message(target, text, reply_markup=multi_choice_keyboard(question, session.get("pending_multi", []), lang))
    else:
        msg = await bot.send_message(target, text, reply_markup=remove_keyboard())

    session["last_question_message_id"] = msg.message_id
    await save_session(state, session)


async def save_session(state: FSMContext, session):
    await state.update_data(session=session, lang=session.get("lang", DEFAULT_LANG))
    repo.save_progress(session["user"]["telegram_user_id"], session)


async def save_answer_and_advance(state: FSMContext, answer_value=None, answer_text="", skipped=False):
    data = await state.get_data()
    session = data["session"]
    question = get_current_question(session)
    lang = session.get("lang", DEFAULT_LANG)

    session["answers"][question.question_code] = {
        "question_text": question.get_text(lang),
        "question_text_uz": question.get_text("uz"),
        "question_text_ru": question.get_text("ru"),
        "question_type": question.question_type,
        "answer_value": answer_value,
        "answer_text": answer_text,
        "skipped": skipped,
        "answered_at": now_iso(),
    }
    session["question_index"] += 1
    session["pending_multi"] = []

    await save_session(state, session)

    survey = surveys[session["survey_code"]]
    if session["question_index"] >= len(survey.questions):
        response_id = str(uuid.uuid4())
        payload = {
            "response_id": response_id,
            "session_id": session["session_id"],
            "lang": lang,
            "survey_code": session["survey_code"],
            "survey_title": survey.get_title(lang),
            "survey_title_uz": survey.get_title("uz"),
            "survey_title_ru": survey.get_title("ru"),
            "started_at": session["started_at"],
            "finished_at": now_iso(),
            "user": session["user"],
            "answers": session["answers"],
        }
        response_path = repo.save_response(payload)
        append_response(payload)
        repo.clear_progress(session["user"]["telegram_user_id"])
        await state.finish()
        await state.update_data(lang=lang)
        await bot.send_message(
            session["user"]["telegram_user_id"],
            tr(lang, "finished", response_id=response_id, filename=response_path.name),
            reply_markup=remove_keyboard(),
        )
        return

    await show_current_question(session["user"]["telegram_user_id"], state)


def validate_text_answer(question, text, lang):
    text = text.strip()
    if not text:
        return False, tr(lang, "empty_answer")
    if question.validation_regex and not re.match(question.validation_regex, text):
        if question.question_type == "integer":
            return False, tr(lang, "integer_error")
        if question.question_type == "phone":
            return False, tr(lang, "phone_error")
        return False, tr(lang, "format_error")
    return True, ""


@dp.message_handler(commands=["start"], state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await show_language_menu(message, state)


@dp.message_handler(commands=["language"], state="*")
async def cmd_language(message: types.Message, state: FSMContext):
    await show_language_menu(message, state)


@dp.message_handler(commands=["cancel"], state="*")
async def cmd_cancel(message: types.Message, state: FSMContext):
    lang = await get_user_lang(state, message.from_user.id)
    repo.clear_progress(message.from_user.id)
    await state.finish()
    await state.update_data(lang=lang)
    await message.answer(tr(lang, "cancelled"), reply_markup=remove_keyboard())


@dp.message_handler(commands=["continue"], state="*")
async def cmd_continue(message: types.Message, state: FSMContext):
    progress = repo.load_progress(message.from_user.id)
    lang = progress.get("lang", DEFAULT_LANG) if progress else await get_user_lang(state, message.from_user.id)
    if not progress:
        await message.answer(tr(lang, "no_saved_session"))
        return
    await state.set_state(SurveyStates.answering.state)
    await state.update_data(session=progress, lang=lang)
    await message.answer(tr(lang, "session_loaded"), reply_markup=remove_keyboard())
    await show_current_question(message.chat.id, state)


@dp.message_handler(commands=["export_results"], state="*")
async def cmd_export_results(message: types.Message, state: FSMContext):
    lang = await get_user_lang(state, message.from_user.id)
    if message.from_user.id not in ADMIN_IDS:
        await message.answer(tr(lang, "admin_only"))
        return

    response_files = repo.list_response_files()
    if not response_files:
        await message.answer(tr(lang, "no_results"))
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = EXPORTS_DIR / f"responses_export_{timestamp}.xlsx"
    export_responses_to_excel(response_files, surveys, output_path)
    await message.answer_document(types.InputFile(output_path))


@dp.callback_query_handler(lambda c: c.data.startswith("lang:"), state="*")
async def language_selected(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split(":", 1)[1]
    await state.update_data(lang=lang)
    progress = repo.load_progress(callback.from_user.id)
    if progress:
        progress["lang"] = lang
        repo.save_progress(callback.from_user.id, progress)
    await callback.message.edit_text(tr(lang, "change_language"))
    await show_survey_menu(callback.message, state)
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("sv:"), state="*")
async def survey_selected(callback: types.CallbackQuery, state: FSMContext):
    survey_code = callback.data.split(":", 1)[1]
    lang = await get_user_lang(state, callback.from_user.id)
    survey = surveys[survey_code]

    session = {
        "session_id": str(uuid.uuid4()),
        "survey_code": survey_code,
        "lang": lang,
        "question_index": 0,
        "started_at": now_iso(),
        "user": build_user_dict(callback.from_user),
        "answers": {},
        "pending_multi": [],
    }

    await state.set_state(SurveyStates.answering.state)
    await save_session(state, session)
    await callback.message.edit_text(tr(lang, "starting", survey_title=survey.get_title(lang), description=survey.get_description(lang)))
    await show_current_question(callback.message.chat.id, state)
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "skip", state=SurveyStates.answering)
async def skip_question(callback: types.CallbackQuery, state: FSMContext):
    lang = await get_user_lang(state, callback.from_user.id)
    await callback.answer(tr(lang, "skipped"))
    await save_answer_and_advance(state, answer_value=None, answer_text="", skipped=True)


@dp.callback_query_handler(lambda c: c.data.startswith("sc:"), state=SurveyStates.answering)
async def single_choice_selected(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    session = data["session"]
    lang = session.get("lang", DEFAULT_LANG)
    question = get_current_question(session)
    if question.question_type != "single_choice":
        await callback.answer()
        return
    option = question.options[int(callback.data.split(":", 1)[1])]
    await callback.answer(tr(lang, "selected", label=option.get_label(lang)))
    await save_answer_and_advance(state, answer_value=option.value, answer_text=option.get_label(lang), skipped=False)


@dp.callback_query_handler(lambda c: c.data.startswith("mt:"), state=SurveyStates.answering)
async def multi_toggle(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    session = data["session"]
    lang = session.get("lang", DEFAULT_LANG)
    question = get_current_question(session)
    if question.question_type != "multi_choice":
        await callback.answer()
        return
    option_index = int(callback.data.split(":", 1)[1])
    selected = set(session.get("pending_multi", []))
    if option_index in selected:
        selected.remove(option_index)
    else:
        selected.add(option_index)
    session["pending_multi"] = sorted(selected)
    await save_session(state, session)
    await callback.message.edit_reply_markup(reply_markup=multi_choice_keyboard(question, session["pending_multi"], lang))
    await callback.answer(tr(lang, "updated"))


@dp.callback_query_handler(lambda c: c.data == "mdone", state=SurveyStates.answering)
async def multi_done(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    session = data["session"]
    lang = session.get("lang", DEFAULT_LANG)
    question = get_current_question(session)
    if question.question_type != "multi_choice":
        await callback.answer()
        return
    selected_indexes = session.get("pending_multi", [])
    if not selected_indexes:
        await callback.answer(tr(lang, "need_one_option"), show_alert=True)
        return
    selected_options = [question.options[idx] for idx in selected_indexes]
    await callback.answer(tr(lang, "answer_saved"))
    await save_answer_and_advance(
        state,
        answer_value=[opt.value for opt in selected_options],
        answer_text=" | ".join(opt.get_label(lang) for opt in selected_options),
        skipped=False,
    )


@dp.message_handler(state=SurveyStates.answering, content_types=types.ContentType.TEXT)
async def text_answer_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    session = data.get("session")
    lang = session.get("lang", DEFAULT_LANG) if session else await get_user_lang(state, message.from_user.id)
    if not session:
        await message.answer(tr(lang, "session_not_found"))
        return
    question = get_current_question(session)
    if question.question_type in {"single_choice", "multi_choice"}:
        await message.answer(tr(lang, "use_buttons"))
        return
    is_valid, error_message = validate_text_answer(question, message.text, lang)
    if not is_valid:
        await message.answer(error_message)
        return
    try:
        await message.delete()
    except Exception:
        pass
    await save_answer_and_advance(state, answer_value=message.text.strip(), answer_text=message.text.strip(), skipped=False)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
