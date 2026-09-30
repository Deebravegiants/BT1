# [?] .github: archive crashers and fix set-crashers-count step (#5992)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2021-01-27
Source: https://github.com/cometbft/cometbft/commit/c3d2f68c0576d168103107fa5b6460899db258ba
Type: security-commit

## Details
.github: archive crashers and fix set-crashers-count step (#5992)

## Patch
### .github/workflows/fuzz-nightly.yml
```diff
@@ -39,9 +39,23 @@ jobs:
         working-directory: test/fuzz
         run: timeout 10m make fuzz-rpc-server
 
+      - name: Archive crashers
+        uses: actions/upload-artifact@v2
+        with:
+          name: crashers
+          path: test/fuzz/**/crashers
+          retention-days: 1
+
+      - name: Archive suppressions
+        uses: actions/upload-artifact@v2
+        with:
+          name: suppressions
+          path: test/fuzz/**/suppressions
+          retention-days: 1
+
       - name: Set crashers count
         working-directory: test/fuzz
-        run: echo "::set-output name=crashers-count::$(find . -type d -name "crashers" | xargs -I % sh -c 'ls % | wc -l' | awk '{total += $1} END {print total}')"
+        run: echo "::set-output name=crashers-count::$(find . -type d -name 'crashers' | xargs -I % sh -c 'ls % | wc -l' | awk '{total += $1} END {print total}')"
         id: set-crashers-count
 
     outputs:
```
