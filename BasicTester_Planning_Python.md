# BasicTester (Python Edition) — Planning & Roadmap

> Rebuild dari .NET ke **FastAPI + Jinja2 + Playwright Python**
> Fitur baru: **Auto Input Value dari JSON Schema**

---

## 🏗️ Tech Stack

| Layer | Teknologi | Keterangan |
|---|---|---|
| **Backend** | FastAPI | Modern, async, auto Swagger docs |
| **Frontend** | Jinja2 Template + HTML/CSS/JS | Server-side rendering, no build step |
| **Testing Engine** | Playwright (Python) | `playwright-python`, no Node.js needed |
| **Storage** | In-memory (dict) → SQLite | Fase 1 in-memory, Fase 3 upgrade ke SQLite |
| **Package Manager** | pip + venv | Standard Python workflow |

---

## 📁 Struktur Project

```
basictester/
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Dependencies
├── .env                     # Config (port, debug, dll)
│
├── routers/
│   └── test.py              # Route: list, create, edit, run, detect
│
├── services/
│   └── playwright_service.py  # Logic Playwright (detect & run test)
│
├── models/
│   └── schemas.py           # Pydantic models (TestScenario, FormSchema, dll)
│
├── utils/
│   └── schema_value_generator.py  # ★ Auto Input Value logic
│
├── storage/
│   └── memory_store.py      # In-memory storage (dict-based)
│
├── templates/
│   ├── base.html            # Master layout
│   ├── index.html           # List scenarios
│   ├── create.html          # Create new scenario
│   ├── edit.html            # Edit scenario
│   └── run.html             # Run test + Auto Fill Values
│
├── static/
│   ├── css/
│   │   └── main.css         # Custom design system (black & white)
│   └── js/
│       └── test-form.js     # Schema parser + Auto Input logic (JS)
│
└── test_results/            # Screenshots & logs (auto-created)
```

---

## 🎯 Fitur Prioritas Utama

### ★ Auto Input Value — JSON Schema Type Detection

Saat user paste JSON Schema, sistem otomatis deteksi `type` tiap field dan generate nilai test yang realistis.

#### Logic di `utils/schema_value_generator.py`

```python
def generate_value(field: dict) -> str | bool | int:
    field_type = field.get("type", "text")
    field_name = field.get("name", "").lower()
    placeholder = field.get("placeholder", "")

    # Smart name detection (prioritas lebih tinggi dari type)
    if any(k in field_name for k in ["email"]):
        return "test@example.com"
    if any(k in field_name for k in ["phone", "tel", "hp", "mobile"]):
        return "+62812345678"
    if any(k in field_name for k in ["name", "nama", "fullname"]):
        return "John Doe"
    if any(k in field_name for k in ["address", "alamat"]):
        return "Jl. Contoh No. 123, Jakarta"
    if any(k in field_name for k in ["city", "kota"]):
        return "Jakarta"

    # Type-based mapping
    type_map = {
        "email":    "test@example.com",
        "password": "Test@12345",
        "number":   42,
        "tel":      "+62812345678",
        "url":      "https://test.com",
        "date":     "2025-01-01",
        "checkbox": True,
        "textarea": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "text":     placeholder or "Sample text",
        "select":   None,  # ambil options[0] di frontend
    }
    return type_map.get(field_type, "test value")
```

#### API Endpoint untuk Auto Fill

```
POST /api/generate-values
Body: { "fields": [...] }
Response: { "values": { "fieldName": "generatedValue", ... } }
```

#### Alur Kerja

```
User paste JSON Schema
    ↓
JS parse schema di browser (real-time)
    ↓
Kirim ke POST /api/generate-values
    ↓
Python generate nilai per field
    ↓
JS auto-fill input fields di Run page
    ↓
User review → klik "Run Test"
```

---

## 🚀 Semua Fitur (Build dari Awal)

### 1. Manajemen Test Scenario
- List semua scenario (`GET /`)
- Buat baru (`GET/POST /create`)
- Edit (`GET/POST /edit/{id}`)
- Hapus (`DELETE /delete/{id}`)

