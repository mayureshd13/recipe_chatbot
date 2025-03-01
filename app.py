import streamlit as st
import pandas as pd
import urllib.parse
from deep_translator import GoogleTranslator
from rapidfuzz import process, fuzz


st.set_page_config(page_title="RecipeBot", page_icon="logo.png")

# Load dataset
df = pd.read_csv("recipes.csv")

# Available languages for translation
languages = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Punjabi": "pa"
}

# Initialize session state for favorites
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# Language selection dropdown
selected_lang = st.selectbox("🌎 Select Language:", list(languages.keys()), index=0)

# Function to translate text
def translate_text(text, target_lang):
    if target_lang != "en":  # No need to translate if English is selected
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    return text

def format_recipe(name):
    # Normalize input and dataset text for better matching
    name = name.strip().lower()
    df["TranslatedRecipeName"] = df["TranslatedRecipeName"].astype(str).str.strip().str.lower()

    # First, try exact match
    recipe = df[df["TranslatedRecipeName"] == name]

    # If no exact match, try partial match
    if recipe.empty:
        recipe = df[df["TranslatedRecipeName"].str.contains(name, case=False, na=False)]

    if not recipe.empty:
        data = recipe.iloc[0]
        ingredients = data['TranslatedIngredients'].split(',')
        instructions = data['TranslatedInstructions'].split('. ')
        target_lang = languages[selected_lang]
        
        # Display structured recipe format
        st.markdown(f"## 🍽️ {translate_text(data['TranslatedRecipeName'], target_lang)}")
        
        # Recipe Image with Frame (Border)
        st.markdown(
            f'<div style="border: 3px solid #4CAF50; padding: 5px; display: inline-block;">'
            f'<img src="{data["image-url"]}" width="300"></div>',
            unsafe_allow_html=True,
        )

        # Ingredients section
        st.markdown("### 🥕 Ingredients:")
        st.markdown("\n".join([f"- {translate_text(ingredient.strip(), target_lang)}" for ingredient in ingredients]))

        # Instructions section (Better formatted)
        st.markdown("### 📖 Instructions:")
        st.markdown("\n".join([f"✔️ {translate_text(step.strip(), target_lang)}" for step in instructions]))

        # More Info as a Button
        st.markdown(
            f'<a href="{data["URL"]}" target="_blank"><button style="background-color:#4CAF50; color:white; border:none; padding:10px 15px; border-radius:5px; cursor:pointer;">🔗 More Info</button></a>',
            unsafe_allow_html=True,
        )

        # Add to Favorites Button
        if st.button(f"⭐ Add to Favorites", key=f"fav_{data['TranslatedRecipeName']}"):
            if data['TranslatedRecipeName'] not in st.session_state.favorites:
                st.session_state.favorites.append(data['TranslatedRecipeName'])
                st.success(f"Added {data['TranslatedRecipeName']} to Favorites!")

        # Share Recipe Feature (Copy & WhatsApp)
        # Translate the recipe based on the selected language
        target_lang = languages[selected_lang]
        translated_recipe_name = translate_text(data['TranslatedRecipeName'], target_lang)
        translated_ingredients = [translate_text(ingredient.strip(), target_lang) for ingredient in ingredients]
        translated_instructions = [translate_text(step.strip(), target_lang) for step in instructions]

        # Combine translated recipe parts into a single string
        translated_recipe_text = f"{translated_recipe_name}\n\nIngredients:\n" + "\n".join(translated_ingredients) + "\n\nInstructions:\n" + "\n".join(translated_instructions)

        # Encode the translated recipe text
        encoded_translated_text = urllib.parse.quote(translated_recipe_text)

        # Generate the WhatsApp link with the translated text
        whatsapp_url = f"https://wa.me/?text={encoded_translated_text}"

        # Display the recipe text for copying
        col1, col2 = st.columns(2)
        with col1:
            st.text_area("📋 Copy and paste this recipe:", translated_recipe_text, height=150)

        # WhatsApp share button with the translated text
        with col2:
            st.markdown(
                f'<a href="{whatsapp_url}" target="_blank">'
                f'<button style="background-color:#25D366; color:white; border:none; padding:10px 15px; border-radius:5px; cursor:pointer;">📲 Share on WhatsApp</button>'
                f'</a>',
                unsafe_allow_html=True
    )

        st.markdown('</div>', unsafe_allow_html=True)  # Close center div

    else:
        st.warning("❌ Recipe not found. Try another name or select from suggestions.")

# Function to suggest a random recipe
def suggest_random_recipe():
    recipe = df.sample(1).iloc[0]
    format_recipe(recipe['TranslatedRecipeName'])

# Function to get recipe suggestions with better search handling
def get_suggestions(query, df):
    if not query:
        return []
    
    query = query.strip().lower().replace(" ", "")  # Normalize user input (remove spaces)
    
    # Normalize dataset by removing spaces and converting to lowercase
    df["NormalizedRecipeName"] = df["TranslatedRecipeName"].str.lower().str.replace(" ", "", regex=False)
    
    # Find exact or partial matches
    exact_matches = df[df["NormalizedRecipeName"].str.contains(query, case=False, na=False)]
    
    if not exact_matches.empty:
        return exact_matches["TranslatedRecipeName"].tolist()
    
    # If no exact match, use fuzzy matching
    possible_matches = process.extract(query, df["TranslatedRecipeName"].tolist(), scorer=fuzz.partial_ratio, limit=5)
    
    # Return results where similarity score is above a threshold (e.g., 70)
    return [match[0] for match in possible_matches if match[1] > 70]

# Streamlit UI
st.markdown("""
    <h1 style='display: inline;'>🍜 RecipeBot</h1>
    <span style='font-size: 14px; font-style: italic; color: gray;'>By Mayuresh D</span>
""", unsafe_allow_html=True)
st.write("A smart recipe assistant! Click **Start** to begin.")

# Start button
if st.button("Start Chat"):
    st.session_state.started = True
    st.session_state.bot_message = "Hello! I'm RecipeBot 🤖. What recipe are you looking for today ?"

# Initialize session state
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.bot_message = ""

if st.session_state.started:
    st.markdown(f"🗨️ **Bot:** {st.session_state.bot_message}")

    # Press 'Enter' to search using Streamlit Form
    with st.form("search_form"):
        user_input = st.text_input("🔍 Start typing a recipe name...", key="recipe_input")
        submitted = st.form_submit_button("Search")

    # Show recipe name suggestions
    suggestions = get_suggestions(user_input,df)
    selected_recipe = None
    if suggestions:
        selected_recipe = st.selectbox("🔽 Suggested Recipes:", suggestions, key="suggestions")
    
    # "Surprise Me!" random recipe button
    if st.button("🎲 Surprise Me!"):
        suggest_random_recipe()

    # Display recipe details when:
    # 1️⃣ User presses Enter (submitted via form)
    # 2️⃣ User selects a recipe from suggestions
    if submitted and user_input:
        format_recipe(user_input)
    elif selected_recipe:  # Automatically display selected recipe
        format_recipe(selected_recipe)

# Display Favorite Recipes Section
st.markdown("## ❤️ My Favorites")
if st.session_state.favorites:
    for fav_recipe in st.session_state.favorites:
        st.write(f"⭐ {fav_recipe}")
        if st.button(f"❌ Remove {fav_recipe}", key=f"remove_{fav_recipe}"):
            st.session_state.favorites.remove(fav_recipe)
            st.rerun()
else:
    st.write("You have no favorite recipes yet.")
