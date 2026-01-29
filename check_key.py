import google.generativeai as genai

# --- שים כאן את המפתח החדש שלך ---
MY_API_KEY = "AIzaSyA-BX0mmCj-9-Di9K-xUqmoa2CzpH9XSJc"

genai.configure(api_key=MY_API_KEY)

print("------------------------------------------------")
print("בודק מודלים זמינים...")
try:
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            available_models.append(m.name)
            
    print("------------------------------------------------")
    
    target_model = "models/gemini-1.5-flash"
    if target_model in available_models:
        print(f"✅ יש! המודל {target_model} זמין.")
    else:
        print(f"❌ המודל {target_model} חסר. עליך לעדכן את הספרייה.")

except Exception as e:
    print(f"שגיאה: {e}")