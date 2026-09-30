# [?] enclave: Fix a buffer overflow

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2021-06-07
Source: https://github.com/Phala-Network/phala-blockchain/commit/47e09597fb680d2de1d44e2c5434982e1bf3c489
Type: security-commit

## Details
enclave: Fix a buffer overflow

## Patch
### standalone/pruntime/enclave/src/lib.rs
```diff
@@ -768,7 +768,7 @@ pub extern "C" fn ecall_handle(
         ptr::copy_nonoverlapping(
             output_json_vec_len_ptr,
             output_len_ptr,
-            std::mem::size_of_val(&output_json_vec_len),
+            1,
         );
     }
 
```
