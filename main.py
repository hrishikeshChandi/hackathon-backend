import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from routers import uploads, scraper
from config.constants import HOST, PORT, MODULE

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scraper.router)
app.include_router(uploads.router)

if __name__ == "__main__":
    uvicorn.run(MODULE, host=HOST, port=PORT, reload=True)
