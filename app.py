import streamlit as st
import pandas as pd
import requests
import json
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, value

# AI API wrapper for OpenRouter (DeepSeek model)
def ai_wrapper(query):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",  # Replace with your actual key
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat-v3.1:free",
                "messages": [
                    {
                        "role": "user",
                        "content": query 
                    }
                ],
            })
        )
        response.raise_for_status()  # Raise an error for bad status codes
        result = response.json()
        # Extract the generated text from OpenRouter's response structure
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error in API call: {str(e)}"

# Streamlit App
st.title("Prototype: Fxdata, Pwani AI Hub")

tab1, tab2, tab3 = st.tabs(["Product Development", "Innovation", "Order Efficiency"])

with tab1:
    st.header("Product Development & Market Intro")
    product_idea = st.text_input("Enter product idea:")
    if st.button("Analyze Market & Suggest Launch"):
        if product_idea:
            query = f"Predict market trends and launch strategy for: {product_idea}"
            result = ai_wrapper(query)
            st.write("AI Suggestion:", result)
            # Add predictive analytics (e.g., mock trend data)
            trends = pd.DataFrame({"Trend": ["Demand Growth", "Competitor Gap"], "Score": [0.8, 0.6]})
            st.table(trends)
        else:
            st.warning("Please enter a product idea.")

with tab2:
    st.header("Foster Innovation")
    challenge = st.text_input("Enter company challenge:")
    if st.button("Generate Ideas"):
        if challenge:
            query = f"Generate innovative ideas for: {challenge}"
            result = ai_wrapper(query)
            st.write("AI Ideas:", result)
        else:
            st.warning("Please enter a company challenge.")

with tab3:
    st.header("Improve Order Efficiency")
    st.subheader("Upload Order Data (CSV: columns 'Item', 'Demand', 'Cost')")
    uploaded_file = st.file_uploader("Choose CSV", type="csv")
    if uploaded_file and st.button("Optimize Orders"):
        try:
            df = pd.read_csv(uploaded_file)
            # Validate required columns
            required_columns = ['Item', 'Demand', 'Cost']
            if not all(col in df.columns for col in required_columns):
                st.error("CSV must contain 'Item', 'Demand', and 'Cost' columns.")
            else:
                prob = LpProblem("Order_Optimization", LpMinimize)
                items = df['Item'].tolist()
                demand = dict(zip(items, df['Demand']))
                cost = dict(zip(items, df['Cost']))
                vars = {item: LpVariable(item, lowBound=0) for item in items}
                prob += lpSum([cost[item] * vars[item] for item in items])  # Objective: Minimize cost
                for item in items:
                    prob += vars[item] >= demand[item]  # Constraints: Meet demand
                prob.solve()
                optimized = {item: value(vars[item]) for item in items}
                st.write("Optimized Orders:", optimized)
                total_cost = value(prob.objective)
                st.write(f"Total Minimized Cost: {total_cost}")
        except Exception as e:
            st.error(f"Error in optimization: {str(e)}")