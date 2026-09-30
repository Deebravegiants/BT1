# [?] fix: Prevent debugger crashing on circuits with no opcodes (#4283)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-02-06
Source: https://github.com/noir-lang/noir/commit/2e328454054a7c90b8b762b7c9ff0823eb0997c5
Type: security-commit

## Details
fix: Prevent debugger crashing on circuits with no opcodes (#4283)

# Description

## Problem\*

Resolves #4231

The REPL debugger is not handling the case when the compiled circuit has
no opcodes and since it assumes there will be some opcodes, it panics on
continue.

## Summary\*

With this PR, the REPL debugger will start in a "finished" stated in
those cases and the DAP will not start the main loop.

## Additional Context

This edge case is very unlikely to happen, especially after applying
#4185 which changes the default mode for the debugger to Brillig (seems
to generate at least a trampoline-like fragment even for empty programs)
and after the introduction of debugging instrumentation. Nevertheless it
will still be possible (eg. empty program and passing `--acir-mode`
option).

## Documentation\*

Check one:
- [X] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[Exceptional Case]** Documentation to be submitted in a separate
PR.

# PR Checklist\*

- [X] I have tested the changes locally.
- [X] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### tooling/debugger/src/dap.rs
```diff
@@ -125,9 +125,9 @@ impl<'a, R: Read, W: Write, B: BlackBoxFunctionSolver> DapSession<'a, R, W, B> {
     }
 
     pub fn run_loop(&mut self) -> Result<(), ServerError> {
-        self.running = true;
+        self.running = self.context.get_current_opcode_location().is_some();
 
-        if matches!(self.context.get_current_source_location(), None) {
+        if self.running && matches!(self.context.get_current_source_location(), None) {
             // TODO: remove this? This is to ensure that the tool has a proper
             // source location to show when first starting the debugger, but
             // maybe the default behavior should be to start executing until the
```

### tooling/debugger/src/repl.rs
```diff
@@ -38,14 +38,13 @@ impl<'a, B: BlackBoxFunctionSolver> ReplDebugger<'a, B> {
             initial_witness.clone(),
             foreign_call_executor,
         );
-        Self {
-            context,
-            blackbox_solver,
-            circuit,
-            debug_artifact,
-            initial_witness,
-            last_result: DebugCommandResult::Ok,
-        }
+        let last_result = if context.get_current_opcode_location().is_none() {
+            // handle circuit with no opcodes
+            DebugCommandResult::Done
+        } else {
+            DebugCommandResult::Ok
+        };
+        Self { context, blackbox_solver, circuit, debug_artifact, initial_witness, last_result }
     }
 
     pub fn show_current_vm_status(&self) {
```
