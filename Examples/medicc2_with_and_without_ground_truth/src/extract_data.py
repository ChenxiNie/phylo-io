from pathlib import Path
import pandas as pd
import json

PIPELINE_PATH_BASE = Path("/Users/chenxi/Projects/Phylogenetics/phylo-io/5.1-SPR-MEDICC2-evolve/medicc2_with_and_without_ground_truth/run2_2026-03-28_5.1-SPR-MEDICC2-with-without-ground-truth_leaves30_events3_iterations30")
BENCHMARKING_PATH = PIPELINE_PATH_BASE / "benchmarking"
RECONSTRUCTION_PATH = PIPELINE_PATH_BASE / "reconstruction"
TREES_PATH = PIPELINE_PATH_BASE / "trees"

# --- load all_metrics.tsv ---
metrics = pd.read_csv(BENCHMARKING_PATH / "all_metrics.tsv", sep="\t")

# pivot so each iteration has one row with both tools side by side
medicc2_rows = metrics[metrics["tool"] == "medicc2"].set_index(["iteration", "num_leaves"])
gt_rows = metrics[metrics["tool"] == "medicc2_with_ground_truth"].set_index(["iteration", "num_leaves"])

leaf_counts = sorted(metrics["num_leaves"].unique().tolist())
results = []

for leaf_dir in sorted(RECONSTRUCTION_PATH.glob("leaves_*"), key=lambda p: int(p.name.split("_")[-1])):
    leaf_count = int(leaf_dir.name.split("_")[1])

    for iter_dir in sorted(leaf_dir.glob("iteration_*"), key=lambda p: int(p.name.split("_")[1])):
        iteration = int(iter_dir.name.split("_")[1])
        orig = iter_dir / "original"

        # --- tree lengths from summary TSVs ---
        def read_tree_length(tsv_path):
            df = pd.read_csv(tsv_path, sep="\t", header=None)
            row = df[df[0] == "tree_length"]
            return float(row[1].iloc[0])

        tree_length_medicc2 = read_tree_length(orig / "medicc2_input_summary.tsv")
        tree_length_medicc2_gt = read_tree_length(orig / "medicc2_with_ground_truth_input_summary.tsv")

        # --- coloring logic ---
        if tree_length_medicc2 == tree_length_medicc2_gt:
            color = "grey"
        elif tree_length_medicc2 > tree_length_medicc2_gt:
            color = "red"
        else:
            color = "green"

        # --- normalized RF from all_metrics.tsv ---
        key = (iteration, leaf_count)
        normalized_rf_medicc2 = float(medicc2_rows.loc[key, "normalized_rf"])
        normalized_rf_medicc2_gt = float(gt_rows.loc[key, "normalized_rf"])

        # --- newicks ---
        ground_truth_newick = open(TREES_PATH / f"leaves_{leaf_count}" / f"iteration_{iteration}" / "ground_truth.nwk").read().strip()
        medicc2_newick = open(orig / "medicc2_reconstructed.nwk").read().strip()
        medicc2_gt_newick = open(orig / "medicc2_with_ground_truth_reconstructed.nwk").read().strip()

        results.append({
            "leaf_count": leaf_count,
            "iteration": iteration,
            "tree_length_medicc2": tree_length_medicc2,
            "tree_length_medicc2_gt": tree_length_medicc2_gt,
            "color": color,
            "normalized_rf_medicc2": normalized_rf_medicc2,
            "normalized_rf_medicc2_gt": normalized_rf_medicc2_gt,
            "ground_truth_newick": ground_truth_newick,
            "medicc2_newick": medicc2_newick,
            "medicc2_gt_newick": medicc2_gt_newick,
        })

all_rf = [r["normalized_rf_medicc2"] for r in results] + [r["normalized_rf_medicc2_gt"] for r in results]
max_rf = max(all_rf) + 0.05

output = {
    "run_name": PIPELINE_PATH_BASE.name,
    "leaf_counts": leaf_counts,
    "max_rf": max_rf,
    "data": results,
}

output_path = Path(__file__).parent / "data.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"Written {len(results)} records to {output_path}")

# quick sanity check
colors = {}
for r in results:
    colors[r["color"]] = colors.get(r["color"], 0) + 1
print(f"Color breakdown: {colors}")
