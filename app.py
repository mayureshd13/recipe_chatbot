import streamlit as st
import pandas as pd
import random
from deep_translator import GoogleTranslator

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

# Function to format and display recipe details
def format_recipe(name):
    recipe = df[df["TranslatedRecipeName"].str.contains(name, case=False, na=False)]
    
    if not recipe.empty:
        data = recipe.iloc[0]
        ingredients = data['TranslatedIngredients'].split(',')
        instructions = data['TranslatedInstructions'].split('. ')
        target_lang = languages[selected_lang]
        
        # Display structured recipe format
        st.markdown(f"## 🍽️ {translate_text(data['TranslatedRecipeName'], target_lang)}")
        st.image(data['image-url'], width=300)

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
    else:
        st.warning("❌ Recipe not found. Try another name or select from suggestions.")

# Function to suggest a random recipe
def suggest_random_recipe():
    recipe = df.sample(1).iloc[0]
    format_recipe(recipe['TranslatedRecipeName'])

# Get recipe suggestions based on user input
def get_suggestions(query):
    if query:
        return df[df["TranslatedRecipeName"].str.contains(query, case=False, na=False)]["TranslatedRecipeName"].tolist()
    return []

# Streamlit UI
st.title("🍜 RecipeBot")
st.write("A smart recipe assistant! Click **Start** to begin.")

# Start button
if st.button("Start Chat"):
    st.session_state.started = True
    st.session_state.bot_message = "Hello! I'm RecipeBot 🤖. What recipe are you looking for today?"

# Initialize session state
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.bot_message = ""

if st.session_state.started:
    st.markdown(f"🗨️ **Bot:** {st.session_state.bot_message}")

    # Recipe search input with dynamic suggestions
    user_input = st.text_input("🔍 Start typing a recipe name...", key="recipe_input")

    # Show recipe name suggestions
    suggestions = get_suggestions(user_input)
    if suggestions:
        selected_recipe = st.selectbox("🔽 Suggested Recipes:", suggestions, key="suggestions")
        user_input = selected_recipe

    # "Surprise Me!" random recipe button
    if st.button("🎲 Surprise Me!"):
        suggest_random_recipe()

    # Display recipe details
    if user_input:
        format_recipe(user_input)

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