# [?] fix: check for overflow with hexadecimal inputs (#3004)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2023-10-06
Source: https://github.com/noir-lang/noir/commit/db1e736240c0b74f6f59504db5a50de1c749d395
Type: security-commit

## Details
fix: check for overflow with hexadecimal inputs (#3004)

## Patch
### tooling/noirc_abi/src/input_parser/mod.rs
```diff
@@ -194,48 +194,46 @@ mod serialization_tests {
 }
 
 fn parse_str_to_field(value: &str) -> Result<FieldElement, InputParserError> {
-    if value.starts_with("0x") {
-        FieldElement::from_hex(value).ok_or_else(|| InputParserError::ParseHexStr(value.to_owned()))
+    let big_num = if let Some(hex) = value.strip_prefix("0x") {
+        BigUint::from_str_radix(hex, 16)
     } else {
         BigUint::from_str_radix(value, 10)
-            .map_err(|err_msg| InputParserError::ParseStr(err_msg.to_string()))
-            .and_then(|bigint| {
-                if bigint < FieldElement::modulus() {
-                    Ok(field_from_big_uint(bigint))
-                } else {
-                    Err(InputParserError::ParseStr(format!(
-                        "Input exceeds field modulus. Values must fall within [0, {})",
-                        FieldElement::modulus(),
-                    )))
-                }
-            })
-    }
+    };
+    big_num.map_err(|err_msg| InputParserError::ParseStr(err_msg.to_string())).and_then(|bigint| {
+        if bigint < FieldElement::modulus() {
+            Ok(field_from_big_uint(bigint))
+        } else {
+            Err(InputParserError::ParseStr(format!(
+                "Input exceeds field modulus. Values must fall within [0, {})",
+                FieldElement::modulus(),
+            )))
+        }
+    })
 }
 
 fn parse_str_to_signed(value: &str, witdh: u32) -> Result<FieldElement, InputParserError> {
-    if value.starts_with("0x") {
-        FieldElement::from_hex(value).ok_or_else(|| InputParserError::ParseHexStr(value.to_owned()))
+    let big_num = if let Some(hex) = value.strip_prefix("0x") {
+        BigInt::from_str_radix(hex, 16)
     } else {
         BigInt::from_str_radix(value, 10)
-            .map_err(|err_msg| InputParserError::ParseStr(err_msg.to_string()))
-            .and_then(|bigint| {
-                let modulus: BigInt = FieldElement::modulus().into();
-                let bigint = if bigint.sign() == num_bigint::Sign::Minus {
-                    BigInt::from(2).pow(witdh) + bigint
-                } else {
-                    bigint
-                };
-                if bigint.is_zero() || (bigint.sign() == num_bigint::Sign::Plus && bigint < modulus)
-                {
-                    Ok(field_from_big_int(bigint))
-                } else {
-                    Err(InputParserError::ParseStr(format!(
-                        "Input exceeds field modulus. Values must fall within [0, {})",
-                        FieldElement::modulus(),
-                    )))
-                }
-            })
-    }
+    };
+
+    big_num.map_err(|err_msg| InputParserError::ParseStr(err_msg.to_string())).and_then(|bigint| {
+        let modulus: BigInt = FieldElement::modulus().into();
+        let bigint = if bigint.sign() == num_bigint::Sign::Minus {
+            BigInt::from(2).pow(witdh) + bigint
+        } else {
+            bigint
+        };
+        if bigint.is_zero() || (bigint.sign() == num_bigint::Sign::Plus && bigint < modulus) {
+            Ok(field_from_big_int(bigint))
+        } else {
+            Err(InputParserError::ParseStr(format!(
+                "Input exceeds field modulus. Values must fall within [0, {})",
+                FieldElement::modulus(),
+            )))
+        }
+    })
 }
 
 fn field_from_big_uint(bigint: BigUint) -> FieldElement {
```
