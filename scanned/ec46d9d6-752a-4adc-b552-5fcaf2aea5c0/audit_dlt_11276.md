# [?] fix(frontend): No negative overflow when quoting signed integer (#10331)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-11-12
Source: https://github.com/noir-lang/noir/commit/794b685f77ec3b4c1c885c4131ee7792e949511d
Type: security-commit

## Details
fix(frontend): No negative overflow when quoting signed integer (#10331)

Co-authored-by: Jake Fecher <jfecher11@gmail.com>

## Patch
### compiler/noirc_frontend/src/hir/comptime/value.rs
```diff
@@ -578,7 +578,10 @@ impl Value {
                 if value < 0 {
                     vec![
                         Token::Minus,
-                        Token::Int((-value as u128).into(), Some(IntegerTypeSuffix::I8)),
+                        Token::Int(
+                            u128::from(value.unsigned_abs()).into(),
+                            Some(IntegerTypeSuffix::I8),
+                        ),
                     ]
                 } else {
                     vec![Token::Int((value as u128).into(), Some(IntegerTypeSuffix::I8))]
@@ -588,7 +591,10 @@ impl Value {
                 if value < 0 {
                     vec![
                         Token::Minus,
-                        Token::Int((-value as u128).into(), Some(IntegerTypeSuffix::I16)),
+                        Token::Int(
+                            u128::from(value.unsigned_abs()).into(),
+                            Some(IntegerTypeSuffix::I16),
+                        ),
                     ]
                 } else {
                     vec![Token::Int((value as u128).into(), Some(IntegerTypeSuffix::I16))]
@@ -598,7 +604,10 @@ impl Value {
                 if value < 0 {
                     vec![
                         Token::Minus,
-                        Token::Int((-value as u128).into(), Some(IntegerTypeSuffix::I32)),
+                        Token::Int(
+                            u128::from(value.unsigned_abs()).into(),
+                            Some(IntegerTypeSuffix::I32),
+                        ),
                     ]
                 } else {
                     vec![Token::Int((value as u128).into(), Some(IntegerTypeSuffix::I32))]
@@ -608,7 +617,10 @@ impl Value {
                 if value < 0 {
                     vec![
                         Token::Minus,
-                        Token::Int((-value as u128).into(), Some(IntegerTypeSuffix::I64)),
+                        Token::Int(
+                            u128::from(value.unsigned_abs()).into(),
+                            Some(IntegerTypeSuffix::I64),
+                        ),
                     ]
                 } else {
                     vec![Token::Int((value as u128).into(), Some(IntegerTypeSuffix::I64))]
```

### compiler/noirc_frontend/src/tests/meta_quote_roundtrip.rs
```diff
@@ -73,27 +73,29 @@ proptest! {
         assert_no_errors(&src);
     }
 
-    // TODO(https://github.com/noir-lang/noir/issues/10328): Although it is a very low chance, all these tests have the possibility to be flakey
-    // #[test]
-    // fn roundtrip_i8_values(n in any::<i8>()) {
-    //     let src = make_roundtrip_test("i8", n.to_string());
-    //     assert_no_errors(&src);
-    // }
-    // #[test]
-    // fn roundtrip_i16_values(n in any::<i16>()) {
-    //     let src = make_roundtrip_test("i16", n.to_string());
-    //     assert_no_errors(&src);
-    // }
-    // #[test]
-    // fn roundtrip_i32_values(n in any::<i32>()) {
-    //     let src = make_roundtrip_test("i32", n.to_string());
-    //     assert_no_errors(&src);
-    // }
-    // #[test]
-    // fn roundtrip_i64_values(n in any::<i64>()) {
-    //     let src = make_roundtrip_test("i64", n.to_string());
-    //     assert_no_errors(&src);
-    // }
+    #[test]
+    fn roundtrip_i8_values(n in any::<i8>()) {
+        let src = make_roundtrip_test("i8", n.to_string());
+        assert_no_errors(&src);
+    }
+
+    #[test]
+    fn roundtrip_i16_values(n in any::<i16>()) {
+        let src = make_roundtrip_test("i16", n.to_string());
+        assert_no_errors(&src);
+    }
+
+    #[test]
+    fn roundtrip_i32_values(n in any::<i32>()) {
+        let src = make_roundtrip_test("i32", n.to_string());
+        assert_no_errors(&src);
+    }
+
+    #[test]
+    fn roundtrip_i64_values(n in any::<i64>()) {
+        let src = make_roundtrip_test("i64", n.to_string());
+        assert_no_errors(&src);
+    }
 }
 
 #[test]
@@ -102,9 +104,7 @@ fn roundtrip_zero_field() {
     assert_no_errors(&src);
 }
 
-// TODO(https://github.com/noir-lang/noir/issues/10328)
 #[test]
-#[ignore]
 fn roundtrip_i64_min() {
     let src = make_roundtrip_test("i64", i64::MIN.to_string());
     assert_no_errors(&src);
```
