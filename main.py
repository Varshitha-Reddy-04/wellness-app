from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import random

# ================= DATABASE SETUP =================

DATABASE_URL = "sqlite:///./wellness.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class LogDB(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    mood = Column(Integer)
    sleep = Column(Float)
    work_hours = Column(Float)
    screen_time = Column(Float)


Base.metadata.create_all(bind=engine)

# ================= APP =================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= MODEL =================

class Log(BaseModel):
    mood: int
    sleep: float
    work_hours: float
    screen_time: float


# ✅ ADD HERE (just below Log model)

class LogResponse(BaseModel):
    status: str
    burnout_score: int
    insight: str
    suggestions: list[str]
    quote: str
    all_quotes: list[str]
    music: list[str]

# ================= LOGIC =================

def calculate_burnout(log):
    score = 0
    if log.mood <= 2:
        score += 30
    if log.sleep < 6:
        score += 30
    if log.work_hours > 8:
        score += 40
    return score


def get_suggestions(log):
    suggestions = []

    if log.sleep < 6:
        suggestions.append("Try sleeping earlier today 😴")

    if log.work_hours > 8:
        suggestions.append("Take short breaks during work 🧘")

    if log.mood <= 2:
        suggestions.append("Talk to someone you trust ❤️")

    if not suggestions:
        suggestions.append("You're doing great! Keep it up 👍")

    return suggestions


def generate_insight(log):
    if log.sleep < 6 and log.work_hours > 8:
        return "Your stress may be caused by high workload and lack of sleep."
    elif log.mood <= 2:
        return "Your mood has been low. Try taking some time to relax."
    else:
        return "Your routine looks balanced. Keep it up 👍"


def get_emotional_support(log):
    low = [
        "Tough times don’t last, but tough people do 💪",
        "You are stronger than you think 🌟",
        "Every day is a fresh start 🌅"
    ]

    medium = [
        "Keep going, you’re doing great 👍",
        "Small progress is still progress 🚀"
    ]

    high = [
        "You’re doing amazing! Keep shining ✨",
        "Stay positive and spread good vibes 😄"
    ]

    if log.mood <= 2:
        return {
            "quote": random.choice(low),
            "all_quotes": low,
            "music": [
                "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            ]
        }

    elif log.mood == 3:
        return {
            "quote": random.choice(medium),
            "all_quotes": medium,
            "music": [
                "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            ]
        }

    else:
        return {
            "quote": random.choice(high),
            "all_quotes": high,
            "music": []
        }

# ================= ROUTES =================

@app.get("/")
def home():
    return {"message": "Wellness AI is running 🚀"}


@app.post("/log",response_model=LogResponse)
def create_log(log: Log):
    db: Session = SessionLocal()

    # ✅ Save to database
    new_entry = LogDB(
        mood=log.mood,
        sleep=log.sleep,
        work_hours=log.work_hours,
        screen_time=log.screen_time
    )

    db.add(new_entry)
    db.commit()

    # ✅ AI logic
    score = calculate_burnout(log)
    suggestions = get_suggestions(log)
    insight = generate_insight(log)
    support = get_emotional_support(log)

    return {
        "status": "success",
        "burnout_score": score,
        "insight": insight,
        "suggestions": suggestions,
        "quote": support["quote"],
        "all_quotes": support["all_quotes"],
        "music": support["music"]
    }


@app.get("/history")
def get_history():
    db: Session = SessionLocal()
    logs = db.query(LogDB).all()

    return [
        {
            "mood": l.mood,
            "sleep": l.sleep,
            "work_hours": l.work_hours,
            "screen_time": l.screen_time
        }
        for l in logs
    ]