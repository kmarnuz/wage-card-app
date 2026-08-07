"""
Wage Card Calculation Engine
Computes all salary components, statutory deductions, and compliance checks.
"""

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StatutoryConfig:
    """Configurable statutory rates (can change via government notifications)."""
    pf_employee_pct: float = 0.12          # 12%
    pf_employer_pct: float = 0.13          # 13%
    pf_employee_cap: float = 1800.0        # Max employee PF per month
    pf_employer_cap: float = 1950.0        # Max employer PF per month
    esic_employee_pct: float = 0.0075      # 0.75%
    esic_employer_pct: float = 0.0325      # 3.25%
    esic_wage_ceiling: float = 21000.0     # ESIC applicability threshold
    basic_cap: float = 15000.0             # Max Basic salary
    flexi_cap_pct: float = 0.50            # Max Flexi as % of Basic
    hra_cap: float = 7500.0                # Max HRA
    nsa_per_night: float = 115.0           # Night Shift Allowance per night


@dataclass
class PTaxSlab:
    """Professional Tax slab entry."""
    threshold: float       # Gross earnings upper limit
    amount: float          # PT amount for this slab
    special_month: Optional[str] = None   # e.g., "February", "March"
    special_amount: Optional[float] = None  # Amount in special month


@dataclass
class LWFConfig:
    """Labour Welfare Fund configuration for a state."""
    employee_amount: float = 0.0
    employer_amount: float = 0.0
    frequency: str = "N/A"            # "Monthly", "Jun & Dec", "Dec only", "N/A"
    is_percentage: bool = False        # True for states like Haryana
    employee_cap: Optional[float] = None
    employer_cap: Optional[float] = None


@dataclass
class WageInput:
    """Input parameters for wage calculation."""
    # Location & Role
    state: str
    city: str
    site_code: str
    entity: str = "AMZL"
    mw_zone: str = "A"
    region: str = "NA"
    mw_category: str = "Semi Skilled"   # Semi Skilled / Skilled
    business_title: str = "Associate"
    short_bt: str = "UTR LM AA"

    # Working hours
    weekly_hours: float = 45.0
    daily_hours: float = 9.0
    monthly_ot_limit: Optional[float] = None

    # Minimum wage
    minimum_wage: float = 0.0
    mw_effective_date: str = ""

    # Salary components (inputs)
    basic: float = 0.0
    flexi: float = 0.0
    lta: float = 0.0
    hra: float = 0.0
    conveyance: float = 0.0

    # Variable pay (defaults)
    ot_hours: float = 0.0         # Default OT hours for calculation
    nsa_amount: float = 0.0       # NSA total
    attendance_incentive: float = 0.0

    # Tenure
    tenure_years: int = 0


@dataclass
class WageOutput:
    """Complete wage card output with all calculated fields."""
    # Earnings
    basic: float = 0.0
    flexi: float = 0.0
    lta: float = 0.0
    hra: float = 0.0
    conveyance: float = 0.0
    gross: float = 0.0

    # OT
    per_hour_ot_total: float = 0.0
    per_hour_ot_included: float = 0.0
    per_hour_ot_balance: float = 0.0

    # Employee Deductions
    pf_employee: float = 0.0
    esic_employee: float = 0.0
    pt_employee: float = 0.0
    lwf_employee: float = 0.0
    gross_deductions: float = 0.0
    net_salary: float = 0.0

    # Employer Contributions
    pf_employer: float = 0.0
    esic_employer: float = 0.0
    lwf_employer: float = 0.0

    # CTC & Total Remuneration
    ctc: float = 0.0
    total_remuneration: float = 0.0

    # Variable components (for reference)
    ot_default: float = 0.0
    nsa: float = 0.0
    attendance_incentive: float = 0.0

    # Compliance
    included_wages: float = 0.0
    excluded_wages: float = 0.0
    included_pct: float = 0.0
    cap_50_amount: float = 0.0
    cap_50_met: bool = True

    # Validation
    mw_compliant: bool = True
    mw_gap: float = 0.0


