"""
Data models for the Wage Card application.
These represent the database schema for DynamoDB or any persistence layer.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class MinimumWage:
    """Minimum wage entry for a state/city/zone/skill combination."""
    state: str
    city: str
    mw_zone: str          # A, B, C etc.
    skill_category: str    # Semi Skilled, Skilled, Unskilled
    amount: float
    effective_date: str    # ISO date
    notification_ref: str = ""   # Government notification reference
    created_at: str = ""
    created_by: str = ""


@dataclass
class SiteConfig:
    """Site master data."""
    site_code: str
    entity: str            # AMZL, AMZN, etc.
    state: str
    state_code: str
    city: str
    mw_zone: str
    region: str
    weekly_hours: float = 45.0
    daily_hours: float = 9.0
    monthly_ot_limit: Optional[float] = None


@dataclass
class RoleConfig:
    """Role/Business Title configuration."""
    business_title: str         # Associate, Supervisor, PA, ADE
    short_bt: str               # UTR LM AA, Supervisor, LM PA, ADE
    skill_category: str         # Semi Skilled, Skilled
    attendance_incentive: float = 0.0
    nsa_per_night: float = 115.0


@dataclass
class WageCardEntry:
    """
    A single wage card row — represents one unique combination
    of site + role + tenure with its salary structure.
    """
    # Primary key
    id: str = ""                    # Auto-generated UUID

    # Dimensions
    entity: str = ""
    state: str = ""
    state_code: str = ""
    city: str = ""
    mw_zone: str = ""
    region: str = ""
    mw_category: str = ""           # Semi Skilled / Skilled
    business_title: str = ""
    short_bt: str = ""
    site_codes: str = ""            # Comma-separated
    tenure_years: int = 0

    # Working hours
    weekly_hours: float = 45.0
    daily_hours: float = 9.0
    monthly_ot_limit: Optional[float] = None

    # Minimum wage reference
    minimum_wage: float = 0.0
    mw_effective_date: str = ""

    # Salary inputs (editable)
    basic: float = 0.0
    flexi: float = 0.0
    lta: float = 0.0
    hra: float = 0.0
    conveyance: float = 0.0

    # Calculated fields (auto-computed)
    gross: float = 0.0
    per_hour_ot_total: float = 0.0
    per_hour_ot_included: float = 0.0
    per_hour_ot_balance: float = 0.0
    pf_employee: float = 0.0
    esic_employee: float = 0.0
    pt_employee: str = "As applicable"
    lwf_employee: str = "As applicable"
    gross_deductions: float = 0.0
    net_salary: float = 0.0
    pf_employer: float = 0.0
    esic_employer: float = 0.0
    lwf_employer: str = "As applicable"
    ctc: float = 0.0

    # Variable components (defaults for reference)
    ot_default: float = 0.0
    nsa: float = 0.0
    attendance_incentive: float = 0.0

    # Compliance
    total_remuneration: float = 0.0
    included_wages: float = 0.0
    included_pct: float = 0.0
    excluded_wages: float = 0.0
    cap_50_amount: float = 0.0
    cap_50_met: bool = True
    mw_compliant: bool = True

    # Audit
    created_at: str = ""
    updated_at: str = ""
    created_by: str = ""
    updated_by: str = ""
    version: int = 1


@dataclass
class AuditLog:
    """Change audit trail."""
    id: str = ""
    entity_type: str = ""        # wage_card, minimum_wage, config
    entity_id: str = ""
    action: str = ""             # create, update, delete
    changes: dict = field(default_factory=dict)  # {field: {old: x, new: y}}
    user: str = ""
    timestamp: str = ""
    reason: str = ""             # e.g., "MW revision per state notification"
