# [?] shred: fix overflow in shred filter (#11608)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-03-28
Source: https://github.com/anza-xyz/agave/commit/800907b932e92c39b1869647642c729d97799930
Type: security-commit

## Details
shred: fix overflow in shred filter (#11608)

## Patch
### ledger/src/shred.rs
```diff
@@ -845,8 +845,11 @@ where
                 return true;
             };
 
+            let expected_data_complete_index = fec_set_index
+                .checked_add(DATA_SHREDS_PER_FEC_BLOCK as u32)
+                .and_then(|index| index.checked_sub(1));
             if shred_flags.contains(ShredFlags::DATA_COMPLETE_SHRED)
-                && index != fec_set_index + DATA_SHREDS_PER_FEC_BLOCK as u32 - 1
+                && (expected_data_complete_index != Some(index))
             {
                 stats.unexpected_data_complete_shred += 1;
 
@@ -887,8 +890,12 @@ where
 /// - `index` is between `fec_set_index` and `fec_set_index + DATA_SHREDS_PER_FEC_BLOCK`
 /// - `fec_set_index` is a multiple of `DATA_SHREDS_PER_FEC_BLOCK`
 fn check_fixed_fec_set(index: u32, fec_set_index: u32) -> bool {
+    let Some(fec_set_end_exclusive) = fec_set_index.checked_add(DATA_SHREDS_PER_FEC_BLOCK as u32)
+    else {
+        return false;
+    };
     index >= fec_set_index
-        && index < fec_set_index + DATA_SHREDS_PER_FEC_BLOCK as u32
+        && index < fec_set_end_exclusive
         && fec_set_index.is_multiple_of(DATA_SHREDS_PER_FEC_BLOCK as u32)
 }
 
```
