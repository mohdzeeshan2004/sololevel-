import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import math
import os
import random

# Set page config
st.set_page_config(
    page_title="Daily Tracker - Leveling System",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with enhanced styling
st.markdown("""
    <style>
    .level-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s ease;
    }
    .level-container:hover {
        transform: translateY(-5px);
    }
    .rank-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        transition: transform 0.3s ease;
    }
    .rank-container:hover {
        transform: translateY(-5px);
    }
    .season-container {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 5px 0;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
    }
    .task-completed {
        background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        transition: all 0.3s ease;
        animation: slideIn 0.3s ease;
    }
    .task-pending {
        background: linear-gradient(90deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 4px solid #ffc107;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        transition: all 0.3s ease;
        animation: slideIn 0.3s ease;
    }
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    .achievement-badge {
        display: inline-block;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 10px 16px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        margin: 5px;
        box-shadow: 0 4px 12px rgba(255, 165, 0, 0.3);
        animation: popIn 0.5s ease;
    }
    @keyframes popIn {
        0% {
            transform: scale(0.8);
            opacity: 0;
        }
        50% {
            transform: scale(1.1);
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    .motivation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        font-size: 18px;
        font-style: italic;
    }
    .milestone-card {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    .streak-card {
        background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
        font-weight: bold;
    }
    .reward-notification {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 165, 0, 0.4);
        animation: pulse 0.5s ease;
    }
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    .daily-challenge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        border: 2px solid #FFD700;
    }
    .progress-detail {
        background: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Motivational quotes
MOTIVATIONAL_QUOTES = [
    "🌟 Every small step counts! Keep going!",
    "💪 You're building a better version of yourself!",
    "🚀 Success is the sum of small efforts repeated day after day!",
    "⭐ Your consistency is your superpower!",
    "🔥 Don't break the chain! Keep that streak alive!",
    "🎯 Progress, not perfection!",
    "💎 You're becoming unstoppable!",
    "🏆 Your future self will thank you!",
    "✨ Every task completed is a victory!",
    "🌱 Small daily habits create big life changes!",
    "👑 You are the hero of your own story!",
    "⚡ Discipline is choosing what you want most over what you want now!",
    "🎪 Fun fact: Winners never quit, quitters never win!",
    "🌈 Today's effort = Tomorrow's success!",
    "🎭 Your mind is your greatest superpower!",
]

DAILY_CHALLENGES = [
    {"name": "Power Hour", "description": "Complete 3 tasks in one hour", "reward": 50},
    {"name": "Perfect Day", "description": "Complete ALL tasks for the day", "reward": 100},
    {"name": "Consistency King", "description": "Complete tasks 3 days in a row", "reward": 75},
    {"name": "Early Bird", "description": "Complete a task before 9 AM", "reward": 30},
    {"name": "Night Owl", "description": "Complete a task after 9 PM", "reward": 25},
]

TIER_EMOJIS = {
    1: "🐤", 2: "🦅", 3: "🦁", 4: "🐉", 5: "👑",
    10: "⭐", 20: "💫", 30: "✨", 50: "🌟", 100: "🏆"
}

# Data storage utilities
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def save_user_data(filename="tracker_data.json"):
    """Save user data to JSON file"""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w') as f:
            json.dump(st.session_state.user_data, f, indent=4)
        return True, filepath
    except Exception as e:
        return False, str(e)

def load_user_data(filename="tracker_data.json"):
    """Load user data from JSON file"""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        return None

def get_saved_files():
    """Get list of all saved data files"""
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
        return files
    except:
        return []

def delete_save_file(filename):
    """Delete a saved data file"""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except:
        return False

# Initialize session state
if "user_data" not in st.session_state:
    loaded_data = load_user_data()
    if loaded_data:
        st.session_state.user_data = loaded_data
    else:
        st.session_state.user_data = {
            "current_season": 1,
            "level": 1,
            "experience": 0,
            "exp_needed": 100,
            "rank": "BRONZE",
            "rank_points": 0,
            "daily_tasks": [],
            "completion_history": {},
            "achievements": [],
            "last_level_up": None,
            "last_saved": None,
            "total_tasks_completed": 0,
            "total_exp_earned": 0,
            "best_streak": 0,
            "daily_bonus_claimed": False,
            "last_bonus_date": None,
            "setup_complete": False
        }

# Rank system
RANK_SYSTEM = [
    {"rank": "BRONZE", "min_points": 0, "color": "#CD7F32", "emoji": "🥉"},
    {"rank": "SILVER", "min_points": 100, "color": "#C0C0C0", "emoji": "🥈"},
    {"rank": "GOLD", "min_points": 250, "color": "#FFD700", "emoji": "🥇"},
    {"rank": "PLATINUM", "min_points": 500, "color": "#E5E4E2", "emoji": "💎"},
    {"rank": "DIAMOND", "min_points": 1000, "color": "#B9F2FF", "emoji": "✨"},
    {"rank": "MASTER", "min_points": 2000, "color": "#8B0000", "emoji": "🔥"},
    {"rank": "GRANDMASTER", "min_points": 3500, "color": "#FFD700", "emoji": "⚡"},
    {"rank": "LEGEND", "min_points": 5000, "color": "#FF6347", "emoji": "👑"},
]

DIFFICULTY_COLORS = {
    "common": "#95a5a6",
    "rare": "#3498db",
    "epic": "#9b59b6",
    "legendary": "#f39c12"
}

DIFFICULTY_EXP = {
    "common": 1,
    "rare": 1.5,
    "epic": 2.5,
    "legendary": 5
}

SEASONS = {
    1: {"name": "The Awakening", "start_date": "Jan 1", "end_date": "Mar 31"},
    2: {"name": "Rise of Power", "start_date": "Apr 1", "end_date": "Jun 30"},
    3: {"name": "Dark Shadow", "start_date": "Jul 1", "end_date": "Sep 30"},
    4: {"name": "Eternal Destiny", "start_date": "Oct 1", "end_date": "Dec 31"},
}

CATEGORIES = {
    "fitness": "🏋️",
    "learning": "📚",
    "wellness": "💪",
    "productivity": "⚙️",
    "mindfulness": "🧠",
    "creativity": "🎨",
    "social": "👥",
    "health": "❤️"
}

ACHIEVEMENTS = {
    "first_task": {"name": "First Step", "description": "Complete your first task", "emoji": "👣"},
    "five_tasks": {"name": "Getting Started", "description": "Complete 5 tasks", "emoji": "🚀"},
    "ten_tasks": {"name": "Growing Stronger", "description": "Complete 10 tasks", "emoji": "💪"},
    "fifty_tasks": {"name": "Warrior", "description": "Complete 50 tasks", "emoji": "⚔️"},
    "hundred_tasks": {"name": "Unstoppable", "description": "Complete 100 tasks", "emoji": "⚡"},
    "week_streak": {"name": "On Fire", "description": "Achieve 7-day streak", "emoji": "🔥"},
    "month_streak": {"name": "Unstoppable Force", "description": "Achieve 30-day streak", "emoji": "💥"},
    "level_ten": {"name": "Rising Star", "description": "Reach Level 10", "emoji": "⭐"},
    "rank_gold": {"name": "Golden Champion", "description": "Reach Gold rank", "emoji": "👑"},
    "rank_legend": {"name": "Legendary", "description": "Reach Legend rank", "emoji": "🌟"},
}

def get_current_rank(rank_points):
    """Get current rank based on rank points"""
    for i in range(len(RANK_SYSTEM) - 1, -1, -1):
        if rank_points >= RANK_SYSTEM[i]["min_points"]:
            return RANK_SYSTEM[i]
    return RANK_SYSTEM[0]

def get_exp_needed_for_level(level):
    """Calculate EXP needed to reach next level"""
    return 100 + (level - 1) * 50

def check_achievements():
    """Check and award achievements"""
    user = st.session_state.user_data
    total_completed = user.get("total_tasks_completed", 0)
    
    achievements_to_award = []
    
    conditions = [
        (total_completed == 1, "first_task"),
        (total_completed == 5, "five_tasks"),
        (total_completed == 10, "ten_tasks"),
        (total_completed == 50, "fifty_tasks"),
        (total_completed == 100, "hundred_tasks"),
        (get_completion_streak() == 7, "week_streak"),
        (get_completion_streak() == 30, "month_streak"),
        (user["level"] == 10, "level_ten"),
        (user["rank"] == "GOLD", "rank_gold"),
        (user["rank"] == "LEGEND", "rank_legend"),
    ]
    
    for condition, ach_id in conditions:
        if condition and ach_id not in user["achievements"]:
            user["achievements"].append(ach_id)
            achievements_to_award.append(ach_id)
    
    return achievements_to_award

def add_experience(exp_amount):
    """Add experience and handle level up"""
    user = st.session_state.user_data
    user["experience"] += exp_amount
    user["total_exp_earned"] = user.get("total_exp_earned", 0) + exp_amount
    leveled_up = False
    
    while user["experience"] >= user["exp_needed"]:
        user["experience"] -= user["exp_needed"]
        user["level"] += 1
        user["rank_points"] += 10
        user["exp_needed"] = get_exp_needed_for_level(user["level"])
        user["last_level_up"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        leveled_up = True
    
    new_rank = get_current_rank(user["rank_points"])
    user["rank"] = new_rank["rank"]
    
    return leveled_up

def get_today_key():
    """Get today's date as key"""
    return datetime.now().strftime("%Y-%m-%d")

def mark_task_complete(task_id):
    """Mark a task as complete for today"""
    today = get_today_key()
    
    if today not in st.session_state.user_data["completion_history"]:
        st.session_state.user_data["completion_history"][today] = []
    
    for task in st.session_state.user_data["daily_tasks"]:
        if task["id"] == task_id:
            exp_earned = task["exp"] * DIFFICULTY_EXP.get(task["difficulty"], 1)
            leveled_up = add_experience(int(exp_earned))
            st.session_state.user_data["completion_history"][today].append(task_id)
            st.session_state.user_data["rank_points"] += 5
            st.session_state.user_data["total_tasks_completed"] += 1
            achievements = check_achievements()
            return leveled_up, achievements
    
    return False, []

def get_today_completed():
    """Get completed tasks for today"""
    today = get_today_key()
    return st.session_state.user_data["completion_history"].get(today, [])

def get_completion_streak():
    """Calculate current completion streak"""
    today = datetime.now()
    streak = 0
    
    for i in range(100):
        check_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if check_date in st.session_state.user_data["completion_history"]:
            if len(st.session_state.user_data["completion_history"][check_date]) > 0:
                streak += 1
            else:
                break
        else:
            break
    
    if streak > st.session_state.user_data.get("best_streak", 0):
        st.session_state.user_data["best_streak"] = streak
    
    return streak

def claim_daily_bonus():
    """Claim daily bonus"""
    today = get_today_key()
    last_claimed = st.session_state.user_data.get("last_bonus_date")
    
    if last_claimed != today:
        add_experience(25)
        st.session_state.user_data["daily_bonus_claimed"] = True
        st.session_state.user_data["last_bonus_date"] = today
        save_user_data()
        return True
    return False

# Sidebar
st.sidebar.title("⚔️ Daily Tracker")

col_save1, col_save2 = st.sidebar.columns(2)
with col_save1:
    if st.button("💾 Save", key="save_btn", use_container_width=True):
        success, _ = save_user_data()
        if success:
            st.session_state.user_data["last_saved"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.sidebar.success("✅ Saved!")

with col_save2:
    if st.button("📥 Load", key="load_btn", use_container_width=True):
        loaded = load_user_data()
        if loaded:
            st.session_state.user_data = loaded
            st.sidebar.success("✅ Loaded!")
            st.rerun()

st.sidebar.divider()

# Daily bonus
today = get_today_key()
if st.session_state.user_data.get("last_bonus_date") != today:
    if st.sidebar.button("🎁 Claim Daily Bonus (+25 EXP)", use_container_width=True):
        if claim_daily_bonus():
            st.sidebar.success("🎉 +25 EXP claimed!")
            st.rerun()
else:
    st.sidebar.caption("✅ Daily bonus claimed today!")

st.sidebar.divider()

page = st.sidebar.radio("Navigation", ["🏠 Home", "⚔️ Quests", "📊 Stats", "🏆 Achievements", "💾 Data", "⚙️ Settings"])

# Main Header
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    rank_info = get_current_rank(st.session_state.user_data['rank_points'])
    st.markdown(f"""
    <div class='level-container'>
        <h2>⚔️ LEVEL {st.session_state.user_data['level']}</h2>
        <p>Experience: {st.session_state.user_data['experience']}/{st.session_state.user_data['exp_needed']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    progress = st.session_state.user_data['experience'] / st.session_state.user_data['exp_needed']
    st.progress(min(progress, 1.0))

with col2:
    st.markdown(f"""
    <div class='rank-container'>
        <h2>{rank_info['emoji']} {rank_info['rank']}</h2>
        <p>Rank Points: {st.session_state.user_data['rank_points']}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    season = SEASONS[st.session_state.user_data['current_season']]
    st.markdown(f"""
    <div class='season-container'>
        <h4>Season {st.session_state.user_data['current_season']}</h4>
        <p style='margin: 5px 0;'>{season['name']}</p>
        <small>{season['start_date']} - {season['end_date']}</small>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Daily Motivation
st.markdown(f"""
<div class='motivation-card'>
✨ {random.choice(MOTIVATIONAL_QUOTES)} ✨
</div>
""", unsafe_allow_html=True)

# PAGE: Home/Dashboard
if page == "🏠 Home":
    if len(st.session_state.user_data["daily_tasks"]) == 0:
        col1, col2 = st.columns(2)
        with col1:
            st.warning("⚠️ No quests yet! Create your first quest to begin your journey!")
        with col2:
            if st.button("➕ Create First Quest", use_container_width=True):
                st.switch_page("pages/quests")
    else:
        # Stats row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Tasks", len(st.session_state.user_data["daily_tasks"]))
        
        with col2:
            today_completed = len(get_today_completed())
            st.metric("✅ Today", f"{today_completed}/{len(st.session_state.user_data['daily_tasks'])}")
        
        with col3:
            streak = get_completion_streak()
            st.metric("🔥 Streak", f"{streak} days")
        
        with col4:
            next_rank_idx = next((i for i, r in enumerate(RANK_SYSTEM) if r["rank"] == st.session_state.user_data['rank']), 0)
            if next_rank_idx < len(RANK_SYSTEM) - 1:
                pts_to_next = RANK_SYSTEM[next_rank_idx + 1]["min_points"] - st.session_state.user_data['rank_points']
                st.metric("🎯 Next Rank", f"{pts_to_next} pts")
            else:
                st.metric("🎯 Next Rank", "MAX ✨")
        
        st.divider()
        
        # Streak visual
        streak = get_completion_streak()
        if streak >= 3:
            st.markdown(f"""
            <div class='streak-card'>
            🔥 AMAZING! You're on a {streak}-day streak! 🔥
            </div>
            """, unsafe_allow_html=True)
        elif streak >= 1:
            st.markdown(f"""
            <div class='milestone-card'>
            ⭐ Great start! {streak} day streak going! Keep it up!
            </div>
            """, unsafe_allow_html=True)
        
        st.subheader("📋 Today's Quests")
        today_tasks = get_today_completed()
        completion_rate = (len(today_tasks) / len(st.session_state.user_data["daily_tasks"])) * 100
        
        st.progress(completion_rate / 100, text=f"Progress: {completion_rate:.0f}%")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            selected_category = st.selectbox("Filter by Category", ["All"] + list(CATEGORIES.keys()), key="dashboard_filter")
        
        for task in st.session_state.user_data["daily_tasks"]:
            if selected_category != "All" and task.get("category") != selected_category:
                continue
            
            is_completed = task["id"] in today_tasks
            color = "task-completed" if is_completed else "task-pending"
            status = "✅" if is_completed else "⭕"
            exp_amount = task["exp"] * DIFFICULTY_EXP.get(task["difficulty"], 1)
            category_icon = CATEGORIES.get(task.get("category"), "📌")
            
            st.markdown(f"""
            <div class='{color}'>
                <b>{status} {task['name']}</b> {category_icon} - {int(exp_amount)} EXP [{task['difficulty'].upper()}]
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Level Progress")
            fig = go.Figure(data=[
                go.Bar(
                    x=["Current", "Needed"],
                    y=[st.session_state.user_data['experience'], st.session_state.user_data['exp_needed']],
                    marker_color=['#667eea', '#764ba2']
                )
            ])
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🏆 Rank Progression")
            rank_data = []
            for rank in RANK_SYSTEM:
                rank_data.append({
                    "Rank": rank["rank"],
                    "Points": rank["min_points"],
                    "Current": st.session_state.user_data['rank_points'] >= rank["min_points"]
                })
            
            df_ranks = pd.DataFrame(rank_data)
            fig = px.bar(
                df_ranks,
                x="Rank",
                y="Points",
                color="Current",
                color_discrete_map={True: '#FF6347', False: '#95a5a6'}
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# PAGE: Quests
elif page == "⚔️ Quests":
    st.subheader("⚔️ Daily Quests")
    st.write(f"**Current Date:** {datetime.now().strftime('%A, %B %d, %Y')}")
    
    today_completed = get_today_completed()
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_category = st.selectbox("Filter by Category", ["All"] + list(CATEGORIES.keys()), key="quests_filter")
    
    with col2:
        if len(st.session_state.user_data["daily_tasks"]) > 0:
            completion_rate = (len(today_completed) / len(st.session_state.user_data["daily_tasks"])) * 100
            st.metric("Completion", f"{completion_rate:.0f}%")
    
    with col3:
        if st.button("📊 Summary"):
            st.session_state.show_summary = not st.session_state.get("show_summary", False)
    
    if st.session_state.get("show_summary", False) and len(st.session_state.user_data["daily_tasks"]) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Tasks:** {len(today_completed)}")
        with col2:
            total_exp = sum(task["exp"] * DIFFICULTY_EXP.get(task["difficulty"], 1) 
                           for task in st.session_state.user_data["daily_tasks"] 
                           if task["id"] in today_completed)
            st.info(f"**EXP:** {int(total_exp)}")
        with col3:
            st.info(f"**Streak:** {get_completion_streak()} 🔥")
    
    st.divider()
    
    if len(st.session_state.user_data["daily_tasks"]) == 0:
        st.info("📝 No quests yet! Add your first quest below.")
    else:
        for task in st.session_state.user_data["daily_tasks"]:
            if selected_category != "All" and task.get("category") != selected_category:
                continue
            
            is_completed = task["id"] in today_completed
            exp_amount = task["exp"] * DIFFICULTY_EXP.get(task["difficulty"], 1)
            category_icon = CATEGORIES.get(task.get("category"), "📌")
            
            col1, col2, col3, col4, col5 = st.columns([3, 1, 0.8, 0.8, 0.8])
            
            with col1:
                difficulty_color = DIFFICULTY_COLORS.get(task["difficulty"], "#95a5a6")
                status_icon = "✅" if is_completed else "⭕"
                st.markdown(f"""
                **{status_icon} {task['name']}** {category_icon}  
                <span style='color: {difficulty_color}; font-weight: bold;'>[{task['difficulty'].upper()}]</span> - {int(exp_amount)} EXP
                """, unsafe_allow_html=True)
            
            with col2:
                st.write(f"🎯 +{int(exp_amount)}" if not is_completed else "✨")
            
            with col3:
                if not is_completed:
                    if st.button("✅", key=f"task_{task['id']}"):
                        leveled_up, achievements = mark_task_complete(task['id'])
                        if leveled_up:
                            st.balloons()
                        if achievements:
                            st.success(f"🏆 Achievement unlocked!")
                        save_user_data()
                        st.rerun()
                else:
                    st.write("✔️")
            
            with col4:
                if st.button("❌", key=f"undo_{task['id']}"):
                    today = get_today_key()
                    if today in st.session_state.user_data["completion_history"]:
                        if task["id"] in st.session_state.user_data["completion_history"][today]:
                            st.session_state.user_data["completion_history"][today].remove(task["id"])
                            save_user_data()
                            st.rerun()
            
            with col5:
                if st.button("🗑️", key=f"delete_{task['id']}"):
                    st.session_state.user_data["daily_tasks"] = [
                        t for t in st.session_state.user_data["daily_tasks"] if t["id"] != task["id"]
                    ]
                    save_user_data()
                    st.rerun()
    
    st.divider()
    
    st.subheader("➕ Add New Quest")
    with st.expander("Click to create a new quest"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_task_name = st.text_input("Quest Name", placeholder="e.g., Morning Run")
        
        with col2:
            new_category = st.selectbox("Category", list(CATEGORIES.keys()), key="new_task_category")
        
        col3, col4 = st.columns(2)
        
        with col3:
            new_difficulty = st.selectbox("Difficulty", ["common", "rare", "epic", "legendary"], key="new_task_difficulty")
        
        with col4:
            new_exp = st.number_input("Base EXP", min_value=5, max_value=200, value=10, step=5)
        
        if st.button("✨ Add Quest", type="primary"):
            if new_task_name:
                new_id = max([t["id"] for t in st.session_state.user_data["daily_tasks"]], default=0) + 1
                st.session_state.user_data["daily_tasks"].append({
                    "id": new_id,
                    "name": new_task_name,
                    "difficulty": new_difficulty,
                    "exp": new_exp,
                    "category": new_category
                })
                save_user_data()
                st.success(f"Quest '{new_task_name}' added! ⚔️")
                st.rerun()

# PAGE: Statistics
elif page == "📊 Stats":
    st.subheader("📊 Statistics & History")
    
    if len(st.session_state.user_data["completion_history"]) == 0:
        st.info("📈 Complete some tasks to see stats!")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📅 Days Active", len(st.session_state.user_data["completion_history"]))
        
        with col2:
            st.metric("✅ Total Completed", st.session_state.user_data.get("total_tasks_completed", 0))
        
        with col3:
            st.metric("⭐ Total EXP", st.session_state.user_data.get("total_exp_earned", 0))
        
        with col4:
            st.metric("🔥 Best Streak", st.session_state.user_data.get("best_streak", 0))
        
        st.divider()
        
        tab1, tab2, tab3 = st.tabs(["Activity", "Tasks", "Categories"])
        
        with tab1:
            today = datetime.now()
            heatmap_data = []
            
            for i in range(29, -1, -1):
                date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                completed = len(st.session_state.user_data["completion_history"].get(date, []))
                heatmap_data.append({"Date": date, "Tasks": completed})
            
            df_heatmap = pd.DataFrame(heatmap_data)
            fig = px.bar(df_heatmap, x="Date", y="Tasks", color="Tasks", color_continuous_scale="Viridis")
            fig.update_layout(height=300, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            task_completion = defaultdict(int)
            for date, task_ids in st.session_state.user_data["completion_history"].items():
                for task_id in task_ids:
                    task_completion[task_id] += 1
            
            if task_completion and len(st.session_state.user_data["daily_tasks"]) > 0:
                stats_data = []
                for task in st.session_state.user_data["daily_tasks"]:
                    stats_data.append({
                        "Quest": task["name"],
                        "Completed": task_completion.get(task["id"], 0),
                        "Difficulty": task["difficulty"]
                    })
                
                df_stats = pd.DataFrame(stats_data).sort_values("Completed", ascending=False)
                fig = px.bar(df_stats, x="Quest", y="Completed", color="Difficulty", color_discrete_map=DIFFICULTY_COLORS)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            category_completion = defaultdict(int)
            for date, task_ids in st.session_state.user_data["completion_history"].items():
                for task_id in task_ids:
                    for task in st.session_state.user_data["daily_tasks"]:
                        if task["id"] == task_id:
                            category_completion[task.get("category", "other")] += 1
            
            if category_completion:
                cat_data = [{"Category": cat, "Count": count} for cat, count in category_completion.items()]
                df_cat = pd.DataFrame(cat_data)
                fig = px.pie(df_cat, values="Count", names="Category")
                st.plotly_chart(fig, use_container_width=True)

# PAGE: Achievements
elif page == "🏆 Achievements":
    st.subheader("🏆 Achievements & Milestones")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("✅ Completed", st.session_state.user_data.get("total_tasks_completed", 0))
    
    with col2:
        st.metric("🏅 Achievements", f"{len(st.session_state.user_data['achievements'])}/{len(ACHIEVEMENTS)}")
    
    with col3:
        st.metric("🔥 Streak", f"{get_completion_streak()} days")
    
    with col4:
        st.metric("⭐ Level", st.session_state.user_data['level'])
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 🎖️ Earned Achievements")
        if st.session_state.user_data["achievements"]:
            for ach_id in st.session_state.user_data["achievements"]:
                ach = ACHIEVEMENTS.get(ach_id)
                if ach:
                    st.markdown(f"<div class='achievement-badge'>{ach['emoji']} {ach['name']}</div>", unsafe_allow_html=True)
                    st.caption(ach["description"])
        else:
            st.info("🚀 Start completing tasks!")
    
    with col2:
        st.write("### 🎯 Next Achievements")
        next_count = 0
        for ach_id, ach in ACHIEVEMENTS.items():
            if ach_id not in st.session_state.user_data["achievements"] and next_count < 5:
                st.write(f"**{ach['emoji']} {ach['name']}**")
                st.caption(ach["description"])
                next_count += 1
    
    st.divider()
    
    st.write("### 📈 Progress")
    total_tasks = st.session_state.user_data.get("total_tasks_completed", 0)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.progress(min(total_tasks / 100, 1.0), text=f"{total_tasks}/100")
        st.caption("Unstoppable")
    
    with col2:
        streak = get_completion_streak()
        st.progress(min(streak / 30, 1.0), text=f"{streak}/30")
        st.caption("Month Streak")
    
    with col3:
        st.progress(st.session_state.user_data['rank_points'] / 5000, text=f"{st.session_state.user_data['rank_points']}/5000")
        st.caption("Legend Rank")

# PAGE: Data Manager
elif page == "💾 Data":
    st.subheader("💾 Data Management")
    
    tab1, tab2 = st.tabs(["Save/Load", "Download/Upload"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Now", use_container_width=True):
                save_user_data()
                st.session_state.user_data["last_saved"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success("✅ Saved!")
        
        with col2:
            if st.button("📥 Load Now", use_container_width=True):
                loaded = load_user_data()
                if loaded:
                    st.session_state.user_data = loaded
                    st.success("✅ Loaded!")
                    st.rerun()
        
        if st.session_state.user_data.get("last_saved"):
            st.caption(f"Last saved: {st.session_state.user_data['last_saved']}")
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            json_data = json.dumps(st.session_state.user_data, indent=4)
            st.download_button("📥 Download JSON", json_data, file_name=f"tracker_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json")
        
        with col2:
            uploaded = st.file_uploader("📤 Upload JSON", type="json")
            if uploaded:
                try:
                    uploaded_data = json.load(uploaded)
                    if st.button("Load Uploaded", key="load_upload"):
                        st.session_state.user_data = uploaded_data
                        save_user_data()
                        st.success("✅ Loaded!")
                        st.rerun()
                except:
                    st.error("Invalid JSON")

# PAGE: Settings
elif page == "⚙️ Settings":
    st.subheader("⚙️ Settings")
    
    tab1, tab2 = st.tabs(["Profile", "Advanced"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.write("### Profile")
            username = st.text_input("Username", "Adventurer")
            if st.session_state.user_data.get("last_level_up"):
                st.caption(f"Last level up: {st.session_state.user_data['last_level_up']}")
        
        with col2:
            st.write("### Stats")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total EXP", st.session_state.user_data.get("total_exp_earned", 0))
            with col_b:
                st.metric("Days Active", len(st.session_state.user_data["completion_history"]))
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Progress", type="secondary"):
                if st.checkbox("Confirm reset"):
                    st.session_state.user_data = {
                        "current_season": 1,
                        "level": 1,
                        "experience": 0,
                        "exp_needed": 100,
                        "rank": "BRONZE",
                        "rank_points": 0,
                        "daily_tasks": [],
                        "completion_history": {},
                        "achievements": [],
                        "last_level_up": None,
                        "last_saved": None,
                        "total_tasks_completed": 0,
                        "total_exp_earned": 0,
                        "best_streak": 0,
                        "setup_complete": False
                    }
                    save_user_data()
                    st.rerun()
        
        with col2:
            new_season = st.selectbox("Season", list(SEASONS.keys()))
            if st.button("🎮 New Season", type="secondary"):
                st.session_state.user_data["current_season"] = new_season
                st.session_state.user_data["level"] = 1
                st.session_state.user_data["experience"] = 0
                st.session_state.user_data["rank_points"] = 0
                st.session_state.user_data["completion_history"] = {}
                save_user_data()
                st.rerun()
        
        st.divider()
        st.info("""
        **Daily Tracker v5.0** 🚀
        
        ✨ Features:
        - 🎮 8-Tier Ranking System
        - 🏆 10+ Achievements
        - 📊 Advanced Statistics
        - 💾 Persistent Data Storage
        - 🎁 Daily Bonus Rewards
        - 📈 Progress Tracking
        - 🔥 Streak Counter
        - 💪 Motivation & Inspiration
        """)

st.sidebar.divider()
st.sidebar.write("**Made by Mohd Zeeshan Khan ⚔️ for Daily Champions**")
