from pathlib import Path
import pandas as pd 
import json 

PIPELINE_PATH_BASE=Path("/Users/chenxi/Projects/Phylogenetics/phylo-io/5.1-SPR-MEDICC2-evolve/leaves_30-50-baseline/run2_2026-03-27_5.1-SPR-MEDICC2-30-50-baseline_leaves30-50_events3_iterations30")
CN_PROFILEs_PATH=PIPELINE_PATH_BASE/ "cn_profiles"
TREES_PATH=PIPELINE_PATH_BASE/ "trees"
RECONSTRUCTION_PATH=PIPELINE_PATH_BASE/ "reconstruction" 

leaf_counts = []
results = []

for leaf_dir in sorted(RECONSTRUCTION_PATH.glob("leaves_*"), key=lambda p: int(p.name.split("_")[-1])):
    leaf_count = int(leaf_dir.name.split("_")[1]) # "leaves_30" -> 30
    leaf_counts.append(leaf_count)

    for iter_dir in sorted(leaf_dir.glob("iteration_*"),
                           key=lambda p: int(p.name.split("_")[1])): # sort by iteration number
        iteration = int(iter_dir.name.split("_")[1]) # "iteration_0" -> 0

        medicc_summary_tsv_path = iter_dir / "original" / "medicc2_input_summary.tsv"
        medicc_summary_pd = pd.read_csv(medicc_summary_tsv_path, sep="\t", header=None)
        tree_length_row = medicc_summary_pd[medicc_summary_pd[0] == 'tree_length']
        medicc_tree_length = float(tree_length_row[1].iloc[0]) # extract the tree length value from the row 

        # Load the ground truth tree length from events.tsv \
        ground_truth_events_tsv_path = CN_PROFILEs_PATH / f"leaves_{leaf_count}" / f"iteration_{iteration}" / "events.tsv"
        ground_truth_events_pd = pd.read_csv(ground_truth_events_tsv_path, sep="\t")
        ground_truth_event_count = len(ground_truth_events_pd) # the number of events is the tree length for the ground truth tree 

        ground_truth_newick_path = TREES_PATH / f"leaves_{leaf_count}" / f"iteration_{iteration}" / "ground_truth.nwk"
        ground_truth_newick = open(ground_truth_newick_path).read().strip() # read the ground truth newick string 

        reconstructed_newick_path = iter_dir / "original" / "medicc2_reconstructed.nwk"
        reconstructed_newick = open(reconstructed_newick_path).read().strip() # read the reconstructed newick string

        results.append({
            "leaf_count": leaf_count,
            "iteration": iteration,
            "tree_length_medicc": medicc_tree_length,
            "n_events_ground_truth": ground_truth_event_count,
            "ground_truth_newick": ground_truth_newick,
            "reconstructed_newick": reconstructed_newick
        })

output = {
    "run_name": PIPELINE_PATH_BASE.name,
    "leaf_counts": leaf_counts,
    "data": results
}

output_path = Path(__file__).parent / "data.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2) 

print(f"Written {len(results)} records to {output_path}")