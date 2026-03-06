import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS = {
    int(item.strip())
    for item in os.getenv("ADMIN_IDS", "").split(",")
    if item.strip().isdigit()
}

QUESTIONNAIRE_XLSX = Path(
    os.getenv(
        "QUESTIONNAIRE_XLSX",
        str(BASE_DIR / "questionnaire" / "aifu_questionnaire_config.xlsx"),
    )
).resolve()

DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data"))).resolve()
JSON_DIR = DATA_DIR / "json"
PROGRESS_DIR = JSON_DIR / "progress"
RESPONSES_DIR = JSON_DIR / "responses"
EXPORTS_DIR = DATA_DIR / "exports"

for path in [DATA_DIR, JSON_DIR, PROGRESS_DIR, RESPONSES_DIR, EXPORTS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

APP_TITLE = "AIFU Survey Bot"
DEFAULT_LANG = "uz"
SUPPORTED_LANGS = ("uz", "ru")

I18N = {
    "uz": {
        "lang_name": "🇺🇿 O'zbekcha",
        "welcome": "<b>{app_title}</b>\n\nTilni tanlang.",
        "menu_title": "<b>{app_title}</b>\n\nKerakli so'rovnoma turini tanlang.{extra}",
        "continue_hint": "\n\nSizda tugallanmagan so'rovnoma bor. Davom ettirish uchun /continue ni bosing.",
        "block_label": "blok",
        "question_label": "Savol",
        "multi_help": "Bir nechta variant tanlashingiz mumkin. Tanlab bo'lgach <b>✅ Tayyor</b> ni bosing.",
        "text_help": "Javobni matn ko'rinishida yuboring.",
        "skip_help": "{skip_text} tugmasi bilan savolni o'tkazib yuborishingiz mumkin.",
        "skip_text": "⏭ O'tkazib yuborish",
        "done_text": "✅ Tayyor",
        "cancelled": "Bekor qilindi.",
        "no_saved_session": "Davom ettiriladigan saqlangan sessiya topilmadi.",
        "session_loaded": "Saqlangan sessiya yuklandi.",
        "admin_only": "Bu buyruq faqat admin uchun.",
        "no_results": "Hali javoblar yo'q.",
        "starting": "<b>{survey_title}</b>\n\n{description}\n\nBoshlaymiz.",
        "skipped": "Savol o'tkazib yuborildi.",
        "selected": "Tanlandi: {label}",
        "updated": "Yangilandi",
        "need_one_option": "Kamida bitta variant tanlang yoki savolni o'tkazib yuboring.",
        "answer_saved": "Javob saqlandi",
        "session_not_found": "Sessiya topilmadi. /start ni bosing.",
        "use_buttons": "Iltimos, tugmalardan foydalaning.",
        "empty_answer": "Javob bo'sh bo'lmasin.",
        "integer_error": "Faqat raqam yuboring. Masalan: 22",
        "phone_error": "Telefon raqamni to'g'ri formatda yuboring. Masalan: +998 90 123 45 67",
        "format_error": "Kiritilgan qiymat formatga mos emas.",
        "finished": "✅ So'rovnoma yakunlandi. Rahmat!",
        "change_language": "Til o'zgartirildi.",
    },
    "ru": {
        "lang_name": "🇷🇺 Русский",
        "welcome": "<b>{app_title}</b>\n\nВыберите язык.",
        "menu_title": "<b>{app_title}</b>\n\nВыберите тип опроса.{extra}",
        "continue_hint": "\n\nУ вас есть незавершённый опрос. Для продолжения нажмите /continue.",
        "block_label": "блок",
        "question_label": "Вопрос",
        "multi_help": "Можно выбрать несколько вариантов. После выбора нажмите <b>✅ Готово</b>.",
        "text_help": "Отправьте ответ в виде текста.",
        "skip_help": "Вы можете пропустить вопрос кнопкой {skip_text}.",
        "skip_text": "⏭ Пропустить",
        "done_text": "✅ Готово",
        "cancelled": "Отменено.",
        "no_saved_session": "Сохранённая сессия для продолжения не найдена.",
        "session_loaded": "Сохранённая сессия загружена.",
        "admin_only": "Эта команда доступна только администратору.",
        "no_results": "Пока нет ответов.",
        "starting": "<b>{survey_title}</b>\n\n{description}\n\nНачинаем.",
        "skipped": "Вопрос пропущен.",
        "selected": "Выбрано: {label}",
        "updated": "Обновлено",
        "need_one_option": "Выберите хотя бы один вариант или пропустите вопрос.",
        "answer_saved": "Ответ сохранён",
        "session_not_found": "Сессия не найдена. Нажмите /start.",
        "use_buttons": "Пожалуйста, используйте кнопки.",
        "empty_answer": "Ответ не должен быть пустым.",
        "integer_error": "Отправьте только число. Например: 22",
        "phone_error": "Введите телефон в правильном формате. Например: +998 90 123 45 67",
        "format_error": "Введённое значение не соответствует формату.",
        "finished": "✅ Опрос завершён. Спасибо!",
        "change_language": "Язык изменён.",
    },
}
