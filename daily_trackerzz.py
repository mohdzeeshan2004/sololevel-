import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import math

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
    .task-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 15px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    .task-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
    .exp-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        transition: width 0.5s ease;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "user_data" not in st.session_state:
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
        "setup_complete": False
    }

# Rank system (similar to PUBG)
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

# Season info
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

# Achievements system
ACHIEVEMENTS = {
    "first_task": {"name": "First Step", "description": "Complete your first task", "emoji": "👣"},
    "five_tasks": {"name": "Getting Started", "description": "Complete 5 tasks", "emoji": "🚀"},
    "ten_tasks": {"name": "Growing Stronger", "description": "Complete 10 tasks", "emoji": "💪"},
    "fifty_tasks": {"name": "Warrior", "description": "Complete 50 tasks", "emoji": "⚔️"},
    "hundred_tasks": {"name": "Unstoppable", "description": "Complete 100 tasks", "emoji": "⚡"},
    "week_streak": {"name": "On Fire", "description": "Achieve 7-day streak", "emoji": "🔥"},
    "level_ten": {"name": "Rising Star", "description": "Reach Level 10", "emoji": "⭐"},
    "rank_gold": {"name": "Golden Champion", "description": "Reach Gold rank", "emoji": "👑"},
}

def get_current_rank(rank_points):
    """Get current rank based on rank points"""
    for i in range(len(RANK_SYSTEM) - 1, -1, -1):
        if rank_points >= RANK_SYSTEM[i]["min_points"]:
            return RANK_SYSTEM[i]
    return RANK_SYSTEM[0]

def get_exp_needed_for_level(level):
    """Calculate EXP needed to reach next level (scales with level)"""
    return 100 + (level - 1) * 50

def check_achievements():
    """Check and award achievements"""
    user = st.session_state.user_data
    total_completed = sum(len(tasks) for tasks in user["completion_history"].values())
    
    achievements_to_award = []
    
    if total_completed == 1 and "first_task" not in user["achievements"]:
        user["achievements"].append("first_task")
        achievements_to_award.append("first_task")
    elif total_completed == 5 and "five_tasks" not in user["achievements"]:
        user["achievements"].append("five_tasks")
        achievements_to_award.append("five_tasks")
    elif total_completed == 10 and "ten_tasks" not in user["achievements"]:
        user["achievements"].append("ten_tasks")
        achievements_to_award.append("ten_tasks")
    elif total_completed == 50 and "fifty_tasks" not in user["achievements"]:
        user["achievements"].append("fifty_tasks")
        achievements_to_award.append("fifty_tasks")
    elif total_completed == 100 and "hundred_tasks" not in user["achievements"]:
        user["achievements"].append("hundred_tasks")
        achievements_to_award.append("hundred_tasks")
    elif get_completion_streak() == 7 and "week_streak" not in user["achievements"]:
        user["achievements"].append("week_streak")
        achievements_to_award.append("week_streak")
    elif user["level"] == 10 and "level_ten" not in user["achievements"]:
        user["achievements"].append("level_ten")
        achievements_to_award.append("level_ten")
    elif user["rank"] == "GOLD" and "rank_gold" not in user["achievements"]:
        user["achievements"].append("rank_gold")
        achievements_to_award.append("rank_gold")
    
    return achievements_to_award

def add_experience(exp_amount):
    """Add experience and handle level up"""
    user = st.session_state.user_data
    user["experience"] += exp_amount
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
    
    return streak

# Sidebar Navigation
st.sidebar.title("⚔️ Daily Tracker")
page = st.sidebar.radio("Navigation", ["Dashboard", "Daily Quests", "Statistics", "Achievements", "Settings"])

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

# PAGE: Dashboard
if page == "Dashboard":
    if len(st.session_state.user_data["daily_tasks"]) == 0:
        st.warning("⚠️ No tasks created yet! Go to Daily Quests to add your first task.")
        st.info("👉 Click on 'Daily Quests' in the sidebar to get started!")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Tasks", len(st.session_state.user_data["daily_tasks"]))
        
        with col2:
            today_completed = len(get_today_completed())
            st.metric("✅ Today Completed", f"{today_completed}/{len(st.session_state.user_data['daily_tasks'])}")
        
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
        
        # Today's Tasks Preview with Categories
        st.subheader("📋 Today's Quests")
        today_tasks = get_today_completed()
        
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

