# [?] fix: remove panic when generic array length is not resolvable (#4408)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-02-26
Source: https://github.com/noir-lang/noir/commit/00ab3db86b06111d144516e862902b8604284611
Type: security-commit

## Details
fix: remove panic when generic array length is not resolvable (#4408)

# Description

## Problem\*

Resolves #4407 

## Summary\*

We currently have no way to gracefully error during monomorphization and
so must panic if we run into any errors.

This PR then adds the `MonomorphizationError` enum with an example error
type. We've also added a `CompileError` which unifies `RuntimeError` and
`MonomorphizationError` so they can be converted into `FileDiagnostic`s


## Additional Context



## Documentation\*

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[Exceptional Case]** Documentation to be submitted in a separate
PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### Cargo.lock
```diff
@@ -2947,6 +2947,7 @@ dependencies = [
  "noirc_macros",
  "rust-embed",
  "serde",
+ "thiserror",
  "tracing",
 ]
 
```

### compiler/noirc_driver/Cargo.toml
```diff
@@ -23,6 +23,7 @@ serde.workspace = true
 fxhash.workspace = true
 rust-embed.workspace = true
 tracing.workspace = true
+thiserror.workspace = true
 
 aztec_macros = { path = "../../aztec_macros" }
 noirc_macros = { path = "../../noirc_macros" }
```

### compiler/noirc_driver/src/lib.rs
```diff
@@ -16,9 +16,10 @@ use noirc_frontend::graph::{CrateId, CrateName};
 use noirc_frontend::hir::def_map::{Contract, CrateDefMap};
 use noirc_frontend::hir::Context;
 use noirc_frontend::macros_api::MacroProcessor;
-use noirc_frontend::monomorphization::{monomorphize, monomorphize_debug};
+use noirc_frontend::monomorphization::{monomorphize, monomorphize_debug, MonomorphizationError};
 use noirc_frontend::node_interner::FuncId;
 use std::path::Path;
+use thiserror::Error;
 use tracing::info;
 
 mod abi_gen;
@@ -107,6 +108,24 @@ fn parse_expression_width(input: &str) -> Result<ExpressionWidth, std::io::Error
     }
 }
 
+#[derive(Debug, Error)]
+pub enum CompileError {
+    #[error(transparent)]
+    MonomorphizationError(#[from] MonomorphizationError),
+
+    #[error(transparent)]
+    RuntimeError(#[from] RuntimeError),
+}
+
+impl From<CompileError> for FileDiagnostic {
+    fn from(error: CompileError) -> FileDiagnostic {
+        match error {
+            CompileError::RuntimeError(err) => err.into(),
+            CompileError::MonomorphizationError(err) => err.into(),
+        }
+    }
+}
+
 /// Helper type used to signify where only warnings are expected in file diagnostics
 pub type Warnings = Vec<FileDiagnostic>;
 
@@ -436,11 +455,11 @@ pub fn compile_no_check(
     main_function: FuncId,
     cached_program: Option<CompiledProgram>,
     force_compile: bool,
-) -> Result<CompiledProgram, RuntimeError> {
+) -> Result<CompiledProgram, CompileError> {
     let program = if options.instrument_debug {
-        monomorphize_debug(main_function, &mut context.def_interner, &context.debug_instrumenter)
+        monomorphize_debug(main_function, &mut context.def_interner, &context.debug_instrumenter)?
     } else {
-        monomorphize(main_function, &mut context.def_interner)
+        monomorphize(main_function, &mut context.def_interner)?
     };
 
     let hash = fxhash::hash64(&program);
```

### compiler/noirc_evaluator/src/errors.rs
```diff
@@ -158,7 +158,7 @@ impl RuntimeError {
             RuntimeError::InternalError(cause) => {
                 Diagnostic::simple_error(
                     "Internal Consistency Evaluators Errors: \n
-                    This is likely a bug. Consider Opening an issue at https://github.com/noir-lang/noir/issues".to_owned(),
+                    This is likely a bug. Consider opening an issue at https://github.com/noir-lang/noir/issues".to_owned(),
                     cause.to_string(),
                     noirc_errors::Span::inclusive(0, 0)
                 )
```

### compiler/noirc_frontend/src/monomorphization/debug.rs
```diff
@@ -8,7 +8,7 @@ use crate::hir_def::expr::*;
 use crate::node_interner::ExprId;
 
 use super::ast::{Expression, Ident};
-use super::Monomorphizer;
+use super::{MonomorphizationError, Monomorphizer};
 
 const DEBUG_MEMBER_ASSIGN_PREFIX: &str = "__debug_member_assign_";
 const DEBUG_VAR_ID_ARG_SLOT: usize = 0;
@@ -39,18 +39,19 @@ impl<'interner> Monomorphizer<'interner> {
         &mut self,
         call: &HirCallExpression,
         arguments: &mut [Expression],
-    ) {
-        let original_func = Box::new(self.expr(call.func));
+    ) -> Result<(), MonomorphizationError> {
+        let original_func = Box::new(self.expr(call.func)?);
         if let Expression::Ident(Ident { name, .. }) = original_func.as_ref() {
             if name == "__debug_var_assign" {
-                self.patch_debug_var_assign(call, arguments);
+                self.patch_debug_var_assign(call, arguments)?;
             } else if name == "__debug_var_drop" {
-                self.patch_debug_var_drop(call, arguments);
+                self.patch_debug_var_drop(call, arguments)?;
             } else if let Some(arity) = name.strip_prefix(DEBUG_MEMBER_ASSIGN_PREFIX) {
                 let arity = arity.parse::<usize>().expect("failed to parse member assign arity");
-                self.patch_debug_member_assign(call, arguments, arity);
+                self.patch_debug_member_assign(call, arguments, arity)?;
             }
         }
+        Ok(())
     }
 
     /// Update instrumentation code inserted on variable assignment. We need to
@@ -59,7 +60,11 @@ impl<'interner> Monomorphizer<'interner> {
     /// variable are possible if using generic functions, hence the temporary ID
     /// created when injecting the instrumentation code can map to multiple IDs
     /// at runtime.
-    fn patch_debug_var_assign(&mut self, call: &HirCallExpression, arguments: &mut [Expression]) {
+    fn patch_debug_var_assign(
+        &mut self,
+        call: &HirCallExpression,
+        arguments: &mut [Expression],
+    ) -> Result<(), MonomorphizationError> {
         let hir_arguments = vecmap(&call.arguments, |id| self.interner.expression(id));
         let var_id_arg = hir_arguments.get(DEBUG_VAR_ID_ARG_SLOT);
         let Some(HirExpression::Literal(HirLiteral::Integer(source_var_id, _))) = var_id_arg else {
@@ -73,13 +78,18 @@ impl<'interner> Monomorphizer<'interner> {
         // then update the ID used for tracking at runtime
         let var_id = self.debug_type_tracker.insert_var(source_var_id, var_type);
         let interned_var_id = self.intern_var_id(var_id, &call.location);
-        arguments[DEBUG_VAR_ID_ARG_SLOT] = self.expr(interned_var_id);
+        arguments[DEBUG_VAR_ID_ARG_SLOT] = self.expr(interned_var_id)?;
+        Ok(())
     }
 
     /// Update instrumentation code for a variable being dropped out of scope.
     /// Given the source_var_id we search for the last assigned debug var_id and
     /// replace it instead.
-    fn patch_debug_var_drop(&mut self, call: &HirCallExpression, arguments: &mut [Expression]) {
+    fn patch_debug_var_drop(
+        &mut self,
+        call: &HirCallExpression,
+        arguments: &mut [Expression],
+    ) -> Result<(), MonomorphizationError> {
         let hir_arguments = vecmap(&call.arguments, |id| self.interner.expression(id));
         let var_id_arg = hir_arguments.get(DEBUG_VAR_ID_ARG_SLOT);
         let Some(HirExpression::Literal(HirLiteral::Integer(source_var_id, _))) = var_id_arg else {
@@ -92,7 +102,8 @@ impl<'interner> Monomorphizer<'interner> {
             .get_var_id(source_var_id)
             .unwrap_or_else(|| unreachable!("failed to find debug variable"));
         let interned_var_id = self.intern_var_id(var_id, &call.location);
-        arguments[DEBUG_VAR_ID_ARG_SLOT] = self.expr(interned_var_id);
+        arguments[DEBUG_VAR_ID_ARG_SLOT] = self.expr(interned_var_id)?;
+        Ok(())
     }
 
     /// Update instrumentation code inserted when assigning to a member of an
@@ -106,7 +117,7 @@ impl<'interner> Monomorphizer<'interner> {
         call: &HirCallExpression,
         arguments: &mut [Expression],
         arity: usize,
-    ) {
+    ) -> Result<(), MonomorphizationError> {
         let hir_arguments = vecmap(&call.arguments, |id| self.interner.expression(id));
         let var_id_arg = hir_arguments.get(DEBUG_VAR_ID_ARG_SLOT);
         let Some(HirExpression::Literal(HirLiteral::Integer(source_var_id, _))) = var_id_arg else {
@@ -149,7 +160,7 @@ impl<'interner> Monomorphizer<'interner> {
                         call.location.span,
                         call.location.file,
                     );
-                    arguments[DEBUG_MEMBER_FIELD_INDEX_ARG_SLOT + i] = self.expr(index_id);
+                    arguments[DEBUG_MEMBER_FIELD_INDEX_ARG_SLOT + i] = self.expr(index_id)?;
                 } else {
                     // array/string element using constant index
                     cursor_type = element_type_at_index(cursor_type, index as usize);
@@ -165,7 +176,8 @@ impl<'interner> Monomorphizer<'interner> {
             .get_var_id(source_var_id)
             .unwrap_or_else(|| unreachable!("failed to find debug variable"));
         let interned_var_id = self.intern_var_id(var_id, &call.location);
-        arguments[DEBUG_VAR_ID_ARG_SLOT] = self.expr(interned_var_id);
+        arguments[DEBUG_VAR_ID_ARG_SLOT] = self.expr(interned_var_id)?;
+        Ok(())
     }
 
     fn intern_var_id(&mut self, var_id: DebugVarId, location: &Location) -> ExprId {
```

### compiler/noirc_frontend/src/monomorphization/mod.rs
```diff
@@ -9,13 +9,14 @@
 //! The entry point to this pass is the `monomorphize` function which, starting from a given
 //! function, will monomorphize the entire reachable program.
 use acvm::FieldElement;
-use iter_extended::{btree_map, vecmap};
-use noirc_errors::Location;
+use iter_extended::{btree_map, try_vecmap, vecmap};
+use noirc_errors::{CustomDiagnostic, FileDiagnostic, Location};
 use noirc_printable_type::PrintableType;
 use std::{
     collections::{BTreeMap, HashMap, VecDeque},
     unreachable,
 };
+use thiserror::Error;
 
 use crate::{
     debug::DebugInstrumenter,
@@ -87,6 +88,40 @@ struct Monomorphizer<'interner> {
 
 type HirType = crate::Type;
 
+#[derive(Debug, Error)]
+pub enum MonomorphizationError {
+    #[error("Length of generic array could not be determined.")]
+    UnknownArrayLength { location: Location },
+}
+
+impl MonomorphizationError {
+    fn call_stack(&self) -> Vec<Location> {
+        match self {
+            MonomorphizationError::UnknownArrayLength { location } => vec![*location],
+        }
+    }
+}
+
+impl From<MonomorphizationError> for FileDiagnostic {
+    fn from(error: MonomorphizationError) -> FileDiagnostic {
+        let call_stack = error.call_stack();
+        let file_id = call_stack.last().map(|location| location.file).unwrap_or_default();
+        let diagnostic = error.into_diagnostic();
+        diagnostic.in_file(file_id).with_call_stack(call_stack)
+    }
+}
+
+impl MonomorphizationError {
+    fn into_diagnostic(self) -> CustomDiagnostic {
+        CustomDiagnostic::simple_error(
+                "Internal Consistency Evaluators Errors: \n
+                This is likely a bug. Consider opening an issue at https://github.com/noir-lang/noir/issues".to_owned(),
+                self.to_string(),
+                noirc_errors::Span::inclusive(0, 0)
+            )
+    }
+}
+
 /// Starting from the given `main` function, monomorphize the entire program,
 /// replacing all references to type variables and NamedGenerics with concrete
 /// types, duplicating definitions as necessary to do so.
@@ -99,26 +134,29 @@ type HirType = crate::Type;
 /// this function. Typically, this is the function named "main" in the source project,
 /// but it can also be, for example, an arbitrary test function for running `nargo test`.
 #[tracing::instrument(level = "trace", skip(main, interner))]
-pub fn monomorphize(main: node_interner::FuncId, interner: &mut NodeInterner) -> Program {
+pub fn monomorphize(
+    main: node_interner::FuncId,
+    interner: &mut NodeInterner,
+) -> Result<Program, MonomorphizationError> {
     monomorphize_debug(main, interner, &DebugInstrumenter::default())
 }
 
 pub fn monomorphize_debug(
     main: node_interner::FuncId,
     interner: &mut NodeInterner,
     debug_instrumenter: &DebugInstrumenter,
-) -> Program {
+) -> Result<Program, MonomorphizationError> {
     let debug_type_tracker = DebugTypeTracker::build_from_debug_instrumenter(debug_instrumenter);
     let mut monomorphizer = Monomorphizer::new(interner, debug_type_tracker);
-    let function_sig = monomorphizer.compile_main(main);
+    let function_sig = monomorphizer.compile_main(main)?;
 
     while !monomorphizer.queue.is_empty() {
         let (next_fn_id, new_id, bindings, trait_method) = monomorphizer.queue.pop_front().unwrap();
         monomorphizer.locals.clear();
 
         perform_instantiation_bindings(&bindings);
         let impl_bindings = monomorphizer.perform_impl_bindings(trait_method, next_fn_id);
-        monomorphizer.function(next_fn_id, new_id);
+        monomorphizer.function(next_fn_id, new_id)?;
         undo_instantiation_bindings(impl_bindings);
         undo_instantiation_bindings(bindings);
     }
@@ -128,7 +166,7 @@ pub fn monomorphize_debug(
         monomorphizer.interner.function_meta(&main);
 
     let (debug_variables, debug_types) = monomorphizer.debug_type_tracker.extract_vars_and_types();
-    Program::new(
+    let program = Program::new(
         functions,
         function_sig,
         *return_distinctness,
@@ -137,7 +175,8 @@ pub fn monomorphize_debug(
         *kind == FunctionKind::Recursive,
         debug_variables,
         debug_types,
-    )
+    );
+    Ok(program)
 }
 
 impl<'interner> Monomorphizer<'interner> {
@@ -233,10 +272,13 @@ impl<'interner> Monomorphizer<'interner> {
         self.globals.entry(id).or_default().insert(typ, new_id);
     }
 
-    fn compile_main(&mut self, main_id: node_interner::FuncId) -> FunctionSignature {
+    fn compile_main(
+        &mut self,
+        main_id: node_interner::FuncId,
+    ) -> Result<FunctionSignature, MonomorphizationError> {
         let new_main_id = self.next_function_id();
         assert_eq!(new_main_id, Program::main_id());
-        self.function(main_id, new_main_id);
+        self.function(main_id, new_main_id)?;
         self.return_location =
             self.interner.function(&main_id).block(self.interner).statements().last().and_then(
                 |x| match self.interner.statement(x) {
@@ -245,10 +287,14 @@ impl<'interner> Monomorphizer<'interner> {
                 },
             );
         let main_meta = self.interner.function_meta(&main_id);
-        main_meta.function_signature()
+        Ok(main_meta.function_signature())
     }
 
-    fn function(&mut self, f: node_interner::FuncId, id: FuncId) {
+    fn function(
+        &mut self,
+        f: node_interner::FuncId,
+        id: FuncId,
+    ) -> Result<(), MonomorphizationError> {
         if let Some((self_type, trait_id)) = self.interner.get_function_trait(&f) {
             let the_trait = self.interner.get_trait(trait_id);
             the_trait.self_type_typevar.force_bind(self_type);
@@ -268,10 +314,11 @@ impl<'interner> Monomorphizer<'interner> {
             || matches!(modifiers.contract_function_type, Some(ContractFunctionType::Open));
 
         let parameters = self.parameters(&meta.parameters);
-        let body = self.expr(body_expr_id);
+        let body = self.expr(body_expr_id)?;
         let function = ast::Function { id, name, parameters, body, return_type, unconstrained };
 
         self.push_function(id, function);
+        Ok(())
     }
 
     fn push_function(&mut self, id: FuncId, function: ast::Function) {
@@ -331,15 +378,18 @@ impl<'interner> Monomorphizer<'interner> {
         }
     }
 
-    fn expr(&mut self, expr: node_interner::ExprId) -> ast::Expression {
+    fn expr(
+        &mut self,
+        expr: node_interner::ExprId,
+    ) -> Result<ast::Expression, MonomorphizationError> {
         use ast::Expression::Literal;
         use ast::Literal::*;
 
-        match self.interner.expression(&expr) {
-            HirExpression::Ident(ident) => self.ident(ident, expr),
+        let expr = match self.interner.expression(&expr) {
+            HirExpression::Ident(ident) => self.ident(ident, expr)?,
             HirExpression::Literal(HirLiteral::Str(contents)) => Literal(Str(contents)),
             HirExpression::Literal(HirLiteral::FmtStr(contents, idents)) => {
-                let fields = vecmap(idents, |ident| self.expr(ident));
+                let fields = try_vecmap(idents, |ident| self.expr(ident))?;
                 Literal(FmtStr(
                     contents,
                     fields.len() as u64,
@@ -367,27 +417,27 @@ impl<'interner> Monomorphizer<'interner> {
                 }
             }
             HirExpression::Literal(HirLiteral::Array(array)) => match array {
-                HirArrayLiteral::Standard(array) => self.standard_array(expr, array),
+                HirArrayLiteral::Standard(array) => self.standard_array(expr, array)?,
                 HirArrayLiteral::Repeated { repeated_element, length } => {
-                    self.repeated_array(expr, repeated_element, length)
+                    self.repeated_array(expr, repeated_element, length)?
                 }
             },
             HirExpression::Literal(HirLiteral::Unit) => ast::Expression::Block(vec![]),
-            HirExpression::Block(block) => self.block(block.0),
+            HirExpression::Block(block) => self.block(block.0)?,
 
             HirExpression::Prefix(prefix) => {
                 let location = self.interner.expr_location(&expr);
                 ast::Expression::Unary(ast::Unary {
                     operator: prefix.operator,
-                    rhs: Box::new(self.expr(prefix.rhs)),
+                    rhs: Box::new(self.expr(prefix.rhs)?),
                     result_type: self.convert_type(&self.interner.id_type(expr)),
                     location,
                 })
             }
 
             HirExpression::Infix(infix) => {
-                let lhs = self.expr(infix.lhs);
-                let rhs = self.expr(infix.rhs);
+                let lhs = self.expr(infix.lhs)?;
+                let rhs = self.expr(infix.rhs)?;
                 let operator = infix.operator.kind;
                 let location = self.interner.expr_location(&expr);
                 if self.interner.get_selected_impl_for_expression(expr).is_some() {
@@ -418,26 +468,27 @@ impl<'interner> Monomorphizer<'interner> {
                 }
             }
 
-            HirExpression::Index(index) => self.index(expr, index),
+            HirExpression::Index(index) => self.index(expr, index)?,
 
             HirExpression::MemberAccess(access) => {
                 let field_index = self.interner.get_field_index(expr);
-                let expr = Box::new(self.expr(access.lhs));
+                let expr = Box::new(self.expr(access.lhs)?);
                 ast::Expression::ExtractTupleField(expr, field_index)
             }
 
-            HirExpression::Call(call) => self.function_call(call, expr),
+            HirExpression::Call(call) => self.function_call(call, expr)?,
 
             HirExpression::Cast(cast) => ast::Expression::Cast(ast::Cast {
-                lhs: Box::new(self.expr(cast.lhs)),
+                lhs: Box::new(self.expr(cast.lhs)?),
                 r#type: self.convert_type(&cast.r#type),
                 location: self.interner.expr_location(&expr),
             }),
 
             HirExpression::If(if_expr) => {
-                let cond = self.expr(if_expr.condition);
-                let then = self.expr(if_expr.consequence);
-                let else_ = if_expr.alternative.map(|alt| Box::new(self.expr(alt)));
+                let cond = self.expr(if_expr.condition)?;
+                let then = self.expr(if_expr.consequence)?;
+                let else_ =
+                    if_expr.alternative.map(|alt| self.expr(alt)).transpose()?.map(Box::new);
                 ast::Expression::If(ast::If {
                     condition: Box::new(cond),
                     consequence: Box::new(then),
@@ -447,77 +498,87 @@ impl<'interner> Monomorphizer<'interner> {
             }
 
             HirExpression::Tuple(fields) => {
-                let fields = vecmap(fields, |id| self.expr(id));
+                let fields = try_vecmap(fields, |id| self.expr(id))?;
                 ast::Expression::Tuple(fields)
             }
-            HirExpression::Constructor(constructor) => self.constructor(constructor, expr),
+            HirExpression::Constructor(constructor) => self.constructor(constructor, expr)?,
 
-            HirExpression::Lambda(lambda) => self.lambda(lambda, expr),
+            HirExpression::Lambda(lambda) => self.lambda(lambda, expr)?,
 
             HirExpression::MethodCall(hir_method_call) => {
                 unreachable!("Encountered HirExpression::MethodCall during monomorphization {hir_method_call:?}")
             }
             HirExpression::Error => unreachable!("Encountered Error node during monomorphization"),
-        }
+        };
+
+        Ok(expr)
     }
 
     fn standard_array(
         &mut self,
         array: node_interner::ExprId,
         array_elements: Vec<node_interner::ExprId>,
-    ) -> ast::Expression {
+    ) -> Result<ast::Expression, MonomorphizationError> {
         let typ = self.convert_type(&self.interner.id_type(array));
-        let contents = vecmap(array_elements, |id| self.expr(id));
-        ast::Expression::Literal(ast::Literal::Array(ast::ArrayLiteral { contents, typ }))
+        let contents = try_vecmap(array_elements, |id| self.expr(id))?;
+        Ok(ast::Expression::Literal(ast::Literal::Array(ast::ArrayLiteral { contents, typ })))
     }
 
     fn repeated_array(
         &mut self,
         array: node_interner::ExprId,
         repeated_element: node_interner::ExprId,
         length: HirType,
-    ) -> ast::Expression {
+    ) -> Result<ast::Expression, MonomorphizationError> {
         let typ = self.convert_type(&self.interner.id_type(array));
 
-        let length = length
-            .evaluate_to_u64()
-            .expect("Length of array is unknown when evaluating numeric generic");
+        let length = length.evaluate_to_u64().ok_or_else(|| {
+            let location = self.interner.expr_location(&array);
+            MonomorphizationError::UnknownArrayLength { location }
+        })?;
 
-        let contents = vecmap(0..length, |_| self.expr(repeated_element));
-        ast::Expression::Literal(ast::Literal::Array(ast::ArrayLiteral { contents, typ }))
+        let contents = try_vecmap(0..length, |_| self.expr(repeated_element))?;
+        Ok(ast::Expression::Literal(ast::Literal::Array(ast::ArrayLiteral { contents, typ })))
     }
 
-    fn index(&mut self, id: node_interner::ExprId, index: HirIndexExpression) -> ast::Expression {
+    fn index(
+        &mut self,
+        id: node_interner::ExprId,
+        index: HirIndexExpression,
+    ) -> Result<ast::Expression, MonomorphizationError> {
         let element_type = self.convert_type(&self.interner.id_type(id));
 
-        let collection = Box::new(self.expr(index.collection));
-        let index = Box::new(self.expr(index.index));
+        let collection = Box::new(self.expr(index.collection)?);
+        let index = Box::new(self.expr(index.index)?);
         let location = self.interner.expr_location(&id);
-        ast::Expression::Index(ast::Index { collection, index, element_type, location })
+        Ok(ast::Expression::Index(ast::Index { collection, index, element_type, location }))
     }
 
-    fn statement(&mut self, id: StmtId) -> ast::Expression {
+    fn statement(&mut self, id: StmtId) -> Result<ast::Expression, MonomorphizationError> {
         match self.interner.statement(&id) {
             HirStatement::Let(let_statement) => self.let_statement(let_statement),
             HirStatement::Constrain(constrain) => {
-                let expr = self.expr(constrain.0);
+                let expr = self.expr(constrain.0)?;
                 let location = self.interner.expr_location(&constrain.0);
-                let assert_message =
-                    constrain.2.map(|assert_msg_expr| Box::new(self.expr(assert_msg_expr)));
-                ast::Expression::Constrain(Box::new(expr), location, assert_message)
+                let assert_message = constrain
+                    .2
+                    .map(|assert_msg_expr| self.expr(assert_msg_expr))
+                    .transpose()?
+                    .map(Box::new);
+                Ok(ast::Expression::Constrain(Box::new(expr), location, assert_message))
             }
             HirStatement::Assign(assign) => self.assign(assign),
             HirStatement::For(for_loop) => {
                 self.is_range_loop = true;
-                let start = self.expr(for_loop.start_range);
-                let end = self.expr(for_loop.end_range);
+                let start = self.expr(for_loop.start_range)?;
+                let end = self.expr(for_loop.end_range)?;
                 self.is_range_loop = false;
                 let index_variable = self.next_local_id();
                 self.define_local(for_loop.identifier.id, index_variable);
 
-                let block = Box::new(self.expr(for_loop.block));
+                let block = Box::new(self.expr(for_loop.block)?);
 
-                ast::Expression::For(ast::For {
+                Ok(ast::Expression::For(ast::For {
                     index_variable,
                     index_name: self.interner.definition_name(for_loop.identifier.id).to_owned(),
                     index_type: self.convert_type(&self.interner.id_type(for_loop.start_range)),
@@ -526,25 +587,30 @@ impl<'interner> Monomorphizer<'interner> {
                     start_range_location: self.interner.expr_location(&for_loop.start_range),
                     end_range_location: self.interner.expr_location(&for_loop.end_range),
                     block,
-                })
+                }))
             }
             HirStatement::Expression(expr) => self.expr(expr),
-            HirStatement::Semi(expr) => ast::Expression::Semi(Box::new(self.expr(expr))),
+            HirStatement::Semi(expr) => {
+                self.expr(expr).map(|expr| ast::Expression::Semi(Box::new(expr)))
+            }
             HirStatement::Error => unreachable!(),
         }
     }
 
-    fn let_statement(&mut self, let_statement: HirLetStatement) -> ast::Expression {
-        let expr = self.expr(let_statement.expression);
+    fn let_statement(
+        &mut self,
+        let_statement: HirLetStatement,
+    ) -> Result<ast::Expression, MonomorphizationError> {
+        let expr = self.expr(let_statement.expression)?;
         let expected_type = self.interner.id_type(let_statement.expression);
-        self.unpack_pattern(let_statement.pattern, expr, &expected_type)
+        Ok(self.unpack_pattern(let_statement.pattern, expr, &expected_type))
     }
 
     fn constructor(
         &mut self,
         constructor: HirConstructorExpression,
         id: node_interner::ExprId,
-    ) -> ast::Expression {
+    ) -> Result<ast::Expression, MonomorphizationError> {
         let typ = self.interner.id_type(id);
         let field_types = unwrap_struct_type(&typ);
 
@@ -561,7 +627,7 @@ impl<'interner> Monomorphizer<'interner> {
             let typ = self.convert_type(field_type);
 
             field_vars.insert(field_name.0.contents.clone(), (new_id, typ));
-            let expression = Box::new(self.expr(expr_id));
+            let expression = Box::new(self.expr(expr_id)?);
 
             new_exprs.push(ast::Expression::Let(ast::Let {
                 id: new_id,
@@ -586,11 +652,15 @@ impl<'interner> Monomorphizer<'interner> {
 
         // Finally we can return the created Tuple from the new block
         new_exprs.push(ast::Expression::Tuple(field_idents));
-        ast::Expression::Block(new_exprs)
+        Ok(ast::Expression::Block(new_exprs))
     }
 
-    fn block(&mut self, statement_ids: Vec<StmtId>) -> ast::Expression {
-        ast::Expression::Block(vecmap(statement_ids, |id| self.statement(id)))
+    fn block(
+        &mut self,
+        statement_ids: Vec<StmtId>,
+    ) -> Result<ast::Expression, MonomorphizationError> {
+        let stmts = try_vecmap(statement_ids, |id| self.statement(id));
+        stmts.map(ast::Expression::Block)
     }
 
     fn unpack_pattern(
@@ -701,15 +771,19 @@ impl<'interner> Monomorphizer<'interner> {
         Some(ast::Ident { location: Some(ident.location), mutable, definition, name, typ })
     }
 
-    fn ident(&mut self, ident: HirIdent, expr_id: node_interner::ExprId) -> ast::Expression {
+    fn ident(
+        &mut self,
+        ident: HirIdent,
+        expr_id: node_interner::ExprId,
+    ) -> Result<ast::Expression, MonomorphizationError> {
         let typ = self.interner.id_type(expr_id);
 
         if let ImplKind::TraitMethod(method, _, _) = ident.impl_kind {
-            return self.resolve_trait_method_reference(expr_id, typ, method);
+            return Ok(self.resolve_trait_method_reference(expr_id, typ, method));
         }
 
         let definition = self.interner.definition(ident.id);
-        match &definition.kind {
+        let ident = match &definition.kind {
             DefinitionKind::Function(func_id) => {
                 let mutable = definition.mutable;
                 let location = Some(ident.location);
@@ -736,7 +810,7 @@ impl<'interner> Monomorphizer<'interner> {
                         "Globals should have a corresponding let statement by monomorphization"
                     )
                 };
-                self.expr(let_.expression)
+                self.expr(let_.expression)?
             }
             DefinitionKind::Local(_) => self.lookup_captured_expr(ident.id).unwrap_or_else(|| {
                 let ident = self.local_ident(&ident).unwrap();
@@ -757,7 +831,9 @@ impl<'interner> Monomorphizer<'interner> {
                 let typ = self.convert_type(&typ);
                 ast::Expression::Literal(ast::Literal::Integer(value, typ, location))
             }
-        }
+        };
+
+        Ok(ident)
     }
 
     /// Convert a non-tuple/struct type to a monomorphized type
@@ -949,12 +1025,12 @@ impl<'interner> Monomorphizer<'interner> {
         &mut self,
         call: HirCallExpression,
         id: node_interner::ExprId,
-    ) -> ast::Expression {
-        let original_func = Box::new(self.expr(call.func));
-        let mut arguments = vecmap(&call.arguments, |id| self.expr(*id));
+    ) -> Result<ast::Expression, MonomorphizationError> {
+        let original_func = Box::new(self.expr(call.func)?);
+        let mut arguments = try_vecmap(&call.arguments, |id| self.expr(*id))?;
         let hir_arguments = vecmap(&call.arguments, |id| self.interner.expression(id));
 
-        self.patch_debug_instrumentation_call(&call, &mut arguments);
+        self.patch_debug_instrumentation_call(&call, &mut arguments)?;
 
         let return_type = self.interner.id_type(id);
         let return_type = self.convert_type(&return_type);
@@ -969,7 +1045,7 @@ impl<'interner> Monomorphizer<'interner> {
                     // The second argument is expected to always be an ident
                     self.append_printable_type_info(&hir_arguments[1], &mut arguments);
                 } else if name.as_str() == "assert_message" {
-                    // The first argument to the `assert_message` oracle is the expression passed as a mesage to an `assert` or `assert_eq` statement
+                    // The first argument to the `assert_message` oracle is the expression passed as a message to an `assert` or `assert_eq` statement
                     self.append_printable_type_info(&hir_arguments[0], &mut arguments);
                 }
             }
@@ -1017,9 +1093,9 @@ impl<'interner> Monomorphizer<'interner> {
 
         if !block_expressions.is_empty() {
             block_expressions.push(call);
-            ast::Expression::Block(block_expressions)
+            Ok(ast::Expression::Block(block_expressions))
         } else {
-            call
+            Ok(call)
         }
     }
 
@@ -1190,47 +1266,59 @@ impl<'interner> Monomorphizer<'interner> {
             .collect()
     }
 
-    fn assign(&mut self, assign: HirAssignStatement) -> ast::Expression {
-        let expression = Box::new(self.expr(assign.expression));
-        let lvalue = self.lvalue(assign.lvalue);
-        ast::Expression::Assign(ast::Assign { expression, lvalue })
+    fn assign(
+        &mut self,
+        assign: HirAssignStatement,
+    ) -> Result<ast::Expression, MonomorphizationError> {
+        let expression = Box::new(self.expr(assign.expression)?);
+        let lvalue = self.lvalue(assign.lvalue)?;
+        Ok(ast::Expression::Assign(ast::Assign { expression, lvalue }))
     }
 
-    fn lvalue(&mut self, lvalue: HirLValue) -> ast::LValue {
-        match lvalue {
+    fn lvalue(&mut self, lvalue: HirLValue) -> Result<ast::LValue, MonomorphizationError> {
+        let value = match lvalue {
             HirLValue::Ident(ident, _) => self
                 .lookup_captured_lvalue(ident.id)
                 .unwrap_or_else(|| ast::LValue::Ident(self.local_ident(&ident).unwrap())),
             HirLValue::MemberAccess { object, field_index, .. } => {
                 let field_index = field_index.unwrap();
-                let object = Box::new(self.lvalue(*object));
+                let object = Box::new(self.lvalue(*object)?);
                 ast::LValue::MemberAccess { object, field_index }
             }
             HirLValue::Index { array, index, typ } => {
                 let location = self.interner.expr_location(&index);
-                let array = Box::new(self.lvalue(*array));
-                let index = Box::new(self.expr(index));
+                let array = Box::new(self.lvalue(*array)?);
+                let index = Box::new(self.expr(index)?);
                 let element_type = self.convert_type(&typ);
                 ast::LValue::Index { array, index, element_type, location }
             }
             HirLValue::Dereference { lvalue, element_type } => {
-                let reference = Box::new(self.lvalue(*lvalue));
+                let reference = Box::new(self.lvalue(*lvalue)?);
                 let element_type = self.convert_type(&element_type);
                 ast::LValue::Dereference { reference, element_type }
             }
-        }
+        };
+
+        Ok(value)
     }
 
-    fn lambda(&mut self, lambda: HirLambda, expr: node_interner::ExprId) -> ast::Expression {
+    fn lambda(
+        &mut self,
+        lambda: HirLambda,
+        expr: node_interner::ExprId,
+    ) -> Result<ast::Expression, MonomorphizationError> {
         if lambda.captures.is_empty() {
             self.lambda_no_capture(lambda)
         } else {
-            let (setup, closure_variable) = self.lambda_with_setup(lambda, expr);
-            ast::Expression::Block(vec![setup, closure_variable])
+            let (setup, closure_variable) = self.lambda_with_setup(lambda, expr)?;
+            Ok(ast::Expression::Block(vec![setup, closure_variable]))
         }
     }
 
-    fn lambda_no_capture(&mut self, lambda: HirLambda) -> ast::Expression {
+    fn lambda_no_capture(
+        &mut self,
+        lambda: HirLambda,
+    ) -> Result<ast::Expression, MonomorphizationError> {
         let ret_type = self.convert_type(&lambda.return_type);
         let lambda_name = "lambda";
         let parameter_types = vecmap(&lambda.parameters, |(_, typ)| self.convert_type(typ));
@@ -1240,7 +1328,7 @@ impl<'interner> Monomorphizer<'interner> {
             vecmap(lambda.parameters, |(pattern, typ)| (pattern, typ, Visibility::Private)).into();
 
         let parameters = self.parameters(&parameters);
-        let body = self.expr(lambda.body);
+        let body = self.expr(lambda.body)?;
 
         let id = self.next_function_id();
         let return_type = ret_type.clone();
@@ -1254,20 +1342,20 @@ impl<'interner> Monomorphizer<'interner> {
             ast::Type::Function(parameter_types, Box::new(ret_type), Box::new(ast::Type::Unit));
 
         let name = lambda_name.to_owned();
-        ast::Expression::Ident(ast::Ident {
+        Ok(ast::Expression::Ident(ast::Ident {
             definition: Definition::Function(id),
             mutable: false,
             location: None,
             name,
             typ,
-        })
+        }))
     }
 
     fn lambda_with_setup(
         &mut self,
         lambda: HirLambda,
         expr: node_interner::ExprId,
-    ) -> (ast::Expression, ast::Expression) {
+    ) -> Result<(ast::Expression, ast::Expression), MonomorphizationError> {
         // returns (<closure setup>, <closure variable>)
         //   which can be used directly in callsites or transformed
         //   directly to a single `Expression`
@@ -1343,7 +1431,7 @@ impl<'interner> Monomorphizer<'interner> {
 
         self.lambda_envs_stack
             .push(LambdaContext { env_ident: env_ident.clone(), captures: lambda.captures });
-        let body = self.expr(lambda.body);
+        let body = self.expr(lambda.body)?;
         self.lambda_envs_stack.pop();
 
         let lambda_fn_typ: ast::Type =
@@ -1385,7 +1473,7 @@ impl<'interner> Monomorphizer<'interner> {
             typ: ast::Type::Tuple(vec![env_typ, lambda_fn_typ]),
         });
 
-        (block_let_stmt, closure_ident)
+        Ok((block_let_stmt, closure_ident))
     }
 
     /// Implements std::unsafe::zeroed by returning an appropriate zeroed
```

### compiler/noirc_frontend/src/tests.rs
```diff
@@ -1130,7 +1130,7 @@ mod test {
     fn check_rewrite(src: &str, expected: &str) {
         let (_program, mut context, _errors) = get_program(src);
         let main_func_id = context.def_interner.find_function("main").unwrap();
-        let program = monomorphize(main_func_id, &mut context.def_interner);
+        let program = monomorphize(main_func_id, &mut context.def_interner).unwrap();
         assert!(format!("{}", program) == expected);
     }
 
```

### tooling/nargo/src/ops/test.rs
```diff
@@ -1,5 +1,5 @@
 use acvm::{acir::native_types::WitnessMap, BlackBoxFunctionSolver};
-use noirc_driver::{compile_no_check, CompileOptions};
+use noirc_driver::{compile_no_check, CompileError, CompileOptions};
 use noirc_errors::{debug_info::DebugInfo, FileDiagnostic};
 use noirc_evaluator::errors::RuntimeError;
 use noirc_frontend::hir::{def_map::TestFunction, Context};
@@ -45,14 +45,18 @@ pub fn run_test<B: BlackBoxFunctionSolver>(
 /// that a constraint was never satisfiable.
 /// An example of this is the program `assert(false)`
 /// In that case, we check if the test function should fail, and if so, we return `TestStatus::Pass`.
-fn test_status_program_compile_fail(err: RuntimeError, test_function: TestFunction) -> TestStatus {
+fn test_status_program_compile_fail(err: CompileError, test_function: TestFunction) -> TestStatus {
     // The test has failed compilation, but it should never fail. Report error.
     if !test_function.should_fail() {
         return TestStatus::CompileError(err.into());
     }
 
     // The test has failed compilation, extract the assertion message if present and check if it's expected.
-    let assert_message = if let RuntimeError::FailedConstraint { assert_message, .. } = &err {
+    let assert_message = if let CompileError::RuntimeError(RuntimeError::FailedConstraint {
+        assert_message,
+        ..
+    }) = &err
+    {
         assert_message.clone()
     } else {
         None
```
