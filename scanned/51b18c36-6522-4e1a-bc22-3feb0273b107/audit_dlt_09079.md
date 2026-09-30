# [?] fix(core): avoid underflow in offset validation

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-08-31
Source: https://github.com/trezor/trezor-firmware/commit/fa008a3bc6cb4f02435a6d5c00841862dcaefedf
Type: security-commit

## Details
fix(core): avoid underflow in offset validation

[no changelog]

## Patch
### core/embed/rust/src/translations/blob.rs
```diff
@@ -53,7 +53,8 @@ fn validate_offset_table(
     // sentinel needs to be at least data_len - MAX_TABLE_PADDING, and at most
     // data_len
     let sentinel: usize = prev.into();
-    if sentinel < data_len - MAX_TABLE_PADDING || sentinel > data_len {
+    // saturating_sub: data_len can be smaller than MAX_TABLE_PADDING
+    if sentinel < data_len.saturating_sub(MAX_TABLE_PADDING) || sentinel > data_len {
         return Err(INVALID_TRANSLATIONS_BLOB);
     }
     Ok(())
@@ -704,4 +705,24 @@ mod tests {
         // Asking for the sentinel id must not panic and must return None.
         assert_eq!(table.get(SENTINEL_ID), None);
     }
+
+    #[test]
+    fn test_validate_offset_table_small_data() {
+        // data_len smaller than MAX_TABLE_PADDING must not underflow
+        // (overflow-checked builds would panic).
+        assert!(validate_offset_table(0, core::iter::once(0)).is_ok());
+        assert!(validate_offset_table(1, core::iter::once(0)).is_ok());
+        assert!(validate_offset_table(2, core::iter::once(0)).is_ok());
+        assert!(validate_offset_table(3, core::iter::once(0)).is_ok());
+        assert!(validate_offset_table(4, core::iter::once(0)).is_err());
+        assert!(validate_offset_table(5, core::iter::once(0)).is_err());
+        // sentinel pointing beyond the data is still rejected
+        assert!(validate_offset_table(0, [0, 1].into_iter()).is_err());
+        assert!(validate_offset_table(1, [0, 1].into_iter()).is_ok());
+        assert!(validate_offset_table(2, [0, 1].into_iter()).is_ok());
+        assert!(validate_offset_table(3, [0, 1].into_iter()).is_ok());
+        assert!(validate_offset_table(4, [0, 1].into_iter()).is_ok());
+        assert!(validate_offset_table(5, [0, 1].into_iter()).is_err());
+        assert!(validate_offset_table(6, [0, 1].into_iter()).is_err());
+    }
 }
```
