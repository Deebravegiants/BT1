# [?] fix(fuzz): Handle overflow errors from the elaborator (#9014)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-25
Source: https://github.com/noir-lang/noir/commit/e25b5d7d135ca6f6da63ac46ed83d0c50579f6cc
Type: security-commit

## Details
fix(fuzz): Handle overflow errors from the elaborator (#9014)

## Patch
### Cargo.lock
```diff
@@ -3404,6 +3404,7 @@ dependencies = [
  "noir_greybox_fuzzer",
  "noirc_abi",
  "noirc_driver",
+ "noirc_errors",
  "noirc_evaluator",
  "noirc_frontend",
  "proptest",
```

### tooling/ast_fuzzer/Cargo.toml
```diff
@@ -31,6 +31,7 @@ iter-extended.workspace = true
 nargo.workspace = true
 noirc_abi.workspace = true
 noirc_driver.workspace = true
+noirc_errors.workspace = true
 noirc_evaluator.workspace = true
 noirc_frontend = { workspace = true, features = ["test_utils"] }
 noir_greybox_fuzzer.workspace = true
```

### tooling/ast_fuzzer/src/compare/comptime.rs
```diff
@@ -4,6 +4,8 @@ use std::path::Path;
 use std::rc::Rc;
 use std::{cell::RefCell, collections::BTreeMap};
 
+use acir::FieldElement;
+use acir::native_types::WitnessMap;
 use arbitrary::Unstructured;
 use bn254_blackbox_solver::Bn254BlackBoxSolver;
 use color_eyre::eyre::{self, WrapErr};
@@ -15,10 +17,14 @@ use noirc_driver::{
     CompilationResult, CompileOptions, CompiledProgram, CrateId, compile_main,
     file_manager_with_stdlib, prepare_crate,
 };
+use noirc_errors::CustomDiagnostic;
 use noirc_evaluator::ssa::SsaProgramArtifact;
+use noirc_frontend::elaborator::ElaboratorError;
+use noirc_frontend::hir::def_collector::dc_crate::CompilationError;
 use noirc_frontend::{elaborator::interpret, hir::Context, monomorphization::ast::Program};
 
 use super::{CompareArtifact, CompareCompiledResult, CompareOptions, HasPrograms};
+use crate::compare::compiled::ExecResult;
 use crate::{
     Config, DisplayAstAsNoirComptime, arb_program_comptime, program_abi, program_wrap_expression,
 };
@@ -84,81 +90,68 @@ impl CompareComptime {
         &self,
         f_comptime: impl FnOnce(Program) -> arbitrary::Result<(SsaProgramArtifact, CompareOptions)>,
     ) -> eyre::Result<CompareCompiledResult> {
+        let initial_witness = self.input_witness()?;
+        let (res2, _) = Self::exec_bytecode(&self.ssa.artifact.program, initial_witness.clone());
+
+        // TODO(#8973): The print output is currently not captured by the elaborator, so we have to ignore it.
+        let empty_print = "";
+
         // log source code before interpreting
         log::debug!("comptime src:\n{}", self.source);
-
-        let comptime_res = match interpret(&format!("comptime {}", self.source)) {
+        let comptime_expr = match interpret(&format!("comptime {}", self.source)) {
+            Ok(expr) => expr,
             Err(e) => {
-                panic!("elaborator error while interpreting generated comptime code: {:?}", e)
+                let assertion_diagnostic = match &e {
+                    ElaboratorError::Compile(errors) => errors
+                        .iter()
+                        .map(CustomDiagnostic::from)
+                        .find(Self::is_assertion_diagnostic),
+
+                    ElaboratorError::Interpret(e) => {
+                        let e = CompilationError::from(e.clone());
+                        let e = CustomDiagnostic::from(&e);
+                        Self::is_assertion_diagnostic(&e).then_some(e)
+                    }
+                    _ => None,
+                };
+
+                if let Some(e) = assertion_diagnostic {
+                    return self.comptime_failure(
+                        &e,
+                        empty_print.into(),
+                        (res2, empty_print.into()),
+                    );
+                } else {
+                    panic!(
+                        "elaborator error while interpreting generated comptime code: {e:?}\n{}",
+                        self.source
+                    );
+                }
             }
-            Ok(res) => res,
         };
 
-        let program_comptime = program_wrap_expression(comptime_res)?;
+        let program_comptime = program_wrap_expression(comptime_expr);
         let comptime_ssa = CompareArtifact::from(f_comptime(program_comptime)?);
 
-        let blackbox_solver = Bn254BlackBoxSolver(false);
-        let initial_witness = self.abi.encode(&BTreeMap::new(), None).wrap_err("abi::encode")?;
-
-        let do_exec = |program| {
-            let mut print = Vec::new();
-
-            let mut foreign_call_executor = DefaultForeignCallBuilder::default()
-                .with_mocks(false)
-                .with_output(&mut print)
-                .build();
-
-            nargo::ops::execute_program(
-                program,
-                initial_witness.clone(),
-                &blackbox_solver,
-                &mut foreign_call_executor,
-            )
-        };
-
-        let res1 = do_exec(&comptime_ssa.artifact.program);
-        let res2 = do_exec(&self.ssa.artifact.program);
+        let (res1, _) =
+            Self::exec_bytecode(&comptime_ssa.artifact.program, initial_witness.clone());
 
         CompareCompiledResult::new(
             &self.abi,
             &Default::default(),
             &self.ssa.artifact.error_types,
-            (res1, "".into()),
-            (res2, "".into()),
+            (res1, empty_print.into()),
+            (res2, empty_print.into()),
         )
     }
 
     /// Execute the Noir code (via nargo) and the SSA, then compare the results.
     pub fn exec(&self) -> eyre::Result<CompareCompiledResult> {
-        let blackbox_solver = Bn254BlackBoxSolver(false);
-
-        // These comptime programs have no inputs.
-        let initial_witness = self.abi.encode(&BTreeMap::new(), None).wrap_err("abi::encode")?;
-
-        let decode_print = |print| String::from_utf8(print).expect("should be valid utf8 string");
-
-        // Execute a compiled Program.
-        let do_exec = |program| {
-            let mut output = Vec::new();
-
-            let mut foreign_call_executor = DefaultForeignCallBuilder::default()
-                .with_mocks(false)
-                .with_output(&mut output)
-                .build();
-
-            let res = nargo::ops::execute_program(
-                program,
-                initial_witness.clone(),
-                &blackbox_solver,
-                &mut foreign_call_executor,
-            );
-            let print = decode_print(output);
-
-            (res, print)
-        };
+        let initial_witness = self.input_witness()?;
 
         // Execute the 2nd (Brillig) program.
-        let (res2, print2) = do_exec(&self.ssa.artifact.program);
+        let (res2, print2) =
+            Self::exec_bytecode(&self.ssa.artifact.program, initial_witness.clone());
 
         // Try to compile the 1st (comptime) version from string.
         log::debug!("comptime src:\n{}", self.source);
@@ -168,40 +161,23 @@ impl CompareComptime {
             Vec::new(),
         ) {
             (Ok((program, _)), output) => (program, output),
-            (Err(e), output) => {
+            (Err(errors), output) => {
                 // If the comptime code failed to compile, it could be because it executed the code
                 // and encountered an overflow, which would be a runtime error in Brillig.
-                let is_assertion = e.iter().any(|e| {
-                    e.secondaries.iter().any(|s| s.message == "Assertion failed")
-                        || e.message.contains("overflow")
-                        || e.message.contains("divide by zero")
-                });
-                if is_assertion {
-                    let msg = format!("{e:?}");
-                    let err = ExecutionError::AssertionFailed(
-                        acvm::pwg::ResolvedAssertionPayload::String(msg),
-                        vec![],
-                        None,
-                    );
-                    let res1 = Err(NargoError::ExecutionError(err));
-                    let print1 = decode_print(output);
-                    return CompareCompiledResult::new(
-                        &self.abi,
-                        &Default::default(), // We failed to compile the program, so no error types.
-                        &self.ssa.artifact.error_types,
-                        (res1, print1),
-                        (res2, print2),
-                    );
+                let assertion_diagnostic = errors.iter().find(|e| Self::is_assertion_diagnostic(e));
+
+                if let Some(e) = assertion_diagnostic {
+                    return self.comptime_failure(e, Self::decode_print(output), (res2, print2));
                 } else {
-                    panic!("failed to compile program:\n{e:?}\n{}", self.source);
+                    panic!("failed to compile program:\n{errors:?}\n{}", self.source);
                 }
             }
         };
-        // Capture any println that happened during the compilation, which in these tests should be the whole program.
-        let comptime_print = String::from_utf8(output1).expect("should be valid utf8 string");
 
-        // Execute the 1st (comptime) program.
-        let (res1, print1) = do_exec(&program1.program);
+        // Capture any println that happened during the compilation, which in these tests should be the whole program.
+        let comptime_print = Self::decode_print(output1);
+        // Execute the 1st (comptime) program, capturing the rest of the output.
+        let (res1, print1) = Self::exec_bytecode(&program1.program, initial_witness);
 
         CompareCompiledResult::new(
             &self.abi,
@@ -229,6 +205,69 @@ impl CompareComptime {
 
         Ok(Self { program, abi, source, ssa, force_brillig })
     }
+
+    /// Execute the program bytecode, returning the execution result along with the captured print output.
+    fn exec_bytecode(
+        program: &acir::circuit::Program<FieldElement>,
+        initial_witness: WitnessMap<FieldElement>,
+    ) -> ExecResult {
+        let blackbox_solver = Bn254BlackBoxSolver(false);
+        let mut output = Vec::new();
+
+        let mut foreign_call_executor =
+            DefaultForeignCallBuilder::default().with_mocks(false).with_output(&mut output).build();
+
+        let res = nargo::ops::execute_program(
+            program,
+            initial_witness,
+            &blackbox_solver,
+            &mut foreign_call_executor,
+        );
+        let print = Self::decode_print(output);
+
+        (res, print)
+    }
+
+    /// Decode the print output into a string.
+    fn decode_print(output: Vec<u8>) -> String {
+        String::from_utf8(output).expect("should be valid utf8 string")
+    }
+
+    /// Comptime test programs have no inputs.
+    fn input_witness(&self) -> eyre::Result<WitnessMap<FieldElement>> {
+        self.abi.encode(&BTreeMap::new(), None).wrap_err("abi::encode")
+    }
+
+    /// Check if a comptime error is due to some kind of arithmetic or constraint failure.
+    fn is_assertion_diagnostic(e: &CustomDiagnostic) -> bool {
+        e.secondaries.iter().any(|s| s.message == "Assertion failed")
+            || e.message.contains("overflow")
+            || e.message.contains("divide by zero")
+    }
+
+    /// Fabricate a result from a comptime `CustomDiagnostic` on the 1st side,
+    /// and a full `ExecResult` on the 2nd side.
+    fn comptime_failure(
+        &self,
+        e: &CustomDiagnostic,
+        print1: String,
+        (res2, print2): ExecResult,
+    ) -> eyre::Result<CompareCompiledResult> {
+        let msg = format!("{e:?}");
+        let err = ExecutionError::AssertionFailed(
+            acvm::pwg::ResolvedAssertionPayload::String(msg),
+            vec![],
+            None,
+        );
+        let res1 = Err(NargoError::ExecutionError(err));
+        CompareCompiledResult::new(
+            &self.abi,
+            &Default::default(), // We failed to compile the program, so no error types.
+            &self.ssa.artifact.error_types,
+            (res1, print1),
+            (res2, print2),
+        )
+    }
 }
 
 impl HasPrograms for CompareComptime {
```

### tooling/ast_fuzzer/src/program/mod.rs
```diff
@@ -73,7 +73,7 @@ pub fn arb_program_comptime(u: &mut Unstructured, config: Config) -> arbitrary::
 /// Build a program with the single `main` function returning
 /// the result of a given expression (used for conversion of the
 /// comptime interpreter execution results for comparison)
-pub fn program_wrap_expression(expr: Expression) -> arbitrary::Result<Program> {
+pub fn program_wrap_expression(expr: Expression) -> Program {
     let mut ctx = Context::new(Config::default());
 
     let decl_main = FunctionDeclaration {
@@ -86,12 +86,10 @@ pub fn program_wrap_expression(expr: Expression) -> arbitrary::Result<Program> {
     };
 
     ctx.set_function_decl(FuncId(0), decl_main);
-    ctx.gen_function_with_body(&mut Unstructured::new(&[]), FuncId(0), |_u, _fctx| {
-        Ok(expr.clone())
-    })?;
+    ctx.gen_function_with_body(&mut Unstructured::new(&[]), FuncId(0), |_u, _fctx| Ok(expr))
+        .expect("shouldn't access any randomness");
 
-    let program = ctx.finalize();
-    Ok(program)
+    ctx.finalize()
 }
 
 /// ID of variables in scope.
@@ -344,7 +342,7 @@ impl Context {
         &mut self,
         u: &mut Unstructured,
         id: FuncId,
-        f: impl Fn(&mut Unstructured, FunctionContext) -> arbitrary::Result<Expression>,
+        f: impl FnOnce(&mut Unstructured, FunctionContext) -> arbitrary::Result<Expression>,
     ) -> arbitrary::Result<()> {
         let fctx = FunctionContext::new(self, id);
         let body = f(u, fctx)?;
```
