import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class JsonRepository:
    def __init__(self, progress_dir: Path, responses_dir: Path):
        self.progress_dir = progress_dir
        self.responses_dir = responses_dir
        self.progress_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)

    def _progress_path(self, user_id: int) -> Path:
        return self.progress_dir / f"{user_id}.json"

    def save_progress(self, user_id: int, payload: Dict[str, Any]) -> Path:
        path = self._progress_path(user_id)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load_progress(self, user_id: int) -> Optional[Dict[str, Any]]:
        path = self._progress_path(user_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def clear_progress(self, user_id: int) -> None:
        path = self._progress_path(user_id)
        if path.exists():
            path.unlink()

    def save_response(self, payload: Dict[str, Any]) -> Path:
        day_dir = self.responses_dir / datetime.utcnow().strftime("%Y-%m-%d")
        day_dir.mkdir(parents=True, exist_ok=True)

        response_id = payload["response_id"]
        response_path = day_dir / f"{response_id}.json"
        response_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        jsonl_path = self.responses_dir / "responses.jsonl"
        with jsonl_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")

        return response_path

    def list_response_files(self) -> List[Path]:
        files = []
        for path in self.responses_dir.rglob("*.json"):
            if path.name == "responses.jsonl":
                continue
            files.append(path)
        return sorted(files)
