# BasicTester Web - React Implementation

A modern web-based form testing tool built with React and Vite, featuring automated form scenario management, field auto-detection, and dynamic schema configuration.

## 🎯 Current Features (Phase 1-2)

### 1. **Test Scenario Management**
- Create new test scenarios with name, description, and target URL
- View all test scenarios in a card-based grid layout
- Edit existing scenarios
- Delete scenarios with confirmation
- Persistent storage using browser LocalStorage

### 2. **Auto-Detect Form Fields**
- Automatic detection of form fields from target URL
- Support for authenticated forms (login required)
- Backend Playwright integration for real form detection
- Smart schema generation based on URL patterns

### 3. **Dynamic Form Schema**
- JSON-based schema editor for form definitions
- Live form preview as you define the schema
- Support for multiple field types:
  - Text inputs (text, email, password, tel, url, number)
  - Textarea
  - Select dropdowns with options
  - Checkboxes and radio buttons
  - Date fields
  - File uploads
- Field inspector for easy editing
- Add/remove fields dynamically

### 4. **Login Authentication Support**
- Configure login credentials for protected forms
- Support for login, email, and password fields
- Automatic authentication during form detection and test execution
- Secure credential handling

### 5. **Playwright Automation**
- Automated test execution using Playwright
- Fill form fields with test data
- Submit forms and capture responses
- Real browser automation for accurate testing

### 6. **Screenshot Capture**
- Automatic screenshot capture before and after form submission
- Visual debugging with before/after screenshots
- Base64 encoded images for easy display
- Screenshot storage in test results

### 7. **Test Results History**
- Track all test execution results
- Status badges (Passed/Failed/Error)
- Test duration and timestamp tracking
- History of recent test runs per scenario
- Persistent test result storage

## 📚 Project Structure

```
src/
├── components/
│   ├── ScenarioList.jsx        # Display all scenarios with test history
│   ├── CreateScenario.jsx      # Create new scenario form
│   ├── EditScenario.jsx        # Edit scenario form
│   ├── RunTest.jsx             # Execute tests with Playwright
│   ├── SchemaEditor.jsx        # JSON schema editor
│   ├── FormPreview.jsx         # Live form preview
│   ├── AutoDetectForm.jsx      # Auto-detect fields
│   └── TestResults.jsx         # Display test results and screenshots
├── services/
│   ├── storageService.js       # LocalStorage management + test history
│   ├── autoDetectService.js    # Form field detection
│   └── utils.js                # Utility functions
├── styles/
│   ├── main.css                # Global styles
│   └── components.css          # Component styles
├── App.jsx                     # Main app component
└── main.jsx                    # Entry point
```

## 🚀 Getting Started

### Prerequisites
- Node.js v16 or higher
- npm or yarn
- Playwright (will be installed automatically)

### Installation

1. Navigate to the project directory:
```bash
cd basic-tester-web
```

2. Install dependencies:
```bash
npm install
```

3. Start the backend server (in separate terminal):
```bash
npm run server
```
Backend will run on `http://localhost:3001`

4. Start the frontend development server:
```bash
npm run dev
```
Frontend will run on `http://localhost:3000`

### Or run both together:
```bash
npm run dev:full
```

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` folder.

### Backend Setup

The application requires a Node.js backend for Playwright automation. Make sure:

1. Node.js is installed: `node --version`
2. Playwright is installed globally: `npm install -g playwright`
3. Playwright browsers are installed: `playwright install chromium`
4. Backend server is running on port 3001

## 🎨 Design System

- **Custom Design System** - No Bootstrap, pure CSS
- **High Contrast** - Black text on white background (WCAG AA compliant)
- **Responsive** - Mobile-first approach
- **Dark Mode Support** - Automatically responds to system preference
- **Modern Typography** - System fonts for better performance

### Color Palette

- **Primary**: Black (#000000) / White (#ffffff)
- **Success**: Green (#008800)
- **Warning**: Orange (#cc6600)
- **Danger**: Red (#cc0000)
- **Info**: Blue (#0000cc)

## 💾 Data Storage

Currently uses **browser LocalStorage** for data persistence. This means:
- ✅ Data persists across browser sessions
- ✅ Test history and results are stored locally
- ✅ No backend required for data storage
- ❌ Data is not synchronized across devices
- ❌ Limited by browser storage quota (~5-10MB)

Data is stored with key: `basicTester_scenarios`

### Storage Structure
- **Scenarios**: Array of test scenario objects
- **Test History**: Last 10 test results per scenario
- **Last Result**: Most recent test execution result
- **Form Schemas**: JSON schema definitions
- **Login Credentials**: Authentication data (stored locally)

## 🔄 Component Flow

```
App.jsx (State Management)
├── ScenarioList (View all scenarios with test history)
├── CreateScenario (Create new)
│   ├── AutoDetectForm (Auto-detect fields)
│   └── SchemaEditor (Define schema)
│       └── FormPreview (Live preview)
├── EditScenario (Edit existing)
│   ├── AutoDetectForm
│   └── SchemaEditor
│       └── FormPreview
└── RunTest (Execute tests)
    ├── TestResults (Display results)
    │   ├── Screenshot display
    │   └── Test history
    └── Backend API (Playwright automation)
