# [?] fix: check "negate with overflow" in comptime code + allow u1 to be used in comptime code (#8969)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-20
Source: https://github.com/noir-lang/noir/commit/256c67899ade021c0140a204dd00801eaebda055
Type: security-commit

## Details
fix: check "negate with overflow" in comptime code + allow u1 to be used in comptime code (#8969)

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>

## Patch
### compiler/noirc_frontend/src/hir/comptime/display.rs
```diff
@@ -373,7 +373,8 @@ impl Display for ValuePrinter<'_, '_> {
             Value::I16(value) => write!(f, "{value}"),
             Value::I32(value) => write!(f, "{value}"),
             Value::I64(value) => write!(f, "{value}"),
-            Value::U1(value) => write!(f, "{value}"),
+            Value::U1(false) => write!(f, "0"),
+            Value::U1(true) => write!(f, "1"),
             Value::U8(value) => write!(f, "{value}"),
             Value::U16(value) => write!(f, "{value}"),
             Value::U32(value) => write!(f, "{value}"),
```

### compiler/noirc_frontend/src/hir/comptime/errors.rs
```diff
@@ -126,10 +126,17 @@ pub enum InterpreterError {
         operator: &'static str,
         location: Location,
     },
-    MathError {
+    BinaryOperationOverflow {
         operator: &'static str,
         location: Location,
     },
+    NegateWithOverflow {
+        location: Location,
+    },
+    CannotApplyMinusToType {
+        location: Location,
+        typ: &'static str,
+    },
     CastToNonNumericType {
         typ: Type,
         location: Location,
@@ -301,7 +308,9 @@ impl InterpreterError {
             | InterpreterError::TypeUnsupported { location, .. }
             | InterpreterError::InvalidValueForUnary { location, .. }
             | InterpreterError::InvalidValuesForBinary { location, .. }
-            | InterpreterError::MathError { location, .. }
+            | InterpreterError::BinaryOperationOverflow { location, .. }
+            | InterpreterError::NegateWithOverflow { location, .. }
+            | InterpreterError::CannotApplyMinusToType { location, .. }
             | InterpreterError::CastToNonNumericType { location, .. }
             | InterpreterError::NonStructInConstructor { location, .. }
             | InterpreterError::NonEnumInConstructor { location, .. }
@@ -504,7 +513,7 @@ impl<'a> From<&'a InterpreterError> for CustomDiagnostic {
                 let msg = format!("No implementation for `{lhs}` {operator} `{rhs}`");
                 CustomDiagnostic::simple_error(msg, String::new(), *location)
             }
-            InterpreterError::MathError { operator, location } => {
+            InterpreterError::BinaryOperationOverflow { operator, location } => {
                 let msg = if *operator == "/" {
                     "Attempt to divide by zero".to_string()
                 } else {
@@ -520,6 +529,14 @@ impl<'a> From<&'a InterpreterError> for CustomDiagnostic {
                 };
                 CustomDiagnostic::simple_error(msg, String::new(), *location)
             }
+            InterpreterError::NegateWithOverflow { location } => {
+                let msg = "Attempt to negate with overflow".to_string();
+                CustomDiagnostic::simple_error(msg, String::new(), *location)
+            }
+            InterpreterError::CannotApplyMinusToType { location, typ } => {
+                let msg = format!("Cannot apply unary operator `-` to type `{typ}`");
+                CustomDiagnostic::simple_error(msg, String::new(), *location)
+            }
             InterpreterError::CastToNonNumericType { typ, location } => {
                 let msg = format!("Cannot cast to non-numeric type `{typ}`");
                 CustomDiagnostic::simple_error(msg, String::new(), *location)
```

### compiler/noirc_frontend/src/hir/comptime/interpreter.rs
```diff
@@ -1,6 +1,7 @@
 use std::collections::VecDeque;
 use std::{collections::hash_map::Entry, rc::Rc};
 
+use acvm::AcirField;
 use acvm::blackbox_solver::BigIntSolverWithId;
 use im::Vector;
 use iter_extended::try_vecmap;
@@ -1279,6 +1280,7 @@ impl<'local, 'interner> Interpreter<'local, 'interner> {
             self.evaluate_for_loop(start..end, get_index, for_.identifier.id, for_.block)
         } else if loop_index_type.is_unsigned() {
             let get_index = match start_value {
+                Value::U1(_) => |i| Value::U1(i == 1),
                 Value::U8(_) => |i| Value::U8(i as u8),
                 Value::U16(_) => |i| Value::U16(i as u16),
                 Value::U32(_) => |i| Value::U32(i as u32),
@@ -1469,7 +1471,14 @@ fn evaluate_integer(typ: Type, value: SignedField, location: Location) -> IResul
     } else if let Type::Integer(sign, bit_size) = &typ {
         match (sign, bit_size) {
             (Signedness::Unsigned, IntegerBitSize::One) => {
-                return Err(InterpreterError::TypeUnsupported { typ, location });
+                let field_value = value.to_field_element();
+                if field_value.is_zero() {
+                    Ok(Value::U1(false))
+                } else if field_value.is_one() {
+                    Ok(Value::U1(true))
+                } else {
+                    Err(InterpreterError::IntegerOutOfRangeForType { value, typ, location })
+                }
             }
             (Signedness::Unsigned, IntegerBitSize::Eight) => {
                 let value = value
@@ -1573,6 +1582,13 @@ fn bounds_check(array: Value, index: Value, location: Location) -> IResult<(Vect
         Value::I16(value) => value as usize,
         Value::I32(value) => value as usize,
         Value::I64(value) => value as usize,
+        Value::U1(value) => {
+            if value {
+                1_usize
+            } else {
+                0_usize
+            }
+        }
         Value::U8(value) => value as usize,
         Value::U16(value) => value as usize,
         Value::U32(value) => value as usize,
@@ -1595,15 +1611,30 @@ fn evaluate_prefix_with_value(rhs: Value, operator: UnaryOp, location: Location)
     match operator {
         UnaryOp::Minus => match rhs {
             Value::Field(value) => Ok(Value::Field(-value)),
-            Value::I8(value) => Ok(Value::I8(-value)),
-            Value::I16(value) => Ok(Value::I16(-value)),
-            Value::I32(value) => Ok(Value::I32(-value)),
-            Value::I64(value) => Ok(Value::I64(-value)),
-            Value::U8(value) => Ok(Value::U8(0 - value)),
-            Value::U16(value) => Ok(Value::U16(0 - value)),
-            Value::U32(value) => Ok(Value::U32(0 - value)),
-            Value::U64(value) => Ok(Value::U64(0 - value)),
-            Value::U128(value) => Ok(Value::U128(0 - value)),
+            Value::I8(value) => value
+                .checked_neg()
+                .map(Value::I8)
+                .ok_or_else(|| InterpreterError::NegateWithOverflow { location }),
+            Value::I16(value) => value
+                .checked_neg()
+                .map(Value::I16)
+                .ok_or_else(|| InterpreterError::NegateWithOverflow { location }),
+            Value::I32(value) => value
+                .checked_neg()
+                .map(Value::I32)
+                .ok_or_else(|| InterpreterError::NegateWithOverflow { location }),
+            Value::I64(value) => value
+                .checked_neg()
+                .map(Value::I64)
+                .ok_or_else(|| InterpreterError::NegateWithOverflow { location }),
+            Value::U1(_) => Err(InterpreterError::CannotApplyMinusToType { location, typ: "u1" }),
+            Value::U8(_) => Err(InterpreterError::CannotApplyMinusToType { location, typ: "u8" }),
+            Value::U16(_) => Err(InterpreterError::CannotApplyMinusToType { location, typ: "u16" }),
+            Value::U32(_) => Err(InterpreterError::CannotApplyMinusToType { location, typ: "u32" }),
+            Value::U64(_) => Err(InterpreterError::CannotApplyMinusToType { location, typ: "u64" }),
+            Value::U128(_) => {
+                Err(InterpreterError::CannotApplyMinusToType { location, typ: "u128" })
+            }
             value => {
                 let operator = "minus";
                 let typ = value.get_type().into_owned();
@@ -1616,6 +1647,7 @@ fn evaluate_prefix_with_value(rhs: Value, operator: UnaryOp, location: Location)
             Value::I16(value) => Ok(Value::I16(!value)),
             Value::I32(value) => Ok(Value::I32(!value)),
             Value::I64(value) => Ok(Value::I64(!value)),
+            Value::U1(value) => Ok(Value::U1(!value)),
             Value::U8(value) => Ok(Value::U8(!value)),
             Value::U16(value) => Ok(Value::U16(!value)),
             Value::U32(value) => Ok(Value::U32(!value)),
@@ -1647,6 +1679,7 @@ fn evaluate_prefix_with_value(rhs: Value, operator: UnaryOp, location: Location)
 
 fn to_u128(value: Value) -> Option<u128> {
     match value {
+        Value::U1(value) => Some(if value { 1_u128 } else { 0_u128 }),
         Value::U8(value) => Some(value as u128),
         Value::U16(value) => Some(value as u128),
         Value::U32(value) => Some(value as u128),
```

### compiler/noirc_frontend/src/hir/comptime/interpreter/infix.rs
```diff
@@ -21,7 +21,7 @@ pub(super) fn evaluate_infix(
         InterpreterError::InvalidValuesForBinary { lhs, rhs, location, operator }
     };
 
-    let math_error = |operator| InterpreterError::MathError { location, operator };
+    let math_error = |operator| InterpreterError::BinaryOperationOverflow { location, operator };
 
     /// Generate matches that can promote the type of one side to the other if they are compatible.
     macro_rules! match_values {
@@ -280,7 +280,7 @@ mod test {
         "#;
 
         let err = interpret_expect_error(src);
-        let InterpreterError::MathError { operator, .. } = err else {
+        let InterpreterError::BinaryOperationOverflow { operator, .. } = err else {
             panic!("Expected overflow error");
         };
         assert_eq!(operator, "<<");
@@ -295,7 +295,7 @@ mod test {
         "#;
 
         let err = interpret_expect_error(src);
-        let InterpreterError::MathError { operator, .. } = err else {
+        let InterpreterError::BinaryOperationOverflow { operator, .. } = err else {
             panic!("Expected overflow error");
         };
         assert_eq!(operator, "<<");
@@ -414,7 +414,10 @@ mod test {
             }
         "#;
         let result = interpret_expect_error(src);
-        assert!(matches!(result, InterpreterError::MathError { operator: "/", location: _ }));
+        assert!(matches!(
+            result,
+            InterpreterError::BinaryOperationOverflow { operator: "/", location: _ }
+        ));
     }
 
     #[test]
@@ -425,7 +428,10 @@ mod test {
             }
         "#;
         let result = interpret_expect_error(src);
-        assert!(matches!(result, InterpreterError::MathError { operator: "/", location: _ }));
+        assert!(matches!(
+            result,
+            InterpreterError::BinaryOperationOverflow { operator: "/", location: _ }
+        ));
     }
 
     #[test]
```

### compiler/noirc_frontend/src/hir/comptime/value.rs
```diff
@@ -575,6 +575,7 @@ impl Value {
                 | I16(_)
                 | I32(_)
                 | I64(_)
+                | U1(_)
                 | U8(_)
                 | U16(_)
                 | U32(_)
@@ -648,6 +649,7 @@ impl Value {
             Self::I16(value) => (*value >= 0).then_some((*value as u128).into()),
             Self::I32(value) => (*value >= 0).then_some((*value as u128).into()),
             Self::I64(value) => (*value >= 0).then_some((*value as u128).into()),
+            Self::U1(value) => Some(FieldElement::from(*value)),
             Self::U8(value) => Some((*value as u128).into()),
             Self::U16(value) => Some((*value as u128).into()),
             Self::U32(value) => Some((*value as u128).into()),
```

### test_programs/compile_failure/comptime_negate_with_overflow/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "comptime_negate_with_overflow"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.33.0"
+
+[dependencies]
```

### test_programs/compile_failure/comptime_negate_with_overflow/src/main.nr
```diff
@@ -0,0 +1,10 @@
+fn main() {
+    comptime {
+        let i: i8 = -(128 as i8);
+    }
+
+    comptime {
+        let i: u8 = 1;
+        let _ = -i;
+    }
+}
\ No newline at end of file
```

### tooling/nargo_cli/tests/snapshots/compile_failure/comptime_negate_with_overflow/execute__tests__stderr.snap
```diff
@@ -0,0 +1,40 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+warning: Casting value of type Field to a smaller type (i8)
+  ┌─ src/main.nr:3:23
+  │
+3 │         let i: i8 = -(128 as i8);
+  │                       --------- casting untyped value (128) to a type with a maximum size (127) that's smaller than it
+  │
+
+warning: unused variable i
+  ┌─ src/main.nr:3:13
+  │
+3 │         let i: i8 = -(128 as i8);
+  │             - unused variable
+  │
+
+error: Attempt to negate with overflow
+  ┌─ src/main.nr:3:21
+  │
+3 │         let i: i8 = -(128 as i8);
+  │                     ------------
+  │
+
+error: Cannot apply unary operator `-` to type `u8`
+  ┌─ src/main.nr:8:17
+  │
+8 │         let _ = -i;
+  │                 --
+  │
+
+error: Cannot apply unary operator `-` to type `u8`
+  ┌─ src/main.nr:8:17
+  │
+8 │         let _ = -i;
+  │                 --
+  │
+
+Aborting due to 3 previous errors
```
