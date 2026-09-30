# [?] fix: potential verifier panic in `unzip_and_prefix_sums` (#2536)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2026-02-02
Source: https://github.com/succinctlabs/sp1/commit/8ee332966622f4a50af536c0edb3eecd280c86c3
Type: security-commit

## Details
fix: potential verifier panic in `unzip_and_prefix_sums` (#2536)

Co-authored-by: Tamir Hemo <tamir@succinct.xyz>

## Patch
### slop/crates/jagged/src/verifier.rs
```diff
@@ -125,6 +125,11 @@ impl<GC: IopCtx, Verifier: MultilinearPcsVerifier<GC>> JaggedPcsVerifier<GC, Ver
             log_m,
         } = proof;
 
+        // Each round must have at least one table committed to.
+        if row_counts_and_column_counts.iter().any(|rc_cc| rc_cc.is_empty()) {
+            return Err(JaggedPcsVerifierError::IncorrectShape);
+        }
+
         let PrefixSumsMaxLogRowCount {
             row_counts,
             column_counts,
```
