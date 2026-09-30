# [?] Fix panic code generation. (#6305)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2024-08-28
Source: https://github.com/starkware-libs/cairo/commit/19fe99acdd97ef77bfd70f4d3381498053f49cf1
Type: security-commit

## Details
Fix panic code generation. (#6305)

## Patch
### crates/cairo-lang-semantic/src/expr/expansion_test_data/inline_macros
```diff
@@ -107,7 +107,7 @@ test_expand_expr(expect_diagnostics: false)
 panic!()
 
 //! > expanded_code
-core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, 0, 0)
+core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, 0, 0])
 
 //! > diagnostics
 
@@ -122,7 +122,7 @@ test_expand_expr(expect_diagnostics: false)
 panic!("0123456")
 
 //! > expanded_code
-core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, 0x30313233343536, 7)
+core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, 0x30313233343536, 7])
 
 //! > diagnostics
 
@@ -137,7 +137,7 @@ test_expand_expr(expect_diagnostics: false)
 panic!("0123456789012345678901234567890")
 
 //! > expanded_code
-core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 1, 0x30313233343536373839303132333435363738393031323334353637383930, 0, 0)
+core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 1, 0x30313233343536373839303132333435363738393031323334353637383930, 0, 0])
 
 //! > diagnostics
 
@@ -152,7 +152,7 @@ test_expand_expr(expect_diagnostics: false)
 panic!("01234567890123456789012345678901234")
 
 //! > expanded_code
-core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 1, 0x30313233343536373839303132333435363738393031323334353637383930, 0x31323334, 4)
+core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 1, 0x30313233343536373839303132333435363738393031323334353637383930, 0x31323334, 4])
 
 //! > diagnostics
 
```

### crates/cairo-lang-semantic/src/inline_macros/panic.rs
```diff
@@ -23,7 +23,7 @@ fn try_handle_simple_panic(
         [] => {
             // Trivial panic!() with no arguments case.
             builder.add_str(
-                "core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, 0, 0);",
+                "core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, 0, 0]);",
             );
             return true;
         }
@@ -60,10 +60,10 @@ fn try_handle_simple_panic(
         // Adding the empty remainder word.
         builder.add_str("0, ");
     }
-    builder.add_str(&format!("{remainder_size}))"));
+    builder.add_str(&format!("{remainder_size}]))"));
 
     builder.add_str(&format!(
-        "core::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, '{}', {}",
+        "core::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, '{}', {}])",
         format_str,
         format_str.len()
     ));
```
