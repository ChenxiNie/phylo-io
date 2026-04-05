This folder contains visualizations to the result stored in baseline folder of 5.1-SPR-MEDICC2-evolve

## Starting the project

Two servers must run simultaneously in separate terminals.

**Frontend (run from repo root):**
```bash
mamba activate phylo-web
cd /Users/chenxi/Projects/Phylogenetics/phylo-io
python -m http.server 8080 > /tmp/phylo-frontend.log 2>&1 &
```

**Backend (run from cn_backend folder):**
```bash
cd /Users/chenxi/Projects/Phylogenetics/phylo-io/Examples/baseline_visualization_medicc_with_ground_truth_tree_agains_ground_truth/cn_backend
uvicorn main:app --port 8001 --reload > /tmp/phylo-backend.log 2>&1 &
```

Both run in the background — the terminal stays free. To check logs if something goes wrong:
```bash
tail -f /tmp/phylo-frontend.log
tail -f /tmp/phylo-backend.log
```

**Then open in browser:**
```
http://localhost:8080/Examples/baseline_visualization_medicc_with_ground_truth_tree_agains_ground_truth/index.html
```

## Stopping the project

```bash
pkill -f "uvicorn main:app"
pkill -f "http.server 8080"
```

Or by port:
```bash
lsof -ti :8001 | xargs kill
lsof -ti :8080 | xargs kill
```