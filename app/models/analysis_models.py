from pydantic import BaseModel, Field
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    ingredients_text: str
    product_name: Optional[str] = None


class AnalysisResult(BaseModel):
    summary: str = ""
    harmful_additives: List[str] = Field(default_factory=list)
    hidden_sugars: List[str] = Field(default_factory=list)
    maida_trap_alert: bool = False
    fake_marketing_alert: bool = False
    recommendation: str = ""


class AnalyzeResponse(BaseModel):
    product_name: Optional[str] = None
    analysis: str

class OCRRequest(BaseModel):
    # Depending on how we handle the image (multipart usually), but for metadata:
    pass # Image will be uploaded as File

### depricated above !


from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class HealthRisk(BaseModel):
    ingredient: str = ""
    risk: str = ""
    health_impact: str = ""
    regulatory_status: str = ""

class MarketingTrap(BaseModel):
    claim: str = ""
    reality: str = ""

class AlertDetail(BaseModel):
    detected: bool = False
    explanation: str = ""

class PopulationWarnings(BaseModel):
    children: str = ""
    pregnant_women: str = ""
    diabetics: str = ""
    allergy_risk: str = ""

class AnalysisResult(BaseModel):
    product_name: str = ""
    overall_verdict: str = "Consume With Caution"
    summary: str = ""
    health_risks: List[HealthRisk] = Field(default_factory=list)
    positive_highlights: List[str] = Field(default_factory=list)
    hidden_sugars: List[str] = Field(default_factory=list)
    harmful_additives: List[str] = Field(default_factory=list)
    marketing_traps: List[MarketingTrap] = Field(default_factory=list)
    population_warnings: PopulationWarnings = Field(default_factory=PopulationWarnings)
    # This matches the "alerts" object in the JSON
    alerts: Dict[str, AlertDetail] = Field(default_factory=dict)
    consumption_advice: str = ""
    recommendation: str = ""