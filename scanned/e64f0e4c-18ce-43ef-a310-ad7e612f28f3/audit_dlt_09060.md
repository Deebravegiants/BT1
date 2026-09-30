# [?] Fix potential race condition on gen_networks script when building with -j

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2025-07-03
Source: https://github.com/LedgerHQ/app-ethereum/commit/7cb22a210a897366deaacbf0a8f0c52d4d7e42ec
Type: security-commit

## Details
Fix potential race condition on gen_networks script when building with -j

## Patch
### tools/gen_networks.py
```diff
@@ -117,5 +117,7 @@ def main(output_dir: str) -> bool:
     parser = argparse.ArgumentParser()
     parser.add_argument("OUTPUT_DIR")
     args = parser.parse_args()
+    # also created by the SDK, but just in case this script is called too soon
+    os.makedirs(args.OUTPUT_DIR, exist_ok=True)
     assert os.path.isdir(args.OUTPUT_DIR)
     quit(0 if main(args.OUTPUT_DIR) else 1)
```
