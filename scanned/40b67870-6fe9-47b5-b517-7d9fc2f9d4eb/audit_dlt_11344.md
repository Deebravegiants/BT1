# [?] fix: correctly detect signed/unsigned integer overflows/underflows (#5375)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-07-03
Source: https://github.com/noir-lang/noir/commit/0603bd39bff1183725e9aeeaba678c421c7b1daf
Type: security-commit

## Details
fix: correctly detect signed/unsigned integer overflows/underflows (#5375)

# Description

## Problem

Resolves #5372

## Summary

Correctly detects overflows/underflows for basic integer types. The sign
of a field element value is now also propagated to the ssa phase. But
previously, the field value was applied some casting before reaching the
ssa phase so checking that value like that was a bit strange. In this PR
that conversion is delayed until the ssa phase, and the value can be
checked prior to that conversion.

## Additional Context

None.

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
### compiler/noirc_evaluator/src/ssa/ir/types.rs
```diff
@@ -31,12 +31,20 @@ impl NumericType {
 
     /// Returns true if the given Field value is within the numeric limits
     /// for the current NumericType.
-    pub(crate) fn value_is_within_limits(self, field: FieldElement) -> bool {
+    pub(crate) fn value_is_within_limits(self, field: FieldElement, negative: bool) -> bool {
         match self {
-            NumericType::Signed { bit_size } | NumericType::Unsigned { bit_size } => {
+            NumericType::Unsigned { bit_size } => {
+                if negative {
+                    return false;
+                }
                 let max = 2u128.pow(bit_size) - 1;
                 field <= max.into()
             }
+            NumericType::Signed { bit_size } => {
+                let max =
+                    if negative { 2u128.pow(bit_size - 1) } else { 2u128.pow(bit_size - 1) - 1 };
+                field <= max.into()
+            }
             NumericType::NativeField => true,
         }
     }
@@ -210,3 +218,27 @@ impl std::fmt::Display for NumericType {
         }
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    #[test]
+    fn test_u8_is_within_limits() {
+        let u8 = NumericType::Unsigned { bit_size: 8 };
+        assert!(!u8.value_is_within_limits(FieldElement::from(1_i128), true));
+        assert!(u8.value_is_within_limits(FieldElement::from(0_i128), false));
+        assert!(u8.value_is_within_limits(FieldElement::from(255_i128), false));
+        assert!(!u8.value_is_within_limits(FieldElement::from(256_i128), false));
+    }
+
+    #[test]
+    fn test_i8_is_within_limits() {
+        let i8 = NumericType::Signed { bit_size: 8 };
+        assert!(!i8.value_is_within_limits(FieldElement::from(129_i128), true));
+        assert!(i8.value_is_within_limits(FieldElement::from(128_i128), true));
+        assert!(i8.value_is_within_limits(FieldElement::from(0_i128), false));
+        assert!(i8.value_is_within_limits(FieldElement::from(127_i128), false));
+        assert!(!i8.value_is_within_limits(FieldElement::from(128_i128), false));
+    }
+}
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/context.rs
```diff
@@ -266,20 +266,37 @@ impl<'a> FunctionContext<'a> {
     pub(super) fn checked_numeric_constant(
         &mut self,
         value: impl Into<FieldElement>,
+        negative: bool,
         typ: Type,
     ) -> Result<ValueId, RuntimeError> {
         let value = value.into();
 
-        if let Type::Numeric(typ) = typ {
-            if !typ.value_is_within_limits(value) {
+        if let Type::Numeric(numeric_type) = typ {
+            if !numeric_type.value_is_within_limits(value, negative) {
                 let call_stack = self.builder.get_call_stack();
-                return Err(RuntimeError::IntegerOutOfBounds { value, typ, call_stack });
+                return Err(RuntimeError::IntegerOutOfBounds {
+                    value,
+                    typ: numeric_type,
+                    call_stack,
+                });
             }
+
+            let value = if negative {
+                match numeric_type {
+                    NumericType::NativeField => -value,
+                    NumericType::Signed { bit_size } | NumericType::Unsigned { bit_size } => {
+                        let base = 1_u128 << bit_size;
+                        FieldElement::from(base) - value
+                    }
+                }
+            } else {
+                value
+            };
+
+            Ok(self.builder.numeric_constant(value, typ))
         } else {
             panic!("Expected type for numeric constant to be a numeric type, found {typ}");
         }
-
-        Ok(self.builder.numeric_constant(value, typ))
     }
 
     /// helper function which add instructions to the block computing the absolute value of the
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/mod.rs
```diff
@@ -219,10 +219,10 @@ impl<'a> FunctionContext<'a> {
                     _ => unreachable!("ICE: unexpected slice literal type, got {}", array.typ),
                 })
             }
-            ast::Literal::Integer(value, typ, location) => {
+            ast::Literal::Integer(value, negative, typ, location) => {
                 self.builder.set_location(*location);
                 let typ = Self::convert_non_tuple_type(typ);
-                self.checked_numeric_constant(*value, typ).map(Into::into)
+                self.checked_numeric_constant(*value, *negative, typ).map(Into::into)
             }
             ast::Literal::Bool(value) => {
                 // Don't need to call checked_numeric_constant here since `value` can only be true or false
```

### compiler/noirc_frontend/src/monomorphization/ast.rs
```diff
@@ -93,7 +93,7 @@ pub struct For {
 pub enum Literal {
     Array(ArrayLiteral),
     Slice(ArrayLiteral),
-    Integer(FieldElement, Type, Location),
+    Integer(FieldElement, /*sign*/ bool, Type, Location), // false for positive integer and true for negative
     Bool(bool),
     Unit,
     Str(String),
```

### compiler/noirc_frontend/src/monomorphization/mod.rs
```diff
@@ -422,20 +422,7 @@ impl<'interner> Monomorphizer<'interner> {
             HirExpression::Literal(HirLiteral::Integer(value, sign)) => {
                 let location = self.interner.id_location(expr);
                 let typ = Self::convert_type(&self.interner.id_type(expr), location)?;
-
-                if sign {
-                    match typ {
-                        ast::Type::Field => Literal(Integer(-value, typ, location)),
-                        ast::Type::Integer(_, bit_size) => {
-                            let bit_size: u32 = bit_size.into();
-                            let base = 1_u128 << bit_size;
-                            Literal(Integer(FieldElement::from(base) - value, typ, location))
-                        }
-                        _ => unreachable!("Integer literal must be numeric"),
-                    }
-                } else {
-                    Literal(Integer(value, typ, location))
-                }
+                Literal(Integer(value, sign, typ, location))
             }
             HirExpression::Literal(HirLiteral::Array(array)) => match array {
                 HirArrayLiteral::Standard(array) => self.standard_array(expr, array, false)?,
@@ -904,7 +891,7 @@ impl<'interner> Monomorphizer<'interner> {
                 let value = FieldElement::from(value as u128);
                 let location = self.interner.id_location(expr_id);
                 let typ = Self::convert_type(&typ, ident.location)?;
-                ast::Expression::Literal(ast::Literal::Integer(value, typ, location))
+                ast::Expression::Literal(ast::Literal::Integer(value, false, typ, location))
             }
         };
 
@@ -1222,7 +1209,9 @@ impl<'interner> Monomorphizer<'interner> {
                         let bits = (FieldElement::max_num_bits() as u128).into();
                         let typ =
                             ast::Type::Integer(Signedness::Unsigned, IntegerBitSize::SixtyFour);
-                        Some(ast::Expression::Literal(ast::Literal::Integer(bits, typ, location)))
+                        Some(ast::Expression::Literal(ast::Literal::Integer(
+                            bits, false, typ, location,
+                        )))
                     }
                     "zeroed" => {
                         let location = self.interner.expr_location(expr_id);
@@ -1262,7 +1251,12 @@ impl<'interner> Monomorphizer<'interner> {
         let int_type = Type::Integer(crate::ast::Signedness::Unsigned, arr_elem_bits);
 
         let bytes_as_expr = vecmap(bytes, |byte| {
-            Expression::Literal(Literal::Integer((byte as u128).into(), int_type.clone(), location))
+            Expression::Literal(Literal::Integer(
+                (byte as u128).into(),
+                false,
+                int_type.clone(),
+                location,
+            ))
         });
 
         let typ = Type::Slice(Box::new(int_type));
@@ -1549,7 +1543,7 @@ impl<'interner> Monomorphizer<'interner> {
         match typ {
             ast::Type::Field | ast::Type::Integer(..) => {
                 let typ = typ.clone();
-                ast::Expression::Literal(ast::Literal::Integer(0_u128.into(), typ, location))
+                ast::Expression::Literal(ast::Literal::Integer(0_u128.into(), false, typ, location))
             }
             ast::Type::Bool => ast::Expression::Literal(ast::Literal::Bool(false)),
             ast::Type::Unit => ast::Expression::Literal(ast::Literal::Unit),
@@ -1704,7 +1698,8 @@ impl<'interner> Monomorphizer<'interner> {
                 let operator =
                     if matches!(operator.kind, Less | Greater) { Equal } else { NotEqual };
 
-                let int_value = ast::Literal::Integer(ordering_value, ast::Type::Field, location);
+                let int_value =
+                    ast::Literal::Integer(ordering_value, false, ast::Type::Field, location);
                 let rhs = Box::new(ast::Expression::Literal(int_value));
                 let lhs = Box::new(ast::Expression::ExtractTupleField(Box::new(result), 0));
 
```

### compiler/noirc_frontend/src/monomorphization/printer.rs
```diff
@@ -102,7 +102,7 @@ impl AstPrinter {
                 self.print_comma_separated(&array.contents, f)?;
                 write!(f, "]")
             }
-            super::ast::Literal::Integer(x, _, _) => x.fmt(f),
+            super::ast::Literal::Integer(x, _, _, _) => x.fmt(f),
             super::ast::Literal::Bool(x) => x.fmt(f),
             super::ast::Literal::Str(s) => s.fmt(f),
             super::ast::Literal::FmtStr(s, _, _) => {
```

### test_programs/compile_failure/signed_integer_literal_overflow/Nargo.toml
```diff
@@ -1,5 +1,5 @@
 [package]
-name = "integer_literal_overflow"
+name = "signed_integer_literal_overflow"
 type = "bin"
 authors = [""]
 [dependencies]
\ No newline at end of file
```

### test_programs/compile_failure/signed_integer_literal_overflow/src/main.nr
```diff
@@ -0,0 +1,5 @@
+fn main() {
+    foo(128)
+}
+
+fn foo(_x: i8) {}
```

### test_programs/compile_failure/signed_integer_literal_underflow/Nargo.toml
```diff
@@ -0,0 +1,5 @@
+[package]
+name = "signed_integer_literal_underflow"
+type = "bin"
+authors = [""]
+[dependencies]
\ No newline at end of file
```

### test_programs/compile_failure/signed_integer_literal_underflow/src/main.nr
```diff
@@ -0,0 +1,5 @@
+fn main() {
+    foo(-129)
+}
+
+fn foo(_x: i8) {}
```

### test_programs/compile_failure/unsigned_integer_literal_overflow/Nargo.toml
```diff
@@ -0,0 +1,5 @@
+[package]
+name = "unsigned_integer_literal_overflow"
+type = "bin"
+authors = [""]
+[dependencies]
\ No newline at end of file
```
