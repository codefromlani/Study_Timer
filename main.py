from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI(title="Aesthetic Study Timer")

# Data models
class Timer(BaseModel):
    duration: int # duration in minutes
    start_time: datetime | None = None
    is_running: bool = False

class StudySession(BaseModel):
    start_time: datetime
    end_time: datetime | None = None
    duration: int
    completed: bool = False

class Achievement(BaseModel):
    id: str
    name: str
    description: str
    icon: str # Unicode icon representation
    unlocked: bool = False
    unlocked_date: datetime | None = None

class UserStats(BaseModel):
    total_study_time: int = 0 # in minutes
    current_streak: int = 0
    longest_streak: int = 0
    last_study_date: datetime | None = None
    achievements: Dict[str, Achievement] = {}


# In-memory storage
active_timer = Timer(duration=25) # Default 25 min timer
study_sessions: List[StudySession] = []
user_stats = UserStats()

# Achievement definitions
ACHIEVEMENTS = {
    "first_session": Achievement(
        id="first_session",
        name="First Steps",
        description="Complete your first study session",
        icon="🌱"
    ),
    "three_day_streak": Achievement(
        id="three_day_streak",
        name="Consistent Learner",
        description="Maintain a 3-day study streak",
         icon="🔥"
    ),
    "week_streak": Achievement(
        id="week_streak",
        name="Weekly Warrior",
        description="Maintain a 7-day study streak",
         icon="⚔️"
    ),
    "study_master": Achievement(
        id="study_master",
        name="Study Master",
        description="Complete 10 hours of studying",
         icon="👑"
    )
}


@app.get("/")
async def root():
    return{"message": "Welcome to Aesthetic Study Timer!"}

@app.post("/timer/start")
async def start_timer(duration: int = 25):
    """Start a new study timer"""
    global active_timer
    active_timer = Timer(duration=duration, start_time=datetime.now(), is_running=True)
    return active_timer

@app.get("/timer/status")
async def get_timer_status():
    """Get current timer status"""
    if not active_timer.is_running:
        return {"status": "stopped", "remaining": 0}
    
    elapsed = datetime.now() - active_timer.start_time
    remaining = timedelta(minutes=active_timer.duration) - elapsed

    if remaining.total_seconds() <= 0:
        active_timer.is_running = False
        return {"status": "completed", "remaining": 0}
    
    return{
        "status": "running",
        "remaining_seconds": int(remaining.total_seconds()),
        "remaining_formatted": str(timedelta(seconds=int(remaining.total_seconds())))
    }

@app.post("/timer/stop")
async def stop_timer():
    """Stop the current timer"""
    global active_timer
    if not active_timer.is_running:
        raise HTTPException(status_code=400, detail="Timer is not running")
    
    active_timer.is_running = False

    # Record the study session
    session = StudySession(
        start_time=active_timer.start_time,
        end_time=datetime.now(),
        duration=active_timer.duration,
        completed=True
    )
    study_sessions.append(session)

    return {"message": "Timer stopped successfully"}