```

## 📝 Scenario Data Format

```json
{
  "id": 1234567890,
  "name": "Login Form Test",
  "description": "Test login functionality",
  "targetUrl": "https://example.com/login",
  "hasAuth": false,
  "createdAt": "2024-01-15T10:30:00Z",
  "lastResult": {
    "success": true,
    "status": "passed",
    "message": "Form submitted successfully",
    "duration": 2450,
    "timestamp": "2024-01-15T10:35:22Z",
    "submittedData": { "email": "test@example.com", "password": "test123" },
    "finalUrl": "https://example.com/dashboard",
    "pageTitle": "Dashboard",
    "screenshot": "data:image/png;base64,...",
    "afterSubmitScreenshot": "data:image/png;base64,...",
    "error": null
  },
  "testHistory": [
    {
      "success": true,
      "status": "passed",
      "message": "Form submitted successfully",
      "duration": 2450,
      "timestamp": "2024-01-15T10:35:22Z",
      "submittedData": { "email": "test@example.com", "password": "test123" },
      "finalUrl": "https://example.com/dashboard",
      "pageTitle": "Dashboard",
      "screenshot": "data:image/png;base64,...",
      "afterSubmitScreenshot": "data:image/png;base64,...",
      "error": null
    }
  ],
  "formSchema": {
    "title": "Login Form",
    "description": "User login form",
    "fields": [
      {
        "name": "email",
        "label": "Email Address",
        "type": "email",
        "required": true,
        "placeholder": "user@example.com"
      },
      {
        "name": "password",
        "label": "Password",
        "type": "password",
        "required": true,
        "placeholder": "Enter password"
      }
    ]
  },
  "loginCredentials": {
    "loginUrl": "",
    "loginField": "login",
    "emailField": "email",
    "passwordField": "password",
    "login": "",
    "email": "",
    "password": ""
  }
}
```

## 🔌 API Integration

The application integrates with a Node.js backend running Playwright:

### Backend Endpoints

#### `POST /api/detect-form`
Auto-detect form fields from a URL.

**Request:**
```json
{
  "targetUrl": "https://example.com/form",
  "authentication": {
    "login": "user123",
    "email": "user@example.com",
    "password": "password123",
    "loginUrl": "https://example.com/login"
  }
}
```

**Response:**
```json
{
  "success": true,
  "schema": {
    "title": "Contact Form",
    "description": "Detected from https://example.com/form",
    "fields": [...]
  }
}
```

#### `POST /api/run-test`
Execute automated test with Playwright.

**Request:**
```json
{
  "targetUrl": "https://example.com/form",
  "formSchema": { ... },
  "testData": { "field1": "value1", "field2": "value2" },
  "authentication": { ... }
}
```

**Response:**
```json
{
  "success": true,
  "status": "passed",
  "message": "Form submitted successfully",
  "duration": 2450,
  "timestamp": "2024-01-15T10:35:22Z",
  "screenshot": "data:image/png;base64,...",
  "afterSubmitScreenshot": "data:image/png;base64,...",
  "submittedData": { ... },
  "finalUrl": "...",
  "pageTitle": "...",
  "error": null
}
```

## 🧪 Test Execution

### How It Works

1. **Select Scenario**: Choose a scenario from the list
2. **Fill Test Data**: Enter values for each form field
3. **Configure Authentication**: If required, enter login credentials
4. **Run Test**: Click "Run Test" to execute with Playwright
5. **View Results**: See status, duration, screenshots, and history

### Test Results

Each test execution returns:
- **Status**: `passed`, `failed`, or `error`
- **Duration**: Time taken to complete the test
- **Screenshots**: Before and after form submission
- **Submitted Data**: What was actually sent
- **Final URL**: Where the browser ended up
- **Error Details**: If something went wrong

### Test History

- Stores last 10 test runs per scenario
- Shows status badges and timestamps
- Quick overview of recent test performance
- Helps track changes over time

## 📋 Supported Field Types

| Type | Input | Use Case |
|------|-------|----------|
| `text` | Text input | Names, addresses |
| `email` | Email input | Email addresses |
| `password` | Password input | Passwords |
| `number` | Number input | Age, quantity |
| `tel` | Tel input | Phone numbers |
| `url` | URL input | Website URLs |
| `textarea` | Textarea | Long text, messages |
| `select` | Dropdown | Selection from options |
| `checkbox` | Checkbox | Multiple selections |
| `radio` | Radio button | Single selection |
| `date` | Date picker | Dates |
| `file` | File upload | File attachments |

## 🌐 Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🛠️ Development Notes

### Adding a New Component

1. Create component file in `src/components/`
2. Import styles in the component
3. Export component from component file
4. Import and use in `App.jsx` or parent component

### Adding Styling

- Global styles: `src/styles/main.css`
- Component styles: `src/styles/components.css`
- Use CSS variables for consistency

### Local Storage Operations

```javascript
import { getScenarios, addScenario, updateScenario, deleteScenario, saveTestResult } from './services/storageService'

