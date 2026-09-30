# [?] Fix underflow in verify_indexed_attestation

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2019-05-23
Source: https://github.com/sigp/lighthouse/commit/55ef75a44eb17bf5ecf6737ccf8f6e5987598993
Type: security-commit

## Details
Fix underflow in verify_indexed_attestation

## Patch
### eth2/state_processing/src/per_block_processing/verify_indexed_attestation.rs
```diff
@@ -62,11 +62,13 @@ fn verify_indexed_attestation_parametric<T: EthSpec>(
 
     // Check that both vectors of indices are sorted
     let check_sorted = |list: &Vec<u64>| {
-        for i in 0..list.len() - 1 {
-            if list[i] >= list[i + 1] {
+        list.windows(2).enumerate().try_for_each(|(i, pair)| {
+            if pair[0] >= pair[1] {
                 invalid!(Invalid::BadValidatorIndicesOrdering(i));
+            } else {
+                Ok(())
             }
-        }
+        })?;
         Ok(())
     };
     check_sorted(custody_bit_0_indices)?;
```
