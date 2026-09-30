# [?] Fix  panic

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2023-12-15
Source: https://github.com/Conflux-Chain/conflux-rust/commit/62801e5383549c8513b4a2b8c873e2165e8f8169
Type: security-commit

## Details
Fix  panic

## Patch
### core/src/executive/internal_contract/impls/cross_space.rs
```diff
@@ -144,12 +144,14 @@ pub fn withdraw_gas(spec: &Spec) -> U256 {
 pub struct Resume {
     pub params: ActionParams,
     pub gas_retained: U256,
+    pub wait_return_log: bool,
 }
 
 impl ResumeCreate for Resume {
     fn resume_create(
         self: Box<Self>, result: ContractCreateResult,
     ) -> Box<dyn Exec> {
+        let wait_return_log = self.wait_return_log;
         let pass_result = match result {
             ContractCreateResult::Created(address, gas_left) => {
                 let encoded_output = address.address.0.abi_encode();
@@ -160,19 +162,22 @@ impl ResumeCreate for Resume {
                     gas_left,
                     return_data: Ok(return_data),
                     apply_state: true,
+                    wait_return_log,
                 }
             }
             ContractCreateResult::Failed(err) => PassResult {
                 resume: *self,
                 gas_left: U256::zero(),
                 return_data: Err(err),
                 apply_state: false,
+                wait_return_log,
             },
             ContractCreateResult::Reverted(gas_left, data) => PassResult {
                 resume: *self,
                 gas_left,
                 return_data: Ok(data),
                 apply_state: false,
+                wait_return_log,
             },
         };
         Box::new(pass_result)
@@ -183,6 +188,7 @@ impl ResumeCall for Resume {
     fn resume_call(
         self: Box<Self>, result: MessageCallResult,
     ) -> Box<dyn Exec> {
+        let wait_return_log = self.wait_return_log;
         let pass_result = match result {
             MessageCallResult::Success(gas_left, data) => {
                 let encoded_output = data.to_vec().abi_encode();
@@ -193,19 +199,22 @@ impl ResumeCall for Resume {
                     gas_left,
                     return_data: Ok(return_data),
                     apply_state: true,
+                    wait_return_log,
                 }
             }
             MessageCallResult::Failed(err) => PassResult {
                 resume: *self,
                 gas_left: U256::zero(),
                 return_data: Err(err),
                 apply_state: false,
+                wait_return_log,
             },
             MessageCallResult::Reverted(gas_left, data) => PassResult {
                 resume: *self,
                 gas_left,
                 return_data: Ok(data),
                 apply_state: false,
+                wait_return_log,
             },
         };
         Box::new(pass_result)
@@ -217,6 +226,7 @@ pub struct PassResult {
     gas_left: U256,
     return_data: Result<ReturnData, vm::Error>,
     apply_state: bool,
+    wait_return_log: bool,
 }
 
 impl Exec for PassResult {
@@ -226,9 +236,8 @@ impl Exec for PassResult {
     ) -> ExecTrapResult<GasLeft>
     {
         let context = &mut context.internal_ref();
-        let static_flag = context.static_flag;
 
-        if !static_flag {
+        if self.wait_return_log {
             ReturnEvent::log(
                 &(),
                 &self.apply_state,
@@ -337,6 +346,8 @@ pub fn call_to_evmcore(
         params_type: vm::ParamsType::Separate,
     };
 
+    let mut wait_return_log = false;
+
     if call_type == CallType::Call {
         let nonce = context.state.nonce(&mapped_sender)?;
         context.state.inc_nonce(&mapped_sender)?;
@@ -346,13 +357,15 @@ pub fn call_to_evmcore(
             params,
             context,
         )?;
+        wait_return_log = true;
     }
 
     return Ok(ExecTrap::Call(
         next_params,
         Box::new(Resume {
             params: params.clone(),
             gas_retained: reserved_gas,
+            wait_return_log,
         }),
     ));
 }
@@ -439,6 +452,7 @@ pub fn create_to_evmcore(
         Box::new(Resume {
             params: params.clone(),
             gas_retained: reserved_gas,
+            wait_return_log: true,
         }),
     ));
 }
```
