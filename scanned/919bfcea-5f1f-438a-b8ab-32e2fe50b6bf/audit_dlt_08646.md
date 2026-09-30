# [?] Prevent a crash that happens when `config["harvester"]["plot_directories"]` is not a list (#13551)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2022-09-30
Source: https://github.com/Chia-Network/chia-blockchain/commit/42e67f049e460a640f2457065676e13cf90441ad
Type: security-commit

## Details
Prevent a crash that happens when `config["harvester"]["plot_directories"]` is not a list (#13551)

## Patch
### chia/plotting/util.py
```diff
@@ -69,7 +69,7 @@ class PlotRefreshResult:
 def get_plot_directories(root_path: Path, config: Dict = None) -> List[str]:
     if config is None:
         config = load_config(root_path, "config.yaml")
-    return config["harvester"]["plot_directories"]
+    return config["harvester"]["plot_directories"] or []
 
 
 def get_plot_filenames(root_path: Path) -> Dict[Path, List[Path]]:
@@ -93,6 +93,8 @@ def add_plot_directory(root_path: Path, str_path: str) -> Dict:
     with lock_and_load_config(root_path, "config.yaml") as config:
         if str(Path(str_path).resolve()) in get_plot_directories(root_path, config):
             raise ValueError(f"Path already added: {path}")
+        if not config["harvester"]["plot_directories"]:
+            config["harvester"]["plot_directories"] = []
         config["harvester"]["plot_directories"].append(str(Path(str_path).resolve()))
         save_config(root_path, "config.yaml", config)
     return config
```
