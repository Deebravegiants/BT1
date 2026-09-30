# [?] fix: Remove panics in the interpreter when a builtin fails to type check (#5382)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-07-02
Source: https://github.com/noir-lang/noir/commit/c8161c81a3c6599a3b0380f4c80c730a41a75f22
Type: security-commit

## Details
fix: Remove panics in the interpreter when a builtin fails to type check (#5382)

# Description

## Problem\*

Resolves comment:
https://github.com/noir-lang/noir/pull/5341#pullrequestreview-2142302988

## Summary\*

Before this PR, we could panic if a builtin within a comptime block
fails to type check, and is later executed by the interpreter.

## Additional Context

## Documentation\*

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
### compiler/noirc_frontend/src/hir/comptime/interpreter/builtin.rs
```diff
@@ -16,62 +16,102 @@ pub(super) fn call_builtin(
     location: Location,
 ) -> IResult<Value> {
     match name {
-        "array_len" => array_len(&arguments),
-        "as_slice" => as_slice(arguments),
-        "slice_push_back" => slice_push_back(arguments),
-        "struct_def_as_type" => struct_def_as_type(interner, arguments),
-        "struct_def_generics" => struct_def_generics(interner, arguments),
-        "struct_def_fields" => struct_def_fields(interner, arguments),
+        "array_len" => array_len(interner, arguments, location),
+        "as_slice" => as_slice(interner, arguments, location),
+        "slice_push_back" => slice_push_back(interner, arguments, location),
+        "struct_def_as_type" => struct_def_as_type(interner, arguments, location),
+        "struct_def_generics" => struct_def_generics(interner, arguments, location),
+        "struct_def_fields" => struct_def_fields(interner, arguments, location),
         _ => {
             let item = format!("Comptime evaluation for builtin function {name}");
             Err(InterpreterError::Unimplemented { item, location })
         }
     }
 }
 
-fn array_len(arguments: &[(Value, Location)]) -> IResult<Value> {
-    assert_eq!(arguments.len(), 1, "ICE: `array_len` should only receive a single argument");
-    match &arguments[0].0 {
+fn check_argument_count(
+    expected: usize,
+    arguments: &[(Value, Location)],
+    location: Location,
+) -> IResult<()> {
+    if arguments.len() == expected {
+        Ok(())
+    } else {
+        let actual = arguments.len();
+        Err(InterpreterError::ArgumentCountMismatch { expected, actual, location })
+    }
+}
+
+fn array_len(
+    interner: &NodeInterner,
+    mut arguments: Vec<(Value, Location)>,
+    location: Location,
+) -> IResult<Value> {
+    check_argument_count(1, &arguments, location)?;
+
+    match arguments.pop().unwrap().0 {
         Value::Array(values, _) | Value::Slice(values, _) => Ok(Value::U32(values.len() as u32)),
-        // Type checking should prevent this branch being taken.
-        _ => unreachable!("ICE: Cannot query length of types other than arrays or slices"),
+        value => {
+            let type_var = Box::new(interner.next_type_variable());
+            let expected = Type::Array(type_var.clone(), type_var);
+            Err(InterpreterError::TypeMismatch { expected, value, location })
+        }
     }
 }
 
-fn as_slice(mut arguments: Vec<(Value, Location)>) -> IResult<Value> {
-    assert_eq!(arguments.len(), 1, "ICE: `as_slice` should only receive a single argument");
+fn as_slice(
+    interner: &NodeInterner,
+    mut arguments: Vec<(Value, Location)>,
+    location: Location,
+) -> IResult<Value> {
+    check_argument_count(1, &arguments, location)?;
+
     let (array, _) = arguments.pop().unwrap();
     match array {
         Value::Array(values, Type::Array(_, typ)) => Ok(Value::Slice(values, Type::Slice(typ))),
-        // Type checking should prevent this branch being taken.
-        _ => unreachable!("ICE: Cannot convert types other than arrays into slices"),
+        value => {
+            let type_var = Box::new(interner.next_type_variable());
+            let expected = Type::Array(type_var.clone(), type_var);
+            Err(InterpreterError::TypeMismatch { expected, value, location })
+        }
     }
 }
 
-fn slice_push_back(mut arguments: Vec<(Value, Location)>) -> IResult<Value> {
-    assert_eq!(arguments.len(), 2, "ICE: `slice_push_back` should only receive two arguments");
+fn slice_push_back(
+    interner: &NodeInterner,
+    mut arguments: Vec<(Value, Location)>,
+    location: Location,
+) -> IResult<Value> {
+    check_argument_count(2, &arguments, location)?;
+
     let (element, _) = arguments.pop().unwrap();
     let (slice, _) = arguments.pop().unwrap();
     match slice {
         Value::Slice(mut values, typ) => {
             values.push_back(element);
             Ok(Value::Slice(values, typ))
         }
-        // Type checking should prevent this branch being taken.
-        _ => unreachable!("ICE: `slice_push_back` expects a slice as its first argument"),
+        value => {
+            let type_var = Box::new(interner.next_type_variable());
+            let expected = Type::Slice(type_var);
+            Err(InterpreterError::TypeMismatch { expected, value, location })
+        }
     }
 }
 
 /// fn as_type(self) -> Quoted
 fn struct_def_as_type(
     interner: &NodeInterner,
     mut arguments: Vec<(Value, Location)>,
+    location: Location,
 ) -> IResult<Value> {
-    assert_eq!(arguments.len(), 1, "ICE: `generics` should only receive a single argument");
-    let (struct_def, span) = match arguments.pop() {
-        Some((Value::StructDefinition(id), location)) => (id, location.span),
-        other => {
-            unreachable!("ICE: `as_type` expected a `StructDefinition` argument, found {other:?}")
+    check_argument_count(1, &arguments, location)?;
+
+    let (struct_def, span) = match arguments.pop().unwrap() {
+        (Value::StructDefinition(id), location) => (id, location.span),
+        value => {
+            let expected = Type::Quoted(QuotedType::StructDefinition);
+            return Err(InterpreterError::TypeMismatch { expected, location, value: value.0 });
         }
     };
 
@@ -95,42 +135,44 @@ fn struct_def_as_type(
 fn struct_def_generics(
     interner: &NodeInterner,
     mut arguments: Vec<(Value, Location)>,
+    location: Location,
 ) -> IResult<Value> {
-    assert_eq!(arguments.len(), 1, "ICE: `generics` should only receive a single argument");
-    let (struct_def, span) = match arguments.pop() {
-        Some((Value::StructDefinition(id), location)) => (id, location.span),
-        other => {
-            unreachable!("ICE: `as_type` expected a `StructDefinition` argument, found {other:?}")
+    check_argument_count(1, &arguments, location)?;
+
+    let (struct_def, span) = match arguments.pop().unwrap() {
+        (Value::StructDefinition(id), location) => (id, location.span),
+        value => {
+            let expected = Type::Quoted(QuotedType::StructDefinition);
+            return Err(InterpreterError::TypeMismatch { expected, location, value: value.0 });
         }
     };
 
     let struct_def = interner.get_struct(struct_def);
+    let struct_def = struct_def.borrow();
 
-    let generics = struct_def
-        .borrow()
-        .generics
-        .iter()
-        .map(|generic| {
-            let name = SpannedToken::new(Token::Ident(generic.type_var.borrow().to_string()), span);
-            Value::Code(Rc::new(Tokens(vec![name])))
-        })
-        .collect();
+    let generics = struct_def.generics.iter().map(|generic| {
+        let name = SpannedToken::new(Token::Ident(generic.type_var.borrow().to_string()), span);
+        Value::Code(Rc::new(Tokens(vec![name])))
+    });
 
     let typ = Type::Slice(Box::new(Type::Quoted(QuotedType::Quoted)));
-    Ok(Value::Slice(generics, typ))
+    Ok(Value::Slice(generics.collect(), typ))
 }
 
 /// fn fields(self) -> [(Quoted, Quoted)]
 /// Returns (name, type) pairs of each field of this StructDefinition
 fn struct_def_fields(
     interner: &mut NodeInterner,
     mut arguments: Vec<(Value, Location)>,
+    location: Location,
 ) -> IResult<Value> {
-    assert_eq!(arguments.len(), 1, "ICE: `generics` should only receive a single argument");
-    let (struct_def, span) = match arguments.pop() {
-        Some((Value::StructDefinition(id), location)) => (id, location.span),
-        other => {
-            unreachable!("ICE: `as_type` expected a `StructDefinition` argument, found {other:?}")
+    check_argument_count(1, &arguments, location)?;
+
+    let (struct_def, span) = match arguments.pop().unwrap() {
+        (Value::StructDefinition(id), location) => (id, location.span),
+        value => {
+            let expected = Type::Quoted(QuotedType::StructDefinition);
+            return Err(InterpreterError::TypeMismatch { expected, location, value: value.0 });
         }
     };
 
```