// Get all scenarios
const scenarios = getScenarios()

// Add new scenario
addScenario(scenarioData)

// Update scenario
updateScenario(updatedScenarioData)

// Delete scenario
deleteScenario(scenarioId)

// Save test result
saveTestResult(scenarioId, testResultData)
```

### Running Tests

```javascript
import { runTest } from './services/testService'

// Execute test
const result = await runTest({
  targetUrl: 'https://example.com/form',
  formSchema: schema,
  testData: data,
  authentication: credentials
})
```

## 📌 Known Limitations

1. **Backend Required** - Requires Node.js backend for Playwright automation
2. **Browser Storage Only** - Data stored in browser LocalStorage (no server persistence)
3. **Single User** - No multi-user support
4. **No File Export** - Cannot export scenarios to file
5. **Limited Test History** - Only stores last 10 test runs per scenario
6. **Screenshot Size** - Large screenshots may impact performance

## 🚧 Next Steps (Phase 3-4)

- [ ] Database persistence (SQL Server/SQLite)
- [ ] Export/import scenarios to JSON files
- [ ] Bulk test execution across multiple scenarios
- [ ] Test scheduling and automation
- [ ] Email notifications for test results
- [ ] Detailed test reports (PDF/Excel export)
- [ ] Multi-user support with authentication
- [ ] API endpoint testing capabilities
- [ ] Visual regression testing
- [ ] Performance testing (load time metrics)
- [ ] Mobile responsive testing
- [ ] Cross-browser testing support

## 📚 Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [Playwright Documentation](https://playwright.dev)
- [Express.js Documentation](https://expressjs.com)
- [CSS Variables](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [LocalStorage API](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)

## 🔧 Backend Server

The application includes a Node.js backend server (`server.js`) that provides:

### Features
- **Form Detection**: Uses Playwright to analyze web forms
- **Test Execution**: Automated form filling and submission
- **Authentication**: Handles login forms automatically
- **Screenshot Capture**: Takes before/after screenshots
- **CORS Support**: Allows frontend communication

### Running the Backend

```bash
# Install dependencies (if needed)
npm install

# Start server
npm run server

# Or run with frontend
npm run dev:full
```

### API Endpoints

- `GET /api/health` - Health check
- `POST /api/detect-form` - Detect form fields
- `POST /api/run-test` - Execute test

### Configuration

- **Port**: 3001 (configurable)
- **Browser**: Chromium (headless)
- **Timeout**: 90 seconds per test
- **Screenshot Format**: PNG (base64 encoded)

## 📄 License

Same as parent BasicTester project.

---

**Happy Testing with Playwright!** 🚀
