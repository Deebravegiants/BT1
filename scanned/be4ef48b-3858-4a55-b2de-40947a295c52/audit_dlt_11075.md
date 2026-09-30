# [?] ctb: Fix data race in generate-l2-genesis

## Summary
Severity: Unknown
Chain: Kroma
Component: kroma-network/kroma
Published: 2023-11-28
Source: https://github.com/kroma-network/kroma/commit/9bb13a0974a986ddabff9ac7c0086516974e33ad
Type: security-commit

## Details
ctb: Fix data race in generate-l2-genesis

Forge reads the genesis outfile before it is completely written. This leads to errors like the following:

```
[FAIL. Reason: setup failed: failed to parse json file: "/root/project/packages/contracts-bedrock/.testdata/genesis.json": EOF while parsing a value at line 1 column 0]
```

To fix this, this PR adds a loop at the end of the file that checks if the L2 outfile is over 8 megabytes. This is a hack - a longer term fix would be to investigate why the process Forge calls via `vm.ffi` exits prior to fully writing the file. I tried calling `Sync()` from within the Go code, but it didn't fix the issue.

## Patch
### packages/contracts-bedrock/scripts/generate-l2-genesis.sh
```diff
@@ -1,5 +1,7 @@
 #!/usr/bin/env bash
 
+set -euo pipefail
+
 # Create a L2 genesis.json suitable for the solidity tests to
 # ingest using `vm.loadAllocs(string)`.
 # This script depends on the relative path to the op-node from
@@ -30,3 +32,16 @@ if [ ! -f "$OUTFILE_L2" ]; then
     --outfile.l2 "$OUTFILE_L2" \
     --outfile.rollup "$OUTFILE_ROLLUP" > /dev/null 2>&1
 fi
+
+# Wait for the L2 outfile to be over 8M for up to 2 seconds
+# This is a hack to ensure that the outfile is fully written
+# before the solidity tests try to read it
+for i in {1..8}; do
+  if [ $(du -m "$OUTFILE_L2" | cut -f1) -ge 8 ]; then
+    exit 0
+  fi
+  sleep 0.25
+done
+
+echo "L2 genesis file not generated in time. Exiting."
+exit 1
\ No newline at end of file
```
