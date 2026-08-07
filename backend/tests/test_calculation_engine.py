"""
Validation tests against the sample AMZL Wage Card spreadsheet.
Tests the calculation engine against known correct values from the Excel file.
"""

import sys
sys.path.insert(0, '/workspace/wage-card-app/backend/src')

from services.calculation_engine import (
    WageCalculationEngine, WageInput, StatutoryConfig, LWFConfig, PTaxSlab
)
from config.statutory_data import get_ptax_slabs, get_lwf_config


def test_row6_orissa_associate_0yr():
    """
    Row 6: AMZL, ORISSA, BHUBANESWAR, Semi Skilled, Associate, 0 Yr
    Basic=14312, Flexi=0, LTA=0, HRA=0, Conv=0
    Expected: Gross=14312, OT=164, PF_EE=1717.44, ESIC_EE=108,
              Net=12486.56, PF_ER=1860.56, ESIC_ER=466, CTC=16638.56
    """
    engine = WageCalculationEngine()
    lwf = get_lwf_config("ORISSA")
    ptax = get_ptax_slabs("ORISSA")

    wage_input = WageInput(
        state="ORISSA",
        city="BHUBANESWAR",
        site_code="BBIE,BBIF,ORBD",
        mw_category="Semi Skilled",
        business_title="Associate",
        short_bt="UTR LM AA",
        weekly_hours=45,
        daily_hours=9,
        minimum_wage=13572,
        mw_effective_date="2026-04-01",
        basic=14312,
        flexi=0,
        lta=0,
        hra=0,
        conveyance=0,
        attendance_incentive=3000,
        nsa_amount=0,
        ot_hours=0,
        tenure_years=0,
    )

    result = engine.calculate(wage_input, ptax, lwf)

    print("=== Row 6: ORISSA, Associate, 0 Yr ===")
    _assert_close("Gross", result.gross, 14312)
    _assert_close("OT Total", result.per_hour_ot_total, 164)
    _assert_close("OT Included", result.per_hour_ot_included, 147)
    _assert_close("OT Balance", result.per_hour_ot_balance, 17)
    _assert_close("PF Employee", result.pf_employee, 1717.44)
    _assert_close("ESIC Employee", result.esic_employee, 108)
    _assert_close("Net Salary", result.net_salary, 12486.56, tolerance=1)
    _assert_close("PF Employer", result.pf_employer, 1860.56)
    _assert_close("ESIC Employer", result.esic_employer, 466)
    _assert_close("CTC", result.ctc, 16638.56, tolerance=1)
    _assert_close("Included Wages", result.included_wages, 14312)
    assert result.mw_compliant, "MW should be compliant"
    assert result.cap_50_met, "50% cap should be met"
    print("  ✅ All checks passed!\n")


def test_row7_orissa_supervisor_0yr():
    """
    Row 7: AMZL, ORISSA, BHUBANESWAR, Skilled, Supervisor, 0 Yr
    Basic=15000, Flexi=4358, LTA=0, HRA=0, Conv=0
    Expected: Gross=19358, OT=217, PF_EE=1800, ESIC_EE=146
    """
    engine = WageCalculationEngine()
    lwf = get_lwf_config("ORISSA")
    ptax = get_ptax_slabs("ORISSA")

    wage_input = WageInput(
        state="ORISSA",
        city="BHUBANESWAR",
        site_code="BBIE,BBIF,ORBD",
        mw_category="Skilled",
        business_title="Supervisor",
        short_bt="Supervisor",
        weekly_hours=45,
        daily_hours=9,
        minimum_wage=14872,
        mw_effective_date="2026-04-01",
        basic=15000,
        flexi=4358,
        lta=0,
        hra=0,
        conveyance=0,
        attendance_incentive=800,
        nsa_amount=0,
        ot_hours=0,
        tenure_years=0,
    )

    result = engine.calculate(wage_input, ptax, lwf)

    print("=== Row 7: ORISSA, Supervisor, 0 Yr ===")
    _assert_close("Gross", result.gross, 19358)
    _assert_close("OT Total", result.per_hour_ot_total, 217)
    _assert_close("OT Included", result.per_hour_ot_included, 199)
    _assert_close("OT Balance", result.per_hour_ot_balance, 18)
    _assert_close("PF Employee", result.pf_employee, 1800)
    _assert_close("ESIC Employee", result.esic_employee, 146)
    _assert_close("Net Salary", result.net_salary, 17412, tolerance=1)
    _assert_close("PF Employer", result.pf_employer, 1950)
    _assert_close("ESIC Employer", result.esic_employer, 630)
    _assert_close("CTC", result.ctc, 21938, tolerance=1)
    assert result.mw_compliant, "MW should be compliant"
    assert result.cap_50_met, "50% cap should be met"
    print("  ✅ All checks passed!\n")


