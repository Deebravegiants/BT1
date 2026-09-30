# [?] Use DoS level constants and parameters for ZIP 213 rejections

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2020-03-05
Source: https://github.com/zcash/zcash/commit/743a5f437feab5bd020a03a1e501338c80c55817
Type: security-commit

## Details
Use DoS level constants and parameters for ZIP 213 rejections

## Patch
### src/main.cpp
```diff
@@ -893,8 +893,10 @@ bool ContextualCheckTransaction(
         if (tx.IsCoinBase()) {
             // A coinbase transaction cannot have output descriptions
             if (tx.vShieldedOutput.size() > 0)
-                return state.DoS(100, error("CheckTransaction(): coinbase has output descriptions"),
-                                REJECT_INVALID, "bad-cb-has-output-description");
+                return state.DoS(
+                    dosLevelPotentiallyRelaxing,
+                    error("CheckTransaction(): coinbase has output descriptions"),
+                    REJECT_INVALID, "bad-cb-has-output-description");
         }
     }
 
@@ -910,7 +912,7 @@ bool ContextualCheckTransaction(
                     output.outCiphertext, ovk, output.cv, output.cmu, output.ephemeralKey);
                 if (!outPlaintext) {
                     return state.DoS(
-                        100,
+                        DOS_LEVEL_BLOCK,
                         error("CheckTransaction(): coinbase output description has invalid outCiphertext"),
                         REJECT_INVALID,
                         "bad-cb-output-desc-invalid-outct");
@@ -925,7 +927,7 @@ bool ContextualCheckTransaction(
                     output.cmu)
                 ) {
                     return state.DoS(
-                        100,
+                        DOS_LEVEL_BLOCK,
                         error("CheckTransaction(): coinbase output description has invalid encCiphertext"),
                         REJECT_INVALID,
                         "bad-cb-output-desc-invalid-encct");
```
