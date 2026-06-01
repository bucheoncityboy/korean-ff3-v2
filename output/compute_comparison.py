"""
Task 12: US vs Korea factor comparison tables and factor correlations.

Inputs:
  - fama-ff3-/appendix_output/factors.csv (US, 1963-07~1991-12, 342 months)
  - korean_ff3_v2/data/factors_korea.csv (KR, 2000-07~2026-05, 311 months)

Outputs:
  - korean_ff3_v2/output/us_vs_korea_factor_summary.csv
  - korean_ff3_v2/output/factor_correlations.csv

IMPORTANT: US and KR periods are different (342 vs 311 months).
All comparisons include a period caveat.
"""

import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(r"C:\Users\PC\Desktop\AI\famakor")

# ── Load data ──────────────────────────────────────────────────────────────
us_raw = pd.read_csv(ROOT / "fama-ff3-" / "appendix_output" / "factors.csv", comment="#")
kr_raw = pd.read_csv(ROOT / "korean_ff3_v2" / "data" / "factors_korea.csv")

# ── Factor columns ─────────────────────────────────────────────────────────
US_FACTORS = ["Mkt-RF", "SMB", "HML"]
KR_FACTORS = ["Mkt-RF", "SMB", "HML"]

us = us_raw[US_FACTORS].copy()
kr = kr_raw[KR_FACTORS].copy()

US_PERIOD = "1963-07~1991-12"
KR_PERIOD = "2000-07~2026-05"
US_N = len(us)  # 342
KR_N = len(kr)  # 311

CAVEAT = (
    f"CAVEAT: US period ({US_PERIOD}, {US_N} months) and KR period "
    f"({KR_PERIOD}, {KR_N} months) differ. "
    "Direct comparison of means/std is affected by different time spans."
)


# ── Compute summary statistics ──────────────────────────────────────────────
def compute_stats(series: pd.Series, factor: str, market: str, period: str, n: int) -> dict:
    mean = series.mean()
    std = series.std(ddof=1)
    t_stat = mean / std * np.sqrt(n) if std > 0 else np.nan
    sharpe = mean / std if std > 0 else np.nan
    return {
        "factor": factor,
        "market": market,
        "period": period,
        "mean": round(mean, 6),
        "std": round(std, 6),
        "t_stat": round(t_stat, 4),
        "sharpe": round(sharpe, 4),
        "min": round(series.min(), 6),
        "max": round(series.max(), 6),
        "n_months": n,
    }


rows = []
for factor in US_FACTORS:
    rows.append(compute_stats(us[factor], factor, "US", US_PERIOD, US_N))
for factor in KR_FACTORS:
    rows.append(compute_stats(kr[factor], factor, "KR", KR_PERIOD, KR_N))

summary_df = pd.DataFrame(rows)

# Add caveat as a metadata row (stored in a comment column approach)
# We'll save the caveat in a separate metadata section

output_dir = ROOT / "korean_ff3_v2" / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# ── Save summary CSV ───────────────────────────────────────────────────────
summary_path = output_dir / "us_vs_korea_factor_summary.csv"

# Write caveat as first line comment, then data
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(f"# {CAVEAT}\n")
summary_df.to_csv(summary_path, index=False, mode="a", encoding="utf-8")

print("=== US vs Korea Factor Summary ===")
print(summary_df.to_string(index=False))
print(f"\nSaved to: {summary_path}")

# ── Compute factor correlations ────────────────────────────────────────────
us_corr = us.corr()
kr_corr = kr.corr()

# Build correlation table with market label
corr_rows = []
for i, f1 in enumerate(US_FACTORS):
    for j, f2 in enumerate(US_FACTORS):
        corr_rows.append({
            "market": "US",
            "factor_1": f1,
            "factor_2": f2,
            "correlation": round(us_corr.iloc[i, j], 6),
        })
for i, f1 in enumerate(KR_FACTORS):
    for j, f2 in enumerate(KR_FACTORS):
        corr_rows.append({
            "market": "KR",
            "factor_1": f1,
            "factor_2": f2,
            "correlation": round(kr_corr.iloc[i, j], 6),
        })

corr_df = pd.DataFrame(corr_rows)

corr_path = output_dir / "factor_correlations.csv"
with open(corr_path, "w", encoding="utf-8") as f:
    f.write(f"# {CAVEAT}\n")
corr_df.to_csv(corr_path, index=False, mode="a", encoding="utf-8")

print("\n=== Factor Correlations ===")
print(corr_df.to_string(index=False))
print(f"\nSaved to: {corr_path}")

# ── Verification ────────────────────────────────────────────────────────────
print("\n=== Verification ===")
print(f"Summary rows: {len(summary_df)} (expected 6)")
print(f"Correlation rows: {len(corr_df)} (expected 18 = 9 US + 9 KR)")
assert len(summary_df) == 6, f"Expected 6 summary rows, got {len(summary_df)}"
assert len(corr_df) == 18, f"Expected 18 correlation rows, got {len(corr_df)}"
assert summary_df["n_months"].unique().tolist() == [US_N, KR_N], "Unexpected n_months"
print("All checks passed!")