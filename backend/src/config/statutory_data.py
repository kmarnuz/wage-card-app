"""
Statutory Data Configuration
Professional Tax slabs and LWF rates by state.
This data is configurable and can be updated via admin UI.
"""

from services.calculation_engine import PTaxSlab, LWFConfig


# =============================================================================
# PROFESSIONAL TAX SLABS BY STATE
# Format: state_name -> list of PTaxSlab (threshold = upper limit for that slab)
# Logic: Find highest threshold where gross >= threshold, use that amount
# =============================================================================

PTAX_SLABS: dict[str, list[PTaxSlab]] = {
    "ANDHRA PRADESH": [
        PTaxSlab(threshold=15000, amount=0),
        PTaxSlab(threshold=15001, amount=150),
        PTaxSlab(threshold=20001, amount=200),
    ],
    "ASSAM": [
        PTaxSlab(threshold=9000, amount=0),
        PTaxSlab(threshold=10001, amount=150),
        PTaxSlab(threshold=15001, amount=180),
        PTaxSlab(threshold=25001, amount=208),
    ],
    "BIHAR": [
        PTaxSlab(threshold=24999, amount=0),
        PTaxSlab(threshold=25000, amount=83),
        PTaxSlab(threshold=41667, amount=167),
        PTaxSlab(threshold=83332, amount=167),
        PTaxSlab(threshold=83333, amount=200),
    ],
    "CHATTISGARH": [
        PTaxSlab(threshold=1, amount=0),
    ],
    "CHANDIGARH": [
        PTaxSlab(threshold=1, amount=0),
    ],
    "DELHI": [
        PTaxSlab(threshold=1, amount=0),
    ],
    "GOA": [
        PTaxSlab(threshold=1, amount=0),
    ],
    "GUJARAT": [
        PTaxSlab(threshold=5999, amount=0),
        PTaxSlab(threshold=6001, amount=0),
        PTaxSlab(threshold=9001, amount=0),
        PTaxSlab(threshold=12001, amount=200),
    ],
    "HARYANA": [
        PTaxSlab(threshold=1, amount=0),
    ],
    "JHARKHAND": [
        PTaxSlab(threshold=24999, amount=100),
        PTaxSlab(threshold=41666, amount=150),
        PTaxSlab(threshold=66666, amount=175),
        PTaxSlab(threshold=83333, amount=208),
    ],
    "KARNATAKA": [
        PTaxSlab(threshold=24999, amount=0),
        PTaxSlab(threshold=25000, amount=200, special_month="February", special_amount=300),
    ],
    "KERALA": [
        PTaxSlab(threshold=1999, amount=0),
        PTaxSlab(threshold=2000, amount=53),
        PTaxSlab(threshold=3000, amount=75),
        PTaxSlab(threshold=5000, amount=100),
        PTaxSlab(threshold=7500, amount=125),
        PTaxSlab(threshold=10000, amount=125),
        PTaxSlab(threshold=12500, amount=125),
        PTaxSlab(threshold=16667, amount=167),
        PTaxSlab(threshold=20833, amount=208),
    ],
    "MADHYA PRADESH": [
        PTaxSlab(threshold=18750, amount=0),
        PTaxSlab(threshold=18751, amount=125),
        PTaxSlab(threshold=25001, amount=167, special_month="March", special_amount=174),
        PTaxSlab(threshold=33334, amount=208, special_month="March", special_amount=212),
    ],
    "MAHARASHTRA": [
        PTaxSlab(threshold=7500, amount=0),
        PTaxSlab(threshold=7501, amount=175),
        PTaxSlab(threshold=10001, amount=200, special_month="February", special_amount=300),
    ],
    "ORISSA": [
        PTaxSlab(threshold=13333, amount=0),
        PTaxSlab(threshold=25000, amount=0),
    ],
    "PONDICHERRY": [
        PTaxSlab(threshold=0, amount=0),
        PTaxSlab(threshold=16666.001, amount=42),
        PTaxSlab(threshold=33333.001, amount=83),
        PTaxSlab(threshold=50000.001, amount=125),
        PTaxSlab(threshold=66666.001, amount=167),
        PTaxSlab(threshold=83333.001, amount=208),
    ],
    "PUNJAB": [
        PTaxSlab(threshold=20832, amount=0),
        PTaxSlab(threshold=20833, amount=200),
    ],
    "RAJASTHAN": [
        PTaxSlab(threshold=1, amount=0),
    ],
    "TAMIL NADU COIMBATORE": [
        PTaxSlab(threshold=3500, amount=29),
        PTaxSlab(threshold=5000, amount=71),
        PTaxSlab(threshold=7500, amount=143),
        PTaxSlab(threshold=10000, amount=208),
    ],
    "TAMILNADU_CHENNAI": [
        PTaxSlab(threshold=0, amount=0),
        PTaxSlab(threshold=3500, amount=23),
        PTaxSlab(threshold=5000, amount=53),
        PTaxSlab(threshold=7500, amount=115),
        PTaxSlab(threshold=10000, amount=171),
        PTaxSlab(threshold=12500, amount=208),
    ],
    "TAMILNADU_MADURAI": [
        PTaxSlab(threshold=3499, amount=0),
        PTaxSlab(threshold=3500, amount=28),
        PTaxSlab(threshold=5000, amount=68),
        PTaxSlab(threshold=7500, amount=140),
        PTaxSlab(threshold=10000, amount=208),
        PTaxSlab(threshold=12500, amount=208),
    ],
    "TAMILNADU_SALEM": [
        PTaxSlab(threshold=3499, amount=0),
        PTaxSlab(threshold=3500, amount=18),
        PTaxSlab(threshold=5000, amount=55),
        PTaxSlab(threshold=7500, amount=103),
        PTaxSlab(threshold=10000, amount=165),
        PTaxSlab(threshold=12500, amount=220),
    ],
    "TAMILNADU_TIRUPUR": [
        PTaxSlab(threshold=3499, amount=0),
        PTaxSlab(threshold=3500, amount=29),
        PTaxSlab(threshold=5000, amount=71),
        PTaxSlab(threshold=7500, amount=143),
        PTaxSlab(threshold=10000, amount=208),
        PTaxSlab(threshold=12500, amount=208),
    ],
    "TAMILNADU_TRICHY": [
        PTaxSlab(threshold=3499, amount=0),
        PTaxSlab(threshold=3500, amount=28),
        PTaxSlab(threshold=5000, amount=72),
        PTaxSlab(threshold=7500, amount=143),
        PTaxSlab(threshold=10000, amount=208),
        PTaxSlab(threshold=12500, amount=208),
    ],
    "TAMILNADU_VELLORE": [
        PTaxSlab(threshold=3499, amount=0),
        PTaxSlab(threshold=3500, amount=24),
        PTaxSlab(threshold=5000, amount=61),
        PTaxSlab(threshold=7500, amount=122),
        PTaxSlab(threshold=10000, amount=183),
        PTaxSlab(threshold=12500, amount=208),
    ],
    "TELANGANA": [
        PTaxSlab(threshold=15000, amount=0),
        PTaxSlab(threshold=15001, amount=150),
        PTaxSlab(threshold=20001, amount=200),
    ],
    "UTTAR PRADESH": [
        PTaxSlab(threshold=1, amount=0),
    ],
    "UTTARAKHAND": [
        PTaxSlab(threshold=1, amount=0),
    ],
    "WEST BENGAL": [
        PTaxSlab(threshold=8500, amount=0),
        PTaxSlab(threshold=10001, amount=110),
        PTaxSlab(threshold=15001, amount=130),
        PTaxSlab(threshold=25001, amount=150),
        PTaxSlab(threshold=40001, amount=200),
    ],
}


