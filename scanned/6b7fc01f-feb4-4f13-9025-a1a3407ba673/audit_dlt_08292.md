# [?] fix memory corruption

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-05-01
Source: https://github.com/firedancer-io/firedancer/commit/3c1ebdecbbccc8168bcfba3c31bdd7891b46bbee
Type: security-commit

## Details
fix memory corruption

## Patch
### src/flamenco/runtime/tests/harness/fd_types_harness.c
```diff
@@ -335,6 +335,7 @@ fd_runtime_fuzz_type_run( fd_runtime_fuzz_runner_t * runner,
     ulong serialized_sz = *(ulong*)temp_buffer;
 
     // Allocate and copy the representation (serialized data)
+    _l += decoded_sz;
     effects->representation = FD_SCRATCH_ALLOC_APPEND(l, alignof(pb_bytes_array_t),
                                                     PB_BYTES_ARRAY_T_ALLOCSIZE(serialized_sz));
     if( FD_UNLIKELY( _l > output_end ) ) {
```
