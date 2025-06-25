# app/user_state_store.py
from datetime import datetime, timedelta

# เก็บ user_id -> {"command": ..., "timestamp": ...}
user_states = {}

# ระยะเวลา timeout (หน่วย: นาที)
STATE_TIMEOUT_MINUTES = 5

def set_user_state(user_id: str, command: str):
    user_states[user_id] = {
        "command": command,
        "timestamp": datetime.now()
    }

def get_user_state(user_id: str):
    state = user_states.get(user_id)
    if not state:
        return None

    if is_state_expired(state["timestamp"]):
        clear_user_state(user_id)
        return None

    return state["command"]

def is_state_expired(timestamp: datetime) -> bool:
    return datetime.now() - timestamp > timedelta(minutes=STATE_TIMEOUT_MINUTES)

def has_user_state(user_id: str) -> bool:
    # เช็กว่า user มี state และยังไม่หมดเวลา
    state = user_states.get(user_id)
    if not state:
        return False
    if is_state_expired(state["timestamp"]):
        clear_user_state(user_id)
        return False
    return True

def clear_user_state(user_id: str):
    user_states.pop(user_id, None)
