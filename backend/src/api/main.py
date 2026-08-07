"""
Wage Card API — FastAPI application.
Provides REST endpoints for wage card management.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import io
from datetime import datetime

import sys
sys.path.insert(0, '/workspace/wage-card-app/backend/src')

from services.calculation_engine import (
    WageCalculationEngine, WageInput, StatutoryConfig, WageOutput
)
from services.database import db
from config.statutory_data import get_ptax_slabs, get_lwf_config, PTAX_SLABS, LWF_RATES

app = FastAPI(
    title="Wage Card Management System",
    description="Manage wage cards, salary structures, and statutory compliance for AMZL India",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize calculation engine
engine = WageCalculationEngine()


# =============================================================================
# REQUEST / RESPONSE MODELS
# =============================================================================

class WageCardRequest(BaseModel):
    """Request to create/update a wage card entry."""
    entity: str = "AMZL"
    state: str
    state_code: str
    city: str
    mw_zone: str = "A"
    region: str = "NA"
    mw_category: str              # Semi Skilled / Skilled
    business_title: str           # Associate, Supervisor, PA, ADE
    short_bt: str
    site_codes: str               # Comma-separated
    tenure_years: int = 0

    weekly_hours: float = 45.0
    daily_hours: float = 9.0
    monthly_ot_limit: Optional[float] = None

    minimum_wage: float
    mw_effective_date: str

    # Salary inputs
    basic: float
    flexi: float = 0.0
    lta: float = 0.0
    hra: float = 0.0
    conveyance: float = 0.0

    # Variable pay defaults
    attendance_incentive: float = 0.0
    nsa_amount: float = 0.0
    ot_hours: float = 0.0


class WageCardResponse(BaseModel):
    """Full wage card with all calculated fields."""
    id: str
    # Inputs
    entity: str
    state: str
    state_code: str
    city: str
    mw_zone: str
    region: str
    mw_category: str
    business_title: str
    short_bt: str
    site_codes: str
    tenure_years: int
    weekly_hours: float
    daily_hours: float
    monthly_ot_limit: Optional[float]
    minimum_wage: float
    mw_effective_date: str

    # Salary components
    basic: float
    flexi: float
    lta: float
    hra: float
    conveyance: float
    gross: float

    # OT
    per_hour_ot_total: float
    per_hour_ot_included: float
    per_hour_ot_balance: float

    # Deductions
    pf_employee: float
    esic_employee: float
    pt_employee: str
    lwf_employee: str
    gross_deductions: float
    net_salary: float

    # Employer
    pf_employer: float
    esic_employer: float
    lwf_employer: str
    ctc: float

    # Variable
    ot_default: float
    nsa: float
    attendance_incentive: float

    # Compliance
    total_remuneration: float
    included_wages: float
    included_pct: float
    excluded_wages: float
    cap_50_amount: float
    cap_50_met: bool
    mw_compliant: bool

    # Audit
    created_at: str
    updated_at: str


class MWUpdateRequest(BaseModel):
    """Request to update minimum wage for a state/city/zone/skill."""
    state: str
    city: str
    mw_zone: str = "A"
    skill_category: str
    new_mw_amount: float
    effective_date: str
    notification_ref: str = ""


class AutoSplitRequest(BaseModel):
    """Request to auto-split salary when MW changes."""
    target_gross: float
    minimum_wage: float
    state: str
    hra_applicable: bool = False


class AutoSplitResponse(BaseModel):
    """Auto-split result."""
    basic: float
    flexi: float
    lta: float
    hra: float
    conveyance: float
    gross: float
    included_wages: float
    mw_compliant: bool


class CalculateRequest(BaseModel):
    """Quick calculation without saving."""
    state: str
    weekly_hours: float = 45.0
    minimum_wage: float = 0.0
    basic: float
    flexi: float = 0.0
    lta: float = 0.0
    hra: float = 0.0
    conveyance: float = 0.0
    attendance_incentive: float = 0.0
    nsa_amount: float = 0.0
    ot_hours: float = 0.0


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
def root():
    return {"service": "Wage Card Management System", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# --- Wage Card CRUD ---

@app.post("/api/wage-cards", response_model=WageCardResponse)
def create_wage_card(request: WageCardRequest):
    """Create a new wage card entry with auto-calculated fields."""
    card_id = str(uuid.uuid4())

    # Run calculations
    wage_input = WageInput(
        state=request.state,
        city=request.city,
        site_code=request.site_codes,
        entity=request.entity,
        mw_zone=request.mw_zone,
        region=request.region,
        mw_category=request.mw_category,
        business_title=request.business_title,
        short_bt=request.short_bt,
        weekly_hours=request.weekly_hours,
        daily_hours=request.daily_hours,
        monthly_ot_limit=request.monthly_ot_limit,
        minimum_wage=request.minimum_wage,
        mw_effective_date=request.mw_effective_date,
        basic=request.basic,
        flexi=request.flexi,
        lta=request.lta,
        hra=request.hra,
        conveyance=request.conveyance,
        attendance_incentive=request.attendance_incentive,
        nsa_amount=request.nsa_amount,
        ot_hours=request.ot_hours,
        tenure_years=request.tenure_years,
    )

    ptax = get_ptax_slabs(request.state)
    lwf = get_lwf_config(request.state)
    result = engine.calculate(wage_input, ptax, lwf)

    now = datetime.utcnow().isoformat()

    card = {
        "id": card_id,
        "entity": request.entity,
        "state": request.state,
        "state_code": request.state_code,
        "city": request.city,
        "mw_zone": request.mw_zone,
        "region": request.region,
        "mw_category": request.mw_category,
        "business_title": request.business_title,
        "short_bt": request.short_bt,
        "site_codes": request.site_codes,
        "tenure_years": request.tenure_years,
        "weekly_hours": request.weekly_hours,
        "daily_hours": request.daily_hours,
        "monthly_ot_limit": request.monthly_ot_limit,
        "minimum_wage": request.minimum_wage,
        "mw_effective_date": request.mw_effective_date,
        # Salary
        "basic": result.basic,
        "flexi": result.flexi,
        "lta": result.lta,
        "hra": result.hra,
        "conveyance": result.conveyance,
        "gross": result.gross,
        # OT
        "per_hour_ot_total": result.per_hour_ot_total,
        "per_hour_ot_included": result.per_hour_ot_included,
        "per_hour_ot_balance": result.per_hour_ot_balance,
        # Deductions
        "pf_employee": result.pf_employee,
        "esic_employee": result.esic_employee,
        "pt_employee": "As applicable",
        "lwf_employee": "As applicable",
        "gross_deductions": result.gross_deductions,
        "net_salary": result.net_salary,
        # Employer
        "pf_employer": result.pf_employer,
        "esic_employer": result.esic_employer,
        "lwf_employer": "As applicable",
        "ctc": result.ctc,
        # Variable
        "ot_default": result.ot_default,
        "nsa": result.nsa,
        "attendance_incentive": result.attendance_incentive,
        # Compliance
        "total_remuneration": result.total_remuneration,
        "included_wages": result.included_wages,
        "included_pct": round(result.included_pct, 4),
        "excluded_wages": result.excluded_wages,
        "cap_50_amount": result.cap_50_amount,
        "cap_50_met": result.cap_50_met,
        "mw_compliant": result.mw_compliant,
        # Audit
        "created_at": now,
        "updated_at": now,
    }

    db.put_wage_card(card)

    # Audit log
    db.put_audit_entry({
        "entity_type": "wage_card",
        "entity_id": card_id,
        "action": "create",
        "timestamp": now,
    })

    return card


@app.get("/api/wage-cards")
def list_wage_cards(
    state: Optional[str] = None,
    city: Optional[str] = None,
    business_title: Optional[str] = None,
    tenure_years: Optional[int] = None,
):
    """List wage cards with optional filters."""
    filters = {}
    if state:
        filters["state"] = state
    if city:
        filters["city"] = city
    if business_title:
        filters["business_title"] = business_title
    if tenure_years is not None:
        filters["tenure_years"] = tenure_years

    cards = db.list_wage_cards(filters)
    return {"count": len(cards), "items": cards}


@app.get("/api/wage-cards/{card_id}", response_model=WageCardResponse)
def get_wage_card(card_id: str):
    """Get a single wage card by ID."""
    card = db.get_wage_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Wage card not found")
    return card


@app.put("/api/wage-cards/{card_id}", response_model=WageCardResponse)
def update_wage_card(card_id: str, request: WageCardRequest):
    """Update an existing wage card (recalculates all fields)."""
    old_card = db.get_wage_card(card_id)
    if not old_card:
        raise HTTPException(status_code=404, detail="Wage card not found")

    # Recalculate
    wage_input = WageInput(
        state=request.state,
        city=request.city,
        site_code=request.site_codes,
        entity=request.entity,
        mw_zone=request.mw_zone,
        region=request.region,
        mw_category=request.mw_category,
        business_title=request.business_title,
        short_bt=request.short_bt,
        weekly_hours=request.weekly_hours,
        daily_hours=request.daily_hours,
        minimum_wage=request.minimum_wage,
        mw_effective_date=request.mw_effective_date,
        basic=request.basic,
        flexi=request.flexi,
        lta=request.lta,
        hra=request.hra,
        conveyance=request.conveyance,
        attendance_incentive=request.attendance_incentive,
        nsa_amount=request.nsa_amount,
        ot_hours=request.ot_hours,
        tenure_years=request.tenure_years,
    )

    ptax = get_ptax_slabs(request.state)
    lwf = get_lwf_config(request.state)
    result = engine.calculate(wage_input, ptax, lwf)

    now = datetime.utcnow().isoformat()

    card = {
        **old_card,
        "entity": request.entity,
        "state": request.state,
        "state_code": request.state_code,
        "city": request.city,
        "mw_zone": request.mw_zone,
        "region": request.region,
        "mw_category": request.mw_category,
        "business_title": request.business_title,
        "short_bt": request.short_bt,
        "site_codes": request.site_codes,
        "tenure_years": request.tenure_years,
        "weekly_hours": request.weekly_hours,
        "daily_hours": request.daily_hours,
        "monthly_ot_limit": request.monthly_ot_limit,
        "minimum_wage": request.minimum_wage,
        "mw_effective_date": request.mw_effective_date,
        "basic": result.basic,
        "flexi": result.flexi,
        "lta": result.lta,
        "hra": result.hra,
        "conveyance": result.conveyance,
        "gross": result.gross,
        "per_hour_ot_total": result.per_hour_ot_total,
        "per_hour_ot_included": result.per_hour_ot_included,
        "per_hour_ot_balance": result.per_hour_ot_balance,
        "pf_employee": result.pf_employee,
        "esic_employee": result.esic_employee,
        "gross_deductions": result.gross_deductions,
        "net_salary": result.net_salary,
        "pf_employer": result.pf_employer,
        "esic_employer": result.esic_employer,
        "ctc": result.ctc,
        "ot_default": result.ot_default,
        "nsa": result.nsa,
        "attendance_incentive": result.attendance_incentive,
        "total_remuneration": result.total_remuneration,
        "included_wages": result.included_wages,
        "included_pct": round(result.included_pct, 4),
        "excluded_wages": result.excluded_wages,
        "cap_50_amount": result.cap_50_amount,
        "cap_50_met": result.cap_50_met,
        "mw_compliant": result.mw_compliant,
        "updated_at": now,
    }

    db.put_wage_card(card)

    # Audit log
    db.put_audit_entry({
        "entity_type": "wage_card",
        "entity_id": card_id,
        "action": "update",
        "timestamp": now,
    })

    return card


@app.delete("/api/wage-cards/{card_id}")
def delete_wage_card(card_id: str):
    """Delete a wage card."""
    if not db.delete_wage_card(card_id):
        raise HTTPException(status_code=404, detail="Wage card not found")

    db.put_audit_entry({
        "entity_type": "wage_card",
        "entity_id": card_id,
        "action": "delete",
        "timestamp": datetime.utcnow().isoformat(),
    })

    return {"status": "deleted", "id": card_id}


# --- Calculation Endpoints ---

@app.post("/api/calculate")
def calculate_wage(request: CalculateRequest):
    """Quick calculation without saving — for preview/simulation."""
    wage_input = WageInput(
        state=request.state,
        city="",
        site_code="",
        weekly_hours=request.weekly_hours,
        minimum_wage=request.minimum_wage,
        basic=request.basic,
        flexi=request.flexi,
        lta=request.lta,
        hra=request.hra,
        conveyance=request.conveyance,
        attendance_incentive=request.attendance_incentive,
        nsa_amount=request.nsa_amount,
        ot_hours=request.ot_hours,
    )

    ptax = get_ptax_slabs(request.state)
    lwf = get_lwf_config(request.state)
    result = engine.calculate(wage_input, ptax, lwf)

    return {
        "gross": result.gross,
        "per_hour_ot_total": result.per_hour_ot_total,
        "per_hour_ot_included": result.per_hour_ot_included,
        "per_hour_ot_balance": result.per_hour_ot_balance,
        "pf_employee": result.pf_employee,
        "esic_employee": result.esic_employee,
        "gross_deductions": result.gross_deductions,
        "net_salary": result.net_salary,
        "pf_employer": result.pf_employer,
        "esic_employer": result.esic_employer,
        "ctc": result.ctc,
        "included_wages": result.included_wages,
        "mw_compliant": result.mw_compliant,
        "cap_50_met": result.cap_50_met,
        "total_remuneration": result.total_remuneration,
    }


@app.post("/api/auto-split", response_model=AutoSplitResponse)
def auto_split(request: AutoSplitRequest):
    """Auto-split salary components to meet MW compliance."""
    result = engine.auto_split_for_mw(
        target_gross=request.target_gross,
        minimum_wage=request.minimum_wage,
        state=request.state,
        hra_applicable=request.hra_applicable,
    )
    return result


# --- MW Management ---

@app.post("/api/minimum-wages/simulate-impact")
def simulate_mw_impact(request: MWUpdateRequest):
    """
    Simulate the impact of a MW change on existing wage cards.
    Shows which cards will be affected and suggests new splits.
    """
    all_cards = db.list_wage_cards()
    affected_cards = []
    for card in all_cards:
        if (card["state"].upper() == request.state.upper() and
            card["city"].upper() == request.city.upper() and
            card["mw_category"].upper() == request.skill_category.upper()):

            current_included = card["included_wages"]
            if current_included < request.new_mw_amount:
                # This card needs updating
                suggested_split = engine.auto_split_for_mw(
                    target_gross=card["gross"],
                    minimum_wage=request.new_mw_amount,
                    state=request.state,
                    hra_applicable=card["hra"] > 0,
                )
                affected_cards.append({
                    "card_id": card["id"],
                    "short_bt": card["short_bt"],
                    "tenure_years": card["tenure_years"],
                    "current_included": current_included,
                    "new_mw": request.new_mw_amount,
                    "gap": request.new_mw_amount - current_included,
                    "suggested_split": suggested_split,
                    "needs_gross_increase": suggested_split["gross"] > card["gross"],
                })

    return {
        "new_mw": request.new_mw_amount,
        "effective_date": request.effective_date,
        "state": request.state,
        "city": request.city,
        "skill_category": request.skill_category,
        "total_affected": len(affected_cards),
        "affected_cards": affected_cards,
    }


# --- Export ---

@app.get("/api/wage-cards/export/excel")
def export_wage_cards_excel(
    state: Optional[str] = None,
    city: Optional[str] = None,
    business_title: Optional[str] = None,
):
    """Export wage cards as Excel file."""
    from services.excel_export import export_wage_cards_to_excel

    filters = {}
    if state:
        filters["state"] = state
    if city:
        filters["city"] = city
    if business_title:
        filters["business_title"] = business_title

    cards = db.list_wage_cards(filters)

    if not cards:
        raise HTTPException(status_code=404, detail="No wage cards found for export")

    excel_bytes = export_wage_cards_to_excel(cards)

    filename = f"WageCards_{state or 'All'}_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# --- Bulk MW Update ---

class BulkMWUpdateRequest(BaseModel):
    """Apply a MW change to all affected wage cards."""
    state: str
    city: str
    mw_zone: str = "A"
    skill_category: str
    new_mw_amount: float
    effective_date: str
    notification_ref: str = ""
    auto_increase_gross: bool = False  # If True, increase gross to meet MW


@app.post("/api/minimum-wages/apply")
def apply_mw_update(request: BulkMWUpdateRequest):
    """
    Apply a MW change: update all affected wage cards with new splits.
    If auto_increase_gross=True, increases gross where needed.
    Otherwise, only restructures within existing gross.
    """
    all_cards = db.list_wage_cards()
    updated_cards = []
    failed_cards = []
    now = datetime.utcnow().isoformat()

    for card in all_cards:
        if (card["state"].upper() != request.state.upper() or
            card["city"].upper() != request.city.upper() or
            card["mw_category"].upper() != request.skill_category.upper()):
            continue

        current_included = card.get("included_wages", 0)
        if current_included >= request.new_mw_amount:
            continue  # Already compliant

        # Calculate new split
        target_gross = card["gross"]
        hra_applicable = card.get("hra", 0) > 0

        split = engine.auto_split_for_mw(
            target_gross=target_gross,
            minimum_wage=request.new_mw_amount,
            state=request.state,
            hra_applicable=hra_applicable,
        )

        # Check if we can meet MW within current gross
        if not split["mw_compliant"] and request.auto_increase_gross:
            # Need to increase gross — set it to MW + excluded components
            new_target = request.new_mw_amount + card.get("hra", 0) + card.get("conveyance", 0)
            split = engine.auto_split_for_mw(
                target_gross=new_target,
                minimum_wage=request.new_mw_amount,
                state=request.state,
                hra_applicable=hra_applicable,
            )

        if not split["mw_compliant"]:
            failed_cards.append({
                "card_id": card["id"],
                "short_bt": card["short_bt"],
                "tenure_years": card["tenure_years"],
                "reason": "Cannot meet MW within current gross without increase",
            })
            continue

        # Update the card
        card["basic"] = split["basic"]
        card["flexi"] = split["flexi"]
        card["lta"] = split["lta"]
        card["hra"] = split["hra"]
        card["conveyance"] = split["conveyance"]
        card["minimum_wage"] = request.new_mw_amount
        card["mw_effective_date"] = request.effective_date

        # Recalculate
        wage_input = WageInput(
            state=card["state"],
            city=card["city"],
            site_code=card.get("site_codes", ""),
            weekly_hours=card.get("weekly_hours", 45),
            minimum_wage=request.new_mw_amount,
            basic=split["basic"],
            flexi=split["flexi"],
            lta=split["lta"],
            hra=split["hra"],
            conveyance=split["conveyance"],
            attendance_incentive=card.get("attendance_incentive", 0),
            nsa_amount=card.get("nsa", 0),
            ot_hours=card.get("ot_default", 0),
        )

        ptax = get_ptax_slabs(card["state"])
        lwf = get_lwf_config(card["state"])
        result = engine.calculate(wage_input, ptax, lwf)

        # Update calculated fields
        card["gross"] = result.gross
        card["per_hour_ot_total"] = result.per_hour_ot_total
        card["per_hour_ot_included"] = result.per_hour_ot_included
        card["per_hour_ot_balance"] = result.per_hour_ot_balance
        card["pf_employee"] = result.pf_employee
        card["esic_employee"] = result.esic_employee
        card["gross_deductions"] = result.gross_deductions
        card["net_salary"] = result.net_salary
        card["pf_employer"] = result.pf_employer
        card["esic_employer"] = result.esic_employer
        card["ctc"] = result.ctc
        card["total_remuneration"] = result.total_remuneration
        card["included_wages"] = result.included_wages
        card["included_pct"] = round(result.included_pct, 4)
        card["excluded_wages"] = result.excluded_wages
        card["cap_50_amount"] = result.cap_50_amount
        card["cap_50_met"] = result.cap_50_met
        card["mw_compliant"] = result.mw_compliant
        card["updated_at"] = now

        db.put_wage_card(card)
        updated_cards.append(card["id"])

        # Audit
        db.put_audit_entry({
            "entity_type": "wage_card",
            "entity_id": card["id"],
            "action": "mw_bulk_update",
            "timestamp": now,
            "details": f"MW updated to {request.new_mw_amount} effective {request.effective_date}",
        })

    # Store the MW record
    db.put_minimum_wage({
        "state": request.state,
        "city": request.city,
        "mw_zone": request.mw_zone,
        "skill_category": request.skill_category,
        "amount": request.new_mw_amount,
        "effective_date": request.effective_date,
        "notification_ref": request.notification_ref,
    })

    return {
        "status": "completed",
        "new_mw": request.new_mw_amount,
        "effective_date": request.effective_date,
        "total_updated": len(updated_cards),
        "total_failed": len(failed_cards),
        "updated_card_ids": updated_cards,
        "failed_cards": failed_cards,
    }


# --- Config Endpoints ---

@app.get("/api/config/ptax/{state}")
def get_ptax_config(state: str):
    """Get Professional Tax slabs for a state."""
    slabs = get_ptax_slabs(state)
    if not slabs:
        raise HTTPException(status_code=404, detail=f"No PTAX config for state: {state}")
    return {
        "state": state,
        "slabs": [{"threshold": s.threshold, "amount": s.amount,
                   "special_month": s.special_month, "special_amount": s.special_amount}
                  for s in slabs]
    }


@app.get("/api/config/lwf/{state}")
def get_lwf_config_endpoint(state: str):
    """Get LWF configuration for a state."""
    lwf = get_lwf_config(state)
    return {
        "state": state,
        "employee_amount": lwf.employee_amount,
        "employer_amount": lwf.employer_amount,
        "frequency": lwf.frequency,
        "is_percentage": lwf.is_percentage,
        "employee_cap": lwf.employee_cap,
        "employer_cap": lwf.employer_cap,
    }


@app.get("/api/config/states")
def list_states():
    """List all configured states."""
    all_states = set(list(PTAX_SLABS.keys()) + list(LWF_RATES.keys()))
    return {"states": sorted(all_states)}


@app.get("/api/config/statutory")
def get_statutory_config():
    """Get current statutory configuration (PF, ESIC rates, caps)."""
    cfg = engine.config
    return {
        "pf_employee_pct": cfg.pf_employee_pct,
        "pf_employer_pct": cfg.pf_employer_pct,
        "pf_employee_cap": cfg.pf_employee_cap,
        "pf_employer_cap": cfg.pf_employer_cap,
        "esic_employee_pct": cfg.esic_employee_pct,
        "esic_employer_pct": cfg.esic_employer_pct,
        "esic_wage_ceiling": cfg.esic_wage_ceiling,
        "basic_cap": cfg.basic_cap,
        "flexi_cap_pct": cfg.flexi_cap_pct,
        "hra_cap": cfg.hra_cap,
        "nsa_per_night": cfg.nsa_per_night,
    }


# --- Audit ---

@app.get("/api/audit-log")
def get_audit_log(limit: int = Query(default=50, le=200)):
    """Get recent audit log entries."""
    entries = db.list_audit_entries(limit=limit)
    return {"entries": entries}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