# =============================================================================
# LABOUR WELFARE FUND (LWF) BY STATE
# =============================================================================

LWF_RATES: dict[str, LWFConfig] = {
    "ANDHRA PRADESH": LWFConfig(
        employee_amount=30, employer_amount=70, frequency="Dec only"
    ),
    "ASSAM": LWFConfig(
        employee_amount=0, employer_amount=0, frequency="N/A"
    ),
    "BIHAR": LWFConfig(
        employee_amount=0, employer_amount=0, frequency="N/A"
    ),
    "CHATTISGARH": LWFConfig(
        employee_amount=15, employer_amount=45, frequency="Jun & Dec"
    ),
    "CHANDIGARH": LWFConfig(
        employee_amount=5, employer_amount=20, frequency="Monthly"
    ),
    "DELHI": LWFConfig(
        employee_amount=1, employer_amount=2, frequency="Jun & Dec"
    ),
    "GOA": LWFConfig(
        employee_amount=60, employer_amount=180, frequency="Jun & Dec"
    ),
    "GUJARAT": LWFConfig(
        employee_amount=6, employer_amount=12, frequency="Jun & Dec"
    ),
    "HARYANA": LWFConfig(
        employee_amount=0.2, employer_amount=0.4, frequency="Monthly",
        is_percentage=True, employee_cap=34, employer_cap=68
    ),
    "JHARKHAND": LWFConfig(
        employee_amount=0, employer_amount=0, frequency="N/A"
    ),
    "KARNATAKA": LWFConfig(
        employee_amount=40, employer_amount=100, frequency="Dec only"
    ),
    "KERALA": LWFConfig(
        employee_amount=50, employer_amount=50, frequency="Monthly"
    ),
    "MADHYA PRADESH": LWFConfig(
        employee_amount=10, employer_amount=30, frequency="Jun & Dec"
    ),
    "MAHARASHTRA": LWFConfig(
        employee_amount=25, employer_amount=75, frequency="Jun & Dec"
    ),
    "ORISSA": LWFConfig(
        employee_amount=10, employer_amount=20, frequency="Jun & Dec"
    ),
    "PONDICHERRY": LWFConfig(
        employee_amount=0, employer_amount=0, frequency="N/A"
    ),
    "PUNJAB": LWFConfig(
        employee_amount=5, employer_amount=20, frequency="Monthly"
    ),
    "RAJASTHAN": LWFConfig(
        employee_amount=0, employer_amount=0, frequency="N/A"
    ),
    "TAMIL NADU COIMBATORE": LWFConfig(
        employee_amount=20, employer_amount=40, frequency="Dec only"
    ),
    "TAMILNADU_CHENNAI": LWFConfig(
        employee_amount=20, employer_amount=40, frequency="Dec only"
    ),
    "TAMILNADU_MADURAI": LWFConfig(
        employee_amount=20, employer_amount=40, frequency="Dec only"
    ),
    "TAMILNADU_SALEM": LWFConfig(
        employee_amount=20, employer_amount=40, frequency="Dec only"
    ),
    "TAMILNADU_TIRUPUR": LWFConfig(
        employee_amount=20, employer_amount=40, frequency="Dec only"
    ),
    "TAMILNADU_TRICHY": LWFConfig(
        employee_amount=20, employer_amount=40, frequency="Dec only"
    ),
    "TAMILNADU_VELLORE": LWFConfig(
        employee_amount=20, employer_amount=40, frequency="Dec only"
    ),
    "TELANGANA": LWFConfig(
        employee_amount=2, employer_amount=5, frequency="Dec only"
    ),
    "UTTAR PRADESH": LWFConfig(
        employee_amount=0, employer_amount=0, frequency="N/A"
    ),
    "UTTARAKHAND": LWFConfig(
        employee_amount=0, employer_amount=0, frequency="N/A"
    ),
    "WEST BENGAL": LWFConfig(
        employee_amount=3, employer_amount=30, frequency="Jun & Dec"
    ),
}


