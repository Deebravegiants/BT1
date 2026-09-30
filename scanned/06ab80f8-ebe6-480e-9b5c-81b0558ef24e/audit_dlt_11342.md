# [?] fix: correct range for overlfowing/underflowing integer assignment (#5416)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-07-05
Source: https://github.com/noir-lang/noir/commit/30c50f52a6d58163e39006b73f4eb5003afc239b
Type: security-commit

## Details
fix: correct range for overlfowing/underflowing integer assignment (#5416)

# Description

## Problem

Resolves #5419

## Summary

This is similar to #5372, except that here the compiler does an early
check with explicitly annotated types, and in the related issue the
check is done later on, once unknown types are resolved.

Also in this PR:
- a test was moved from `test_programs` to `noirc_frontend/src/tests.rs`
because the error produced here can be caught there
- the error message produced in both places is now exactly the same
(showing the possible range of values, which helps to know why you
exceeded the min/max)

## Additional Context

None

## Documentation

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_evaluator/src/errors.rs
```diff
@@ -23,8 +23,13 @@ pub enum RuntimeError {
     IndexOutOfBounds { index: usize, array_size: usize, call_stack: CallStack },
     #[error("Range constraint of {num_bits} bits is too large for the Field size")]
     InvalidRangeConstraint { num_bits: u32, call_stack: CallStack },
-    #[error("{value} does not fit within the type bounds for {typ}")]
-    IntegerOutOfBounds { value: FieldElement, typ: NumericType, call_stack: CallStack },
+    #[error("The value `{value:?}` cannot fit into `{typ}` which has range `{range}`")]
+    IntegerOutOfBounds {
+        value: FieldElement,
+        typ: NumericType,
+        range: String,
+        call_stack: CallStack,
+    },
     #[error("Expected array index to fit into a u64")]
     TypeConversion { from: String, into: String, call_stack: CallStack },
     #[error("{name:?} is not initialized")]
```

### compiler/noirc_evaluator/src/ssa/ir/types.rs
```diff
@@ -29,23 +29,37 @@ impl NumericType {
         }
     }
 
-    /// Returns true if the given Field value is within the numeric limits
-    /// for the current NumericType.
-    pub(crate) fn value_is_within_limits(self, field: FieldElement, negative: bool) -> bool {
+    /// Returns None if the given Field value is within the numeric limits
+    /// for the current NumericType. Otherwise returns a string describing
+    /// the limits, as a range.
+    pub(crate) fn value_is_outside_limits(
+        self,
+        field: FieldElement,
+        negative: bool,
+    ) -> Option<String> {
         match self {
             NumericType::Unsigned { bit_size } => {
+                let max = 2u128.pow(bit_size) - 1;
                 if negative {
-                    return false;
+                    return Some(format!("0..={}", max));
+                }
+                if field <= max.into() {
+                    None
+                } else {
+                    Some(format!("0..={}", max))
                 }
-                let max = 2u128.pow(bit_size) - 1;
-                field <= max.into()
             }
             NumericType::Signed { bit_size } => {
-                let max =
-                    if negative { 2u128.pow(bit_size - 1) } else { 2u128.pow(bit_size - 1) - 1 };
-                field <= max.into()
+                let min = 2u128.pow(bit_size - 1);
+                let max = 2u128.pow(bit_size - 1) - 1;
+                let target_max = if negative { min } else { max };
+                if field <= target_max.into() {
+                    None
+                } else {
+                    Some(format!("-{}..={}", min, max))
+                }
             }
-            NumericType::NativeField => true,
+            NumericType::NativeField => None,
         }
     }
 }
@@ -224,21 +238,21 @@ mod tests {
     use super::*;
 
     #[test]
-    fn test_u8_is_within_limits() {
+    fn test_u8_value_is_outside_limits() {
         let u8 = NumericType::Unsigned { bit_size: 8 };
-        assert!(!u8.value_is_within_limits(FieldElement::from(1_i128), true));
-        assert!(u8.value_is_within_limits(FieldElement::from(0_i128), false));
-        assert!(u8.value_is_within_limits(FieldElement::from(255_i128), false));
-        assert!(!u8.value_is_within_limits(FieldElement::from(256_i128), false));
+        assert!(u8.value_is_outside_limits(FieldElement::from(1_i128), true).is_some());
+        assert!(u8.value_is_outside_limits(FieldElement::from(0_i128), false).is_none());
+        assert!(u8.value_is_outside_limits(FieldElement::from(255_i128), false).is_none());
+        assert!(u8.value_is_outside_limits(FieldElement::from(256_i128), false).is_some());
     }
 
     #[test]
-    fn test_i8_is_within_limits() {
+    fn test_i8_value_is_outside_limits() {
         let i8 = NumericType::Signed { bit_size: 8 };
-        assert!(!i8.value_is_within_limits(FieldElement::from(129_i128), true));
-        assert!(i8.value_is_within_limits(FieldElement::from(128_i128), true));
-        assert!(i8.value_is_within_limits(FieldElement::from(0_i128), false));
-        assert!(i8.value_is_within_limits(FieldElement::from(127_i128), false));
-        assert!(!i8.value_is_within_limits(FieldElement::from(128_i128), false));
+        assert!(i8.value_is_outside_limits(FieldElement::from(129_i128), true).is_some());
+        assert!(i8.value_is_outside_limits(FieldElement::from(128_i128), true).is_none());
+        assert!(i8.value_is_outside_limits(FieldElement::from(0_i128), false).is_none());
+        assert!(i8.value_is_outside_limits(FieldElement::from(127_i128), false).is_none());
+        assert!(i8.value_is_outside_limits(FieldElement::from(128_i128), false).is_some());
     }
 }
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/context.rs
```diff
@@ -272,11 +272,12 @@ impl<'a> FunctionContext<'a> {
         let value = value.into();
 
         if let Type::Numeric(numeric_type) = typ {
-            if !numeric_type.value_is_within_limits(value, negative) {
+            if let Some(range) = numeric_type.value_is_outside_limits(value, negative) {
                 let call_stack = self.builder.get_call_stack();
                 return Err(RuntimeError::IntegerOutOfBounds {
-                    value,
+                    value: if negative { -value } else { value },
                     typ: numeric_type,
+                    range,
                     call_stack,
                 });
             }
```

### compiler/noirc_frontend/src/elaborator/lints.rs
```diff
@@ -7,13 +7,12 @@ use crate::{
     },
     hir_def::expr::HirIdent,
     macros_api::{
-        HirExpression, HirLiteral, NodeInterner, NoirFunction, UnaryOp, UnresolvedTypeData,
-        Visibility,
+        HirExpression, HirLiteral, NodeInterner, NoirFunction, Signedness, UnaryOp,
+        UnresolvedTypeData, Visibility,
     },
     node_interner::{DefinitionKind, ExprId, FuncId},
     Type,
 };
-use acvm::AcirField;
 
 use noirc_errors::Span;
 
@@ -196,8 +195,8 @@ pub(super) fn unnecessary_pub_argument(
 }
 
 /// Check if an assignment is overflowing with respect to `annotated_type`
-/// in a declaration statement where `annotated_type` is an unsigned integer
-pub(crate) fn overflowing_uint(
+/// in a declaration statement where `annotated_type` is a signed or unsigned integer
+pub(crate) fn overflowing_int(
     interner: &NodeInterner,
     rhs_expr: &ExprId,
     annotated_type: &Type,
@@ -207,23 +206,36 @@ pub(crate) fn overflowing_uint(
 
     let mut errors = Vec::with_capacity(2);
     match expr {
-        HirExpression::Literal(HirLiteral::Integer(value, false)) => {
-            let v = value.to_u128();
-            if let Type::Integer(_, bit_count) = annotated_type {
+        HirExpression::Literal(HirLiteral::Integer(value, negative)) => match annotated_type {
+            Type::Integer(Signedness::Unsigned, bit_count) => {
                 let bit_count: u32 = (*bit_count).into();
-                let max = 1 << bit_count;
-                if v >= max {
+                let max = 2u128.pow(bit_count) - 1;
+                if value > max.into() || negative {
                     errors.push(TypeCheckError::OverflowingAssignment {
-                        expr: value,
+                        expr: if negative { -value } else { value },
                         ty: annotated_type.clone(),
-                        range: format!("0..={}", max - 1),
+                        range: format!("0..={}", max),
                         span,
                     });
-                };
-            };
-        }
+                }
+            }
+            Type::Integer(Signedness::Signed, bit_count) => {
+                let bit_count: u32 = (*bit_count).into();
+                let min = 2u128.pow(bit_count - 1);
+                let max = 2u128.pow(bit_count - 1) - 1;
+                if (negative && value > min.into()) || (!negative && value > max.into()) {
+                    errors.push(TypeCheckError::OverflowingAssignment {
+                        expr: if negative { -value } else { value },
+                        ty: annotated_type.clone(),
+                        range: format!("-{}..={}", min, max),
+                        span,
+                    });
+                }
+            }
+            _ => (),
+        },
         HirExpression::Prefix(expr) => {
-            overflowing_uint(interner, &expr.rhs, annotated_type);
+            overflowing_int(interner, &expr.rhs, annotated_type);
             if expr.operator == UnaryOp::Minus {
                 errors.push(TypeCheckError::InvalidUnaryOp {
                     kind: "annotated_type".to_string(),
@@ -232,8 +244,8 @@ pub(crate) fn overflowing_uint(
             }
         }
         HirExpression::Infix(expr) => {
-            errors.extend(overflowing_uint(interner, &expr.lhs, annotated_type));
-            errors.extend(overflowing_uint(interner, &expr.rhs, annotated_type));
+            errors.extend(overflowing_int(interner, &expr.lhs, annotated_type));
+            errors.extend(overflowing_int(interner, &expr.rhs, annotated_type));
         }
         _ => {}
     }
```

### compiler/noirc_frontend/src/elaborator/statements.rs
```diff
@@ -86,8 +86,8 @@ impl<'context> Elaborator<'context> {
                     expr_span,
                 }
             });
-            if annotated_type.is_unsigned() {
-                let errors = lints::overflowing_uint(self.interner, &expression, &annotated_type);
+            if annotated_type.is_integer() {
+                let errors = lints::overflowing_int(self.interner, &expression, &annotated_type);
                 for error in errors {
                     self.push_err(error);
                 }
```

### compiler/noirc_frontend/src/hir/type_check/errors.rs
```diff
@@ -35,7 +35,7 @@ pub enum Source {
 pub enum TypeCheckError {
     #[error("Operator {op:?} cannot be used in a {place:?}")]
     OpCannotBeUsed { op: HirBinaryOp, place: &'static str, span: Span },
-    #[error("The literal `{expr:?}` cannot fit into `{ty}` which has range `{range}`")]
+    #[error("The value `{expr:?}` cannot fit into `{ty}` which has range `{range}`")]
     OverflowingAssignment { expr: FieldElement, ty: Type, range: String, span: Span },
     #[error("Type {typ:?} cannot be used in a {place:?}")]
     TypeCannotBeUsed { typ: Type, place: &'static str, span: Span },
```

### compiler/noirc_frontend/src/hir/type_check/stmt.rs
```diff
@@ -368,7 +368,7 @@ impl<'interner> TypeChecker<'interner> {
                     let max = 1 << bit_count;
                     if v >= max {
                         self.errors.push(TypeCheckError::OverflowingAssignment {
-                            expr: value,
+                            expr: -value,
                             ty: annotated_type.clone(),
                             range: format!("0..={}", max - 1),
                             span,
```

### compiler/noirc_frontend/src/hir_def/types.rs
```diff
@@ -665,6 +665,10 @@ impl Type {
         matches!(self.follow_bindings(), Type::Bool)
     }
 
+    pub fn is_integer(&self) -> bool {
+        matches!(self.follow_bindings(), Type::Integer(_, _))
+    }
+
     pub fn is_signed(&self) -> bool {
         matches!(self.follow_bindings(), Type::Integer(Signedness::Signed, _))
     }
```

### compiler/noirc_frontend/src/tests.rs
```diff
@@ -1907,3 +1907,79 @@ fn comptime_let() {
     let errors = get_program_errors(src);
     assert_eq!(errors.len(), 0);
 }
+
+#[test]
+fn overflowing_u8() {
+    let src = r#"
+        fn main() {
+            let _: u8 = 256;
+        }"#;
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 1);
+
+    if let CompilationError::TypeError(error) = &errors[0].0 {
+        assert_eq!(
+            error.to_string(),
+            "The value `2⁸` cannot fit into `u8` which has range `0..=255`"
+        );
+    } else {
+        panic!("Expected OverflowingAssignment error, got {:?}", errors[0].0);
+    }
+}
+
+#[test]
+fn underflowing_u8() {
+    let src = r#"
+        fn main() {
+            let _: u8 = -1;
+        }"#;
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 1);
+
+    if let CompilationError::TypeError(error) = &errors[0].0 {
+        assert_eq!(
+            error.to_string(),
+            "The value `-1` cannot fit into `u8` which has range `0..=255`"
+        );
+    } else {
+        panic!("Expected OverflowingAssignment error, got {:?}", errors[0].0);
+    }
+}
+
+#[test]
+fn overflowing_i8() {
+    let src = r#"
+        fn main() {
+            let _: i8 = 128;
+        }"#;
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 1);
+
+    if let CompilationError::TypeError(error) = &errors[0].0 {
+        assert_eq!(
+            error.to_string(),
+            "The value `2⁷` cannot fit into `i8` which has range `-128..=127`"
+        );
+    } else {
+        panic!("Expected OverflowingAssignment error, got {:?}", errors[0].0);
+    }
+}
+
+#[test]
+fn underflowing_i8() {
+    let src = r#"
+        fn main() {
+            let _: i8 = -129;
+        }"#;
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 1);
+
+    if let CompilationError::TypeError(error) = &errors[0].0 {
+        assert_eq!(
+            error.to_string(),
+            "The value `-129` cannot fit into `i8` which has range `-128..=127`"
+        );
+    } else {
+        panic!("Expected OverflowingAssignment error, got {:?}", errors[0].0);
+    }
+}
```

### cspell.json
```diff
@@ -148,6 +148,7 @@
         "nomicfoundation",
         "noncanonical",
         "nouner",
+        "overflowing",
         "pedersen",
         "peekable",
         "petgraph",
```

### test_programs/compile_failure/overflowing_assignment/Nargo.toml
```diff
@@ -1,5 +0,0 @@
-[package]
-name = "overflowing_assignment"
-type = "bin"
-authors = [""]
-[dependencies]
\ No newline at end of file
```

### test_programs/compile_failure/overflowing_assignment/src/main.nr
```diff
@@ -1,5 +0,0 @@
-fn main() {
-    let x:u8 = -1;
-    let y:u8 = 300;
-    assert(x != y);
-}
```
