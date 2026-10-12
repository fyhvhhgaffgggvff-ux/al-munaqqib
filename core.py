from __future__ import annotations
import io
import math
from datetime import datetime, timezone
from typing import Any
import numpy as np
import pandas as pd
try:
    import lasio
except ImportError:
    lasio = None

# ---------- Pure calculation / parsing functions (unit tested) ----------
def screen_lift_system(q_bpd: float, depth_ft: float, gor_scf_stb: float, viscosity_cp: float) -> dict[str, Any]:
    vals = [q_bpd, depth_ft, gor_scf_stb, viscosity_cp]
    if not all(math.isfinite(float(v)) for v in vals):
        raise ValueError("Inputs must be finite numbers.")
    if q_bpd <= 0 or depth_ft <= 0 or gor_scf_stb < 0 or viscosity_cp <= 0:
        raise ValueError("Production, depth and viscosity must be positive; GOR cannot be negative.")
    # Heuristic screening only; not a vendor sizing calculation.
    if viscosity_cp >= 300:
        system = "PCP (Progressive Cavity Pump)"
        capex, opex = 65000, 120
    elif gor_scf_stb >= 1500 and depth_ft >= 10000:
        system = "Gas Lift"
        capex, opex = 90000, 150
    elif q_bpd >= 3500:
        system = "ESP (Electric Submersible Pump)"
        capex, opex = 120000, 250
    else:
        system = "SRP (Sucker Rod Pump)"
        capex, opex = 45000, 80
    return {"system": system, "capex_usd_estimate": capex, "opex_usd_day_estimate": opex,
            "note": "Rule-based screening and illustrative cost assumptions only; validate with field data, vendors and local costs."}


def calculate_srp(depth_ft: float, production_bpd: float, stroke_in: float, spm: float, efficiency: float = 0.8) -> dict[str, float]:
    if not all(math.isfinite(float(v)) for v in [depth_ft, production_bpd, stroke_in, spm, efficiency]):
        raise ValueError("Inputs must be finite numbers.")
    if min(depth_ft, production_bpd, stroke_in, spm, efficiency) <= 0 or efficiency > 1:
        raise ValueError("Depth, production, stroke, SPM and efficiency must be positive; efficiency must be <= 1.")
    # Simplified displacement-based estimate, not an API RP 11L dynamometer design.
    diameter_in = math.sqrt(production_bpd / (0.1166 * stroke_in * spm * efficiency))
    peak_load_lbf = (0.433 * depth_ft * (math.pi * (diameter_in / 2) ** 2)) + (depth_ft * 1.6)
    motor_hp = (peak_load_lbf * stroke_in * spm) / 375000 + 5
    return {"plunger_diameter_in_estimate": diameter_in, "peak_load_lbf_estimate": peak_load_lbf,
            "motor_hp_estimate": motor_hp}


def calculate_esp(depth_ft: float, production_bpd: float, head_per_stage_ft: float, surface_pressure_psi: float) -> dict[str, float]:
    vals = [depth_ft, production_bpd, head_per_stage_ft, surface_pressure_psi]
    if not all(math.isfinite(float(v)) for v in vals):
        raise ValueError("Inputs must be finite numbers.")
    if depth_ft <= 0 or production_bpd <= 0 or head_per_stage_ft <= 0 or surface_pressure_psi < 0:
        raise ValueError("Depth, production and head per stage must be positive; surface pressure cannot be negative.")
    # Simplified pressure-head conversion. Does not include fluid gradient, friction, intake pressure or pump curves.
    tdh_ft = depth_ft + surface_pressure_psi * 2.31
    stages = math.ceil(tdh_ft / head_per_stage_ft)
    # This is a rough placeholder estimate; actual hydraulic horsepower needs fluid SG and pump efficiency.
    hp_estimate = (production_bpd * tdh_ft) / 135000
    return {"tdh_ft_estimate": tdh_ft, "stages_estimate": float(stages), "motor_hp_placeholder_estimate": hp_estimate}


