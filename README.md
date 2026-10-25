# Credit Default ML Lab

A small machine learning demo for estimating credit limits and classifying default risk using a credit-card dataset.

## Live demo

This project is set up to work as a GitHub Pages static site, so it can be viewed from a Pages URL similar to:

https://lupin-codes2.github.io/Kashmala_Project/

The same repository also includes a local FastAPI app for full backend prediction behavior.

## Project structure

- `main.py` — local FastAPI app for running the project on a Python server
- `train_models.py` — trains the regression and classification models
- `app/` — app package containing feature definitions and backend routes
- `app/static/` — frontend assets used by the local Python app
- `index.html` — GitHub Pages-ready landing page
- `styles.css` — page styling
- `app.js` — browser-side interactions for the static demo
- `data/metrics.json` — model metrics used by the static site
- `requirements.txt` — Python dependencies

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Then open:

http://127.0.0.1:8000/

## Train models

```bash
python train_models.py
```

This creates the model artifacts under the `models/` directory.

## GitHub Pages deployment

This repository includes a static landing page at the root, which is compatible with GitHub Pages.

To enable Pages:

1. Open the GitHub repository.
2. Go to Settings → Pages.
3. Set Source to "Deploy from a branch".
4. Choose the `main` branch and the root folder `/`.
5. Save.

The site will then be available at a URL similar to:

https://lupin-codes2.github.io/Kashmala_Project/

## Notes

GitHub Pages does not host Python/FastAPI routes directly, so the static demo is a front-end version of the project. For the full ML API and prediction endpoints, use the local Python app or deploy the FastAPI application to a server that supports Python.
