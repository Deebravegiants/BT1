# [?] Fix out-of-bounds read in path_advance_in_struct (scan-build ArrayBound)

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-08-11
Source: https://github.com/LedgerHQ/app-ethereum/commit/7dafff5088ccc7f5a618dc748931b8473643d223
Type: security-commit

## Details
Fix out-of-bounds read in path_advance_in_struct (scan-build ArrayBound)

Two issues in the same function:
1. path_struct was NULL-checked after being dereferenced at depth pointer
   computation.
2. depth_count - 1 underflows to 255 when depth_count == 0 (uint8_t),
   producing an out-of-bounds pointer before the depth_count > 0 guard.

Fix: move NULL check first; move depth pointer computation inside the
depth_count > 0 guard so it is only evaluated when safe.

## Patch
### src/features/sign_message_eip712/path.c
```diff
@@ -638,7 +638,6 @@ bool path_new_array_depth(const uint8_t *data, uint8_t length) {
  */
 static bool path_advance_in_struct(void) {
     bool end_reached = true;
-    uint8_t *depth = &path_struct->depths[path_struct->depth_count - 1];
     uint8_t fields_count;
 
     if (path_struct == NULL) {
@@ -648,6 +647,7 @@ static bool path_advance_in_struct(void) {
         return false;
     }
     if (path_struct->depth_count > 0) {
+        uint8_t *depth = &path_struct->depths[path_struct->depth_count - 1];
         *depth += 1;
         end_reached = (*depth == fields_count);
     }
```
