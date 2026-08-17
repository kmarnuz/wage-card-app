"""
POST-UPLOAD UPDATE — single command to run after every template upload / MW revision.

Run:
    python post_upload_update.py

What it does (in order):
  1. Sets Attendance Incentive + Region on all matching cards from the baked-in
     mapping, keyed by (Entity, Site Code, Short BT).
  2. Sets Region for same-site BTs that aren't in the AI list (region-only).
  3. Regenerates all Associate PT cards so PT Attendance Incentive = 50% of the
     matching Associate (same Entity / Site / Year Band). This also keeps PT
     Total Remuneration / Excluded Wages consistent (PT has no OT/NSA).
  4. Saves data.json.

After running, restart the app (or it will pick up data.json on next start) and
commit + push data.json so Render redeploys with the values.
"""
import os
import sys
import json

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "data.json")

# =============================================================================
# 1) ATTENDANCE INCENTIVE + REGION MAPPING  (Entity, Site Code, Short BT)
# =============================================================================
ai_region_data = {
    # INFC
    ("INFC","AMD2","Associate"): {"ai":2050,"region":"West"}, ("INFC","AMD2","PA"): {"ai":1900,"region":"West"}, ("INFC","AMD2","FC-Interpreter"): {"ai":0,"region":"West"},
    ("INFC","ATX1","Associate"): {"ai":1500,"region":"North"}, ("INFC","ATX1","PA"): {"ai":1400,"region":"North"}, ("INFC","ATX1","FC-Interpreter"): {"ai":0,"region":"North"},
    ("INFC","BLR4","Associate"): {"ai":3250,"region":"South"}, ("INFC","BLR4","PA"): {"ai":3250,"region":"South"}, ("INFC","BLR4","FC-Interpreter"): {"ai":0,"region":"South"},
    ("INFC","BLR5","Associate"): {"ai":3050,"region":"South"}, ("INFC","BLR5","PA"): {"ai":3250,"region":"South"}, ("INFC","BLR5","FC-Interpreter"): {"ai":0,"region":"South"},
    ("INFC","BLR7","Associate"): {"ai":3050,"region":"South"}, ("INFC","BLR7","PA"): {"ai":3250,"region":"South"}, ("INFC","BLR7","FC-Interpreter"): {"ai":0,"region":"South"},
    ("INFC","BLR8","Associate"): {"ai":3250,"region":"South"}, ("INFC","BLR8","PA"): {"ai":3250,"region":"South"}, ("INFC","BLR8","FC-Interpreter"): {"ai":0,"region":"South"},
    ("INFC","BOM4","Associate"): {"ai":2450,"region":"West"}, ("INFC","BOM4","PA"): {"ai":2400,"region":"West"}, ("INFC","BOM4","FC-Interpreter"): {"ai":0,"region":"West"},
    ("INFC","BOM5","Associate"): {"ai":2450,"region":"West"}, ("INFC","BOM5","PA"): {"ai":2400,"region":"West"}, ("INFC","BOM5","FC-Interpreter"): {"ai":0,"region":"West"},
    ("INFC","BOM7","Associate"): {"ai":2450,"region":"West"}, ("INFC","BOM7","PA"): {"ai":2400,"region":"West"}, ("INFC","BOM7","FC-Interpreter"): {"ai":0,"region":"West"},
    ("INFC","CJB1","Associate"): {"ai":1950,"region":"South"}, ("INFC","CJB1","PA"): {"ai":1850,"region":"South"}, ("INFC","CJB1","FC-Interpreter"): {"ai":0,"region":"South"},
    ("INFC","DED3","Associate"): {"ai":3250,"region":"North"}, ("INFC","DED3","PA"): {"ai":3250,"region":"North"}, ("INFC","DED3","FC-Interpreter"): {"ai":0,"region":"North"},
    ("INFC","DED4","Associate"): {"ai":3250,"region":"North"}, ("INFC","DED4","PA"): {"ai":3250,"region":"North"}, ("INFC","DED4","FC-Interpreter"): {"ai":0,"region":"North"},
    ("INFC","DED5","Associate"): {"ai":3250,"region":"North"}, ("INFC","DED5","PA"): {"ai":3250,"region":"North"}, ("INFC","DED5","FC-Interpreter"): {"ai":0,"region":"North"},
    ("INFC","DEL2","Associate"): {"ai":3250,"region":"North"}, ("INFC","DEL2","PA"): {"ai":3250,"region":"North"}, ("INFC","DEL2","FC-Interpreter"): {"ai":0,"region":"North"},
    ("INFC","DEL4","Associate"): {"ai":3250,"region":"North"}, ("INFC","DEL4","PA"): {"ai":3250,"region":"North"}, ("INFC","DEL4","FC-Interpreter"): {"ai":0,"region":"North"},
    ("INFC","DEL5","Associate"): {"ai":3250,"region":"North"}, ("INFC","DEL5","PA"): {"ai":3250,"region":"North"}, ("INFC","DEL5","FC-Interpreter"): {"ai":0,"region":"North"},
    ("INFC","DEX3","Associate"): {"ai":1000,"region":"North"}, ("INFC","DEX3","PA"): {"ai":2400,"region":"North"},
    ("INFC","HHS6","Associate"): {"ai":3400,"region":"North"}, ("INFC","HHS6","PA"): {"ai":3250,"region":"North"},
    ("INFC","HYD3","Associate"): {"ai":2200,"region":"South"}, ("INFC","HYD3","PA"): {"ai":1850,"region":"South"}, ("INFC","HYD3","FC-Interpreter"): {"ai":0,"region":"South"},
    ("INFC","HYD8","Associate"): {"ai":2200,"region":"South"}, ("INFC","HYD8","PA"): {"ai":1850,"region":"South"}, ("INFC","HYD8","FC-Interpreter"): {"ai":0,"region":"South"},
    ("INFC","ISK3","Associate"): {"ai":2450,"region":"West"}, ("INFC","ISK3","PA"): {"ai":2400,"region":"West"}, ("INFC","ISK3","FC-Interpreter"): {"ai":0,"region":"West"},
    ("INFC","JPX1","Associate"): {"ai":1650,"region":"North"}, ("INFC","JPX1","PA"): {"ai":1500,"region":"North"},
    ("INFC","LKO1","Associate"): {"ai":1950,"region":"North"}, ("INFC","LKO1","PA"): {"ai":1600,"region":"North"}, ("INFC","LKO1","FC-Interpreter"): {"ai":0,"region":"North"},
    ("INFC","MAA4","Associate"): {"ai":2200,"region":"South"}, ("INFC","MAA4","PA"): {"ai":1850,"region":"South"}, ("INFC","MAA4","FC-Interpreter"): {"ai":0,"region":"South"},
    ("INFC","PNQ2","Associate"): {"ai":1000,"region":"North"}, ("INFC","PNQ2","PA"): {"ai":2400,"region":"North"},
    ("INFC","PNQ3","Associate"): {"ai":2800,"region":"West"}, ("INFC","PNQ3","PA"): {"ai":2750,"region":"West"}, ("INFC","PNQ3","FC-Interpreter"): {"ai":0,"region":"West"},
    # ATS
    ("ATS","BBID","Associate"): {"ai":1200,"region":"North"}, ("ATS","BBID","PA"): {"ai":800,"region":"North"},
    ("ATS","BOMD","Associate"): {"ai":2600,"region":"West"}, ("ATS","BOMD","PA"): {"ai":2400,"region":"West"}, ("ATS","BOMD","SC-Interpreter"): {"ai":0,"region":"West"}, ("ATS","BOMD","SC Supervisor"): {"ai":0,"region":"West"},
    ("ATS","DELU","Associate"): {"ai":3400,"region":"North"}, ("ATS","DELU","PA"): {"ai":3250,"region":"North"}, ("ATS","DELU","SC-Interpreter"): {"ai":0,"region":"North"},
    ("ATS","GURV","Associate"): {"ai":1600,"region":"North"}, ("ATS","GURV","PA"): {"ai":2250,"region":"North"}, ("ATS","GURV","SC-Interpreter"): {"ai":0,"region":"North"}, ("ATS","GURV","SC Supervisor"): {"ai":0,"region":"North"},
    ("ATS","LKOO","Associate"): {"ai":1950,"region":"North"}, ("ATS","LKOO","PA"): {"ai":1600,"region":"North"}, ("ATS","LKOO","SC Supervisor"): {"ai":0,"region":"North"},
    ("ATS","MAMA","Associate"): {"ai":2200,"region":"West"}, ("ATS","MAMA","PA"): {"ai":2100,"region":"West"},
    ("ATS","MBOX","Associate"): {"ai":2600,"region":"West"}, ("ATS","MBOX","PA"): {"ai":2400,"region":"West"}, ("ATS","MBOX","SC-Interpreter"): {"ai":0,"region":"West"},
    ("ATS","MDEA","Associate"): {"ai":3400,"region":"North"}, ("ATS","MDEA","PA"): {"ai":3250,"region":"North"}, ("ATS","MDEA","SC-Interpreter"): {"ai":0,"region":"North"},
    ("ATS","MHYD","Associate"): {"ai":2350,"region":"South"}, ("ATS","MHYD","PA"): {"ai":2100,"region":"South"}, ("ATS","MHYD","SC-Interpreter"): {"ai":0,"region":"South"},
    ("ATS","MJAX","Associate"): {"ai":1850,"region":"North"}, ("ATS","MJAX","PA"): {"ai":2500,"region":"North"},
    ("ATS","MMAA","Associate"): {"ai":2500,"region":"South"}, ("ATS","MMAA","PA"): {"ai":2100,"region":"South"},
    ("ATS","MPNA","Associate"): {"ai":2850,"region":"West"}, ("ATS","MPNA","PA"): {"ai":2450,"region":"West"}, ("ATS","MPNA","SC-Interpreter"): {"ai":0,"region":"West"},
    ("ATS","MSTA","Associate"): {"ai":2050,"region":"West"}, ("ATS","MSTA","PA"): {"ai":1700,"region":"West"},
    ("ATS","NCRU","Associate"): {"ai":3400,"region":"North"}, ("ATS","NCRU","PA"): {"ai":3250,"region":"North"}, ("ATS","NCRU","SC-Interpreter"): {"ai":0,"region":"North"},
    ("ATS","SBCZ","Associate"): {"ai":3100,"region":"South"}, ("ATS","SBCZ","PA"): {"ai":4250,"region":"South"}, ("ATS","SBCZ","SC-Interpreter"): {"ai":0,"region":"South"},
    ("ATS","SXVD","Associate"): {"ai":1200,"region":"South"}, ("ATS","SXVD","PA"): {"ai":800,"region":"South"},
    ("ATS","BLRS","Associate"): {"ai":2900,"region":"South"}, ("ATS","BLRS","SC Supervisor"): {"ai":0,"region":"South"},
    ("ATS","PNQZ","Associate"): {"ai":2850,"region":"South"}, ("ATS","PNQZ","PA"): {"ai":2450,"region":"South"},
    ("ATS","HYD0","Associate"): {"ai":2350,"region":"South"}, ("ATS","HYD0","SC Supervisor"): {"ai":0,"region":"South"},
    ("ATS","VOMM","SC Supervisor"): {"ai":0,"region":"South"},
    # GSF HUB
    ("GSF HUB","HMH4","Associate"): {"ai":2450,"region":"West"}, ("GSF HUB","HMH4","PA"): {"ai":2400,"region":"West"},
    # AMXL
    ("AMXL","BLX1","Associate"): {"ai":3050,"region":"South"}, ("AMXL","BLX1","PA"): {"ai":3300,"region":"South"},
    ("AMXL","HBBB","Associate"): {"ai":1600,"region":"South"}, ("AMXL","HBBB","AMXL Supervisor"): {"ai":0,"region":"South"},
    ("AMXL","HBRA","Associate"): {"ai":1600,"region":"South"}, ("AMXL","HBRA","AMXL Supervisor"): {"ai":0,"region":"South"},
    ("AMXL","HMAA","Associate"): {"ai":1000,"region":"South"}, ("AMXL","HMAA","AMXL Supervisor"): {"ai":0,"region":"South"},
    ("AMXL","HDLB","Associate"): {"ai":1000,"region":"North"}, ("AMXL","HDLB","AMXL Supervisor"): {"ai":0,"region":"North"},
    ("AMXL","HHDA","Associate"): {"ai":1000,"region":"South"}, ("AMXL","HHDA","AMXL Supervisor"): {"ai":0,"region":"South"},
    ("AMXL","HHDC","Associate"): {"ai":1000,"region":"South"}, ("AMXL","HHDC","AMXL Supervisor"): {"ai":0,"region":"South"},
}

