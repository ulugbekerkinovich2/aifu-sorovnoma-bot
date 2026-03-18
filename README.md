# AIFU Telegram Survey Bot - 2 tilli versiya

Bu loyiha:
- `aiogram v2`
- `Python 3.8.10`
- Excel orqali boshqariladigan
- O'zbek + Rus tilli
- JSON storage
- Excel export

bot tayyor loyihasi.

## Yangi imkoniyatlar
- Bot boshida til tanlanadi: `🇺🇿 O'zbekcha / 🇷🇺 Русский`
- Survey nomlari 2 tilda
- Blok nomlari 2 tilda
- Savollar 2 tilda
- Variantlar 2 tilda
- JSON ichida `lang` saqlanadi
- Export Excel ichida `question_text_uz` va `question_text_ru` bor

## Muhim fayllar
- `bot.py` - asosiy bot
- `survey_loader.py` - Excel'dan 2 tilli savollarni o'qiydi
- `questionnaire/aifu_questionnaire_config_bilingual_full.xlsx` - 2 tilli savollar Exceldagi baza
- `exporter.py` - JSON natijalarni Excel'ga chiqaradi
- `pm2.config.js` - PM2 uchun config

## Excel sheetlar
- `surveys`
- `blocks`
- `questions`
- `options`

## O'rnatish
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Ishga tushirish
```bash
python bot.py
```

## PM2
```bash
pm2 start pm2.config.js
pm2 logs aifu-survey-bot
```

## JSON saqlanishi
- progress: `data/json/progress/<user_id>.json`
- javoblar: `data/json/responses/YYYY-MM-DD/<response_id>.json`

## Excel export
```bash
python export_results.py
```

yoki bot ichidan admin:
```bash
/export_results
```
