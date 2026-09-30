# [?] fix: do not crash on invalid strings (#10739)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-12-02
Source: https://github.com/noir-lang/noir/commit/00eadc5b94f900fac3eede72d9024d61086329f4
Type: security-commit

## Details
fix: do not crash on invalid strings (#10739)

## Patch
### compiler/noirc_printable_type/src/lib.rs
```diff
@@ -500,7 +500,7 @@ pub fn decode_string_value<F: AcirField>(field_elements: &[F]) -> String {
         char_byte
     });
 
-    let final_string = str::from_utf8(&string_as_slice).unwrap();
+    let final_string = String::from_utf8_lossy(&string_as_slice).to_string();
     final_string.to_owned()
 }
 
@@ -711,6 +711,21 @@ mod tests {
         assert_eq!(string.unwrap(), "(0x01, 0x02)");
     }
 
+    // Test for issue: https://github.com/noir-lang/noir/issues/10710
+    #[test]
+    fn invalid_string() {
+        use super::decode_string_value;
+        let field_elements: Vec<FieldElement> = vec![
+            FieldElement::from(255_u128),
+            FieldElement::from(255_u128),
+            FieldElement::from(255_u128),
+        ];
+
+        // [255, 255, 255] is not valid UTF-8, and is converted using replacement char.
+        let result = decode_string_value(&field_elements);
+        assert_eq!(result, "���");
+    }
+
     proptest! {
         #[test]
         fn handles_decoding_u128_values(uint_value: u128) {
```
