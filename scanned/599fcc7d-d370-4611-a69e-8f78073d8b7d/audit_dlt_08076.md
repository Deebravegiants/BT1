# [?] miner: fix `addPackageTxs` unsigned integer overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-09-24
Source: https://github.com/bitcoin/bitcoin/commit/b807dfcdc5929c314d43b790c9e705d5bf0a86e8
Type: security-commit

## Details
miner: fix `addPackageTxs` unsigned integer overflow

## Patch
### src/node/miner.cpp
```diff
@@ -397,8 +397,8 @@ void BlockAssembler::addPackageTxs(int& nPackagesSelected, int& nDescendantsUpda
 
             ++nConsecutiveFailed;
 
-            if (nConsecutiveFailed > MAX_CONSECUTIVE_FAILURES && nBlockWeight >
-                    m_options.nBlockMaxWeight - BLOCK_FULL_ENOUGH_WEIGHT_DELTA) {
+            if (nConsecutiveFailed > MAX_CONSECUTIVE_FAILURES && nBlockWeight +
+                    BLOCK_FULL_ENOUGH_WEIGHT_DELTA > m_options.nBlockMaxWeight) {
                 // Give up if we're close to full and haven't succeeded in a while
                 break;
             }
```
