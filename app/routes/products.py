from fastapi import APIRouter, HTTPException, Query
from app.services import openfoodfacts_service
from app.models.product_models import ProductSearchResponse, ProductDetail, ProductResponse

router = APIRouter()

@router.get("/search", response_model=ProductSearchResponse)
async def search_products(q: str = Query(..., description="Product name or barcode"), limit: int = 10):
    """
    Search for products using Open Food Facts API.
    """
    products = openfoodfacts_service.search_products(q, limit)
    return ProductSearchResponse(products=products, count=len(products))

@router.get("/product/{code}", response_model=ProductDetail)
async def get_product_detail(code: str):
    """
    Get generic details for a specific product.
    """
    product = openfoodfacts_service.get_product_details(code)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/barcode/{code}", response_model=ProductResponse)
async def barcode_search(code: str):
    product = openfoodfacts_service.barcode_search(code)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
    