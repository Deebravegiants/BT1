# [?] Fix overflow in `debug` mode

## Summary
Severity: Unknown
Chain: ZK
Component: arkworks-rs/algebra
Published: 2020-12-30
Source: https://github.com/arkworks-rs/algebra/commit/852cf26aa702fea3005bcf8272b1e7f53fa31d80
Type: security-commit

## Details
Fix overflow in `debug` mode

## Patch
### ff/src/fields/macros.rs
```diff
@@ -328,7 +328,7 @@ macro_rules! impl_Fp {
                     let last_bytes = &mut result_bytes[8 * ($limbs - 1)..];
 
                     // The mask only has the last `F::BIT_SIZE` bits set
-                    let flags_mask = u8::MAX << (8 - F::BIT_SIZE);
+                    let flags_mask = u8::MAX.checked_shl(8 - (F::BIT_SIZE as u32)).unwrap_or(0);
 
                     // Mask away the remaining bytes, and try to reconstruct the
                     // flag
```
