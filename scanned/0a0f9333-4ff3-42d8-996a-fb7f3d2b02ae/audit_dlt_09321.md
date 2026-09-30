# [?] fix: avoid panic on missing CREATE2 deployer (#7838)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-05-02
Source: https://github.com/foundry-rs/foundry/commit/d495216638c0adaa3df76190a6835537c579304d
Type: security-commit

## Details
fix: avoid panic on missing CREATE2 deployer (#7838)

* fix: avoid panic on missing CREATE2 deployer

* rm println

* rm println

## Patch
### crates/evm/core/src/utils.rs
```diff
@@ -11,8 +11,8 @@ use revm::{
     db::WrapDatabaseRef,
     handler::register::EvmHandler,
     interpreter::{
-        return_ok, CallContext, CallInputs, CallScheme, CreateInputs, CreateOutcome, Gas,
-        InstructionResult, InterpreterResult, Transfer,
+        return_ok, CallContext, CallInputs, CallOutcome, CallScheme, CreateInputs, CreateOutcome,
+        Gas, InstructionResult, InterpreterResult, Transfer,
     },
     primitives::{CreateScheme, EVMError, SpecId, TransactTo, KECCAK_EMPTY},
     FrameOrResult, FrameResult,
@@ -151,35 +151,38 @@ pub fn create2_handler_register<DB: revm::Database, I: InspectorExt<DB>>(
                 return old_handle(ctx, inputs);
             }
 
-            // Sanity check that CREATE2 deployer exists.
-            let code_hash = ctx.evm.load_account(DEFAULT_CREATE2_DEPLOYER)?.0.info.code_hash;
-            if code_hash == KECCAK_EMPTY {
-                return Ok(FrameOrResult::Result(FrameResult::Create(CreateOutcome {
-                    result: InterpreterResult {
-                        result: InstructionResult::Revert,
-                        output: "missing CREATE2 deployer".into(),
-                        gas: Gas::new(inputs.gas_limit),
-                    },
-                    address: None,
-                })))
-            }
+            let gas_limit = inputs.gas_limit;
 
             // Generate call inputs for CREATE2 factory.
             let mut call_inputs = get_create2_factory_call_inputs(salt, *inputs);
 
             // Call inspector to change input or return outcome.
-            if let Some(outcome) = ctx.external.call(&mut ctx.evm, &mut call_inputs) {
-                create2_overrides_inner
-                    .borrow_mut()
-                    .push((ctx.evm.journaled_state.depth(), call_inputs.clone()));
-                return Ok(FrameOrResult::Result(FrameResult::Call(outcome)));
-            }
+            let outcome = ctx.external.call(&mut ctx.evm, &mut call_inputs);
 
             // Push data about current override to the stack.
             create2_overrides_inner
                 .borrow_mut()
                 .push((ctx.evm.journaled_state.depth(), call_inputs.clone()));
 
+            // Handle potential inspector override.
+            if let Some(outcome) = outcome {
+                return Ok(FrameOrResult::Result(FrameResult::Call(outcome)));
+            }
+
+            // Sanity check that CREATE2 deployer exists.
+            let code_hash = ctx.evm.load_account(DEFAULT_CREATE2_DEPLOYER)?.0.info.code_hash;
+            if code_hash == KECCAK_EMPTY {
+                return Ok(FrameOrResult::Result(FrameResult::Call(CallOutcome {
+                    result: InterpreterResult {
+                        result: InstructionResult::Revert,
+                        output: "missing CREATE2 deployer".into(),
+                        gas: Gas::new(gas_limit),
+                    },
+                    memory_offset: 0..0,
+                })))
+            }
+
+            // Create CALL frame for CREATE2 factory invocation.
             let mut frame_or_result = ctx.evm.make_call_frame(&call_inputs);
 
             if let Ok(FrameOrResult::Frame(frame)) = &mut frame_or_result {
```

### crates/evm/traces/src/decoder/mod.rs
```diff
@@ -310,7 +310,8 @@ impl CallTraceDecoder {
         if trace.address == DEFAULT_CREATE2_DEPLOYER {
             return DecodedCallTrace {
                 label,
-                return_data: None,
+                return_data: (!trace.status.is_ok())
+                    .then(|| self.revert_decoder.decode(&trace.output, Some(trace.status))),
                 contract,
                 func: Some(DecodedCallData { signature: "create2".to_string(), args: vec![] }),
             };
```

### crates/forge/tests/cli/script.rs
```diff
@@ -1321,3 +1321,39 @@ contract SimpleScript is Script {
     let output = cmd.stdout_lossy();
     assert!(output.contains("ONCHAIN EXECUTION COMPLETE & SUCCESSFUL"));
 });
+
+// https://github.com/foundry-rs/foundry/issues/7833
+forgetest_async!(error_no_create2, |prj, cmd| {
+    let (_api, handle) =
+        spawn(NodeConfig::test().with_disable_default_create2_deployer(true)).await;
+
+    foundry_test_utils::util::initialize(prj.root());
+    prj.add_script(
+        "Foo",
+        r#"
+import "forge-std/Script.sol";
+
+contract SimpleContract {}
+
+contract SimpleScript is Script {
+    function run() external {
+        vm.startBroadcast(0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266);
+        new SimpleContract{salt: bytes32(0)}();
+    }
+}
+   "#,
+    )
+    .unwrap();
+
+    cmd.args([
+        "script",
+        "SimpleScript",
+        "--fork-url",
+        &handle.http_endpoint(),
+        "--broadcast",
+        "--unlocked",
+    ]);
+
+    let output = cmd.stderr_lossy();
+    assert!(output.contains("missing CREATE2 deployer"));
+});
```
