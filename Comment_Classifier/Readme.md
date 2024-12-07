# Comment Classification
Comment Classification is the projec to classify the comments accor to the confidence, classification, is it new and its id in the database.

## Installation
1. To use the project firstly you need to create a vertual environment.
```bash
python -m venv .venv
source .venv/bin/activate
```
2. In the next step all required libraries need to be installed.
```bash
pip install -r requirements.txt
```
3. Last step is running the application.
```bash
uvicorn app.main:app --reload
```
### Using Docker (Optionaal)
1. Generate a Docker image.
```bash
docker build -t commend-classifier .
```
2. Run Docker Container
```bash
docker run -d -p 8000:8000 commend-classifier
```

## Usage
To use service of the Projet these cofiguration are important.
 - Request type `http`
 - Request method `POST`
 - Request port `:8000`

 - Request URL `http://localhost:8000/process_comment`

Request parameters are should be sent in the `Json` format.
```json
{
    "comment": "Salom, Menga AISHAning AI servislari yoqaadi."
}
```
comment need to be provied in `comment` parameter and in `str` type to use service.

## Response
Response comes in `json` formaat.
```json
{
    "database_result": {
        "id": 406944,
        "isNew": false
    },
    "prediction_result": {
        "prediction": 1,
        "confidence": 0.7391297435505527
    }
}
```
1. `database_result` - comment details related to database
 - `id` - comment id in database
 - `isNew` - comment is new or existing in database (**true** - accepted, **false** - rejected)
2. `prediction_result` - comment details related to prediction
 - `prediction` - comment's prediction result
 - `confidence` - comment's confidence value between 0 and 1