import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    exit()


app = FastAPI()

# Configure CORS to allow requests from our HTML file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the generative models
vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')
text_model = genai.GenerativeModel('gemini-1.5-flash-latest')

@app.post("/process-notes")
async def process_notes(file: UploadFile = File(...)):
    """
    This endpoint receives an image of notes, extracts text,
    corrects and autocompletes it, and suggests further reading.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    # 1. Read image content and extract text using Gemini Vision
    image_contents = await file.read()
    image_parts = [{"mime_type": file.content_type, "data": image_contents}]
    
    prompt_extract = "Extract all the handwritten text from this image. Output only the raw text."
    
    try:
        response_vision = vision_model.generate_content([prompt_extract, *image_parts])
        raw_text = response_vision.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text from image: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the image.")

    # 2. Correct, autocomplete, and summarize the text using Gemini Pro
    prompt_process = f"""
    You are an expert academic assistant. Based on the raw text extracted from a student's notes, perform the following tasks:
    1.  **Corrected Text**: Fix any spelling, grammar, or factual errors.
    2.  **Autocompleted Notes**: If sentences are incomplete or ideas are not fully explained, expand on them to create a more complete set of notes.
    3.  **Summary**: Provide a concise summary of the key concepts.

    Format your response as a single, clean JSON object with the keys "corrected_text", "autocompleted_notes", and "summary". Do not include any text outside of this JSON object.

    Raw Text:
    ---
    {raw_text}
    ---
    """
    
    try:
        response_process = text_model.generate_content(prompt_process)
        processed_json_str = response_process.text.strip().replace("```json", "").replace("```", "").strip()
        processed_data = json.loads(processed_json_str)
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"Error processing text or parsing JSON response: {str(e)}")

    # 3. Suggest further reading based on the summary
    summary = processed_data.get("summary", "")
    if not summary:
         raise HTTPException(status_code=400, detail="Could not generate a summary to find suggestions.")

    prompt_suggest = f"""
    Based on the following notes summary, recommend 3 to 5 external resources (articles, videos, interactive tutorials) to help a student master these concepts.
    Provide a title, a brief description, and a URL for each resource.

    Format your response as a JSON array of objects, where each object has the keys "title", "description", and "url". Do not include any text outside of this JSON array.

    Summary:
    ---
    {summary}
    ---
    """

    try:
        response_suggest = text_model.generate_content(prompt_suggest)
        suggest_json_str = response_suggest.text.strip().replace("```json", "").replace("```", "").strip()
        suggestions = json.loads(suggest_json_str)
    except (json.JSONDecodeError, Exception) as e:
        suggestions = [{"title": "Error", "description": "Could not generate suggestions.", "url": ""}]

    # 4. Combine all results and return
    final_response = {
        "raw_text": raw_text,
        "corrected_text": processed_data.get("corrected_text", ""),
        "autocompleted_notes": processed_data.get("autocompleted_notes", ""),
        "summary": summary,
        "suggestions": suggestions
    }
    
    return final_response


@app.get("/")
def read_root():
    return {"status": "Notes AI Backend is running!"}