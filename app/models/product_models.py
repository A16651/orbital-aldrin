from pydantic import BaseModel
from typing import List, Optional, Any

class ProductBase(BaseModel):
    product_name: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    id: str  # Barcode or ID

class ProductSearchRequest(BaseModel):
    query: str
    limit: int = 10

class ProductSearchResponse(BaseModel):
    products: List[ProductBase]
    count: int

class ProductDetail(ProductBase):
    ingredients_text: Optional[str] = None
    nutriments: Optional[Any] = None

class ProductResponse(BaseModel):
    code: str
    product_name: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    id: Optional[str] = None
