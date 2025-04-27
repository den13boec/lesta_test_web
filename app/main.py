from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import re
# import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    text = contents.decode("utf-8", errors="ignore")

    words = preprocess(text)
    top_words = compute_tf_idf(words)

    return templates.TemplateResponse(
        "index.html", {"request": request, "table": top_words}
    )


def preprocess(text: str) -> list[str]:
    words = re.findall(r"\b\w+\b", text.lower())
    return words


def compute_tf_idf(words: list[str]) -> list[dict]:
    joined = " ".join(words)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([joined])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]

    tf = Counter(words)
    result = []
    for word, score in zip(feature_names, tfidf_scores):
        result.append({"word": word, "tf": tf[word], "idf": score})
    result.sort(key=lambda x: x["idf"], reverse=True)
    return result[:50]
