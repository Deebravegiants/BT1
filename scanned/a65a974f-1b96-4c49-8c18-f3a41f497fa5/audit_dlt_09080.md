# [?] fix(core): avoid panic on sentinel glyph lookup

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-08-31
Source: https://github.com/trezor/trezor-firmware/commit/79d2aa737a56e5850e74430aff290f54932ee136
Type: security-commit

## Details
fix(core): avoid panic on sentinel glyph lookup

[no changelog]

## Patch
### core/embed/rust/src/translations/blob.rs
```diff
@@ -196,7 +196,9 @@ impl<'a> Table<'a> {
             .ok()
             .and_then(|idx| {
                 let start = self.offsets[idx].offset.into();
-                let end = self.offsets[idx + 1].offset.into();
+                // When `id` is the sentinel, `idx` is the last entry and there
+                // is no next offset to read - return None instead of panicking.
+                let end = self.offsets.get(idx + 1)?.offset.into();
                 self.data.get(start..end)
             })
     }
@@ -682,4 +684,24 @@ mod tests {
         }
         assert_eq!(ENGLISH_CHUNK.get(ENGLISH_CHUNK.len()), None);
     }
+
+    #[test]
+    fn test_table_get() {
+        // Table layout: u16 count, (count + 1) packed (u16 id, u16 offset)
+        // entries (the last one being the sentinel), then the data.
+        let bytes: &[u8] = &[
+            2, 0, // entry count
+            1, 0, 0, 0, // id 1, offset 0
+            2, 0, 3, 0, // id 2, offset 3
+            0xFF, 0xFF, 6, 0, // sentinel id, offset 6
+            b'a', b'b', b'c', b'd', b'e', b'f',
+        ];
+        let table = Table::new(InputStream::new(bytes)).expect("valid table");
+        table.validate().expect("valid table");
+        assert_eq!(table.get(1), Some(&b"abc"[..]));
+        assert_eq!(table.get(2), Some(&b"def"[..]));
+        assert_eq!(table.get(3), None);
+        // Asking for the sentinel id must not panic and must return None.
+        assert_eq!(table.get(SENTINEL_ID), None);
+    }
 }
```