# PAGE: Daily Quests
elif page == "Daily Quests":
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
        if st.button("📊 Show Summary", key="summary_btn"):
            st.session_state.show_summary = not st.session_state.get("show_summary", False)
    
    if st.session_state.get("show_summary", False) and len(st.session_state.user_data["daily_tasks"]) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Tasks Completed:** {len(today_completed)}")
        with col2:
            total_exp_today = sum(task["exp"] * DIFFICULTY_EXP.get(task["difficulty"], 1) 
                                 for task in st.session_state.user_data["daily_tasks"] 
                                 if task["id"] in today_completed)
            st.info(f"**EXP Earned:** {int(total_exp_today)}")
        with col3:
            st.info(f"**Streak:** {get_completion_streak()} 🔥")
    
    st.divider()
    
    if len(st.session_state.user_data["daily_tasks"]) == 0:
        st.info("📝 No quests yet! Add your first quest below to get started.")
    else:
        # Display tasks with completion buttons
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
                    if st.button("✅", key=f"task_{task['id']}", help="Complete this task"):
                        leveled_up, achievements = mark_task_complete(task['id'])
                        if leveled_up:
                            st.balloons()
                        if achievements:
                            st.success(f"🏆 Achievement unlocked!")
                        st.rerun()
                else:
                    st.write("✔️")
            
            with col4:
                if st.button("❌", key=f"undo_{task['id']}", help="Undo completion"):
                    today = get_today_key()
                    if today in st.session_state.user_data["completion_history"]:
                        if task["id"] in st.session_state.user_data["completion_history"][today]:
                            st.session_state.user_data["completion_history"][today].remove(task["id"])
                            st.rerun()
            
            with col5:
                if st.button("🗑️", key=f"delete_{task['id']}", help="Delete this task"):
                    st.session_state.user_data["daily_tasks"] = [
                        t for t in st.session_state.user_data["daily_tasks"] if t["id"] != task["id"]
                    ]
                    st.rerun()
    
    st.divider()
    
    # Add new task with expandable form
    st.subheader("➕ Add New Quest")
    with st.expander("Click to create a new quest", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            new_task_name = st.text_input("Quest Name", placeholder="e.g., Morning Run, Read 30 minutes")
        
        with col2:
            new_category = st.selectbox("Category", list(CATEGORIES.keys()), key="new_task_category")
        
        col3, col4 = st.columns(2)
        
        with col3:
            new_difficulty = st.selectbox("Difficulty", ["common", "rare", "epic", "legendary"], key="new_task_difficulty")
        
        with col4:
            new_exp = st.number_input("Base EXP", min_value=5, max_value=200, value=10, step=5, key="new_task_exp")
        
        col5, col6 = st.columns([1, 1])
        
        with col5:
            if st.button("✨ Add Quest", type="primary", key="add_quest_btn"):
                if new_task_name:
                    new_id = max([t["id"] for t in st.session_state.user_data["daily_tasks"]], default=0) + 1
                    st.session_state.user_data["daily_tasks"].append({
                        "id": new_id,
                        "name": new_task_name,
                        "difficulty": new_difficulty,
                        "exp": new_exp,
                        "category": new_category
                    })
                    st.success(f"Quest '{new_task_name}' added! ⚔️")
                    st.rerun()
                else:
                    st.error("Please enter a quest name!")

# PAGE: Statistics
elif page == "Statistics":
    st.subheader("📊 Statistics & History")
    
    if len(st.session_state.user_data["completion_history"]) == 0:
        st.info("📈 Complete some tasks to see your statistics!")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_days = len(st.session_state.user_data["completion_history"])
            st.metric("📅 Active Days", total_days)
        
        with col2:
            total_tasks_completed = sum(len(tasks) for tasks in st.session_state.user_data["completion_history"].values())
            st.metric("✅ Total Tasks Completed", total_tasks_completed)
        
        with col3:
            avg_per_day = total_tasks_completed / total_days if total_days > 0 else 0
            st.metric("📈 Avg Tasks/Day", f"{avg_per_day:.1f}")
        
        st.divider()
        
        # Tabs for different stats
        tab1, tab2, tab3 = st.tabs(["Activity", "Task Performance", "Category Breakdown"])
        
        with tab1:
            if st.session_state.user_data["completion_history"]:
                st.subheader("📅 Last 30 Days Activity")
                
                today = datetime.now()
                heatmap_data = []
                
                for i in range(29, -1, -1):
                    date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                    completed = len(st.session_state.user_data["completion_history"].get(date, []))
                    heatmap_data.append({
                        "Date": date,
                        "Tasks": completed,
                    })
                
                df_heatmap = pd.DataFrame(heatmap_data)
                
                fig = px.bar(
                    df_heatmap,
                    x="Date",
                    y="Tasks",
                    color="Tasks",
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(height=300, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("🎯 Task Statistics")
            
            task_completion = defaultdict(int)
            for date, task_ids in st.session_state.user_data["completion_history"].items():
                for task_id in task_ids:
                    task_completion[task_id] += 1
            
            if task_completion and len(st.session_state.user_data["daily_tasks"]) > 0:
                stats_data = []
                for task in st.session_state.user_data["daily_tasks"]:
                    completed = task_completion.get(task["id"], 0)
                    stats_data.append({
                        "Quest": task["name"],
                        "Completed": completed,
                        "Difficulty": task["difficulty"]
                    })
                
                df_stats = pd.DataFrame(stats_data).sort_values("Completed", ascending=False)
                
                fig = px.bar(
                    df_stats,
                    x="Quest",
                    y="Completed",
                    color="Difficulty",
                    color_discrete_map=DIFFICULTY_COLORS
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("📂 Completion by Category")
            
            category_completion = defaultdict(int)
            for date, task_ids in st.session_state.user_data["completion_history"].items():
                for task_id in task_ids:
                    for task in st.session_state.user_data["daily_tasks"]:
                        if task["id"] == task_id:
                            category_completion[task.get("category", "other")] += 1
            
            if category_completion:
                cat_data = [{"Category": cat, "Count": count} for cat, count in category_completion.items()]
                df_cat = pd.DataFrame(cat_data)
                
                fig = px.pie(df_cat, values="Count", names="Category", title="Completion Distribution")
                st.plotly_chart(fig, use_container_width=True)

# PAGE: Achievements
elif page == "Achievements":
    st.subheader("🏆 Achievements & Milestones")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_completed = sum(len(tasks) for tasks in st.session_state.user_data["completion_history"].values())
        st.metric("Total Completed", total_completed)
    
    with col2:
        achievements_earned = len(st.session_state.user_data["achievements"])
        st.metric("Achievements", f"{achievements_earned}/{len(ACHIEVEMENTS)}")
    
    with col3:
        st.metric("Current Streak", f"{get_completion_streak()} 🔥")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 🎖️ Earned Achievements")
        if st.session_state.user_data["achievements"]:
            for ach_id in st.session_state.user_data["achievements"]:
                ach = ACHIEVEMENTS.get(ach_id)
                if ach:
                    st.markdown(f"""
                    <div class='achievement-badge'>
                    {ach['emoji']} {ach['name']}
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(ach["description"])
        else:
            st.info("Start completing tasks to earn achievements!")
    
    with col2:
        st.write("### 🎯 Next Achievements")
        next_found = False
        for ach_id, ach in ACHIEVEMENTS.items():
            if ach_id not in st.session_state.user_data["achievements"]:
                st.write(f"**{ach['emoji']} {ach['name']}**")
                st.caption(ach["description"])
                next_found = True
                if not next_found:
                    break
        
        if not next_found:
            st.success("🎉 You've unlocked all achievements!")
    
    st.divider()
    
    # Progress towards achievements
    st.write("### 📈 Progress Towards Achievements")
    
    total_tasks = sum(len(tasks) for tasks in st.session_state.user_data["completion_history"].values())
    
    cols = st.columns(2)
    
    with cols[0]:
        st.write("**Tasks Completed Progress**")
        st.progress(min(total_tasks / 100, 1.0), text=f"{total_tasks}/100")
        st.caption("Milestone: 100 tasks for 'Unstoppable'")
    
    with cols[1]:
        st.write("**Streak Progress**")
        streak = get_completion_streak()
        st.progress(min(streak / 7, 1.0), text=f"{streak}/7 days")
        st.caption("Milestone: 7-day streak for 'On Fire'")

# PAGE: Settings
elif page == "Settings":
    st.subheader("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["Profile", "Manage Tasks", "Advanced"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### User Profile")
            username = st.text_input("Username", value="Adventurer", key="username_input")
            
            if st.session_state.user_data.get("last_level_up"):
                st.caption(f"⏰ Last level up: {st.session_state.user_data['last_level_up']}")
        
        with col2:
            st.write("### Quick Stats")
            total_exp = sum(len(tasks) for tasks in st.session_state.user_data["completion_history"].values()) * 10
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total EXP Earned", int(total_exp))
            with col_b:
                st.metric("Days Active", len(st.session_state.user_data["completion_history"]))
    
    with tab2:
        st.write("### Manage Your Quests")
        
        if len(st.session_state.user_data["daily_tasks"]) > 0:
            task_to_edit = st.selectbox("Select a quest to manage", 
                                         [t["name"] for t in st.session_state.user_data["daily_tasks"]])
            
            selected_task = next((t for t in st.session_state.user_data["daily_tasks"] if t["name"] == task_to_edit), None)
            
            if selected_task:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"🗑️ Delete '{task_to_edit}'", type="secondary"):
                        st.session_state.user_data["daily_tasks"] = [
                            t for t in st.session_state.user_data["daily_tasks"] if t["id"] != selected_task["id"]
                        ]
                        st.success("Quest deleted!")
                        st.rerun()
                
                with col2:
                    if st.button(f"📋 View Details", key="view_details"):
                        st.json(selected_task)
                
                with col3:
                    st.write("")
        else:
            st.info("No quests to manage yet. Create one in Daily Quests!")
    
    with tab3:
        st.write("### Advanced Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Reset Data**")
            if st.button("🔄 Reset All Progress", type="secondary"):
                if st.checkbox("I understand this will delete ALL progress"):
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
                        "setup_complete": False
                    }
                    st.success("Progress reset! All data cleared.")
                    st.rerun()
        
        with col2:
            st.write("**Season Management**")
            new_season = st.selectbox("Change Season", list(SEASONS.keys()), key="season_select")
            
            if st.button("🎮 Start New Season", type="secondary"):
                st.session_state.user_data["current_season"] = new_season
                st.session_state.user_data["level"] = 1
                st.session_state.user_data["experience"] = 0
                st.session_state.user_data["rank_points"] = 0
                st.session_state.user_data["completion_history"] = {}
                st.session_state.user_data["achievements"] = []
                st.success(f"Started Season {new_season}: {SEASONS[new_season]['name']}!")
                st.rerun()
        
        st.divider()
        
        st.write("### About")
        st.info("""
        **Daily Tracker - Leveling System v3.0**
        
        A gamified daily habit tracker inspired by:
        - 🎮 PUBG Ranking System
        - ⚡ Solo Leveling (Sung Jinwoo's Awakening System)
        
        **Enhanced Features:**
        - 📂 Task Categories with filtering
        - 🏆 8+ Achievement System with progress tracking
        - 🎯 Advanced Statistics & Analytics
        - 📊 Interactive Charts & Visualizations
        - ⚙️ Complete Quest Management
        - 🔄 Undo Task Completion
        - ✨ Level-up Celebrations
        - 🎨 Beautiful UI with Animations
        
        **Original Features:**
        - 🎮 8-Tier Ranking System with emojis
        - ⚡ Level Up Progression
        - 🎯 Daily Quests with Multiple Difficulties
        - 📊 Statistics & Progress Tracking
        - 🔥 Streak Counter
        - 🏆 Season Rotation
        """)

st.sidebar.divider()
st.sidebar.write("**Made with ⚔️ for Daily Champions**")