def test_row10_punjab_associate_0yr():
    """
    Row 10: AMZL, PUNJAB, LUDHIANA, Semi Skilled, Associate, 0 Yr
    Basic=14440, Flexi=0, LTA=0, HRA=0, Conv=0
    Expected: Gross=14440, OT=166, PF_EE=1732.8, ESIC_EE=109
    """
    engine = WageCalculationEngine()
    lwf = get_lwf_config("PUNJAB")
    ptax = get_ptax_slabs("PUNJAB")

    wage_input = WageInput(
        state="PUNJAB",
        city="LUDHIANA",
        site_code="LUHD",
        mw_category="Semi Skilled",
        business_title="Associate",
        short_bt="UTR LM AA",
        weekly_hours=45,
        daily_hours=9,
        minimum_wage=14383,
        mw_effective_date="2026-05-01",
        basic=14440,
        flexi=0,
        lta=0,
        hra=0,
        conveyance=0,
        attendance_incentive=3400,
        nsa_amount=0,
        ot_hours=0,
        tenure_years=0,
    )

    result = engine.calculate(wage_input, ptax, lwf)

    print("=== Row 10: PUNJAB, Associate, 0 Yr ===")
    _assert_close("Gross", result.gross, 14440)
    _assert_close("OT Total", result.per_hour_ot_total, 166)
    _assert_close("OT Included", result.per_hour_ot_included, 148)
    _assert_close("OT Balance", result.per_hour_ot_balance, 18)
    _assert_close("PF Employee", result.pf_employee, 1732.8)
    _assert_close("ESIC Employee", result.esic_employee, 109)
    _assert_close("PF Employer", result.pf_employer, 1877.2)
    _assert_close("ESIC Employer", result.esic_employer, 470)
    _assert_close("CTC", result.ctc, 16787.2, tolerance=1)
    assert result.mw_compliant, "MW should be compliant"
    assert result.cap_50_met, "50% cap should be met"
    print("  ✅ All checks passed!\n")


def test_row11_punjab_supervisor_0yr():
    """
    Row 11: AMZL, PUNJAB, LUDHIANA, Skilled, Supervisor, 0 Yr
    Basic=15000, Flexi=7500, LTA=0, HRA=434, Conv=0
    Expected: Gross=22934, OT=254, PF_EE=1800, ESIC_EE=0 (>21000)
    """
    engine = WageCalculationEngine()
    lwf = get_lwf_config("PUNJAB")
    ptax = get_ptax_slabs("PUNJAB")

    wage_input = WageInput(
        state="PUNJAB",
        city="LUDHIANA",
        site_code="LUHD",
        mw_category="Skilled",
        business_title="Supervisor",
        short_bt="Supervisor",
        weekly_hours=45,
        daily_hours=9,
        minimum_wage=15414,
        mw_effective_date="2026-05-01",
        basic=15000,
        flexi=7500,
        lta=0,
        hra=434,
        conveyance=0,
        attendance_incentive=800,
        nsa_amount=0,
        ot_hours=0,
        tenure_years=0,
    )

    result = engine.calculate(wage_input, ptax, lwf)

    print("=== Row 11: PUNJAB, Supervisor, 0 Yr (HRA applicable) ===")
    _assert_close("Gross", result.gross, 22934)
    _assert_close("OT Total", result.per_hour_ot_total, 254)
    _assert_close("OT Included", result.per_hour_ot_included, 231)
    _assert_close("OT Balance", result.per_hour_ot_balance, 23)
    _assert_close("PF Employee", result.pf_employee, 1800)
    _assert_close("ESIC Employee", result.esic_employee, 0)  # >21000 threshold
    _assert_close("Net Salary", result.net_salary, 21134, tolerance=1)
    _assert_close("PF Employer", result.pf_employer, 1950)
    _assert_close("ESIC Employer", result.esic_employer, 0)  # >21000 threshold
    _assert_close("CTC", result.ctc, 24884, tolerance=1)
    _assert_close("Included Wages", result.included_wages, 22500)
    assert result.mw_compliant, "MW should be compliant (22500 >= 15414)"
    assert result.cap_50_met, "50% cap should be met"
    print("  ✅ All checks passed!\n")


