"use strict";

function readForm(form) {
  const values = {};
  for (const [key, value] of new FormData(form).entries()) {
    values[key] = Number(value);
  }
  return values;
}

async function submitPrediction(form) {
  const result = document.getElementById(`${form.id.replace("-form", "")}-result`);
  const button = form.querySelector("button[type='submit']");
  button.disabled = true;
  result.className = "result";
  result.textContent = "Calculating prediction…";

  try {
    const response = await fetch(form.dataset.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(readForm(form)),
    });
    const body = await response.json();
    if (!response.ok) {
      throw new Error(body.detail || "The prediction request failed.");
    }

    result.classList.add("success");
    if (form.id === "regression-form") {
      result.textContent = `Estimated credit limit: NT$ ${Number(body.prediction).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
    } else {
      result.textContent = `Model result: ${body.label} (class ${body.prediction}).`;
    }
  } catch (error) {
    result.classList.add("error");
    result.textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

for (const form of document.querySelectorAll("form[data-endpoint]")) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    submitPrediction(form);
  });
}

async function showMetrics() {
  try {
    const response = await fetch("/api/metrics");
    if (!response.ok) return;
    const metrics = await response.json();
    document.getElementById("r2-score").textContent = Number(metrics.regression_r2).toFixed(3);
    document.getElementById("accuracy-score").textContent = `${(metrics.classification_accuracy * 100).toFixed(1)}%`;
    document.getElementById("test-rows").textContent = Number(metrics.test_rows).toLocaleString();
  } catch {
    // The training command creates this information before the app is run.
  }
}

showMetrics();
