# [?] fix: prevent `SignedField::from(i128::MIN)` from crashing (#9366)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-07-31
Source: https://github.com/noir-lang/noir/commit/9846e1ebd6264ae33f23195c0aa6ccff6947692f
Type: security-commit

## Details
fix: prevent `SignedField::from(i128::MIN)` from crashing (#9366)

## Patch
### compiler/noirc_frontend/src/signed_field.rs
```diff
@@ -219,7 +219,13 @@ impl From<u128> for SignedField {
 
 impl From<i128> for SignedField {
     fn from(value: i128) -> Self {
-        if value < 0 { Self::new((-value).into(), true) } else { Self::new(value.into(), false) }
+        if value == i128::MIN {
+            Self::new(FieldElement::from((i128::MAX as u128) + 1), true)
+        } else if value < 0 {
+            Self::new((-value).into(), true)
+        } else {
+            Self::new(value.into(), false)
+        }
     }
 }
 
@@ -423,4 +429,11 @@ mod tests {
             i128::MIN
         );
     }
+
+    #[test]
+    fn from_i128() {
+        assert_eq!(SignedField::from(i128::MAX).to_i128(), i128::MAX);
+        assert_eq!(SignedField::from(i128::MIN).to_i128(), i128::MIN);
+        assert_eq!(SignedField::from(i128::MIN + 1).to_i128(), i128::MIN + 1);
+    }
 }
```
