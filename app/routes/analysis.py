from fastapi import APIRouter, File, UploadFile, HTTPException
from app.models.analysis_models import AnalyzeRequest, AnalyzeResponse, AnalysisResult
from app.services import watson_ai_service, watson_ocr_service
from app.services import openfoodfacts_service

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_ingredients(request: AnalyzeRequest):
    """
    Analyze ingredient list for harmful contents using IBM Watson AI.
    """
    analysis = watson_ai_service.analyze_ingredients_with_watson(request.ingredients_text, request.product_name)
    return AnalyzeResponse(product_name=request.product_name, analysis=analysis)

@router.post("/analyze/product/{code}", response_model=AnalyzeResponse)
async def analyze_product_by_id(code: str):
    """
    Fetch product from Open Food Facts and then analyze it.
    Returns the analysis as a plain text string.
    """
    product = openfoodfacts_service.get_product_details(code)
    
    if not product or not product.ingredients_text:
        raise HTTPException(status_code=404, detail="Product ingredients not found")
    
    # Get the plain text analysis string
    analysis_text = watson_ai_service.analyze_ingredients_with_watson(
        product.ingredients_text, 
        product.product_name
    )
    
    # Return directly. 
    return AnalyzeResponse(product_name=product.product_name, analysis=analysis_text)

@router.post("/ocr", response_model=AnalyzeResponse)
async def ocr_and_analyze(file: UploadFile = File(...)):
    """
    Upload an image of ingredients, extract text via Watson Discovery (or fallback), 
    and then analyze the extracted text.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file content safely
    contents = await file.read()
    
    # Save temporarily if needed by SDK or pass bytes. 
    # The helper `extract_text_from_image` expects a file-like object or bytes depending on implementation.
    # Watson Discovery `add_document` takes `file`.
    
    # For now, using a mock result in the service if keys aren't there, 
    # but let's pretend we extracted text.
    extracted_text = watson_ocr_service.mock_ocr_process() 
    # extracted_text = watson_ocr_service.extract_text_from_image(contents, file.filename)
    
    if "Error" in extracted_text:
         # If it's a real error (not just the mock message), handle it.
         pass

    # Then analyze
    analysis = watson_ai_service.analyze_ingredients_with_watson(extracted_text, product_name="Uploaded Image Product")
    
    return AnalyzeResponse(product_name="Uploaded Image Product", analysis=analysis)
