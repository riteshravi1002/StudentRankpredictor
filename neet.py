import requests
import cohere
import json
import customtkinter as ctk
from tkinter import scrolledtext

# Set up Cohere API key (Replace with your actual API key)
co = cohere.Client("DJkb1JHfpXy7IVfewQHFhNefuR2O9XTKWh4u6rg1")

# API Endpoints
current_quiz_endpoint = "https://www.jsonkeeper.com/b/LLQT"
quiz_submission_endpoint = "https://api.jsonserve.com/rJvd7g"
historical_quiz_endpoint = "https://api.jsonserve.com/XgAgFJ"

# Function to fetch data from API
def fetch_data(endpoint):
    response = requests.get(endpoint)
    return response.json() if response.status_code == 200 else None

# Function to analyze performance
def analyze_performance(historical_data):
    insights = {}
    for quiz in historical_data:
        topic = quiz["quiz"].get("topic", "Unknown")
        correct_option = quiz["quiz"].get("correct_option_id")
        correct_answers = sum(1 for ans in quiz["response_map"].values() if ans == correct_option)
        total_questions = len(quiz["response_map"])
        accuracy = (correct_answers / total_questions) * 100 if total_questions else 0
        insights[topic] = {"total_questions": total_questions, "correct_answers": correct_answers, "accuracy": accuracy}
    return insights

# Function to predict NEET rank
def predict_neet_rank(quiz_submission_data):
    better_than = quiz_submission_data.get("better_than", 50)
    predicted_rank = int(2400000 * (1 - (better_than / 100)))
    return predicted_rank

# Function to generate AI-based recommendations using Cohere
def generate_recommendations(insights):
    prompt = f"""
    A student is preparing for NEET. Based on their performance data below, provide personalized study recommendations.

    Performance Insights:
    {json.dumps(insights, indent=2)}

    Instructions:
    - Identify weak topics.
    - Suggest question types (conceptual, numerical, theoretical).
    - Recommend difficulty levels to focus on.
    - Provide study techniques to improve accuracy.
    """

    response = co.generate(
        model="command",  # Cohere's model for text generation
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    return response.generations[0].text

# Function to generate student persona using Cohere
def generate_persona(insights):
    prompt = f"""
    Analyze the student's persona based on the performance insights below. Identify strong and weak areas and provide a motivational message.

    Performance Insights:
    {json.dumps(insights, indent=2)}
    """

    response = co.generate(
        model="command",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    return response.generations[0].text

# Function to handle the 'Analyze' button click
def analyze():
    historical_quiz_data = fetch_data(historical_quiz_endpoint)
    quiz_submission_data = fetch_data(quiz_submission_endpoint)

    if not historical_quiz_data or not quiz_submission_data:
        result_textbox.insert("end", "Error fetching data.\n", "error")
        return

    insights = analyze_performance(historical_quiz_data)
    persona = generate_persona(insights)
    predicted_rank = predict_neet_rank(quiz_submission_data)
    recommendations = generate_recommendations(insights)

    result_textbox.delete("1.0", "end")  # Clear previous text
    result_textbox.insert("end", f"🔍 Student Persona:\n{persona}\n\n", "bold")
    result_textbox.insert("end", f"🎯 Predicted NEET Rank: {predicted_rank}\n\n", "highlight")
    result_textbox.insert("end", f"📚 Study Recommendations:\n{recommendations}\n", "normal")

# GUI Setup
ctk.set_appearance_mode("dark")  # Dark mode
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("NEET AI Performance Analyzer")
root.geometry("800x600")  # Adjust window size

frame = ctk.CTkFrame(root, corner_radius=15)
frame.pack(pady=20, padx=20, fill="both", expand=True)

title_label = ctk.CTkLabel(frame, text="📊 NEET AI Performance Analyzer", font=("Arial", 20, "bold"))
title_label.pack(pady=10)

analyze_button = ctk.CTkButton(frame, text="🔎 Analyze Performance", command=analyze, font=("Arial", 16))
analyze_button.pack(pady=10)

# Textbox for results (Resizable & Scrollable)
result_textbox = scrolledtext.ScrolledText(frame, wrap="word", font=("Arial", 14), height=15, width=80)
result_textbox.pack(padx=10, pady=10, fill="both", expand=True)

# Text formatting
result_textbox.tag_config("bold", font=("Arial", 14, "bold"))
result_textbox.tag_config("highlight", font=("Arial", 14, "bold"), foreground="lightblue")
result_textbox.tag_config("error", font=("Arial", 14, "bold"), foreground="red")

root.mainloop()
