import requests
from typing import List, Dict, Any, Set
from app.models.product_models import ProductBase, ProductDetail
from difflib import SequenceMatcher

OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"
OFF_PRODUCT_URL = "https://world.openfoodfacts.org/api/v0/product/"
OFF_barcode_url = "https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

def search_products(query: str, limit: int = 10) -> List[ProductBase]:
    """
    Rule-based search:
    1. Try exact query. If results found -> Return immediately.
    2. If empty -> Split query, pick top 3 longest words.
    3. Search those 3 words individually and combine results.
    """
    
    # --- RULE 1: Exact Query Search ---
    # Try to find the exact match first.
    products = _execute_off_search(query, page_size=limit)
    
    # If we got even 1 result, return it immediately and STOP.
    if products:
        return products

    # --- RULE 2: Fallback (Longest Words) ---
    # If we are here, the exact search failed (returned []).
    words = query.split()
    
    # Only proceed if we have multiple words (e.g., "Amul Butter")
    if len(words) > 1:
        # Sort words by length (descending) and take the top 3
        # Ex: "Amul Butter Pack" -> ["Butter", "Pack", "Amul"] (depending on length ties)
        longest_words = sorted(words, key=len, reverse=True)[:3]
        
        fallback_results = []
        seen_ids: Set[str] = set()
        
        for word in longest_words:
            # Search for this specific word
            word_results = _execute_off_search(word, page_size=limit)
            
            # Append results, ensuring no duplicates
            for p in word_results:
                if p.id not in seen_ids:
                    fallback_results.append(p)
                    seen_ids.add(p.id)
        
        return fallback_results

    # If single word query failed, return nothing
    return []

def _execute_off_search(search_term: str, page_size: int) -> List[ProductBase]:
    """Helper function to execute the raw API request"""
    params = {
        "search_terms": search_term,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size
    }
    try:
        # Timeout set to 5s to keep the UI snappy even if we do multiple calls
        response = requests.get(OFF_SEARCH_URL, params=params, timeout=10) 
        response.raise_for_status()
        data = response.json()
        
        products = []
        for item in data.get('products', []):
            products.append(ProductBase(
                product_name=item.get('product_name', 'Unknown Product'),
                brand=item.get('brands', 'Unknown Brand'),
                image_url=item.get('image_front_small_url', ''),
                id=item.get('code')
            ))
        return products
    except Exception as e:
        print(f"Warning: OFF Search failed for term '{search_term}': {e}")
        return []

def get_product_details(barcode: str) -> ProductDetail:
    url = f"{OFF_PRODUCT_URL}{barcode}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 1:
            product = data.get('product', {})
            return ProductDetail(
                product_name=product.get('product_name', 'Unknown Product'),
                brand=product.get('brands', 'Unknown Brand'),
                image_url=product.get('image_front_url'),
                id=barcode,
                ingredients_text=product.get('ingredients_text'),
                nutriments=product.get('nutriments')
            )
    except Exception as e:
        print(f"Error fetching product details: {e}")
    return None

def barcode_search(code):
    """
    Search for a product in Open Food Facts by barcode.

    :param code: str or int - product barcode (EAN/UPC)
    :return: dict with product data if found, otherwise None
    """
    url = OFF_barcode_url.format(barcode=code)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

    data = response.json()

    # status == 1 means product found
    if data.get("status") == 1:
        return data.get("product")

    # Product not found
    return None