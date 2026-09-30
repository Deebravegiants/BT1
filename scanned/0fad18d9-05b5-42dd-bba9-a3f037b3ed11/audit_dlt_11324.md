# [?] fix: don't panic when shifting too much (#7429)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-02-20
Source: https://github.com/noir-lang/noir/commit/50733708b0a7312c74229601a76f68afe1737b1d
Type: security-commit

## Details
fix: don't panic when shifting too much (#7429)

## Patch
### compiler/noirc_evaluator/Cargo.toml
```diff
@@ -20,6 +20,7 @@ fxhash.workspace = true
 iter-extended.workspace = true
 thiserror.workspace = true
 num-bigint = "0.4"
+num-traits.workspace = true
 im.workspace = true
 serde.workspace = true
 serde_json.workspace = true
```

### compiler/noirc_evaluator/src/ssa/ir/instruction/binary.rs
```diff
@@ -1,4 +1,5 @@
 use acvm::{acir::AcirField, FieldElement};
+use num_traits::ToPrimitive as _;
 use serde::{Deserialize, Serialize};
 
 use super::{
@@ -578,8 +579,8 @@ impl BinaryOp {
             BinaryOp::Xor => |x, y| Some(x ^ y),
             BinaryOp::Eq => |x, y| Some((x == y) as u128),
             BinaryOp::Lt => |x, y| Some((x < y) as u128),
-            BinaryOp::Shl => |x, y| Some(x << y),
-            BinaryOp::Shr => |x, y| Some(x >> y),
+            BinaryOp::Shl => |x, y| y.to_u32().and_then(|y| x.checked_shl(y)),
+            BinaryOp::Shr => |x, y| y.to_u32().and_then(|y| x.checked_shr(y)),
         }
     }
 
@@ -595,8 +596,8 @@ impl BinaryOp {
             BinaryOp::Xor => |x, y| Some(x ^ y),
             BinaryOp::Eq => |x, y| Some((x == y) as i128),
             BinaryOp::Lt => |x, y| Some((x < y) as i128),
-            BinaryOp::Shl => |x, y| Some(x << y),
-            BinaryOp::Shr => |x, y| Some(x >> y),
+            BinaryOp::Shl => |x, y| y.to_u32().and_then(|y| x.checked_shl(y)),
+            BinaryOp::Shr => |x, y| y.to_u32().and_then(|y| x.checked_shr(y)),
         }
     }
 
@@ -625,7 +626,7 @@ mod test {
 
     use super::{
         convert_signed_integer_to_field_element, truncate_field,
-        try_convert_field_element_to_signed_integer,
+        try_convert_field_element_to_signed_integer, BinaryOp,
     };
     use acvm::{AcirField, FieldElement};
     use num_bigint::BigUint;
@@ -653,6 +654,17 @@ mod test {
             let truncated_as_bigint = FieldElement::from_be_bytes_reduce(&truncated_as_bigint.to_bytes_be());
             prop_assert_eq!(truncated_as_field, truncated_as_bigint);
         }
+    }
+
+    #[test]
+    fn get_u128_function_shift_works_with_values_larger_than_127() {
+        assert!(BinaryOp::Shr.get_u128_function()(1, 128).is_none());
+        assert!(BinaryOp::Shl.get_u128_function()(1, 128).is_none());
+    }
 
+    #[test]
+    fn get_i128_function_shift_works_with_values_larger_than_127() {
+        assert!(BinaryOp::Shr.get_i128_function()(1, 128).is_none());
+        assert!(BinaryOp::Shl.get_i128_function()(1, 128).is_none());
     }
 }
```
