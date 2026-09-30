# [?] Patch Fix Phantom Panic

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2023-12-27
Source: https://github.com/Conflux-Chain/conflux-rust/commit/fcd74c8f4cbc3c69d6eeaa7674887adc44f0ce92
Type: security-commit

## Details
Patch Fix Phantom Panic

## Patch
### core/executor/src/internal_contract/impls/cross_space.rs
```diff
@@ -138,6 +138,7 @@ pub fn withdraw_gas(spec: &Spec) -> U256 {
 pub struct Resume {
     pub params: ActionParams,
     pub gas_retained: U256,
+    pub wait_return_log: bool,
 }
 
 impl Resumable for Resume {
@@ -149,6 +150,7 @@ impl Resumable for Resume {
                     params: self.params,
                     result: Err(e),
                     apply_state: false,
+                    wait_return_log: self.wait_return_log,
                 });
             }
         };
@@ -183,6 +185,7 @@ impl Resumable for Resume {
                 data,
                 apply_state,
             }),
+            wait_return_log: self.wait_return_log,
         })
     }
 }
@@ -191,13 +194,14 @@ pub struct PassResult {
     params: ActionParams,
     result: vm::Result<GasLeft>,
     apply_state: bool,
+    wait_return_log: bool,
 }
 
 impl Executable for PassResult {
     fn execute(
         self: Box<Self>, mut context: Context,
     ) -> DbResult<ExecutableOutcome> {
-        if !context.is_static() {
+        if self.wait_return_log {
             ReturnEvent::log(
                 &(),
                 &self.apply_state,
@@ -288,6 +292,8 @@ pub fn call_to_evmcore(
         params_type: vm::ParamsType::Separate,
     };
 
+    let mut wait_return_log = false;
+
     if call_type == CallType::Call {
         let nonce = context.state.nonce(&mapped_sender)?;
         context.state.inc_nonce(&mapped_sender)?;
@@ -297,13 +303,15 @@ pub fn call_to_evmcore(
             params,
             context,
         )?;
+        wait_return_log = true;
     }
 
     Ok((
         next_params,
         Box::new(Resume {
             params: params.clone(),
             gas_retained: reserved_gas,
+            wait_return_log,
         }),
     ))
 }
@@ -390,6 +398,7 @@ pub fn create_to_evmcore(
         Box::new(Resume {
             params: params.clone(),
             gas_retained: reserved_gas,
+            wait_return_log: true,
         }),
     ))
 }
```
