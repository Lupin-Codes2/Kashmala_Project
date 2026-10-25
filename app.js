"use strict";

function readForm(form) {
  const values = {};
  for (const [key, value] of new FormData(form).entries()) {
    values[key] = Number(value);
  }
  return values;
}

function estimateCreditLimit(values) {
  let total = 45000;
  total += Number(values.sex || 0) * 6000;
  total += Number(values.education || 0) * 3200;
  total += Number(values.marriage || 0) * 1400;
  total += Number(values.age || 0) * 250;
  total += Number(values.pay_0 || 0) * -1200;
  total += Number(values.pay_2 || 0) * -900;
  total += Number(values.bill_amt1 || 0) * 0.16;
  total -= Number(values.pay_amt1 || 0) * 0.52;
  return Math.max(0, total);
}

function classifyDefault(values) {
  let riskScore = 0;
  riskScore += Number(values.limit_bal || 0) < 50000 ? 1 : 0;
  riskScore += Number(values.pay_0 || 0) > 0 ? 1 : 0;
  riskScore += Number(values.pay_2 || 0) > 0 ? 1 : 0;
  riskScore += Number(values.bill_amt1 || 0) > 5000 ? 1 : 0;
  riskScore += Number(values.age || 0) < 30 ? 1 : 0;
  const prediction = riskScore >= 2 ? 1 : 0;
  return prediction;
}

async function showMetrics() {
  try {
    const response = await fetch('./data/metrics.json');
    if (!response.ok) return;
    const metrics = await response.json();
    document.getElementById('r2-score').textContent = Number(metrics.regression_r2).toFixed(3);
    document.getElementById('accuracy-score').textContent = `${(metrics.classification_accuracy * 100).toFixed(1)}%`;
    document.getElementById('test-rows').textContent = Number(metrics.test_rows).toLocaleString();
  } catch {
    // The static demo can still be displayed safely without a backend.
  }
}

function bindForm(formId, kind) {
  const form = document.getElementById(formId);
  if (!form) return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const result = document.getElementById(`${formId.replace('-form', '')}-result`);
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    result.className = 'result';
    result.textContent = 'Calculating prediction…';

    const values = readForm(form);

    try {
      if (kind === 'regression') {
        const prediction = estimateCreditLimit(values);
        result.classList.add('success');
        result.textContent = `Estimated credit limit: NT$ ${Number(prediction).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
      } else {
        const prediction = classifyDefault(values);
        const label = prediction === 1 ? 'Likely to default' : 'Not predicted to default';
        result.classList.add('success');
        result.textContent = `Model result: ${label} (class ${prediction}).`;
      }
    } catch (error) {
      result.classList.add('error');
      result.textContent = error.message || 'Prediction failed.';
    } finally {
      button.disabled = false;
    }
  });
}

bindForm('regression-form', 'regression');
bindForm('classification-form', 'classification');
showMetrics();