def test_row8_mp_pa_0yr():
    """
    Row 8: AMZL, MADHYA PRADESH, BHOPAL, Skilled, PA, 0 Yr
    Basic=15000, Flexi=2879, LTA=0, HRA=0, Conv=0
    Expected: Gross=17879, PF_EE=1800, ESIC_EE=135
    """
    engine = WageCalculationEngine()
    lwf = get_lwf_config("MADHYA PRADESH")
    ptax = get_ptax_slabs("MADHYA PRADESH")

    wage_input = WageInput(
        state="MADHYA PRADESH",
        city="BHOPAL",
        site_code="BHOE,BHOG",
        mw_category="Skilled",
        business_title="PA",
        short_bt="LM PA",
        weekly_hours=45,
        daily_hours=9,
        minimum_wage=15144,
        mw_effective_date="2026-04-01",
        basic=15000,
        flexi=2879,
        lta=0,
        hra=0,
        conveyance=0,
        attendance_incentive=1100,
        nsa_amount=0,
        ot_hours=0,
        tenure_years=0,
    )

    result = engine.calculate(wage_input, ptax, lwf)

    print("=== Row 8: MADHYA PRADESH, PA, 0 Yr ===")
    _assert_close("Gross", result.gross, 17879)
    _assert_close("OT Total", result.per_hour_ot_total, 202)
    _assert_close("OT Included", result.per_hour_ot_included, 183)
    _assert_close("OT Balance", result.per_hour_ot_balance, 19)
    _assert_close("PF Employee", result.pf_employee, 1800)
    _assert_close("ESIC Employee", result.esic_employee, 135)
    _assert_close("Net Salary", result.net_salary, 15944, tolerance=1)
    _assert_close("PF Employer", result.pf_employer, 1950)
    _assert_close("ESIC Employer", result.esic_employer, 582)
    _assert_close("CTC", result.ctc, 20411, tolerance=1)
    assert result.mw_compliant, "MW should be compliant"
    assert result.cap_50_met, "50% cap should be met"
    print("  ✅ All checks passed!\n")


def test_auto_split_mw_change():
    """
    Test auto-split logic when MW changes.
    Scenario: Orissa MW increases from 13572 to 15000.
    With current Gross target of ~14312 (just Basic).
    """
    engine = WageCalculationEngine()

    # Current: Basic=14312, everything else 0, Gross=14312
    # New MW = 15000, need to restructure

    result = engine.auto_split_for_mw(
        target_gross=15500,  # Slightly above new MW to allow room
        minimum_wage=15000,
        state="ORISSA",
        hra_applicable=False
    )

    print("=== Auto-Split Test: MW increased to 15000 ===")
    print(f"  Basic: {result['basic']}")
    print(f"  Flexi: {result['flexi']}")
    print(f"  LTA: {result['lta']}")
    print(f"  HRA: {result['hra']}")
    print(f"  Conveyance: {result['conveyance']}")
    print(f"  Gross: {result['gross']}")
    print(f"  Included: {result['included_wages']}")
    print(f"  MW Compliant: {result['mw_compliant']}")

    assert result['mw_compliant'], "Should be MW compliant after split"
    assert result['included_wages'] >= 15000, "Included wages must meet MW"
    assert result['basic'] <= 15000, "Basic must not exceed cap"
    assert result['flexi'] <= result['basic'] * 0.5, "Flexi must not exceed 50% of Basic"
    assert result['gross'] == 15500, "Gross should match target"
    print("  ✅ Auto-split passed!\n")


