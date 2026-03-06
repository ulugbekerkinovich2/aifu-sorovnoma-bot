from datetime import datetime

from config import EXPORTS_DIR, PROGRESS_DIR, QUESTIONNAIRE_XLSX, RESPONSES_DIR
from exporter import export_responses_to_excel
from storage import JsonRepository
from survey_loader import load_questionnaire


def main():
    surveys = load_questionnaire(QUESTIONNAIRE_XLSX)
    repo = JsonRepository(PROGRESS_DIR, RESPONSES_DIR)
    response_files = repo.list_response_files()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = EXPORTS_DIR / f"responses_export_{timestamp}.xlsx"

    export_responses_to_excel(response_files, surveys, output_path)
    print(output_path)


if __name__ == "__main__":
    main()