### 2. Auto-Detect Form Fields (Playwright)
- Input URL → Playwright buka browser headless
- Deteksi semua `input`, `textarea`, `select`, `checkbox`
- Return sebagai JSON schema

```python
# services/playwright_service.py
async def detect_form_fields(url: str) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        fields = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll(
                'input:not([type=hidden]):not([type=submit]), textarea, select'
            )).map(el => ({
                name: el.name || el.id,
                label: el.labels?.[0]?.textContent?.trim() || '',
                type: el.type || el.tagName.toLowerCase(),
                required: el.required,
                placeholder: el.placeholder || '',
                options: el.tagName === 'SELECT'
                    ? Array.from(el.options).map(o => o.value)
                    : []
            }))
        }""")
        await browser.close()
        return fields
```

### 3. ★ Auto Input Value (Fitur Baru)
- API endpoint `POST /api/generate-values`
- Smart name detection + type mapping
- Tombol "Auto Fill" dan "Regenerate" di Run page
- Nilai bisa diedit manual setelah auto-fill

### 4. Run Test dengan Playwright
- Terima form data dari user
- Playwright isi semua field sesuai nilai
- Submit form → ambil screenshot
- Return status Passed / Failed / Error + durasi

### 5. Login Authentication Support
- Optional: centang "Requires Login"
- Isi login URL, field names, credentials
- Playwright login dulu sebelum buka target URL

### 6. Screenshot & Test History
- Screenshot otomatis saat run
- History result per scenario
- Status badge Passed / Failed / Error

---

## 📦 Dependencies (`requirements.txt`)

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
jinja2==3.1.4
python-multipart==0.0.9
playwright==1.47.0
pydantic==2.8.0
python-dotenv==1.0.1
aiofiles==24.1.0
```

Install Playwright browser:
```bash
playwright install chromium
```

---

## 🗓️ Fase Pengembangan

### Fase 1 · Sprint 1–2 — Core + Auto Input Value
- Setup project FastAPI + Jinja2
- Models & in-memory storage
- CRUD scenario (list, create, edit, delete)
- `schema_value_generator.py` + API endpoint
- Tombol "Auto Fill" & "Regenerate" di `run.html`
- Custom CSS design system (black & white)

### Fase 2 · Sprint 3–4 — Playwright Integration
- `playwright_service.py` — detect form fields
- `playwright_service.py` — run test & screenshot
- Login authentication flow
- Test result history per scenario

### Fase 3 · Sprint 5–6 — Polish & Export
- Export / Import scenario (JSON file)
- SQLite persistence (ganti in-memory)
- Bulk test execution
- Error handling & troubleshooting UI
- Responsive mobile design

---

## 🔄 Perbandingan: .NET vs Python

| Aspek | .NET (Lama) | Python (Baru) |
|---|---|---|
| Backend | ASP.NET MVC 5 | FastAPI |
| Language | C# | Python |
| Template | Razor (.cshtml) | Jinja2 (.html) |
| Playwright | Node.js subprocess | `playwright-python` (native) |
| Setup | Visual Studio + NuGet | pip + venv |
| Deployment | IIS (Windows only) | Uvicorn (cross-platform) |
| Auto docs | ❌ | ✅ Swagger UI bawaan |

---

## 🚀 Cara Jalankan (Development)

```bash
# 1. Clone & setup environment
git clone <repo>
cd basictester
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Jalankan server
uvicorn main:app --reload --port 8000

# 4. Buka browser
# App:     http://localhost:8000
# API docs: http://localhost:8000/docs
```

---

## 📝 Catatan

- Implementasi **Auto Input Value** di Fase 1 karena ini fitur utama baru
- In-memory storage cukup untuk Fase 1-2, upgrade ke SQLite di Fase 3
- Playwright Python tidak butuh Node.js — lebih simpel setup-nya
- FastAPI auto-generate Swagger docs di `/docs` — berguna untuk debug API
