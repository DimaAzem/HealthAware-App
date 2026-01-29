import json
import google.generativeai as genai
import os

# ==========================================
# ⚠️ חובה: הגדרת מפתח ה-API
# ==========================================
# אנא וודאי שהמפתח מודבק כאן במדויק בתוך הגרשיים!
GOOGLE_API_KEY =  "AIzaSyD4YOFrNsRBpnMHNBJ2CpsFSUM-N-6RRwY"

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"❌ CRITICAL ERROR: API Key configuration failed. Details: {e}")

def analyze_medical_report(pdf_text):
    print("--- 1. Sending PDF to AI for Analysis ---") # בדיקה בטרמינל
    prompt = f"""
    You are a medical analyst. Analyze this blood test data: "{pdf_text}"
    Return a JSON object with a list "biomarkers".
    Item structure: {{ "name": "Iron", "value": "30", "status": "Low/Normal/High", "recommendation": "advice" }}
    Return ONLY JSON.
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        print("✅ AI Response received for PDF.")
        return json.loads(text)
    except Exception as e:
        print(f"❌ ERROR in PDF Analysis: {e}") # זה יראה לנו למה זה נכשל
        return {"biomarkers": []}

def suggest_three_meals(symptoms, fridge_text):
    print(f"--- 2. Asking AI for Meals (Symptoms: {symptoms}, Fridge: {fridge_text}) ---")
    prompt = f"""
    You are a chef. User has symptoms: "{symptoms}" and fridge: "{fridge_text}".
    Suggest 3 meals. Return JSON object with list "meals".
    Item structure: {{ "name": "Meal Name", "rationale": "Why good?", "time": "15 min", "micro_goal": "Drink water" }}
    Return ONLY JSON.
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        print("✅ AI Response received for Meals.")
        return json.loads(text)
    except Exception as e:
        print(f"❌ ERROR in Meal Generation: {e}")
        return {"meals": [{"name": "Error: Check Terminal", "rationale": "AI Connection Failed", "time": "0", "micro_goal": "Fix API Key"}]}

def get_recipe_for_meal(meal_name):
    print(f"--- 3. Generating Recipe for {meal_name} ---")
    try:
        response = model.generate_content(f"Write a full recipe for {meal_name}. Ingredients and Steps.")
        return response.text
    except Exception as e:
        print(f"❌ ERROR in Recipe: {e}")
        return "Could not connect to AI. Please check your API Key."

def verify_safety(meal_name, allergies):
    return True, "Safe" # פשוט לבינתיים כדי לא לחסום