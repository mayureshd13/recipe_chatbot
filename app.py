import streamlit as st
import pandas as pd
import random

# Load dataset
df = pd.read_csv("recipes.csv")

# Initialize session state for favorites
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# Function to format recipe details
def format_recipe(name):
    recipe = df[df["TranslatedRecipeName"].str.contains(name, case=False, na=False)]
    
    if not recipe.empty:
        data = recipe.iloc[0]
        ingredients = data['TranslatedIngredients'].split(',')
        instructions = data['TranslatedInstructions'].split('. ')
        
        # Display structured recipe format
        st.markdown(f"## 🍽️ {data['TranslatedRecipeName']}")
        st.image(data['image-url'], width=300)  # Show recipe image

        # Ingredients section
        st.markdown("### 🥕 Ingredients:")
        st.markdown("\n".join([f"- {ingredient.strip()}" for ingredient in ingredients]))

        # Instructions section (Better formatted)
        st.markdown("### 📖 Instructions:")
        st.markdown("\n".join([f"✔️ {step.strip()}" for step in instructions]))

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
        user_input = selected_recipe  # Auto-fill the selection

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
            st.rerun()  # Refresh the app after removing
else:
    st.write("You have no favorite recipes yet.")
