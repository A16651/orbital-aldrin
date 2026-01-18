import os
import json
from app.config import get_settings
from app.models.analysis_models import AnalysisResult
import re
import json
import logging
from typing import Optional

logging.basicConfig(
    filename='model_hostory.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Watson SDKs
try:
    from ibm_watson_machine_learning.foundation_models import Model
    from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
except ImportError:
    print("Warning: ibm-watson-machine-learning not installed.")
    Model = None

settings = get_settings()

def clean_and_repair_json(text_output: str) -> Optional[dict]:
    if not text_output:
        return None

    # 1. Clean whitespace and markdown
    cleaned = text_output.strip()
    cleaned = re.sub(r'^```(?:json)?\s*|```$', '', cleaned, flags=re.IGNORECASE).strip()
    
    # 2. HANDLE PRE-FILL CORRECTLY
    # If it already starts with {, don't add another one.
    # If it starts with " (a key), add the brace.
    if not cleaned.startswith('{'):
        cleaned = '{' + cleaned
    
    # 3. FIX LOG-SPECIFIC HALLUCINATIONS
    cleaned = cleaned.replace('[-]', '[]')
    # Fix the Iodine] issue seen in your logs
    cleaned = cleaned.replace(']', '"]').replace('"]', '"]').replace(']]', ']')
    
    # 4. REMOVE DOUBLE BRACES (The most likely culprit for your current error)
    while cleaned.startswith('{{'):
        cleaned = cleaned[1:]
    while cleaned.endswith('}}'):
        cleaned = cleaned[:-1]

    # 5. PARSE
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Final attempt: isolate strictly between first { and last }
        try:
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1:
                return json.loads(cleaned[start:end+1])
        except:
            return None
    return None


def analyze_ingredients_with_watson(ingredients: str, product_name: str = "") -> AnalysisResult:
    """
    Analyzes the ingredients list using IBM watsonx.ai to identify health concerns.
    """
    
    if not settings.ibm_api_key or not settings.project_id:
        # Fallback/Mock for testing without keys
        return AnalysisResult(
            summary="[MOCK] Analysis requires IBM Cloud credentials. Ingredients received: " + ingredients[:50] + "...",
            harmful_additives=["Check credentials"],
            recommendation="Configure .env with IBM keys to get real analysis."
        )

    # Simplified Prompt Engineering
    prompt_input = (
    """
    ROLE : You are a Senior Food Safety & Public Health Analyst specializing in FSSAI (India), EU, and US FDA standards.

    TASK: Analyze the product ingredients below and provide a clear, readable health assessment in plain text.
    
    CONSTRAINTS:
    1. OUTPUT FORMAT: Plain text only. 
    2. FORBIDDEN CHARACTERS: Do NOT use Markdown, asterisks (**), hashtags (#), or backticks (```).
    3. STYLE: Professional, direct, and easy to read. Use newlines to separate sections.
    
    STRUCTURE YOUR RESPONSE AS FOLLOWS:
    
    OVERALL VERDICT
    (e.g. healthy, Safe, Consume with Caution, or Avoid, dont consume often or frequently, etc.)
    
    SUMMARY
    (A concise paragraph explaining the health profile, fake marketing)
    
    KEY RISKS
    (List specific ingredients and why they are harmful. Do not use bullet points, just list them clearly)
    
    POSITIVE HIGHLIGHTS
    (Any good nutritional aspects if any)
    
    RECOMMENDATION
    (Who should consume this and how often)

    MARKETING TRAPS :
    (Any fake marketings, e.g. Product name is Natural juice but actual fruit juice is very less and mostly its water and sugar or
     Product name is something healthy but major ingredients are not healthy. )

    DATA TO ANALYZE:
    Product: {product_name}
    Ingredients: {ingredients}
    
    RESPONSE:
    """
    ).format(product_name=product_name, ingredients=ingredients)

    creds = {
        "url": settings.ibm_service_url,
        "apikey": settings.ibm_api_key
    }
    
    # Initialize Model
    model_id = "ibm/granite-3-8b-instruct"
    
    params = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: 600,
        GenParams.MIN_NEW_TOKENS: 10,
        # We removed "}" from stop sequences since we aren't generating JSON
        GenParams.REPETITION_PENALTY: 1.1
    }

    model = Model(
        model_id=model_id,
        params=params,
        credentials=creds,
        project_id=settings.project_id
    )

    try:
        response = model.generate_text(prompt=prompt_input)
        
        # Standardize extraction
        if isinstance(response, dict):
            raw_text = response.get('generated_text') or response.get('text') or str(response)
        elif hasattr(response, 'generated_text'):
            raw_text = response.generated_text
        else:
            raw_text = str(response)

        # Cleanup: Ensure no stray markdown remains if the model hallucinates it
        final_text = raw_text.replace("**", "").replace("##", "").replace("```", "").strip()
        
        logger.info(f"AI TEXT OUTPUT: {final_text}")

        return final_text

    except Exception as e:
        logger.exception(f"Critical error in analysis: {e}")
        return "Error: A system error occurred during the ingredient analysis. Please try again later."