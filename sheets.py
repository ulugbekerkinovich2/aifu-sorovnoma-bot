import logging
import os

logger = logging.getLogger(__name__)

try:
    import gspread
    from google.oauth2.service_account import Credentials
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

_worksheet = None
_question_codes = []


def init_sheet(surveys_dict):
    """Connect to Google Sheet and set up headers if sheet is empty."""
    global _worksheet, _question_codes

    if not _AVAILABLE:
        logger.warning("gspread not installed — Google Sheets integration disabled")
        return

    creds_path = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "")
    if not creds_path or not sheet_id:
        return

    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=_SCOPES)
        client = gspread.authorize(creds)
        ws = client.open_by_key(sheet_id).sheet1

        _question_codes = [
            q.question_code
            for survey in surveys_dict.values()
            for q in survey.questions
        ]

        if not ws.get_all_values():
            meta_headers = [
                "response_id", "lang", "survey_code", "survey_title",
                "started_at", "finished_at",
                "telegram_user_id", "username", "full_name",
            ]
            ws.append_row(meta_headers + _question_codes)

        _worksheet = ws
        logger.info("Google Sheets connected successfully")
    except Exception as e:
        logger.error(f"Google Sheets init failed: {e}")


def append_response(payload: dict):
    """Append a completed survey response as a new row."""
    if _worksheet is None:
        return
    try:
        user = payload.get("user", {})
        answers = payload.get("answers", {})

        row = [
            payload.get("response_id", ""),
            payload.get("lang", ""),
            payload.get("survey_code", ""),
            payload.get("survey_title", ""),
            payload.get("started_at", ""),
            payload.get("finished_at", ""),
            str(user.get("telegram_user_id", "")),
            user.get("username", ""),
            user.get("full_name", ""),
        ]
        for code in _question_codes:
            ans = answers.get(code, {})
            row.append("" if ans.get("skipped") else ans.get("answer_text", ""))

        _worksheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info(f"Sheets: appended response {payload.get('response_id')}")
    except Exception as e:
        logger.error(f"Sheets append failed: {e}")
