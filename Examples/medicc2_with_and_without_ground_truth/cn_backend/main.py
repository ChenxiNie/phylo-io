from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

BASE = Path("/Users/chenxi/Projects/Phylogenetics/phylo-io/5.1-SPR-MEDICC2-evolve/medicc2_with_and_without_ground_truth/run2_2026-03-28_5.1-SPR-MEDICC2-with-without-ground-truth_leaves30_events3_iterations30")

@app.get("/cn_profile")
def get_cn_profile(node: str, leaf_count: int, iteration: int, source: str = "ground_truth"):
    if source == "medicc2":
        path = BASE / "reconstruction" / f"leaves_{leaf_count}" / f"iteration_{iteration}" / "original" / "medicc2_input_final_cn_profiles.tsv"
    elif source == "medicc2_gt":
        path = BASE / "reconstruction" / f"leaves_{leaf_count}" / f"iteration_{iteration}" / "original" / "medicc2_with_ground_truth_input_final_cn_profiles.tsv"
    else:
        path = BASE / "cn_profiles" / f"leaves_{leaf_count}" / f"iteration_{iteration}" / "cn_profiles.tsv"

    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    df = pd.read_csv(path, sep="\t")
    # medicc2 (without gt) uses "internal1" style — no underscore before the number
    lookup_node = node.replace("internal_", "internal") if source == "medicc2" else node
    rows = df[df["sample_id"] == lookup_node].copy()

    if rows.empty:
        raise HTTPException(status_code=404, detail=f"Node '{node}' not found")

    rows["is_breakpoint"] = (
        (rows["cn_a"].diff().fillna(0) != 0) |
        (rows["cn_b"].diff().fillna(0) != 0)
    )
    rows["breakpoint_count"] = rows["is_breakpoint"].cumsum()

    return rows.to_dict(orient="records")
