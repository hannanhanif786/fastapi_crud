import uvicorn
from fastapi import FastAPI
from user import user_view

app = FastAPI()
app.include_router(user_view.router, prefix="/user", tags=["user"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)

