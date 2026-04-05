from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd

app = FastAPI()

# allow the browser on localhost:8080 to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

BASE = Path("/Users/chenxi/Projects/Phylogenetics/phylo-io/5.1-SPR-MEDICC2-evolve/leaves_30-50-baseline/run2_2026-03-27_5.1-SPR-MEDICC2-30-50-baseline_leaves30-50_events3_iterations30")

@app.get("/cn_profile")
def get_cn_profile(node: str, leaf_count: int, iteration: int, source: str = "ground_truth"):
    if source == "medicc2":
        path = BASE / "reconstruction" / f"leaves_{leaf_count}" / f"iteration_{iteration}" / "original" / "medicc2_input_final_cn_profiles.tsv"
    else:
        path = BASE / "cn_profiles" / f"leaves_{leaf_count}" / f"iteration_{iteration}" / "cn_profiles.tsv"

    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    df = pd.read_csv(path, sep="\t")
    rows = df[df["sample_id"] == node].copy()

    if rows.empty:
        raise HTTPException(status_code=404, detail=f"Node '{node}' not found in iteration {iteration}, leaves {leaf_count}")

    # detect breakpoints: any bin where cn_a or cn_b differs from the previous bin
    rows["is_breakpoint"] = (
        (rows["cn_a"].diff().fillna(0) != 0) |
        (rows["cn_b"].diff().fillna(0) != 0)
    )
    # count cumulative breakpoints so each breakpoint gets an integer label
    rows["breakpoint_count"] = rows["is_breakpoint"].cumsum()

    return rows.to_dict(orient="records")
