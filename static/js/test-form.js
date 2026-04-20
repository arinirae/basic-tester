function parseJsonSchema(text) {
  try {
    return JSON.parse(text || "[]");
  } catch (error) {
    return [];
  }
}

function createFieldElement(field) {
  const wrapper = document.createElement("div");
  wrapper.className = "form-block";

  const label = document.createElement("label");
  label.textContent = field.label || field.name;
  wrapper.appendChild(label);

  if (field.type === "textarea") {
    const input = document.createElement("textarea");
    input.name = field.name;
    input.placeholder = field.placeholder || "";
    input.required = field.required || false;
    wrapper.appendChild(input);
    return wrapper;
  }

  if (field.type === "select") {
    const select = document.createElement("select");
    select.name = field.name;
    select.required = field.required || false;
    const options = field.options || [];
    options.forEach(optionValue => {
      const option = document.createElement("option");
      option.value = optionValue;
      option.textContent = optionValue;
      select.appendChild(option);
    });
    wrapper.appendChild(select);
    return wrapper;
  }

  const input = document.createElement("input");
  input.type = field.type || "text";
  input.name = field.name;
  input.placeholder = field.placeholder || "";
  input.required = field.required || false;

  if (field.type === "checkbox") {
    const labelCheckbox = document.createElement("label");
    labelCheckbox.className = "checkbox-field";
    labelCheckbox.appendChild(input);
    labelCheckbox.appendChild(document.createTextNode(field.label || field.name));
    wrapper.appendChild(labelCheckbox);
    return wrapper;
  }

  wrapper.appendChild(input);
  return wrapper;
}

function setLoading(button, isLoading, label) {
  if (!button) return;
  if (isLoading) {
    button.dataset.originalText = button.textContent;
    button.textContent = label || 'Loading...';
    button.disabled = true;
    button.classList.add('loading');
  } else {
    button.textContent = button.dataset.originalText || label || 'Done';
    button.disabled = false;
    button.classList.remove('loading');
  }
}

function getButtonByHandler(handlerName) {
  return Array.from(document.querySelectorAll('button'))
    .find(button => button.getAttribute('onclick') === handlerName || button.dataset.handler === handlerName);
}

function renderSchemaFields() {
  const button = getButtonByHandler('renderSchemaFields()');
  setLoading(button, true, 'Rendering...');

  const schemaTextarea = document.getElementById("schema-json");
  const container = document.getElementById("field-container");
  container.innerHTML = "";

  const schema = parseJsonSchema(schemaTextarea.value);
  if (!Array.isArray(schema) || schema.length === 0) {
    container.innerHTML = "<p>Schema tidak valid atau kosong. Pastikan schema adalah array JSON.</p>";
    setLoading(button, false);
    return;
  }

  schema.forEach(field => {
    const fieldElement = createFieldElement(field);
    container.appendChild(fieldElement);
  });

  setLoading(button, false);
}

async function autoFillFields() {
  const button = getButtonByHandler('autoFillFields()');
  setLoading(button, true, 'Filling...');

  const schemaTextarea = document.getElementById("schema-json");
  const container = document.getElementById("field-container");
  const schema = parseJsonSchema(schemaTextarea.value);
  if (!Array.isArray(schema) || schema.length === 0) {
    setLoading(button, false);
    return;
  }

  try {
    const response = await fetch("/api/generate-values", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({fields: schema}),
    });
    const data = await response.json();
    const values = data.values || {};

    const inputs = container.querySelectorAll("input, textarea, select");
    inputs.forEach(input => {
      if (values.hasOwnProperty(input.name)) {
        if (input.type === "checkbox") {
          input.checked = !!values[input.name];
        } else {
          input.value = values[input.name] ?? "";
        }
      }
    });
  } finally {
    setLoading(button, false);
  }
}

async function regenerateFields() {
  const button = getButtonByHandler('regenerateFields()');
  setLoading(button, true, 'Regenerating...');
  try {
    renderSchemaFields();
    await autoFillFields();
  } finally {
    setLoading(button, false);
  }
}

function prepareRunPayload() {
  const button = document.querySelector('#run-form button[type=submit]');
  setLoading(button, true, 'Running...');

  const container = document.getElementById("field-container");
  const values = [];
  const inputs = container.querySelectorAll("input, textarea, select");
  inputs.forEach(input => {
    if (!input.name) {
      return;
    }
    const value = input.type === "checkbox" ? input.checked : input.value;
    values.push({name: input.name, value});
  });
  document.getElementById("values-json").value = JSON.stringify(values);
}

async function detectFieldsFromUrl() {
  const button = getButtonByHandler('detectFieldsFromUrl()');
  setLoading(button, true, 'Detecting...');

  const targetInput = document.querySelector('input[name="target_url"]');
  if (!targetInput || !targetInput.value) {
    alert('Masukkan Target URL terlebih dahulu.');
    setLoading(button, false);
    return;
  }

  // Collect login configuration if login is required
  const requiresLoginCheckbox = document.querySelector('input[name="requires_login"]');
  const requiresLogin = requiresLoginCheckbox && requiresLoginCheckbox.checked;
  
  const loginConfig = {};
  if (requiresLogin) {
    loginConfig.requires_login = true;
    loginConfig.login_url = document.querySelector('input[name="login_url"]')?.value || '';
    loginConfig.login_username_field = document.querySelector('input[name="login_username_field"]')?.value || '';
    loginConfig.login_email_field = document.querySelector('input[name="login_email_field"]')?.value || '';
    loginConfig.login_password_field = document.querySelector('input[name="login_password_field"]')?.value || '';
    loginConfig.login_username = document.querySelector('input[name="login_username"]')?.value || '';
    loginConfig.login_email = document.querySelector('input[name="login_email"]')?.value || '';
    loginConfig.login_password = document.querySelector('input[name="login_password"]')?.value || '';
  }

  const payload = {
    url: targetInput.value,
    ...loginConfig
  };

  try {
    const response = await fetch('/api/detect-fields', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();
      alert(error.error || 'Gagal mendeteksi field.');
      return;
    }

    const data = await response.json();
    const schemaTextarea = document.getElementById('schema-json');
    schemaTextarea.value = JSON.stringify(data.fields || [], null, 2);
  } finally {
    setLoading(button, false);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const schemaTextarea = document.getElementById('schema-json');
  if (schemaTextarea && document.getElementById('field-container')) {
    renderSchemaFields();
    autoFillFields();
  }
});
