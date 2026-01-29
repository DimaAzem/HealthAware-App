import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta, datetime
import time
import re
from fpdf import FPDF
import os
import fitz  # PyMuPDF
import json
import random

# --- ספריית OpenAI ---
from openai import OpenAI

# ---------------------------------------------------------
# 1. הגדרות וקונפיגורציה
# ---------------------------------------------------------

# --- שימי את המפתח שלך כאן ---
OPENAI_API_KEY = "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" # <--- כאן להדביק את המפתח של OPENAI

# הגדרת הלקוח
client = None
if OPENAI_API_KEY and OPENAI_API_KEY != "sk-...":
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except:
        pass

st.set_page_config(page_title="HealthAware Intelligence", page_icon="🥗", layout="wide")

if not os.path.exists(".streamlit"):
    os.makedirs(".streamlit")

config_path = ".streamlit/config.toml"
config_content = """
[theme]
base="light"
primaryColor="#10B981"
backgroundColor="#ffffff"
secondaryBackgroundColor="#f0f2f6"
textColor="#000000"
font="sans serif"
"""

with open(config_path, "w") as f:
    f.write(config_content)

# ---------------------------------------------------------
# 2. CSS ועיצוב
# ---------------------------------------------------------

def load_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        html, body, .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
            font-family: 'Poppins', sans-serif !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
        }

        /* כרטיסי מידע */
        div[data-testid="stMetric"] {
            background-color: white;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* Timeline Card */
        .timeline-card {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #10B981;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }

        /* כפתורים */
        div.stButton > button {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #000000 !important;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.2s;
        }
        div.stButton > button:hover {
             background-color: #f3f4f6 !important;
             transform: scale(1.02);
        }

        /* כפתור מחיקה אדום */
        div[data-testid="stExpander"] div.stButton > button {
            background-color: #EF4444 !important;
            border-color: #EF4444 !important;
            color: white !important;
            width: 100%;
        }
        
        /* כפתור מחיקה כבוי */
        div[data-testid="stExpander"] div.stButton > button:disabled {
            background-color: #fee2e2 !important;
            border-color: #fca5a5 !important;
            color: #991b1b !important;
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        /* כפתור ירוק לבחירה */
        button[key^="sel_"] {
             background-color: #10B981 !important;
             border: none !important;
             color: white !important;
             width: 100%;
        }
        
        /* סרגל צד */
        section[data-testid="stSidebar"] .stButton button {
            background-color: transparent !important;
            border: none !important;
            text-align: left !important;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            background-color: #f3f4f6 !important;
        }
        </style>
    """, unsafe_allow_html=True)

load_css()

# --- נתונים גלובליים ---
DIET_OPTIONS = ["No Restrictions (Flexible)", "Vegetarian", "Vegan", "Pescatarian", "Gluten-Free", "Lactose-Free", "Keto", "Paleo", "Kosher", "Halal"]
COMMON_ALLERGENS = ["Peanuts", "Tree Nuts", "Milk (Dairy)", "Eggs", "Wheat", "Soy", "Fish", "Shellfish", "Sesame"]
FOOD_INGREDIENTS = ["Cilantro", "Mushrooms", "Olives", "Tomatoes", "Onions", "Garlic", "Bell Peppers", "Eggplant", "Broccoli", "Spinach", "Avocado", "Coconut", "Mayonnaise", "Tofu", "Red Meat", "Pork", "Lamb", "Salmon", "Tuna", "Shrimp", "Cheese", "Yogurt", "Eggs", "Beans", "Rice", "Quinoa", "Lentils", "Chickpeas", "Oats", "Berries", "Nuts"]
MEAL_TYPES_OPTIONS = ["Breakfast", "Lunch", "Dinner", "Snack"]
GOAL_OPTIONS = ["Maintain Weight", "Lose Weight", "Gain Weight"]

# --- לוגו ---
def render_logo(location="main"):
    svg_raw = """<svg viewBox="0 0 300 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="logo_gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#005792" />
                    <stop offset="50%" stop-color="#2a9d8f" />
                    <stop offset="100%" stop-color="#4caf50" />
                </linearGradient>
            </defs>
            <path d="M10 50 H60 L80 10 L100 90 L120 50 H150 Q 170 50 170 20 H 260 M 170 20 V 80 M 150 50 Q 170 50 170 80 H 260 M 170 40 H 260 M 170 60 H 260" stroke="url(#logo_gradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" />
        </svg>"""
    
    if location == "main":
        st.markdown(f"""
            <div style='display: flex; align-items: center; justify-content: center; margin-bottom: 30px;'>
                <div style='width: 80px; height: 40px; margin-right: 15px; margin-top: 20px;'>{svg_raw}</div>
                <h1 style='margin: 0; font-family: Poppins, sans-serif; font-weight: 700; font-size: 2.5rem; color: #000000;'>HealthAware</h1>
            </div>
            <p style='text-align: center; color: #64748b; font-size: 1.1rem; margin-top: -15px; margin-bottom: 30px;'>Eat Smart. Live Strong. Your Health, Decoded.</p>
        """, unsafe_allow_html=True)
    elif location == "sidebar":
        st.markdown(f"""
            <div style='display: flex; align-items: center; margin-bottom: 10px; margin-top: 10px;'>
                <div style='width: 60px; height: 30px; margin-right: 10px; margin-top: -5px;'>{svg_raw}</div>
                <h3 style='margin: 0; font-family: Poppins, sans-serif; font-weight: 600; font-size: 1.4rem; color: #000000;'>HealthAware</h3>
            </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. פונקציות לוגיקה ו-Callbacks
# ---------------------------------------------------------

def add_manual_item(input_key, storage_list_key, widget_key):
    raw_val = st.session_state[input_key]
    if raw_val:
        new_val = raw_val.strip().title()
        if new_val:
            if new_val not in st.session_state[storage_list_key]:
                st.session_state[storage_list_key].append(new_val)
            current_selection = list(st.session_state.get(widget_key, []))
            if new_val not in current_selection:
                current_selection.append(new_val)
                st.session_state[widget_key] = current_selection
    st.session_state[input_key] = ""

def convert_units_callback():
    if st.session_state.current_user and st.session_state.current_user in st.session_state.users_db:
        user = st.session_state.users_db[st.session_state.current_user]
        profile = user['profile']
        new_unit = st.session_state.units_radio_key
        old_unit = profile.get('units', 'Metric')
        if new_unit == old_unit: return
        if old_unit == "Metric" and new_unit == "Imperial":
            profile['weight'] = round(profile['weight'] * 2.20462, 1)
            profile['height'] = round(profile['height'] / 2.54, 1)
            if 'target_weight' in profile:
                profile['target_weight'] = round(profile['target_weight'] * 2.20462, 1)
        elif old_unit == "Imperial" and new_unit == "Metric":
            profile['weight'] = round(profile['weight'] / 2.20462, 1)
            profile['height'] = round(profile['height'] * 2.54, 0)
            if 'target_weight' in profile:
                profile['target_weight'] = round(profile['target_weight'] / 2.20462, 1)
        profile['units'] = new_unit

def calculate_bmi(weight_kg, height_cm):
    if weight_kg <= 0 or height_cm <= 0: return 0
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)

def get_bmi_status(bmi):
    if bmi <= 0: return "Unknown", "grey"
    if bmi < 18.5: return "Underweight", "#3b82f6"
    elif 18.5 <= bmi < 24.9: return "Healthy Weight", "#10B981"
    elif 25 <= bmi < 29.9: return "Overweight", "#f59e0b"
    else: return "Obese", "#EF4444"

# --- חישובים: מים וקלוריות ---
def calculate_water_target(weight_kg, activity_level):
    base_water_ml = weight_kg * 35
    activity_bonus = 0
    if activity_level == "Active": activity_bonus = 500
    elif activity_level == "Very Active": activity_bonus = 1000
    total_ml = base_water_ml + activity_bonus
    cups = round(total_ml / 250)
    return cups, total_ml

def calculate_bmr_tdee(gender, weight_kg, height_cm, age, activity_level):
    if gender == "Male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    activity_multipliers = {"Sedentary": 1.2, "Lightly Active": 1.375, "Active": 1.55, "Very Active": 1.725}
    tdee = bmr * activity_multipliers.get(activity_level, 1.2)
    return int(bmr), int(tdee)

# --- פונקציות AI (OpenAI + Fallback) ---

def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def extract_text_from_pdf(uploaded_file):
    try:
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc: text += page.get_text()
        if not text or len(text.strip()) < 20: return None 
        return text
    except Exception as e:
        print(f"PDF Reading Error: {e}")
        return None

def safe_openai_call(prompt, fallback_response=None):
    if not client:
        time.sleep(1.5) 
        return fallback_response

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful nutrition and health assistant. You output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        st.error(f"AI Error: {e}. Switching to Demo Mode.")
        return fallback_response

# --- פונקציות הלוגיקה (עם הנחיות מפורטות) ---

def analyze_weight_management(user_profile, bmi_data):
    prompt = f"""
    Act as a Senior Clinical Nutritionist.
    Data: Profile: {user_profile}, Activity: {user_profile.get('activity', 'Active')}, BMI: {bmi_data.get('bmi')}, Goal: {user_profile.get('goal')}.
    Target Weight: {user_profile.get('target_weight')}.
    
    Task: Provide a DETAILED analysis.
    Output JSON: {{ "goal_validation": {{ "is_healthy": true/false, "message": "..." }}, "calorie_target": {{ "min": 2000, "max": 2200 }}, "weight_management_tips": ["...", "...", "..."] }}
    """
    
    mock_data = {
        "goal_validation": {"is_healthy": True, "message": "Your goal fits healthy standards."},
        "calorie_target": {"min": 1800, "max": 2100},
        "weight_management_tips": [
            "Prioritize protein at breakfast (25g+) to stabilize blood sugar.", 
            "Increase NEAT by walking while talking on the phone.", 
            "Implement a 'Kitchen Closed' rule 3 hours before bed."
        ]
    }
    return safe_openai_call(prompt, mock_data)

def analyze_clinical_data(blood_text, general_symptoms):
    if not blood_text and not general_symptoms: return None
    
    prompt = f"""
    Act as a Senior Clinical Nutritionist and Hematologist.
    Input: Symptoms: "{general_symptoms}", Blood Test Text: "{blood_text[:6000]}".
    
    Task:
    1. Identify ALL abnormal clinical findings.
    2. For EACH finding, provide a DETAILED explanation (physiology, causes, impact).
    3. Estimate realistic improvement time.
    4. Provide strict food recommendations.
    
    Output JSON: {{ 
        "clinical_findings": [
            {{ 
               "issue": "Name (e.g. Iron Deficiency)", 
               "status": "Low/High", 
               "target": "Normal Range", 
               "estimated_improvement_time": "Time (e.g. 3 months)", 
               "explanation": "Detailed explanation of the biological mechanism and causes." 
            }}
        ], 
        "clinical_recommendations": ["Rec 1", "Rec 2"], 
        "foods_to_prioritize_clinical": ["Food (Reason)"], 
        "foods_to_limit_clinical": ["Food (Reason)"],
        "recommended_retest_period": "3 months"
    }}
    """
    
    mock_data = {
        "clinical_findings": [
            {"issue": "Simulated Iron Deficiency", "status": "Low", "target": "Normal", "estimated_improvement_time": "3 months", "explanation": "Ferritin levels indicate low iron stores, restricting hemoglobin production and causing fatigue."},
            {"issue": "Vitamin D Insufficiency", "status": "Low", "target": ">30 ng/mL", "estimated_improvement_time": "2-3 months", "explanation": "Critical for bone health and immunity."}
        ],
        "clinical_recommendations": ["Combine plant iron with Vitamin C.", "Separate caffeine from meals."],
        "foods_to_prioritize_clinical": ["Red Meat (Heme iron)", "Lentils", "Bell Peppers"],
        "foods_to_limit_clinical": ["Coffee/Tea with meals", "Bran"],
        "recommended_retest_period": "3 months"
    }
    return safe_openai_call(prompt, mock_data)

def get_daily_advice_immediate(daily_symptoms, user_profile):
    prompt = f"""
    Act as a supportive health coach. User Feeling: "{daily_symptoms}". Allergies: {user_profile.get('allergies')}.
    Output JSON: {{ "daily_tips": ["Detailed Tip 1", "Detailed Tip 2", "Detailed Tip 3"] }}
    """
    mock_data = {"daily_tips": ["Hydration is key today.", "Try magnesium-rich snacks.", "Light stretching recommended."]}
    return safe_openai_call(prompt, mock_data)

def generate_daily_meals(weight_report, clinical_report, daily_symptoms, fridge_have, fridge_missing, user_profile, selected_meal_types, regenerate=False):
    variation = "Ensure different options." if regenerate else ""
    cal_target = weight_report.get('calorie_target', {}) if weight_report else {}
    clin_ctx = json.dumps(clinical_report) if clinical_report else "None"
    
    prompt = f"""
    Act as an expert chef and clinical nutritionist.
    Constraints: Allergies: {user_profile.get('allergies')}, Dislikes: {user_profile.get('dislikes')}.
    Health: {cal_target.get('min','?')} - {cal_target.get('max','?')} kcal. Clinical: {clin_ctx}.
    Today: Feeling: "{daily_symptoms}", Kitchen Have: {fridge_have}, Avoid: {fridge_missing}.
    Meals: {", ".join(selected_meal_types)}. {variation}
    
    Task: Generate EXACTLY 3 distinct options for EACH meal type.
    Explain WHY each meal is good for the specific health goals.
    
    Output JSON: {{ 
        "breakfast": [ 
            {{ 
               "name": "Name", 
               "description": "Description", 
               "health_reason": "Detailed explanation...",
               "ingredients": ["..."], 
               "macros": {{ "calories": 0, "protein": 0 }}, 
               "recipe_steps": ["..."] 
            }},
            {{ "name": "Option 2...", "description": "...", "health_reason": "...", "ingredients": ["..."], "macros": {{ "calories": 0, "protein": 0 }}, "recipe_steps": ["..."] }},
            {{ "name": "Option 3...", "description": "...", "health_reason": "...", "ingredients": ["..."], "macros": {{ "calories": 0, "protein": 0 }}, "recipe_steps": ["..."] }}
        ] 
    }}
    """
    
    mock_meal = {
        "breakfast": [
            {"name": "Iron-Boost Oatmeal", "description": "Warm oats with berries", "health_reason": "Oats provide energy, berries add Vitamin C for iron absorption.", "ingredients": ["Oats", "Strawberries", "Chia"], "macros": {"calories": 350, "protein": 12}, "recipe_steps": ["Cook oats", "Add toppings"]},
            {"name": "Spinach Omelet", "description": "Savory start", "health_reason": "Eggs for protein, spinach for folate.", "ingredients": ["Eggs", "Spinach", "Feta"], "macros": {"calories": 300, "protein": 20}, "recipe_steps": ["Whisk eggs", "Fry with spinach"]},
            {"name": "Yogurt & Nuts", "description": "Quick Protein", "health_reason": "Probiotics for digestion, healthy fats for hormones.", "ingredients": ["Yogurt", "Walnuts", "Honey"], "macros": {"calories": 400, "protein": 18}, "recipe_steps": ["Mix and serve"]}
        ]
    }
    return safe_openai_call(prompt, mock_meal)

def predict_future_wellness(history_df):
    csv_data = history_df.tail(7).to_csv(index=False)
    prompt = f"""
    Act as a predictive health AI.
    Data (last 7 days): {csv_data}
    Task: Predict wellness for next week based on trends.
    Output JSON: {{
        "prediction_header": "Header",
        "predicted_feeling": "Feeling",
        "prediction_text": "Text...",
        "improvement_tip": "Tip..."
    }}
    """
    mock_data = {
        "prediction_header": "Positive Trend",
        "predicted_feeling": "Energetic",
        "prediction_text": "Consistency suggests higher energy levels next week.",
        "improvement_tip": "Keep hydrating."
    }
    return safe_openai_call(prompt, mock_data)

def generate_day_summary_ai(meal_plan, stats, clinical_goals):
    prompt = f"""
    Act as a motivating health coach.
    User finished the day.
    Meals eaten: {json.dumps(meal_plan)}
    Stats: {stats}
    Clinical Goals: {json.dumps(clinical_goals)}
    Task: Write a detailed summary (2-3 sentences) connecting food to goals.
    Output JSON: {{ "summary_text": "..." }}
    """
    mock_data = {"summary_text": "Great job! Your choices supported your iron goals today."}
    return safe_openai_call(prompt, mock_data)

def generate_smart_grocery_list(meal_plan, fridge_have):
    prompt = f"""
    Act as a Personal Shopper.
    Meal Plan: {json.dumps(meal_plan)}
    User already has: {fridge_have}
    Task: Create shopping list.
    Output JSON: {{
        "shopping_list": [
            {{ "category": "Produce", "items": ["Tomato"] }},
            {{ "category": "Dairy", "items": ["Yogurt"] }}
        ]
    }}
    """
    mock_data = {"shopping_list": [{"category": "Produce", "items": ["Spinach"]}, {"category": "Pantry", "items": ["Rice"]}]}
    return safe_openai_call(prompt, mock_data)

def delete_account_callback():
    email_to_delete = st.session_state.current_user
    if email_to_delete in st.session_state.users_db: del st.session_state.users_db[email_to_delete]
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.current_page = "HOME"

# ---------------------------------------------------------
# 4. ניהול Session State
# ---------------------------------------------------------
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "test@gmail.com": {
            "password": "123", "name": "Tester", "setup_complete": True,
            "profile": {"dob": date(1995, 5, 15), "gender": "Male", "weight": 70, "height": 175, "activity": "Active", "diet": ["No Restrictions (Flexible)"], "allergies": [], "dislikes": [], "units": "Metric", "goal": "Lose Weight", "target_weight": 65},
            "settings": {"notifications": True},
            "weight_goal_report": None, "clinical_report": None
        }
    }

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_user" not in st.session_state: st.session_state.current_user = None
if "current_page" not in st.session_state: st.session_state.current_page = "HOME"

if "custom_allergies_list" not in st.session_state: st.session_state.custom_allergies_list = []
if "custom_dislikes_list" not in st.session_state: st.session_state.custom_dislikes_list = []
if "custom_fridge_have_list" not in st.session_state: st.session_state.custom_fridge_have_list = []
if "custom_fridge_missing_list" not in st.session_state: st.session_state.custom_fridge_missing_list = []

# אתחול חובה של רשימות הבחירה לדף Personal Data
if "setup_allergies_sel" not in st.session_state: st.session_state.setup_allergies_sel = []
if "setup_dislikes_sel" not in st.session_state: st.session_state.setup_dislikes_sel = []
if "p_allergies_selected" not in st.session_state: st.session_state.p_allergies_selected = []
if "p_dislikes_selected" not in st.session_state: st.session_state.p_dislikes_selected = []
if "daily_fridge_have_selected" not in st.session_state: st.session_state.daily_fridge_have_selected = []
if "daily_fridge_missing_selected" not in st.session_state: st.session_state.daily_fridge_missing_selected = []

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Date', 'Day', 'Energy', 'Bloating', 'Calories', 'Protein', 'Water', 'Day_Summary'])

if "daily_plan_stage" not in st.session_state: st.session_state.daily_plan_stage = 1
if "meal_options_generated" not in st.session_state: st.session_state.meal_options_generated = {}
if "final_meal_plan" not in st.session_state: st.session_state.final_meal_plan = {}
if "selected_meal_types_for_today" not in st.session_state: st.session_state.selected_meal_types_for_today = []
if "daily_advice_result" not in st.session_state: st.session_state.daily_advice_result = None
if "water_count" not in st.session_state: st.session_state.water_count = 0

# ==========================================
# 5. אפליקציה ראשית
# ==========================================

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        render_logo(location="main")
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_pass")
                st.write("")
                if st.form_submit_button("Log In"):
                    if email in st.session_state.users_db:
                        if password == st.session_state.users_db[email]['password']:
                            st.session_state.logged_in = True
                            st.session_state.current_user = email
                            st.session_state.current_page = "HOME"
                            st.rerun()
                        else: st.error("Incorrect password.")
                    else: st.error("User does not exist.")
        with tab2:
            with st.form("signup_form"):
                n_name = st.text_input("Full Name")
                n_email = st.text_input("New Email").strip()
                n_pass = st.text_input("Create Password", type="password")
                st.write("")
                if st.form_submit_button("Create Account"):
                    if is_valid_email(n_email) and n_email not in st.session_state.users_db:
                        st.session_state.users_db[n_email] = {
                            "password": n_pass, "name": n_name, "setup_complete": False, "setup_step": 1,
                            "profile": {"units": "Metric", "allergies": [], "dislikes": [], "diet": ["No Restrictions (Flexible)"], "goal": "Maintain Weight", "target_weight": 70, "height": 170, "weight": 70},
                            "settings": {"notifications": True},
                            "weight_goal_report": None, "clinical_report": None
                        }
                        st.success("Account created! Log In.")
                    else: st.error("Invalid email or already exists.")

else:
    user_email = st.session_state.current_user
    user = st.session_state.users_db[user_email]
    
    # --- Wizard התקנה ---
    if not user.get("setup_complete"):
        step = user.get("setup_step", 1)
        st.markdown("<br>", unsafe_allow_html=True)
        col_main, col_form, col_pad = st.columns([1, 4, 1])
        with col_form:
            if step == 1:
                st.title("Setup: Profile Data")
                st.progress(33)
                units_option = st.radio("Units", ["Metric", "Imperial"], horizontal=True)
                if units_option == "Metric":
                    h_label, h_val, h_min, h_max = "Height (cm)", 170, 100, 250
                    w_label, w_val, w_min, w_max = "Weight (kg)", 70, 30, 300
                else:
                    h_label, h_val, h_min, h_max = "Height (inches)", 67, 40, 120
                    w_label, w_val, w_min, w_max = "Weight (lbs)", 154, 70, 600
                
                with st.form("setup_step1"):
                    c1, c2 = st.columns(2)
                    with c1:
                        dob = st.date_input("Date of Birth", value=date(2000, 1, 1), min_value=date(1900,1,1))
                        gender = st.selectbox("Biological Sex", ["Female", "Male", "Other"])
                        height = st.number_input(h_label, h_min, h_max, h_val)
                    with c2:
                        weight = st.number_input(w_label, w_min, w_max, w_val)
                        activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Active", "Very Active"])
                        diet = st.multiselect("Dietary Restrictions", DIET_OPTIONS, default=["No Restrictions (Flexible)"])
                    st.write("")
                    if st.form_submit_button("Next Step →"):
                        user["profile"].update({"dob": dob, "gender": gender, "height": height, "weight": weight, "activity": activity, "diet": diet, "units": units_option})
                        if "target_weight" not in user["profile"]: user["profile"]["target_weight"] = weight
                        user["setup_step"] = 2
                        st.rerun()

            elif step == 2:
                st.title("Setup: Allergies")
                st.progress(66)
                if "setup_allergies_sel" not in st.session_state:
                    st.session_state.setup_allergies_sel = user['profile'].get("allergies", [])
                current_selected = st.session_state.setup_allergies_sel
                all_options = sorted(list(set(COMMON_ALLERGENS + st.session_state.custom_allergies_list + current_selected)))
                st.multiselect("Select Allergies:", options=all_options, key="setup_allergies_sel")
                st.text_input("Add custom allergy:", key="input_setup_allergy", on_change=add_manual_item, args=("input_setup_allergy", "custom_allergies_list", "setup_allergies_sel"))
                st.write("---")
                c1, c2, c3 = st.columns([1, 1, 5])
                with c1: 
                    if st.button("Back"): user["setup_step"] = 1; st.rerun()
                with c2: 
                    if st.button("Next"): 
                        user["profile"]["allergies"] = st.session_state.setup_allergies_sel
                        user["setup_step"] = 3
                        st.rerun()

            elif step == 3:
                st.title("Setup: Dislikes")
                st.progress(100)
                if "setup_dislikes_sel" not in st.session_state:
                    st.session_state.setup_dislikes_sel = user['profile'].get("dislikes", [])
                current_selected = st.session_state.setup_dislikes_sel
                all_options = sorted(list(set(FOOD_INGREDIENTS + st.session_state.custom_dislikes_list + current_selected)))
                st.multiselect("Select Dislikes:", options=all_options, key="setup_dislikes_sel")
                st.text_input("Add custom dislike:", key="input_setup_dislike", on_change=add_manual_item, args=("input_setup_dislike", "custom_dislikes_list", "setup_dislikes_sel"))
                st.write("---")
                c1, c2, c3 = st.columns([1, 1, 5])
                with c1:
                    if st.button("Back"): user["setup_step"] = 2; st.rerun()
                with c2:
                    if st.button("Finish Setup"): 
                        user["profile"]["dislikes"] = st.session_state.setup_dislikes_sel
                        user["setup_complete"] = True
                        st.rerun()

    # --- דאשבורד ---
    else:
        with st.sidebar:
            render_logo(location="sidebar")
            st.caption(f"Welcome, **{user['name']}**")
            st.markdown("---")
            btns = {
                "HOME": "Daily Plan 📅",
                "Progress Tracking": "Progress 📈",  
                "Health Profile": "Health Profile 🩺", 
                "Personal Data": "Personal Data 👤",
                "Settings": "Settings ⚙️"
            }
            for page, label in btns.items():
                if st.session_state.current_page == page:
                    st.button(f"→ {label}", disabled=True)
                else:
                    if st.button(label):
                        st.session_state.current_page = page
                        st.rerun()
            st.markdown("---")
            if st.button("Log Out"):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.session_state.current_page = "HOME"
                st.rerun()

        # --- PAGE: HOME ---
        if st.session_state.current_page == "HOME":
            st.header(f"👋 Hi {user['name']}, Let's plan today.")
            
            if not user.get('weight_goal_report') and not user.get('clinical_report'):
                st.info("💡 Tip: Visit 'Health Profile 🩺' to set goals and get personalized long-term advice.")

            if st.session_state.daily_plan_stage == 1:
                st.subheader("Step 1: Daily Check-in & Kitchen")
                
                with st.container(border=True):
                    st.markdown("#### 💬 How do you feel TODAY?")
                    if "daily_symptoms_input_val" not in st.session_state: st.session_state.daily_symptoms_input_val = ""
                    daily_symptoms = st.text_area("Daily symptoms/mood:", value=st.session_state.daily_symptoms_input_val, placeholder="E.g., got my period today, feeling tired...", height=70, key="daily_symptoms_input")
                    st.session_state.daily_symptoms_input_val = daily_symptoms

                    if st.button("✨ Get Today's Advice (Quick Tips)"):
                         if daily_symptoms.strip():
                             with st.spinner("Generating quick tips for today..."):
                                 advice = get_daily_advice_immediate(daily_symptoms, user['profile'])
                                 if advice:
                                     st.session_state.daily_advice_result = advice
                                 else:
                                     st.warning("Could not generate advice. Please try again.")
                         else: st.warning("Please tell us how you feel first.")

                    if st.session_state.daily_advice_result:
                        st.write("")
                        with st.expander("💡 Your Quick Tips for Today", expanded=True):
                             tips = st.session_state.daily_advice_result.get('daily_tips', [])
                             if tips:
                                 for tip in tips: st.success(f"✓ {tip}")

                st.write("")

                with st.container(border=True):
                    st.markdown("#### 🍳 Plan Today's Meals")
                    st.write("Select up to 4 items:")
                    selected_types = st.multiselect("Select meal types:", MEAL_TYPES_OPTIONS, default=["Breakfast", "Lunch", "Dinner"])
                    
                    if 0 < len(selected_types) <= 4:
                        st.write("---")
                        c_fridge, c_missing = st.columns(2)
                        
                        with c_fridge:
                            st.markdown("**✅ What's in your kitchen?**")
                            current_selected = st.session_state.daily_fridge_have_selected
                            all_fridge_opts = sorted(list(set(FOOD_INGREDIENTS + st.session_state.custom_fridge_have_list + current_selected)))
                            st.multiselect("Select ingredients:", options=all_fridge_opts, key="daily_fridge_have_selected")
                            st.text_input("Add ingredient:", key="input_fridge_have", on_change=add_manual_item, args=("input_fridge_have", "custom_fridge_have_list", "daily_fridge_have_selected"))

                        with c_missing:
                            st.markdown("**❌ What do you NOT want to use?**")
                            current_selected_miss = st.session_state.daily_fridge_missing_selected
                            all_missing_opts = sorted(list(set(FOOD_INGREDIENTS + st.session_state.custom_fridge_missing_list + current_selected_miss)))
                            st.multiselect("Select excluded:", options=all_missing_opts, key="daily_fridge_missing_selected")
                            st.text_input("Add excluded:", key="input_fridge_missing", on_change=add_manual_item, args=("input_fridge_missing", "custom_fridge_missing_list", "daily_fridge_missing_selected"))

                        st.write("")
                        if st.button("👨‍🍳 Generate Meal Options", type="primary"):
                            with st.spinner("Chef AI is creating your daily plan..."):
                                st.session_state.selected_meal_types_for_today = [m.lower() for m in selected_types]
                                options = generate_daily_meals(
                                    user.get('weight_goal_report'),
                                    user.get('clinical_report'),
                                    daily_symptoms,
                                    st.session_state.daily_fridge_have_selected, 
                                    st.session_state.daily_fridge_missing_selected, 
                                    user['profile'],
                                    st.session_state.selected_meal_types_for_today
                                )
                                if options:
                                    st.session_state.meal_options_generated = options
                                    st.session_state.daily_plan_stage = 2
                                    st.rerun()
                                else:
                                    st.warning("Could not generate meals. Please try again.")
                    else:
                        st.warning("Please select 1-4 meal types.")

            elif st.session_state.daily_plan_stage == 2 and st.session_state.meal_options_generated:
                col_back, col_title = st.columns([1, 5])
                with col_back:
                     if st.button("⬅️ Back"):
                        st.session_state.daily_plan_stage = 1
                        st.rerun()
                with col_title: st.subheader("Step 2: Choose Your Meals")
                
                required_meals = st.session_state.selected_meal_types_for_today
                all_generated_options = st.session_state.meal_options_generated
                meals_needed_to_select = [m for m in required_meals if m not in st.session_state.final_meal_plan]
                
                if not meals_needed_to_select:
                    st.session_state.daily_plan_stage = 3
                    st.rerun()
                
                current_meal_type = meals_needed_to_select[0]
                options_for_type = all_generated_options.get(current_meal_type, [])

                st.markdown(f"### 🤔 Choose your: **{current_meal_type.capitalize()}**")
                
                col_shuffle_btn, col_spacer = st.columns([1, 5])
                with col_shuffle_btn:
                    if st.button("🔄 Shuffle Options"):
                        with st.spinner("Shuffling..."):
                            daily_symptoms_saved = st.session_state.get("daily_symptoms_input_val", "")
                            new_opts_response = generate_daily_meals(
                                user.get('weight_goal_report'),
                                user.get('clinical_report'),
                                daily_symptoms_saved, 
                                st.session_state.get('daily_fridge_have_selected', []), 
                                st.session_state.get('daily_fridge_missing_selected', []), user['profile'],
                                [current_meal_type],
                                regenerate=True
                            )
                            if new_opts_response and current_meal_type in new_opts_response:
                                st.session_state.meal_options_generated[current_meal_type] = new_opts_response[current_meal_type]
                                st.rerun()

                if not options_for_type:
                    st.error("No options found. Try regenerating.")
                else:
                    cols = st.columns(3)
                    for i, option in enumerate(options_for_type[:3]):
                        with cols[i]:
                            with st.container(border=True):
                                st.markdown(f"#### {option.get('name')}")
                                st.caption(option.get('description'))
                                with st.expander("Ingredients & Macros / Why this meal?"):
                                    st.info(f"💡 {option.get('health_reason', 'Good choice!')}")
                                    st.caption(f"**Macros:** {option.get('macros',{}).get('calories','?')} kcal, {option.get('macros',{}).get('protein','?')}g protein")
                                    ing_list = option.get('ingredients', [])
                                    if ing_list:
                                        for ing in ing_list: st.markdown(f"- {ing}")
                                st.write("---")
                                if st.button(f"Select", key=f"sel_{current_meal_type}_{i}"):
                                    st.session_state.final_meal_plan[current_meal_type] = option
                                    st.rerun()

            elif st.session_state.daily_plan_stage == 3 and st.session_state.final_meal_plan:
                col_back, col_title = st.columns([1, 5])
                with col_back:
                    if st.button("⬅️ Back"):
                          st.session_state.final_meal_plan = {}
                          st.session_state.daily_plan_stage = 2
                          st.rerun()
                with col_title: st.subheader("Your Daily Plan is Ready!")
                
                st.markdown("---")
                total_cals = 0
                total_protein = 0
                order = ['breakfast', 'lunch', 'dinner', 'snack']
                for m_type in order:
                    meal_data = st.session_state.final_meal_plan.get(m_type)
                    if meal_data:
                        macros = meal_data.get('macros', {})
                        cals = macros.get('calories', 0)
                        prot = macros.get('protein', 0)
                        total_cals += cals
                        total_protein += prot
                        with st.expander(f"🍽️ **{m_type.capitalize()}** ({cals} kcal): {meal_data.get('name')}", expanded=True):
                            c_ing, c_rec = st.columns(2)
                            with c_ing:
                                st.markdown("#### Ingredients:")
                                for ing in meal_data.get('ingredients', []): st.write(f"- {ing}")
                            with c_rec:
                                st.markdown("#### Recipe Instructions:")
                                steps = meal_data.get('recipe_steps', [])
                                if isinstance(steps, list):
                                    for idx, step in enumerate(steps): st.write(f"{idx+1}. {step}")
                                else: st.write(steps)

                st.markdown("---")
                st.subheader("📊 Daily Summary")
                c_sum1, c_sum2, c_btn = st.columns([1, 1, 2])
                with c_sum1: st.metric("Total Calories", f"{total_cals}")
                with c_sum2: st.metric("Total Protein", f"{total_protein}g")
                
                with c_btn:
                    # --- מים: חישוב יעד ---
                    st.markdown("#### 💧 Water Tracker")
                    p_w = user['profile'].get('weight', 70)
                    p_a = user['profile'].get('activity', 'Active')
                    target_cups, target_ml = calculate_water_target(p_w, p_a)
                    
                    c_water1, c_water2 = st.columns([1, 2])
                    with c_water1:
                        if st.button("➕ Cup (250ml)"):
                            st.session_state.water_count += 1
                            st.rerun()
                    with c_water2:
                        current = st.session_state.water_count
                        percent = min(1.0, current / target_cups)
                        st.progress(percent)
                        st.caption(f"**{current} / {target_cups} cups** (Target: {target_ml}ml)")

                    st.write("")
                    
                    with st.expander("🛒 Generate Smart Shopping List (AI)", expanded=False):
                        st.write("Need to buy ingredients for this plan?")
                        if st.button("📝 Create List"):
                            with st.spinner("Checking your kitchen..."):
                                fridge_h = st.session_state.daily_fridge_have_selected
                                shop_res = generate_smart_grocery_list(st.session_state.final_meal_plan, fridge_h)
                                if shop_res:
                                    st.session_state['shopping_list_data'] = shop_res.get('shopping_list', [])
                    
                    if 'shopping_list_data' in st.session_state:
                        sl_data = st.session_state['shopping_list_data']
                        st.markdown("#### 🛍️ Your Shopping List")
                        for category in sl_data:
                            st.markdown(f"**{category['category']}**")
                            for item in category['items']:
                                st.checkbox(item, key=f"shop_{item}")
                        st.caption("*Based on ingredients not currently in your 'Kitchen Have' list.")

                    st.write("")
                    st.write("")
                    
                    if st.button("✅ Finish Day & Save to History", type="primary"):
                        with st.spinner("Saving your progress & Generating insights..."):
                            today_date = date.today()
                            day_name = today_date.strftime("%a")
                            
                            eaten_list = [f"{m.capitalize()}: {d['name']}" for m, d in st.session_state.final_meal_plan.items()]
                            stats_str = f"Calories: {total_cals}, Protein: {total_protein}g, Water: {st.session_state.water_count} cups"
                            
                            clin_goals_for_prompt = "None"
                            if user.get('clinical_report'):
                                clin_goals_for_prompt = user['clinical_report'].get('clinical_findings', [])

                            ai_sum_res = generate_day_summary_ai(eaten_list, stats_str, clin_goals_for_prompt)
                            day_insight = ai_sum_res.get('summary_text', 'Good job staying consistent!') if ai_sum_res else "Day completed successfully."

                            new_row = pd.DataFrame({
                                'Date': [today_date],
                                'Day': [day_name],
                                'Energy': [70], 
                                'Bloating': [20],
                                'Calories': [total_cals],
                                'Protein': [total_protein],
                                'Water': [st.session_state.water_count],
                                'Day_Summary': [day_insight]
                            })
                            st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
                            
                            st.success(f"Day saved! Insight: {day_insight}")
                            time.sleep(3)
                            
                            st.session_state.daily_plan_stage = 1
                            st.session_state.meal_options_generated = {}
                            st.session_state.final_meal_plan = {}
                            st.session_state.daily_advice_result = None
                            st.session_state.daily_symptoms_input_val = ""
                            st.session_state.water_count = 0
                            if 'shopping_list_data' in st.session_state: del st.session_state['shopping_list_data']
                            st.rerun()

        # --- PAGE: PROGRESS TRACKING ---
        elif st.session_state.current_page == "Progress Tracking":
            st.header("📈 My Health Journey")
            
            df = st.session_state.history
            streak = len(df) if not df.empty else 0
            
            c_m1, c_m2, c_m3 = st.columns(3)
            with c_m1: st.metric("Login Streak", f"{streak} Days", "Keep going! 🔥")
            with c_m2: 
                avg_cal = int(df['Calories'].mean()) if not df.empty and 'Calories' in df.columns else 0
                st.metric("Avg Calories", f"{avg_cal}", "Weekly Avg")
            with c_m3:
                avg_water = int(df['Water'].mean()) if not df.empty and 'Water' in df.columns else 0
                st.metric("Avg Hydration", f"{avg_water} Cups/Day", "Consistency")

            st.write("---")

            c_sidebar, c_main = st.columns([1, 2])
            
            with c_sidebar:
                with st.container(border=True):
                    st.subheader("⏳ Goal Projection")
                    current_w = user['profile'].get('weight', 70)
                    target_w = user['profile'].get('target_weight', 65)
                    diff = current_w - target_w
                    
                    if diff > 0 and not df.empty: 
                        p_gender = user['profile'].get('gender', 'Female')
                        p_h = user['profile'].get('height', 170)
                        p_age = (date.today() - user['profile'].get('dob', date(2000,1,1))).days // 365
                        p_act = user['profile'].get('activity', 'Active')
                        
                        bmr, tdee = calculate_bmr_tdee(p_gender, current_w, p_h, p_age, p_act)
                        avg_intake = df['Calories'].mean()
                        daily_deficit = tdee - avg_intake
                        
                        if daily_deficit > 100: 
                            days_to_goal = (diff * 7700) / daily_deficit
                            target_date = date.today() + timedelta(days=int(days_to_goal))
                            
                            st.metric("Estimated Arrival", target_date.strftime("%d/%m/%Y"))
                            st.caption(f"Based on your avg deficit of {int(daily_deficit)} kcal/day.")
                            st.progress(min(1.0, max(0.01, 1 - (days_to_goal / 100))))
                        elif daily_deficit < -100:
                            st.warning("You are currently in a calorie surplus.")
                        else:
                            st.info("You are maintaining weight.")
                    else:
                        st.info("Log meals to see your goal timeline.")

                with st.container(border=True):
                    st.subheader("🎯 Clinical Simulation")
                    st.caption("Projected status based on consistency.")
                    
                    clin_rep = user.get('clinical_report')
                    
                    if clin_rep and clin_rep.get('clinical_findings'):
                        findings = clin_rep.get('clinical_findings', [])
                        simulated_progress = min(100, streak * 5) 
                        
                        for f in findings:
                            issue_name = f.get('issue', 'Issue')
                            st.markdown(f"**{issue_name}**")
                            st.progress(simulated_progress / 100)
                            if simulated_progress < 100:
                                st.caption(f"Status: Improving... ({simulated_progress}%)")
                            else:
                                st.caption(f"Status: Likely Improved! Re-test required.")
                            st.markdown("---")
                            
                        upload_date_str = clin_rep.get('upload_date')
                        if upload_date_str:
                            u_date = date.fromisoformat(upload_date_str)
                            retest_str = clin_rep.get('recommended_retest_period', '90 days')
                            try:
                                days_retest = int(re.search(r'\d+', retest_str).group()) * 30 
                            except:
                                days_retest = 90
                                
                            next_date = u_date + timedelta(days=days_retest)
                            days_left = (next_date - date.today()).days
                            if days_left > 0:
                                st.info(f"📅 Lab Verification Due: **{next_date.strftime('%d/%m')}**")
                            else:
                                st.error("⚠️ Lab Test Overdue!")
                    else:
                        st.info("No clinical data found.")
            
            with c_main:
                tab_history, tab_charts = st.tabs(["📅 Daily Journal", "📊 Advanced Analytics"])
                
                with tab_history:
                    st.subheader("Timeline")
                    if df.empty:
                        st.info("No history yet.")
                    else:
                        if 'Date' in df.columns:
                            df_sorted = df.sort_values(by='Date', ascending=False)
                        else:
                            df_sorted = df.iloc[::-1]

                        for index, row in df_sorted.iterrows():
                            with st.container():
                                st.markdown(f"""
                                <div class="timeline-card">
                                    <div style="display:flex; justify-content:space-between;">
                                        <h4 style="margin:0; color:#059669;">{row['Day']} <span style="font-size:0.8em; color:#888;">({str(row['Date'])})</span></h4>
                                        <span style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:10px; font-size:0.8em;">✓ Done</span>
                                    </div>
                                    <p style="font-size:15px; color:#374151; margin-top:10px; font-style:italic;">"{row.get('Day_Summary', 'Day completed.')}"</p>
                                    <div style="display:flex; gap:20px; margin-top:15px; font-weight:500; font-size:14px; border-top:1px solid #eee; padding-top:10px;">
                                        <span>🔥 {row.get('Calories', 0)} kcal</span>
                                        <span>🥩 {row.get('Protein', 0)}g Protein</span>
                                        <span>💧 {row.get('Water', 0)} cups</span>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                with tab_charts:
                    if df.empty:
                        st.warning("Not enough data.")
                    else:
                        st.subheader("Consistency Heatmap")
                        dates_range = [date.today() - timedelta(days=x) for x in range(14)]
                        z_values = []
                        for d in dates_range:
                            if not df[df['Date'] == d].empty:
                                z_values.append(1) 
                            else:
                                z_values.append(0) 
                        
                        fig_heat = go.Figure(data=go.Heatmap(
                            z=[z_values],
                            x=dates_range,
                            y=['Log'],
                            colorscale=[[0, '#f3f4f6'], [1, '#10B981']],
                            showscale=False
                        ))
                        fig_heat.update_layout(height=150, margin=dict(l=20, r=20, t=20, b=20))
                        st.plotly_chart(fig_heat, use_container_width=True)
                        st.caption("Green squares indicate logged days.")

                        st.subheader("Nutrient Trends")
                        fig_bar = px.bar(df, x='Day', y=['Calories', 'Protein'], barmode='group', 
                                         color_discrete_map={"Calories": "#3b82f6", "Protein": "#10B981"})
                        st.plotly_chart(fig_bar, use_container_width=True)

        # --- PAGE: HEALTH PROFILE ---
        elif st.session_state.current_page == "Health Profile":
            st.header("🩺 Health Profile & Long-term Analysis")
            p = user['profile']
            
            with st.container(border=True):
                st.subheader("⚖️ Weight & Goal Management")
                units = p.get('units', 'Metric')
                current_height_val = p.get('height', 170)
                current_weight_val = p.get('weight', 70)

                if units == "Metric":
                    height_cm = current_height_val
                    weight_kg = current_weight_val
                    display_height = f"{height_cm}cm"
                    display_weight = f"{weight_kg}kg"
                    target_label = "Target Weight (kg):"
                else: 
                    height_in = current_height_val
                    weight_lbs = current_weight_val
                    height_cm = height_in * 2.54
                    weight_kg = weight_lbs * 0.453592
                    display_height = f"{height_in} inches"
                    display_weight = f"{weight_lbs} lbs"
                    target_label = "Target Weight (lbs):"

                bmi_val = calculate_bmi(weight_kg, height_cm)
                bmi_status, bmi_color = get_bmi_status(bmi_val)

                col_bmi, col_goals = st.columns([2, 3])
                with col_bmi:
                    st.markdown("#### Current Status")
                    st.metric("Your BMI", f"{bmi_val}", delta=bmi_status, delta_color="off")
                    st.caption(f"{display_height} | {display_weight}")
                    st.markdown(f"Status: <span style='color:{bmi_color}; font-weight:bold'>{bmi_status}</span>", unsafe_allow_html=True)

                with col_goals:
                    st.markdown("#### Set Your Goal")
                    with st.form("goal_form"):
                        new_goal = st.selectbox("I want to:", GOAL_OPTIONS, index=GOAL_OPTIONS.index(p.get('goal', 'Maintain Weight')))
                        target_w_val = p.get('target_weight', current_weight_val)
                        target_w = st.number_input(target_label, value=float(target_w_val), min_value=0.0, step=0.5)
                        
                        if st.form_submit_button("Update Goal & Analyze Weight Plan"):
                            user['profile']['goal'] = new_goal
                            user['profile']['target_weight'] = target_w
                            with st.spinner("Analyzing weight goal..."):
                                bmi_data = {"bmi": bmi_val, "status": bmi_status}
                                wg_report = analyze_weight_management(user['profile'], bmi_data)
                                if wg_report:
                                    user['weight_goal_report'] = wg_report
                                    st.success("Goal updated & analyzed!")
                                    st.rerun()

            if user.get('weight_goal_report'):
                wg_report = user['weight_goal_report']
                with st.expander("📋 Weight & Calorie Recommendations", expanded=True):
                    col_goal_res, col_cal_res = st.columns(2)
                    with col_goal_res:
                        g_val = wg_report.get('goal_validation', {})
                        st.markdown("#### Goal Feasibility")
                        if g_val.get('is_healthy'): st.success(f"✅ {g_val.get('message','')}")
                        else: st.warning(f"⚠️ {g_val.get('message','')}")
                    with col_cal_res:
                         cal_rec = wg_report.get('calorie_target', {})
                         st.markdown("#### Daily Calorie Target")
                         st.metric("Range", f"{cal_rec.get('min', '?')} - {cal_rec.get('max', '?')} kcal")
                    
                    st.markdown("#### 💡 Weight Management Tips (Including Activity)")
                    for tip in wg_report.get('weight_management_tips', []):
                        st.info(f"• {tip}")
            
            st.write("---")
            
            with st.container(border=True):
                st.subheader("🔬 Clinical Analysis (Blood & Symptoms)")
                uploaded_file = st.file_uploader("📂 Upload Blood Test PDF", type="pdf", key="clinical_pdf")
                general_symptoms_input = st.text_area("General/Chronic Symptoms (Not daily feelings):", placeholder="E.g., diagnosed anemia, frequent migraines...", height=100)
                
                if st.button("🔍 Run Clinical Analysis"):
                    if not uploaded_file and not general_symptoms_input:
                        st.error("Please upload a file or enter symptoms first.")
                    else:
                         with st.spinner("Analyzing data & extracting monitoring goals..."):
                            extracted_text = extract_text_from_pdf(uploaded_file) if uploaded_file else ""
                            if uploaded_file and not extracted_text:
                                st.error("Could not read the PDF file. It might be an image scan. Please try a text-based PDF.")
                            else:
                                clin_report = analyze_clinical_data(extracted_text, general_symptoms_input)
                                if clin_report:
                                    clin_report['upload_date'] = date.today().isoformat()
                                    user['clinical_report'] = clin_report
                                    st.success("Analysis complete!")
                                    st.rerun()
                                else:
                                    st.error("Analysis failed. Please check your internet or API key.")

            if user.get('clinical_report'):
                clin_report = user['clinical_report']
                
                upload_date_str = clin_report.get('upload_date')
                if upload_date_str:
                    upload_date = date.fromisoformat(upload_date_str)
                    
                    # חילוץ זמן משוער מה-AI או ברירת מחדל
                    est_time_str = clin_report.get('recommended_retest_period', '3 months')
                    try:
                        months = int(re.search(r'\d+', est_time_str).group())
                    except:
                        months = 3
                        
                    valid_until = upload_date + timedelta(days=months*30)
                    days_left = (valid_until - date.today()).days
                    
                    col_status, col_date = st.columns([2, 1])
                    with col_date: 
                        st.caption(f"Uploaded: {upload_date.strftime('%d/%m/%Y')}")
                    with col_status:
                        if days_left < 0: 
                            st.error(f"⚠️ Re-test Needed! Target date was {valid_until.strftime('%d/%m/%Y')}.")
                        else: 
                            st.success(f"✅ Next Blood Test Recommended: {valid_until.strftime('%d/%m/%Y')} ({days_left} days left)")

                with st.expander("📋 Clinical Findings & Recommendations", expanded=True):
                    col_findings, col_recs = st.columns(2)
                    with col_findings:
                        st.markdown("#### 🩸 Findings")
                        findings = clin_report.get('clinical_findings', [])
                        if not findings: st.info("No specific findings based on data.")
                        for item in findings:
                            if "No specific data provided" in item.get('issue', ''):
                                st.info(f"**{item.get('issue')}**: {item.get('explanation', '')}")
                            else:
                                st.warning(f"**{item.get('issue', 'Issue')}**: {item.get('explanation', '')}")

                    with col_recs:
                        st.markdown("#### 🥦 Clinical Advice")
                        for rec in clin_report.get('clinical_recommendations', []):
                            st.success(f"✓ {rec}")
                        foods_p = clin_report.get('foods_to_prioritize_clinical', [])
                        foods_l = clin_report.get('foods_to_limit_clinical', [])
                        if foods_p or foods_l:
                            c_good, c_bad = st.columns(2)
                            with c_good:
                                if foods_p:
                                    st.markdown("**✅ Prioritize**")
                                    for f in foods_p: st.write(f"• {f}")
                            with c_bad:
                                if foods_l:
                                    st.markdown("**❌ Limit**")
                                    for f in foods_l: st.write(f"• {f}")

        # --- PAGE: PERSONAL DATA ---
        elif st.session_state.current_page == "Personal Data":
            st.header("👤 Personal Data")
            p = user['profile']
            
            with st.container(border=True):
                st.subheader("Basic Info")
                st.markdown("**Units Preference:**")
                st.radio("Select Units:", ["Metric", "Imperial"], index=0 if p.get('units') == "Metric" else 1, horizontal=True, key="units_radio_key", on_change=convert_units_callback)
                st.write("---")
                with st.form("basic_info_edit"):
                    c1, c2 = st.columns(2)
                    with c1:
                        ndob = st.date_input("Date of Birth", value=p.get('dob', date(2000,1,1)))
                        ngen = st.selectbox("Sex", ["Female", "Male", "Other"], index=["Female", "Male", "Other"].index(p.get('gender', 'Female')))
                        if p.get('units') == "Metric":
                            h_label, h_step = "Height (cm)", 1.0
                            w_label, w_step = "Weight (kg)", 0.1
                        else:
                            h_label, h_step = "Height (inches)", 0.5
                            w_label, w_step = "Weight (lbs)", 0.5
                        nh = st.number_input(h_label, value=float(p.get('height', 170)), step=h_step)
                    with c2:
                         nact = st.selectbox("Activity", ["Sedentary", "Lightly Active", "Active", "Very Active"], index=["Sedentary", "Lightly Active", "Active", "Very Active"].index(p.get('activity', 'Active')))
                         nw = st.number_input(w_label, value=float(p.get('weight', 70)), step=w_step)
                    ndiet = st.multiselect("Diet Type", DIET_OPTIONS, default=p.get('diet', ["No Restrictions (Flexible)"]))
                    st.write("")
                    if st.form_submit_button("Save Changes"):
                        user['profile'].update({"dob": ndob, "gender": ngen, "height": nh, "weight": nw, "activity": nact, "diet": ndiet})
                        st.success("Updated Successfully!")
                        st.rerun()
            
            if "p_allergies_selected" not in st.session_state or not st.session_state.p_allergies_selected: st.session_state.p_allergies_selected = p.get('allergies', [])
            if "p_dislikes_selected" not in st.session_state or not st.session_state.p_dislikes_selected: st.session_state.p_dislikes_selected = p.get('dislikes', [])

            c_all, c_dis = st.columns(2)
            with c_all:
                with st.container(border=True):
                    st.subheader("🚫 Allergies")
                    current_selected = st.session_state.p_allergies_selected
                    all_options = sorted(list(set(COMMON_ALLERGENS + st.session_state.custom_allergies_list + current_selected)))
                    st.multiselect("Select:", options=all_options, key="p_allergies_selected")
                    st.text_input("Add custom allergy:", key="input_allergy_p", on_change=add_manual_item, args=("input_allergy_p", "custom_allergies_list", "p_allergies_selected"))
                    user['profile']['allergies'] = st.session_state.p_allergies_selected

            with c_dis:
                with st.container(border=True):
                    st.subheader("🤢 Dislikes")
                    current_selected = st.session_state.p_dislikes_selected
                    all_options = sorted(list(set(FOOD_INGREDIENTS + st.session_state.custom_dislikes_list + current_selected)))
                    st.multiselect("Select:", options=all_options, key="p_dislikes_selected")
                    st.text_input("Add custom dislike:", key="input_dislike_p", on_change=add_manual_item, args=("input_dislike_p", "custom_dislikes_list", "p_dislikes_selected"))
                    user['profile']['dislikes'] = st.session_state.p_dislikes_selected

        # --- PAGE: SETTINGS ---
        elif st.session_state.current_page == "Settings":
            st.header("⚙️ Settings")
            with st.container(border=True):
                st.subheader("🔔 Notifications")
                st.toggle("Enable Daily Reminders", value=user['settings'].get('notifications', True))
                st.toggle("Receive Weekly Health Tips", value=True)
            st.write("")
            with st.container(border=True):
                st.subheader("🔐 Account Security")
                c1, c2 = st.columns(2)
                with c1: current_pass = st.text_input("Current Password", type="password")
                with c2:
                    new_pass = st.text_input("New Password", type="password")
                    confirm_pass = st.text_input("Confirm New Password", type="password")
                if st.button("Update Password"):
                    if current_pass == user['password']:
                        if new_pass == confirm_pass and new_pass:
                            user['password'] = new_pass
                            st.success("Password changed successfully!")
                        else: st.error("New passwords do not match or are empty.")
                    else: st.error("Incorrect current password.")
            st.write("")
            
            # --- אזור מחיקה מאובטח ---
            with st.expander("⚠️ Account Settings"):
                st.warning("Warning: This action is permanent.")
                confirm_delete = st.checkbox("I want to delete my account irreversibly.")
                
                # הכפתור מנוטרל (disabled=True) כל עוד התיבה לא מסומנת (disabled=not confirm_delete)
                if st.button("Delete Account", disabled=not confirm_delete):
                     delete_account_callback()
                     st.rerun()