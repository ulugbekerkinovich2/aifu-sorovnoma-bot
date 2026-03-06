from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Option:
    value: str
    order: int
    labels: Dict[str, str] = field(default_factory=dict)

    def get_label(self, lang: str) -> str:
        return self.labels.get(lang) or self.labels.get("uz") or self.labels.get("ru") or self.value


@dataclass
class Question:
    survey_code: str
    block_code: str
    question_code: str
    question_order: int
    question_order_in_block: int
    block_total_questions: int
    question_type: str
    required: bool
    allow_skip: bool
    texts: Dict[str, str] = field(default_factory=dict)
    help_texts: Dict[str, str] = field(default_factory=dict)
    placeholders: Dict[str, str] = field(default_factory=dict)
    validation_regex: str = ""
    options: List[Option] = field(default_factory=list)

    def get_text(self, lang: str) -> str:
        return self.texts.get(lang) or self.texts.get("uz") or self.texts.get("ru") or ""

    def get_help_text(self, lang: str) -> str:
        return self.help_texts.get(lang) or self.help_texts.get("uz") or self.help_texts.get("ru") or ""

    def get_placeholder(self, lang: str) -> str:
        return self.placeholders.get(lang) or self.placeholders.get("uz") or self.placeholders.get("ru") or ""


@dataclass
class Block:
    survey_code: str
    block_code: str
    roman_no: str
    order_no: int
    titles: Dict[str, str] = field(default_factory=dict)
    intros: Dict[str, str] = field(default_factory=dict)

    def get_title(self, lang: str) -> str:
        return self.titles.get(lang) or self.titles.get("uz") or self.titles.get("ru") or self.block_code

    def get_intro(self, lang: str) -> str:
        return self.intros.get(lang) or self.intros.get("uz") or self.intros.get("ru") or ""


@dataclass
class Survey:
    survey_code: str
    order_no: int
    is_active: bool
    titles: Dict[str, str] = field(default_factory=dict)
    audiences: Dict[str, str] = field(default_factory=dict)
    descriptions: Dict[str, str] = field(default_factory=dict)
    blocks: Dict[str, Block] = field(default_factory=dict)
    questions: List[Question] = field(default_factory=list)

    def get_title(self, lang: str) -> str:
        return self.titles.get(lang) or self.titles.get("uz") or self.titles.get("ru") or self.survey_code

    def get_audience(self, lang: str) -> str:
        return self.audiences.get(lang) or self.audiences.get("uz") or self.audiences.get("ru") or ""

    def get_description(self, lang: str) -> str:
        return self.descriptions.get(lang) or self.descriptions.get("uz") or self.descriptions.get("ru") or ""