class WageCalculationEngine:
    """Core calculation engine for wage card computations."""

    def __init__(self, statutory_config: StatutoryConfig = None):
        self.config = statutory_config or StatutoryConfig()

    def calculate(
        self,
        wage_input: WageInput,
        ptax_slabs: list[PTaxSlab] = None,
        lwf_config: LWFConfig = None,
        include_pt_lwf_in_monthly: bool = False
    ) -> WageOutput:
        """
        Calculate complete wage card from inputs.

        Args:
            include_pt_lwf_in_monthly: If False (default), PT and LWF are shown
                as "As applicable" and NOT included in Gross Deductions/Net/CTC.
                The wage card shows the fixed monthly structure; PT/LWF are
                deducted separately based on their frequency (monthly, Jun/Dec, etc.)
        """
        output = WageOutput()
        cfg = self.config

        # --- Earnings ---
        output.basic = wage_input.basic
        output.flexi = wage_input.flexi
        output.lta = wage_input.lta
        output.hra = wage_input.hra
        output.conveyance = wage_input.conveyance
        output.gross = (
            output.basic + output.flexi + output.lta +
            output.hra + output.conveyance
        )

        # --- Included Wages (statutory base) ---
        output.included_wages = output.basic + output.flexi + output.lta

        # --- OT Calculation ---
        weekly_hrs = wage_input.weekly_hours
        if weekly_hrs > 0:
            # OT rate based on Included Wages (Basic + Flexi + LTA)
            # Per Hour OT = ROUND((Included_Wages * 12 / (52 * Weekly_Hrs)) * 2)
            output.per_hour_ot_total = round(
                (output.included_wages * 12 / (52 * weekly_hrs)) * 2
            )

            # Included OT rate (same as total now since both use included wages)
            output.per_hour_ot_included = output.per_hour_ot_total

            # Balance (no longer applicable)
            output.per_hour_ot_balance = 0

        # --- Employee Deductions ---
        # PF Employee: MIN(12% * Basic, ₹1800)
        output.pf_employee = min(
            cfg.pf_employee_pct * output.basic,
            cfg.pf_employee_cap
        )

        # ESIC Employee: IF(Included_Wages > 21000, 0, ROUNDUP(Included_Wages * 0.75%))
        if output.included_wages > cfg.esic_wage_ceiling:
            output.esic_employee = 0.0
        else:
            output.esic_employee = math.ceil(
                output.included_wages * cfg.esic_employee_pct
            )

        # Professional Tax (slab lookup) — computed but may not be in monthly deduction
        output.pt_employee = self._calculate_ptax(output.gross, ptax_slabs)

        # LWF Employee — computed but may not be in monthly deduction
        if lwf_config:
            output.lwf_employee = self._calculate_lwf_employee(
                output.gross, lwf_config
            )

        # Gross Deductions (includes PT, not LWF)
        if include_pt_lwf_in_monthly:
            output.gross_deductions = (
                output.pf_employee + output.esic_employee +
                output.pt_employee + output.lwf_employee
            )
        else:
            output.gross_deductions = output.pf_employee + output.esic_employee

        # Net Salary
        output.net_salary = output.gross - output.gross_deductions

        # --- Employer Contributions ---
        # PF Employer: MIN(13% * Basic, ₹1950)
        output.pf_employer = min(
            cfg.pf_employer_pct * output.basic,
            cfg.pf_employer_cap
        )

        # ESIC Employer: IF(Included_Wages > 21000, 0, ROUNDUP(Included_Wages * 3.25%))
        if output.included_wages > cfg.esic_wage_ceiling:
            output.esic_employer = 0.0
        else:
            output.esic_employer = math.ceil(
                output.included_wages * cfg.esic_employer_pct
            )

        # LWF Employer — computed but not in monthly CTC
        if lwf_config:
            output.lwf_employer = self._calculate_lwf_employer(
                output.gross, lwf_config
            )

        # --- CTC (monthly view: Gross + PF_ER + ESIC_ER, no LWF) ---
        if include_pt_lwf_in_monthly:
            output.ctc = (
                output.gross + output.pf_employer +
                output.esic_employer + output.lwf_employer
            )
        else:
            output.ctc = (
                output.gross + output.pf_employer + output.esic_employer
            )

        # --- Variable Components (for total remuneration) ---
        # OT Default: If weekly hours = 40, then Per Hour OT * 22
        if wage_input.weekly_hours == 40:
            output.ot_default = output.per_hour_ot_total * 22
        else:
            output.ot_default = wage_input.ot_hours
        output.nsa = wage_input.nsa_amount
        output.attendance_incentive = wage_input.attendance_incentive

        # --- Total Remuneration ---
        # Total Remuneration = CTC + Default OT + NSA + Attendance Incentive
        output.total_remuneration = (
            output.ctc + output.ot_default +
            output.nsa + output.attendance_incentive
        )

        # --- 50% Cap Compliance ---
        # Excluded = OT + NSA + Incentive + HRA + Conveyance
        output.excluded_wages = (
            output.ot_default + output.nsa +
            output.attendance_incentive +
            output.hra + output.conveyance
        )

        output.cap_50_amount = 0.50 * output.total_remuneration
        output.cap_50_met = output.excluded_wages <= output.cap_50_amount

        # Included percentage
        if output.total_remuneration > 0:
            output.included_pct = output.included_wages / output.total_remuneration

        # --- MW Compliance ---
        output.mw_compliant = output.included_wages >= wage_input.minimum_wage
        output.mw_gap = max(0, wage_input.minimum_wage - output.included_wages)

        return output

    def auto_split_for_mw(
        self,
        target_gross: float,
        minimum_wage: float,
        state: str,
        hra_applicable: bool = False
    ) -> dict:
        """
        Auto-allocate salary components from Gross.

        Split order:
        1. Basic = MIN(Gross, ₹15,000)
        2. Flexi = MIN(remaining, ₹7,500)
        3. HRA = MIN(remaining, ₹7,500) — MH/WB: minimum 5% of MW mandatory
        4. Conveyance = residual
        5. LTA = ONLY used if MW > 22,500. LTA = MW - 22,500 (to ensure MW compliance)

        Included Wages (for MW compliance) = Basic + Flexi + LTA
        MW Compliance: Included Wages >= Minimum Wage
        """
        cfg = self.config

        # Check if state requires mandatory HRA (MH and WB)
        is_mh_wb = state.upper() in ('MH', 'WB', 'MAHARASHTRA', 'WEST BENGAL')
        mandatory_hra = 0.0
        if is_mh_wb:
            mandatory_hra = round(0.05 * minimum_wage)  # 5% of MW

        # Step 1: Basic (capped at ₹15,000)
        basic = min(target_gross, cfg.basic_cap)
        remaining = max(0, target_gross - basic)

        # For MH/WB: allocate mandatory HRA first, then Flexi from remaining
        if is_mh_wb:
            # Step 2 (MH/WB): HRA = 5% of MW (mandatory), capped at ₹7,500
            hra = min(mandatory_hra, cfg.hra_cap)
            remaining = max(0, remaining - hra)

            # Step 3 (MH/WB): Flexi from remaining (capped at ₹7,500)
            flexi = min(remaining, 7500.0)
            remaining = max(0, remaining - flexi)

            # Step 4: LTA — ONLY if MW > 22,500
            lta = 0.0
            if minimum_wage > 22500:
                lta = minimum_wage - 22500
                remaining = max(0, remaining - lta)

            # Step 5: If remaining and HRA < 7500, top up HRA
            if remaining > 0 and hra < cfg.hra_cap:
                extra_hra = min(remaining, cfg.hra_cap - hra)
                hra += extra_hra
                remaining = max(0, remaining - extra_hra)

            # Step 6: Conveyance = whatever is left
            conveyance = remaining
        else:
            # Non MH/WB states: Basic → Flexi → LTA → HRA → Conveyance
            # Step 2: Flexi (capped at ₹7,500)
            flexi = min(remaining, 7500.0)
            remaining = max(0, remaining - flexi)

            # Step 3: LTA — ONLY if MW > 22,500
            lta = 0.0
            if minimum_wage > 22500:
                lta = minimum_wage - 22500
                remaining = max(0, remaining - lta)

            # Step 4: HRA (capped at ₹7,500)
            hra = min(remaining, cfg.hra_cap)
            remaining = max(0, remaining - hra)

            # Step 5: Conveyance = whatever is left
            conveyance = remaining

        # Included Wages = Basic + Flexi + LTA
        included_wages = basic + flexi + lta

        return {
            "basic": basic,
            "flexi": flexi,
            "lta": lta,
            "hra": hra,
            "conveyance": conveyance,
            "gross": basic + flexi + lta + hra + conveyance,
            "included_wages": included_wages,
            "mw_compliant": included_wages >= minimum_wage,
        }

    def _calculate_ptax(self, gross: float, slabs: list[PTaxSlab] = None) -> float:
        """Lookup Professional Tax from slab table."""
        if not slabs:
            return 0.0

        # Sort slabs by threshold ascending
        sorted_slabs = sorted(slabs, key=lambda s: s.threshold)

        # Find applicable slab: highest threshold where gross >= threshold
        ptax = 0.0
        for slab in sorted_slabs:
            if gross >= slab.threshold:
                ptax = slab.amount
            else:
                break

        return ptax

    def _calculate_lwf_employee(self, gross: float, lwf: LWFConfig) -> float:
        """Calculate LWF employee contribution."""
        if lwf.frequency == "N/A":
            return 0.0

        if lwf.is_percentage:
            amount = gross * (lwf.employee_amount / 100)
            if lwf.employee_cap:
                amount = min(amount, lwf.employee_cap)
            return amount

        return lwf.employee_amount

    def _calculate_lwf_employer(self, gross: float, lwf: LWFConfig) -> float:
        """Calculate LWF employer contribution."""
        if lwf.frequency == "N/A":
            return 0.0

        if lwf.is_percentage:
            amount = gross * (lwf.employer_amount / 100)
            if lwf.employer_cap:
                amount = min(amount, lwf.employer_cap)
            return amount

        return lwf.employer_amount
