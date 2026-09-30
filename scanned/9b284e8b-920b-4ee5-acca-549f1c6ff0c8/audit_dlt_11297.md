# [?] fix: modulo overflow in comptime (#9348)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-07-30
Source: https://github.com/noir-lang/noir/commit/922efbdb30b35c7e93f8db829436fbe0a03ffae1
Type: security-commit

## Details
fix: modulo overflow in comptime (#9348)

## Patch
### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -1276,9 +1276,15 @@ impl<W: Write> Interpreter<'_, W> {
             BinaryOp::Div => {
                 apply_int_binop_opt!(dfg, lhs, rhs, binary, num_traits::CheckedDiv::checked_div)
             }
-            BinaryOp::Mod => {
-                apply_int_binop_opt!(dfg, lhs, rhs, binary, num_traits::CheckedRem::checked_rem)
-            }
+            BinaryOp::Mod => match (lhs, rhs) {
+                (NumericValue::I8(i8::MIN), NumericValue::I8(-1)) => NumericValue::I8(0),
+                (NumericValue::I16(i16::MIN), NumericValue::I16(-1)) => NumericValue::I16(0),
+                (NumericValue::I32(i32::MIN), NumericValue::I32(-1)) => NumericValue::I32(0),
+                (NumericValue::I64(i64::MIN), NumericValue::I64(-1)) => NumericValue::I64(0),
+                _ => {
+                    apply_int_binop_opt!(dfg, lhs, rhs, binary, num_traits::CheckedRem::checked_rem)
+                }
+            },
             BinaryOp::Eq => apply_int_comparison_op!(lhs, rhs, binary, |a, b| a == b),
             BinaryOp::Lt => apply_int_comparison_op!(lhs, rhs, binary, |a, b| a < b),
             BinaryOp::And => {
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/instructions.rs
```diff
@@ -336,6 +336,21 @@ fn mod_zero() {
     assert!(matches!(error, InterpreterError::DivisionByZero { .. }));
 }
 
+#[test]
+fn regression_9336() {
+    let result = expect_value_with_args(
+        "
+        acir(inline) fn main f0 {
+          b0(v0: i8):
+            v1 = mod i8 -128, v0
+            return v1
+        }
+    ",
+        vec![Value::Numeric(NumericValue::I8(-1))],
+    );
+    assert_eq!(result, Value::Numeric(NumericValue::I8(0)));
+}
+
 #[test]
 fn eq() {
     let value = expect_value(
```

### compiler/noirc_evaluator/src/ssa/parser/mod.rs
```diff
@@ -13,15 +13,17 @@ use super::{
     opt::pure::Purity,
 };
 
-use acvm::{AcirField, FieldElement};
+use acvm::FieldElement;
 use ast::{
     AssertMessage, Identifier, ParsedBlock, ParsedFunction, ParsedGlobal, ParsedGlobalValue,
     ParsedInstruction, ParsedMakeArray, ParsedNumericConstant, ParsedParameter, ParsedSsa,
     ParsedValue,
 };
 use lexer::{Lexer, LexerError};
 use noirc_errors::Span;
-use noirc_frontend::{monomorphization::ast::InlineType, token::IntType};
+use noirc_frontend::{
+    monomorphization::ast::InlineType, signed_field::SignedField, token::IntType,
+};
 use thiserror::Error;
 use token::{Keyword, SpannedToken, Token};
 
@@ -452,7 +454,12 @@ impl<'a> Parser<'a> {
 
         let value = self.parse_value_or_error()?;
         self.eat_or_error(Token::Keyword(Keyword::To))?;
-        let max_bit_size = self.eat_int_or_error()?.to_u128() as u32;
+        let max_bit_size = self.eat_int_or_error()?.try_to_unsigned::<u32>().ok_or(
+            ParserError::InvalidInteger {
+                found: self.token.token().clone(),
+                span: self.token.span(),
+            },
+        )?;
         self.eat_or_error(Token::Keyword(Keyword::Bits))?;
 
         let assert_message =
@@ -573,12 +580,22 @@ impl<'a> Parser<'a> {
         if self.eat_keyword(Keyword::Truncate)? {
             let value = self.parse_value_or_error()?;
             self.eat_or_error(Token::Keyword(Keyword::To))?;
-            let bit_size = self.eat_int_or_error()?.to_u128() as u32;
+            let bit_size = self.eat_int_or_error()?.try_to_unsigned::<u32>().ok_or(
+                ParserError::InvalidInteger {
+                    found: self.token.token().clone(),
+                    span: self.token.span(),
+                },
+            )?;
             self.eat_or_error(Token::Keyword(Keyword::Bits))?;
             self.eat_or_error(Token::Comma)?;
             self.eat_or_error(Token::Keyword(Keyword::MaxBitSize))?;
             self.eat_or_error(Token::Colon)?;
-            let max_bit_size = self.eat_int_or_error()?.to_u128() as u32;
+            let max_bit_size = self.eat_int_or_error()?.try_to_unsigned::<u32>().ok_or(
+                ParserError::InvalidInteger {
+                    found: self.token.token().clone(),
+                    span: self.token.span(),
+                },
+            )?;
             return Ok(ParsedInstruction::Truncate { target, value, bit_size, max_bit_size });
         }
 
@@ -616,7 +633,7 @@ impl<'a> Parser<'a> {
             let token = self.token.token().clone();
             let span = self.token.span();
             let field = self.eat_int_or_error()?;
-            if let Some(offset) = field.try_to_u32().and_then(ArrayOffset::from_u32) {
+            if let Some(offset) = field.try_to_unsigned::<u32>().and_then(ArrayOffset::from_u32) {
                 if offset == ArrayOffset::None {
                     self.unexpected_offset(token, span)
                 } else {
@@ -802,7 +819,7 @@ impl<'a> Parser<'a> {
 
     fn parse_field_value(&mut self) -> ParseResult<Option<ParsedNumericConstant>> {
         if self.eat_keyword(Keyword::Field)? {
-            let value = self.eat_int_or_error()?;
+            let value = self.eat_int_or_error()?.to_field_element();
             Ok(Some(ParsedNumericConstant { value, typ: Type::field() }))
         } else {
             Ok(None)
@@ -816,6 +833,12 @@ impl<'a> Parser<'a> {
                 IntType::Unsigned(bit_size) => Type::unsigned(bit_size),
                 IntType::Signed(bit_size) => Type::signed(bit_size),
             };
+            let value = if typ.is_signed() && value.is_negative() {
+                // 2-complement representation:
+                FieldElement::from(2u128.pow(typ.bit_size())) - value.absolute_value()
+            } else {
+                value.absolute_value()
+            };
             Ok(Some(ParsedNumericConstant { value, typ }))
         } else {
             Ok(None)
@@ -865,7 +888,7 @@ impl<'a> Parser<'a> {
             if self.eat(Token::Semicolon)? {
                 let length = self.eat_int_or_error()?;
                 self.eat_or_error(Token::RightBracket)?;
-                return Ok(Type::Array(Arc::new(element_types), length.to_u128() as u32));
+                return Ok(Type::Array(Arc::new(element_types), length.try_to_unsigned().unwrap()));
             } else {
                 self.eat_or_error(Token::RightBracket)?;
                 return Ok(Type::Slice(Arc::new(element_types)));
@@ -961,26 +984,21 @@ impl<'a> Parser<'a> {
         }
     }
 
-    fn eat_int(&mut self) -> ParseResult<Option<FieldElement>> {
+    fn eat_int(&mut self) -> ParseResult<Option<SignedField>> {
         let negative = self.eat(Token::Dash)?;
 
         if matches!(self.token.token(), Token::Int(..)) {
             let token = self.bump()?;
             match token.into_token() {
-                Token::Int(mut int) => {
-                    if negative {
-                        int = -int;
-                    }
-                    Ok(Some(int))
-                }
+                Token::Int(int) => Ok(Some(SignedField::new(int, negative))),
                 _ => unreachable!(),
             }
         } else {
             Ok(None)
         }
     }
 
-    fn eat_int_or_error(&mut self) -> ParseResult<FieldElement> {
+    fn eat_int_or_error(&mut self) -> ParseResult<SignedField> {
         if let Some(int) = self.eat_int()? { Ok(int) } else { self.expected_int() }
     }
 
@@ -1168,6 +1186,8 @@ pub(crate) enum ParserError {
     MultipleReturnValuesOnlyAllowedForCall { second_target: Identifier },
     #[error("Unexpected integer value for array_get offset")]
     UnexpectedOffset { found: Token, span: Span },
+    #[error("Invalid integer value")]
+    InvalidInteger { found: Token, span: Span },
 }
 
 impl ParserError {
@@ -1185,7 +1205,9 @@ impl ParserError {
             | ParserError::ExpectedByteString { span, .. }
             | ParserError::ExpectedValue { span, .. }
             | ParserError::ExpectedGlobalValue { span, .. }
-            | ParserError::UnexpectedOffset { span, .. } => *span,
+            | ParserError::UnexpectedOffset { span, .. }
+            | ParserError::InvalidInteger { span, .. } => *span,
+
             ParserError::MultipleReturnValuesOnlyAllowedForCall { second_target, .. } => {
                 second_target.span
             }
```

### compiler/noirc_frontend/src/hir/comptime/interpreter/infix.rs
```diff
@@ -222,8 +222,14 @@ pub(super) fn evaluate_infix(
         BinaryOpKind::ShiftLeft => match_bitshift! {
             (lhs_value as lhs "<<" rhs_value as rhs) => lhs.checked_shl(rhs.into())
         },
-        BinaryOpKind::Modulo => match_integer! {
-            (lhs_value as lhs "%" rhs_value as rhs) => lhs.checked_rem(rhs)
+        BinaryOpKind::Modulo => match (&lhs_value, &rhs_value) {
+            (Value::I8(i8::MIN), Value::I8(-1)) => Ok(Value::I8(0)),
+            (Value::I16(i16::MIN), Value::I16(-1)) => Ok(Value::I16(0)),
+            (Value::I32(i32::MIN), Value::I32(-1)) => Ok(Value::I32(0)),
+            (Value::I64(i64::MIN), Value::I64(-1)) => Ok(Value::I64(0)),
+            _ => match_integer! {
+                (lhs_value as lhs "%" rhs_value as rhs) => lhs.checked_rem(rhs)
+            },
         },
     }
 }
@@ -249,6 +255,17 @@ mod test {
         assert_eq!(result, Value::U128(170141183460469231731687303715884105727));
     }
 
+    #[test]
+    fn regression_9336() {
+        let lhs = Value::I8(-128);
+        let rhs = Value::I8(-1);
+        let operator = HirBinaryOp { kind: BinaryOpKind::Modulo, location: Location::dummy() };
+        let location = Location::dummy();
+        let result = evaluate_infix(lhs, rhs, operator, location).unwrap();
+
+        assert_eq!(result, Value::I8(0));
+    }
+
     #[test]
     fn shl_unsigned() {
         let src = r#"
```

### compiler/noirc_frontend/src/signed_field.rs
```diff
@@ -1,6 +1,6 @@
 use acvm::{AcirField, FieldElement};
 
-#[derive(Debug, Copy, Clone, PartialEq, Eq, Hash)]
+#[derive(Debug, Copy, Clone, PartialEq, Eq, Hash, serde::Deserialize, serde::Serialize)]
 pub struct SignedField {
     field: FieldElement,
     is_negative: bool,
```

### docs/docs/noir/concepts/ops.md
```diff
@@ -27,6 +27,7 @@ sidebar_position: 3
 | -         |           Subtracts two private input types together           |            Types must be private input |
 | \*        |          Multiplies two private input types together           |            Types must be private input |
 | /         |            Divides two private input types together            |            Types must be private input |
+| \%        |              Modulo operation                                  |                  Types must be integer |
 | ^         |              XOR two private input types together              |                  Types must be integer |
 | &         |              AND two private input types together              |                  Types must be integer |
 | \|        |              OR two private input types together               |                  Types must be integer |
@@ -40,6 +41,9 @@ sidebar_position: 3
 | ==        |       returns a bool if one value is equal to the other        |       Both types must not be constants |
 | !=        |     returns a bool if one value is not equal to the other      |       Both types must not be constants |
 
+The modulo operator `%` will give an error when the right-hand side operand is zero, and will return `0` when the
+right-hand side operand is `1`, or `-1`.
+
 ### Predicate Operators
 
 `<,<=, !=, == , >, >=` are known as predicate/comparison operations because they compare two values.
```