def vogel_ipr(p_res_psi: float, q_test_bpd: float, p_wf_test_psi: float) -> tuple[float, np.ndarray, np.ndarray]:
    if not all(math.isfinite(float(v)) for v in [p_res_psi, q_test_bpd, p_wf_test_psi]):
        raise ValueError("Inputs must be finite numbers.")
    if p_res_psi <= 0 or q_test_bpd <= 0 or p_wf_test_psi < 0 or p_wf_test_psi >= p_res_psi:
        raise ValueError("Require Pres > 0, Qtest > 0 and 0 <= Pwf(test) < Pres.")
    ratio = p_wf_test_psi / p_res_psi
    denominator = 1 - 0.2 * ratio - 0.8 * ratio**2
    if denominator <= 0:
        raise ValueError("Test point produces an invalid Vogel denominator.")
    q_max = q_test_bpd / denominator
    pwf = np.linspace(0, p_res_psi, 101)
    q = q_max * (1 - 0.2 * (pwf / p_res_psi) - 0.8 * (pwf / p_res_psi) ** 2)
    return q_max, q, pwf


def read_uploaded_data(filename: str, content: bytes) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Read LAS, CSV, XLSX or XLS bytes and return a clean dataframe plus metadata."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if not content:
        raise ValueError("The uploaded file is empty.")
    if ext == "csv":
        try:
            df = pd.read_csv(io.BytesIO(content), sep=None, engine="python")
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(content), sep=None, engine="python", encoding="latin-1")
        meta = {"format": "CSV", "well_name": None, "depth_curve": None, "curves": list(map(str, df.columns))}
    elif ext in {"xlsx", "xls"}:
        df = pd.read_excel(io.BytesIO(content))
        meta = {"format": ext.upper(), "well_name": None, "depth_curve": None, "curves": list(map(str, df.columns))}
    elif ext == "las":
        if lasio is None:
            raise RuntimeError("LAS reader missing. Install dependencies with: pip install -r requirements.txt")
        las = lasio.read(io.BytesIO(content), ignore_data=False)
        df = las.df().reset_index()
        depth_col = str(df.columns[0]) if len(df.columns) else None
        well_name = None
        try:
            well_name = str(las.well.WELL.value).strip() or None
        except Exception:
            pass
        meta = {"format": "LAS", "well_name": well_name, "depth_curve": depth_col,
                "curves": [str(c.mnemonic) for c in las.curves]}
    else:
        raise ValueError("Unsupported file type. Upload LAS, CSV, XLSX or XLS.")
    if df.empty or len(df.columns) == 0:
        raise ValueError("No tabular data was found in the file.")
    df.columns = [str(c).strip() for c in df.columns]
    # Convert numeric-looking columns while preserving textual columns.
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            converted = pd.to_numeric(df[col], errors="coerce")
            nonblank = df[col].notna().sum()
            if nonblank and converted.notna().sum() / nonblank >= 0.8:
                df[col] = converted
    df = df.replace([np.inf, -np.inf], np.nan)
    meta.update({"rows": int(len(df)), "columns": int(len(df.columns)), "missing_cells": int(df.isna().sum().sum())})
    return df, meta


def summarize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        series = df[col]
        numeric = pd.to_numeric(series, errors="coerce")
        valid_numeric = numeric.dropna()
        is_numeric = pd.api.types.is_numeric_dtype(series) or len(valid_numeric) > 0
        row = {"Curve / Column": str(col), "Data type": str(series.dtype), "Valid values": int(series.notna().sum()),
               "Missing values": int(series.isna().sum()), "Missing %": round(float(series.isna().mean() * 100), 2)}
        if is_numeric and not valid_numeric.empty:
            row.update({"Min": float(valid_numeric.min()), "Max": float(valid_numeric.max()),
                        "Mean": float(valid_numeric.mean()), "Std dev": float(valid_numeric.std()) if len(valid_numeric) > 1 else 0.0})
        else:
            row.update({"Min": None, "Max": None, "Mean": None, "Std dev": None})
        rows.append(row)
    return pd.DataFrame(rows)


def make_report(report_parts: dict[str, str]) -> str:
    lines = ["AL-MUNAQQIB ENGINEERING PLATFORM — PRELIMINARY REPORT", f"Generated UTC: {datetime.now(timezone.utc).isoformat()}", "=" * 65]
    for key, value in report_parts.items():
        lines.extend([f"\n{key.upper()}", "-" * 40, value])
    lines += ["", "DISCLAIMER: Preliminary educational screening only. Verify inputs, correlations, units and designs with qualified petroleum engineers and field/vendor data before operational use."]
    return "\n".join(lines)