STATE_CODE_MAP = {
    "AP": "ANDHRA PRADESH", "AS": "ASSAM", "BR": "BIHAR",
    "CG": "CHATTISGARH", "DL": "DELHI", "GA": "GOA",
    "GJ": "GUJARAT", "HR": "HARYANA", "JH": "JHARKHAND",
    "KA": "KARNATAKA", "KL": "KERALA", "MH": "MAHARASHTRA",
    "MP": "MADHYA PRADESH", "OR": "ORISSA", "PB": "PUNJAB",
    "PY": "PONDICHERRY", "RJ": "RAJASTHAN", "TG": "TELANGANA",
    "TN": "TAMILNADU_CHENNAI", "UP": "UTTAR PRADESH",
    "UK": "UTTARAKHAND", "UT": "UTTARAKHAND", "WB": "WEST BENGAL",
    "HY": "HARYANA",
}

def get_ptax_slabs(state: str) -> list[PTaxSlab]:
    """Get Professional Tax slabs for a state (accepts code or full name)."""
    state_upper = state.upper()
    # Try direct match first
    if state_upper in PTAX_SLABS:
        return PTAX_SLABS[state_upper]
    # Try state code mapping
    full_name = STATE_CODE_MAP.get(state_upper, "")
    if full_name and full_name in PTAX_SLABS:
        return PTAX_SLABS[full_name]
    return []


def get_lwf_config(state: str) -> LWFConfig:
    """Get LWF configuration for a state (accepts code or full name)."""
    state_upper = state.upper()
    if state_upper in LWF_RATES:
        return LWF_RATES[state_upper]
    full_name = STATE_CODE_MAP.get(state_upper, "")
    if full_name and full_name in LWF_RATES:
        return LWF_RATES[full_name]
    return LWFConfig()