# AMZL sites (Site -> region + per-BT AI)
amzl_sites = {
    "AGRD": {"region":"North","Associate":1300,"PA":800,"AMZ ADE":800,"CSDL":800},
    "AMDE": {"region":"West","Associate":1750,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "ATQD": {"region":"North","Associate":1000,"PA":800,"AMZ ADE":800,"CSDL":800},
    "BBIF": {"region":"West","Associate":1300,"PA":800,"AMZ ADE":800,"CSDL":800},
    "BDQE": {"region":"West","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "BHOG": {"region":"West","Associate":1250,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "BLRA": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BLRB": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BLRG": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BLRL": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BLRM": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BLRP": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BLT1": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BLT2": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BLT3": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BLT4": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BLUA": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BOMC": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "BOME": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400,"Associate DA":2000},
    "BOMJ": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "BOMK": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "BOML": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400,"Associate DA":2000},
    "BOMN": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "BOMP": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "BOMS": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "BOT2": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "BOT3": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "BRUB": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BRUC": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "BRUD": {"region":"South","Associate":2600,"PA":2250,"AMZ ADE":2250,"CSDL":2250},
    "CCT1": {"region":"North","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "COK41": {"region":"South","Associate":3350,"AMZ ADE":800},
    "DELF": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "DELG": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "DELH": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "DELK": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "DELL": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "DELN": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "DELO": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "DELR": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "DELT": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "DLIH": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "FADA": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "GAUA": {"region":"North","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "GKPL": {"region":"North","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "GNNJ": {"region":"West","Associate":1750,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "GNNT": {"region":"West","Associate":1750,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "GNTD": {"region":"South","Associate":1300,"PA":800,"AMZ ADE":800,"CSDL":800},
    "HRWA": {"region":"North","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "HWHA": {"region":"North","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "HYBK": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "HYDD": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "HYDE": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "HYDH": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "HYDJ": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "HYDK": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "HYDP": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "HYT2": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "HYT3": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "IDRB": {"region":"West","Associate":1250,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "ISKK": {"region":"West","Associate":1250,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "IXCD": {"region":"North","Associate":1750,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "IXCE": {"region":"North","Associate":1750,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "IXDD": {"region":"North","Associate":1300,"PA":800,"AMZ ADE":800,"CSDL":800},
    "IXGK": {"region":"South","Associate":2500,"PA":800,"AMZ ADE":800,"CSDL":800},
    "JAIR": {"region":"West","Associate":1750,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "JDHD": {"region":"West","Associate":1000,"PA":800,"AMZ ADE":800,"CSDL":800},
    "JULD": {"region":"North","Associate":1000,"PA":800,"AMZ ADE":800,"CSDL":800},
    "KNUD": {"region":"North","Associate":1300,"PA":800,"AMZ ADE":800,"CSDL":800},
    "KNUO": {"region":"North","Associate":1300,"PA":800,"AMZ ADE":800,"CSDL":800},
    "KOLE": {"region":"North","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "LKOA": {"region":"North","Associate":1750,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "LKOD": {"region":"North","Associate":1750,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "LKOI": {"region":"North","Associate":1750,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "LUHD": {"region":"North","Associate":1500,"PA":800,"AMZ ADE":800,"CSDL":800},
    "MAAE": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MAAG": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MAAI": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MAAJ": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MAAK": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MAAL": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MAT1": {"region":"South","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MHPN": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MHPQ": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MMCA": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MMCE": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MREE": {"region":"North","Associate":1300,"PA":800,"AMZ ADE":800,"CSDL":800},
    "MUME": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MUMQ": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MUMR": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MUMV": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MUMZ": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "MYQD": {"region":"South","Associate":1300,"PA":800,"AMZ ADE":800,"CSDL":800},
    "NAGF": {"region":"West","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "NAGL": {"region":"West","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "NCRG": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "NCRJ": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "NCT2": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800,"Supervisor":2800},
    "NCT3": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "NCT8": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "NCTC": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "NCTD": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "NCTG": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "NDBA": {"region":"North","Associate":5200,"PA":2800,"AMZ ADE":2800},
    "NZMF": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "NZML": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "NZMM": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "NZMN": {"region":"North","Associate":2000,"PA":2800,"AMZ ADE":2800,"CSDL":2800},
    "PATD": {"region":"North","Associate":1250,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "PNQA": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "PNQJ": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "PNT1": {"region":"West","Associate":2000,"PA":1400,"AMZ ADE":1400,"CSDL":1400},
    "PNYF": {"region":"South","Associate":1500,"PA":800,"AMZ ADE":800},
    "PTJD": {"region":"South","Associate":1750,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "VGAH": {"region":"South","Associate":1300,"PA":800,"AMZ ADE":800,"CSDL":800},
    "VNSD": {"region":"North","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
    "VTZH": {"region":"South","Associate":1550,"PA":1100,"AMZ ADE":1100,"CSDL":1100},
}

for _site, _info in amzl_sites.items():
    _region = _info["region"]
    for _bt, _ai in _info.items():
        if _bt == "region":
            continue
        ai_region_data[("AMZL", _site, _bt)] = {"ai": _ai, "region": _region}

# UFF sites (Site -> region + per-BT AI)
uff_data = {
    "FBOB": {"region":"West","Associate":3250,"PA":1400,"ADE":1400},
    "FHYE": {"region":"South","Associate":2750,"PA":1400,"ADE":1400},
    "FVTG": {"region":"South","Associate":1750},
    "HMA1": {"region":"South","Associate":2800,"PA":1400,"ADE":1400},
    "PBO4": {"region":"West","Associate":3250,"ADE":1400},
    "PBO5": {"region":"West","Associate":3250,"PA":1400,"ADE":1400},
    "PBO6": {"region":"West","Associate":3250,"PA":1400,"ADE":1400},
    "PBO7": {"region":"West","Associate":3250,"ADE":1400},
    "PDL1": {"region":"North","Associate":2000,"PA":2800,"ADE":2800},
    "PDL2": {"region":"North","Associate":2000,"ADE":2800},
    "PDL5": {"region":"North","Associate":2000,"PA":2800,"ADE":2800},
    "PMA1": {"region":"South","Associate":2800,"ADE":1400},
    "SBLY": {"region":"South","Associate":3350,"ADE":2250},
    "SBLZ": {"region":"South","Associate":3350,"PA":2250,"ADE":2250},
    "U3PC": {"region":"South","Associate":2800,"ADE":1400},
    "U3PH": {"region":"South","Associate":2750,"PA":1400,"ADE":1400},
    "UAM1": {"region":"West","Associate":2950,"PA":1100},
    "UBL5": {"region":"South","Associate":3350,"PA":2250,"ADE":2250},
    "UBL6": {"region":"South","Associate":3350,"PA":2250,"ADE":2250},
    "UBL9": {"region":"South","Associate":3350,"PA":2250,"ADE":2250},
    "UBO3": {"region":"West","Associate":3250,"ADE":1400},
    "UBO6": {"region":"West","Associate":3250,"PA":1400,"ADE":1400},
    "UBO7": {"region":"West","Associate":3250,"ADE":1400},
    "UCC1": {"region":"North","Associate":1750,"PA":1100,"ADE":1100},
    "UCC2": {"region":"North","Associate":1750,"PA":1100,"ADE":1100},
    "UDL4": {"region":"North","Associate":2000,"PA":2800,"ADE":2800},
    "UDL6": {"region":"North","Associate":2000,"PA":2800},
    "UMA2": {"region":"South","Associate":2800,"PA":1400,"ADE":1400},
    "UMA7": {"region":"South","Associate":2800,"PA":1400,"ADE":1400},
    "UPN1": {"region":"West","Associate":3350,"PA":1400,"ADE":1400},
    "UPN2": {"region":"West","Associate":3350,"PA":1400,"ADE":1400},
}

for _site, _info in uff_data.items():
    _region = _info["region"]
    for _bt, _ai in _info.items():
        if _bt == "region":
            continue
        ai_region_data[("UFF", _site, _bt)] = {"ai": _ai, "region": _region}


def apply_ai_region(wage_cards):
    """Set Attendance Incentive + Region on non-PT cards from the mapping.
    Returns (ai_region_count, region_only_count)."""
    # Site -> region (for region-only fallback)
    site_region = {}
    for (ent, site, bt), v in ai_region_data.items():
        site_region.setdefault((ent, site), v["region"])

    ai_region_count = 0
    region_only_count = 0
    for card in wage_cards.values():
        if card.get("is_pt"):
            continue  # PT handled by regeneration
        entity = card.get("entity", "")
        site = card.get("site_codes", "")
        short_bt = card.get("short_bt", "")
        key = (entity, site, short_bt)
        if key in ai_region_data:
            info = ai_region_data[key]
            card["attendance_incentive"] = info["ai"]
            card["region"] = info["region"]
            ai_region_count += 1
        elif (entity, site) in site_region:
            reg = site_region[(entity, site)]
            if card.get("region", "") != reg:
                card["region"] = reg
                region_only_count += 1
    return ai_region_count, region_only_count


def main():
    # Import the app's PT generator + calc dependencies (safe: server is under __main__)
    sys.path.insert(0, os.path.join(APP_DIR, "backend", "src"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("wcapp", os.path.join(APP_DIR, "app.py"))
    wcapp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wcapp)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    wage_cards = data.get("wage_cards", {})

    # --- Step 1 + 2: Attendance Incentive + Region on non-PT cards ---
    ai_cnt, region_only_cnt = apply_ai_region(wage_cards)
    print(f"[1] Attendance Incentive + Region set on {ai_cnt} cards")
    print(f"[2] Region-only set on {region_only_cnt} additional cards")

    # --- Step 3: Regenerate PT cards (PT AI = 50% of matching Associate) ---
    non_pt = {cid: c for cid, c in wage_cards.items() if not c.get("is_pt")}
    all_non_pt = list(non_pt.values())
    pt_cards = wcapp.generate_pt_cards(
        all_non_pt, wcapp.engine, wcapp.get_ptax_slabs, wcapp.get_lwf_config
    )
    new_cards = dict(non_pt)
    for pc in pt_cards:
        new_cards[pc["id"]] = pc
    data["wage_cards"] = new_cards
    pt_with_ai = sum(1 for pc in pt_cards if pc.get("attendance_incentive", 0) > 0)
    print(f"[3] Regenerated {len(pt_cards)} PT cards ({pt_with_ai} with AI > 0, = 50% of Associate)")

    # --- Step 4: Save ---
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"[4] Saved {len(new_cards)} total cards to data.json")
    print("Done. Restart the app and commit + push data.json for Render.")


if __name__ == "__main__":
    main()
