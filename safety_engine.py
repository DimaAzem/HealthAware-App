def verify_nutrition_safety(biomarkers, meal_name, ingredients):
    """
    מנוע בטיחות דטרמיניסטי שבודק את המלצת ה-AI מול המדדים הרפואיים.
    """
    is_safe = True
    rationale = "This meal is balanced and safe for your current profile."
    
    # 1. בדיקת חוסר בברזל (הלוגיקה מהמוקאפ)
    iron_level = biomarkers.get('Iron')
    if iron_level is not None and iron_level < 50:
        # אם הברזל נמוך, נוודא שהמנה מכילה רכיבים עשירים בברזל
        iron_rich = ["spinach", "lentils", "chicken", "red meat", "nuts"]
        found_iron = any(item.lower() in str(ingredients).lower() or item.lower() in meal_name.lower() for item in iron_rich)
        
        if found_iron:
            rationale = "Strategic Choice: This meal includes iron-rich ingredients to address your deficiency (Iron < 50 ug/dL)."
        else:
            is_safe = False
            rationale = "Warning: This meal lacks sufficient iron-rich ingredients for your profile."

    # 2. בדיקת גלוקוז (סוכר גבוה)
    glucose_level = biomarkers.get('Glucose')
    if glucose_level is not None and glucose_level > 110:
        sugar_items = ["honey", "sugar", "syrup", "white bread"]
        found_sugar = any(item.lower() in str(ingredients).lower() for item in sugar_items)
        
        if found_sugar:
            is_safe = False
            rationale = "Safety Alert: High Glucose detected. This meal contains prohibited high-glycemic ingredients."

    return is_safe, rationale