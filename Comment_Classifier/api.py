from venv import logger
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from main import get_or_add_comment, predict_comment

app = FastAPI()

class CommentRequest(BaseModel):
    comment: str

@app.post("/process_comment/")
async def process_comment(request: CommentRequest = Body(...)):
    """
    Process a comment:
    1. Check if it exists in the database or add it.
    2. Predict its sentiment or class.
    """
    comment = request.comment
    logger.info("Received comment: %s", comment)

    try:
        db_result = get_or_add_comment(comment)
        prediction_result = predict_comment(comment)

        response = {
            "database_result": {
                "id": int(db_result["id"]),
                "isNew": db_result["isNew"],
            },
            "prediction_result": {
                "prediction": prediction_result["prediction"],
                "confidence": prediction_result["confidence"],
            },
        }
        logger.info("Response: %s", response)
        return response
    except Exception as e:
        logger.error("Error processing comment: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)