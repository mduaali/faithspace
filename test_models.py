import google.generativeai as genai
import os

# Put your key here just for this 10-second test
genai.configure(api_key="YOUR_ACTUAL_API_KEY")

print("Checking available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"✅ Found: {m.name}")