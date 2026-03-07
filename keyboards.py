from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from config import I18N, SUPPORTED_LANGS


def language_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    for lang in SUPPORTED_LANGS:
        keyboard.insert(
            InlineKeyboardButton(
                text=I18N[lang]["lang_name"],
                callback_data=f"lang:{lang}",
            )
        )
    return keyboard


def survey_keyboard(surveys, lang: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for survey in surveys:
        keyboard.add(
            InlineKeyboardButton(
                text=f"📋 {survey.get_title(lang)}",
                callback_data=f"sv:{survey.survey_code}",
            )
        )
    return keyboard


def single_choice_keyboard(question, lang: str):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for idx, option in enumerate(question.options):
        keyboard.insert(
            InlineKeyboardButton(
                text=option.get_label(lang),
                callback_data=f"sc:{idx}",
            )
        )
    return keyboard


def multi_choice_keyboard(question, selected_indexes, lang: str):
    selected_indexes = set(selected_indexes or [])
    keyboard = InlineKeyboardMarkup(row_width=2)
    for idx, option in enumerate(question.options):
        mark = "✅ " if idx in selected_indexes else ""
        keyboard.insert(
            InlineKeyboardButton(
                text=f"{mark}{option.get_label(lang)}",
                callback_data=f"mt:{idx}",
            )
        )
    keyboard.row(InlineKeyboardButton(text=I18N[lang]["done_text"], callback_data="mdone"))
    return keyboard


def tuman_keyboard(tumans: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    for idx, tuman in enumerate(tumans):
        keyboard.insert(InlineKeyboardButton(text=tuman, callback_data=f"tc:{idx}"))
    return keyboard


def remove_keyboard():
    return ReplyKeyboardRemove()