def test_auto_split_with_hra():
    """Test auto-split for a state where HRA is applicable."""
    engine = WageCalculationEngine()

    result = engine.auto_split_for_mw(
        target_gross=25000,
        minimum_wage=15414,
        state="PUNJAB",
        hra_applicable=True
    )

    print("=== Auto-Split Test: With HRA ===")
    print(f"  Basic: {result['basic']}")
    print(f"  Flexi: {result['flexi']}")
    print(f"  LTA: {result['lta']}")
    print(f"  HRA: {result['hra']}")
    print(f"  Conveyance: {result['conveyance']}")
    print(f"  Gross: {result['gross']}")
    print(f"  Included: {result['included_wages']}")

    assert result['mw_compliant'], "Should be MW compliant"
    assert result['basic'] <= 15000, "Basic capped at 15000"
    assert result['flexi'] <= 7500, "Flexi capped at 50% of Basic"
    assert result['hra'] <= 7500, "HRA capped at 7500"
    assert result['gross'] == 25000, "Gross should match target"
    print("  ✅ Auto-split with HRA passed!\n")


def test_1yr_tenure_row6():
    """
    Row 6, 1 Yr tenure: Basic=14885, Flexi=0, LTA=0
    Expected: Gross=14885, OT=171, PF_EE=1786.2, ESIC_EE=112
    """
    engine = WageCalculationEngine()
    lwf = get_lwf_config("ORISSA")
    ptax = get_ptax_slabs("ORISSA")

    wage_input = WageInput(
        state="ORISSA",
        city="BHUBANESWAR",
        site_code="BBIE,BBIF,ORBD",
        mw_category="Semi Skilled",
        business_title="Associate",
        short_bt="UTR LM AA",
        weekly_hours=45,
        daily_hours=9,
        minimum_wage=13572,
        basic=14885,
        flexi=0,
        lta=0,
        hra=0,
        conveyance=0,
        attendance_incentive=3000,
        tenure_years=1,
    )

    result = engine.calculate(wage_input, ptax, lwf)

    print("=== Row 6: ORISSA, Associate, 1 Yr ===")
    _assert_close("Gross", result.gross, 14885)
    _assert_close("OT Total", result.per_hour_ot_total, 171)
    _assert_close("OT Included", result.per_hour_ot_included, 153)
    _assert_close("OT Balance", result.per_hour_ot_balance, 18)
    _assert_close("PF Employee", result.pf_employee, 1786.2)
    _assert_close("ESIC Employee", result.esic_employee, 112)
    _assert_close("PF Employer", result.pf_employer, 1935.05)
    _assert_close("ESIC Employer", result.esic_employer, 484)
    _assert_close("CTC", result.ctc, 17304.05, tolerance=1)
    print("  ✅ All checks passed!\n")


def _assert_close(name: str, actual: float, expected: float, tolerance: float = 0.5):
    """Assert two values are close within tolerance."""
    diff = abs(actual - expected)
    status = "✓" if diff <= tolerance else "✗"
    print(f"  {status} {name}: got {actual:.2f}, expected {expected:.2f} (diff={diff:.2f})")
    if diff > tolerance:
        raise AssertionError(
            f"{name}: {actual:.2f} != {expected:.2f} (diff={diff:.2f} > tolerance={tolerance})"
        )


if __name__ == "__main__":
    print("=" * 60)
    print("WAGE CARD CALCULATION ENGINE - VALIDATION TESTS")
    print("=" * 60)
    print()

    tests = [
        test_row6_orissa_associate_0yr,
        test_row7_orissa_supervisor_0yr,
        test_row8_mp_pa_0yr,
        test_row10_punjab_associate_0yr,
        test_row11_punjab_supervisor_0yr,
        test_1yr_tenure_row6,
        test_auto_split_mw_change,
        test_auto_split_with_hra,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"  ❌ ERROR: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)
