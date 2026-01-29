import google.generativeai as genai

# --- שים כאן את המפתח החדש שלך ---
MY_API_KEY = "AIzaSyCix9FoS8VJmOsn8QEl65kLGiLJBTZgsZ8"

genai.configure(api_key=MY_API_KEY)

print("--- רשימת המודלים הזמינים ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"{m.name}")
except Exception as e:
    print(f"שגיאה: {e}")