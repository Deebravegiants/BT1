# [?] Catch panics from native contracts in try_call, fix #430 (#548)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2022-10-28
Source: https://github.com/stellar/rs-soroban-env/commit/3a213796684769271129b89b557976b4538a904e
Type: security-commit

## Details
Catch panics from native contracts in try_call, fix #430 (#548)

* Catch panics from native contracts in try_call, fix #430

* Change all cfg(feature="testutils") into cfg(any(test, feature="testutils"))

* Make HostError escalation paths more similar between VM and non.

* Capture escalation event itself in escalated HostError

* Adjust expected debug-event counts in tests

## Patch
### soroban-env-common/src/checked_env.rs
```diff
@@ -83,6 +83,7 @@ macro_rules! generate_checked_env_trait {
         pub trait CheckedEnv
         {
             type Error: Debug;
+            fn escalate_error_to_panic(&self,e:Self::Error) -> !;
             $(
                 $(
                     // This invokes the host_function_helper! macro above
@@ -115,12 +116,15 @@ call_macro_with_all_host_functions! { generate_checked_env_trait }
 //
 // and produces the the corresponding method declaration to be used in the Env
 // trait.
-macro_rules! unwrap_function_helper {
+macro_rules! panic_function_helper {
     {fn $fn_id:ident($($arg:ident:$type:ty),*) -> $ret:ty}
     =>
     {
         fn $fn_id(&self, $($arg:$type),*) -> $ret {
-            <Self as CheckedEnv>::$fn_id(self, $($arg),*).unwrap()
+            match <Self as CheckedEnv>::$fn_id(self, $($arg),*) {
+                Ok(x) => x,
+                Err(e) => self.escalate_error_to_panic(e)
+            }
         }
     };
 }
@@ -156,13 +160,13 @@ macro_rules! impl_env_for_checked_env {
 
     {
         // This macro expands to a single item: a blanket impl that makes all
-        // `CheckedEnv+EnvBase` types automatically `Env` types, just unwrapping
-        // their results.
+        // `CheckedEnv+EnvBase` types automatically `Env` types, panicking with
+        // any non-Ok() result.
         impl<T:CheckedEnv+EnvBase> $crate::Env for T
         {
             $(
                 $(
-                    // This invokes the unwrap_function_helper! macro above
+                    // This invokes the panic_function_helper! macro above
                     // passing only the relevant parts of the declaration
                     // matched by the inner pattern above. It is embedded in two
                     // nested `$()*` pattern-repetition expanders that
@@ -171,7 +175,7 @@ macro_rules! impl_env_for_checked_env {
                     // block repetition-level from the outer pattern in the
                     // expansion, flattening all functions from all 'mod' blocks
                     // into the impl.
-                    unwrap_function_helper!{fn $fn_id $args -> $ret}
+                    panic_function_helper!{fn $fn_id $args -> $ret}
                 )*
             )*
         }
```

### soroban-env-common/src/vmcaller_checked_env.rs
```diff
@@ -126,6 +126,7 @@ macro_rules! generate_vmcaller_checked_env_trait {
         {
             type VmUserState;
             type Error: Debug;
+            fn escalate_error_to_panic(&self,e:Self::Error) -> !;
             $(
                 $(
                     // This invokes the host_function_helper! macro above
@@ -205,6 +206,9 @@ macro_rules! impl_checked_env_for_vmcaller_checked_env {
         impl<T:VmCallerCheckedEnv> $crate::CheckedEnv for T
         {
             type Error = <Self as VmCallerCheckedEnv>::Error;
+            fn escalate_error_to_panic(&self,e:Self::Error) -> ! {
+                <Self as VmCallerCheckedEnv>::escalate_error_to_panic(self,e)
+            }
             $(
                 $(
                     // This invokes the vmcaller_none_function_helper! macro above
```

### soroban-env-host/src/host.rs
```diff
@@ -65,11 +65,30 @@ pub(crate) struct RollbackPoint {
     objects: usize,
 }
 
-#[cfg(feature = "testutils")]
+#[cfg(any(test, feature = "testutils"))]
 pub trait ContractFunctionSet {
     fn call(&self, func: &Symbol, host: &Host, args: &[RawVal]) -> Option<RawVal>;
 }
 
+#[cfg(any(test, feature = "testutils"))]
+#[derive(Debug, Clone)]
+pub struct TestContractFrame {
+    pub id: Hash,
+    pub func: Symbol,
+    panic: Rc<RefCell<Option<Status>>>,
+}
+
+#[cfg(any(test, feature = "testutils"))]
+impl TestContractFrame {
+    pub fn new(id: Hash, func: Symbol) -> Self {
+        Self {
+            id,
+            func,
+            panic: Rc::new(RefCell::new(None)),
+        }
+    }
+}
+
 /// Holds contextual information about a single invocation, either
 /// a reference to a contract [`Vm`] or an enclosing [`HostFunction`]
 /// invocation.
@@ -88,7 +107,7 @@ pub(crate) enum Frame {
     HostFunction(HostFunction),
     Token(Hash, Symbol),
     #[cfg(any(test, feature = "testutils"))]
-    TestContract(Hash, Symbol),
+    TestContract(TestContractFrame),
 }
 
 /// Temporary helper for denoting a slice of guest memory, as formed by
@@ -126,7 +145,7 @@ pub(crate) struct HostImpl {
     // of what users will be charged for in production -- it's scaffolding for testing a contract,
     // but shouldn't be charged to the contract itself (and will never be compiled-in to
     // production hosts)
-    #[cfg(feature = "testutils")]
+    #[cfg(any(test, feature = "testutils"))]
     contracts: RefCell<std::collections::HashMap<Hash, Rc<dyn ContractFunctionSet>>>,
 }
 // Host is a newtype on Rc<HostImpl> so we can impl Env for it below.
@@ -186,7 +205,7 @@ impl Host {
             context: Default::default(),
             budget,
             events: Default::default(),
-            #[cfg(feature = "testutils")]
+            #[cfg(any(test, feature = "testutils"))]
             contracts: Default::default(),
         }))
     }
@@ -420,7 +439,7 @@ impl Host {
             }
             Frame::Token(id, _) => id.metered_clone(&self.0.budget),
             #[cfg(any(test, feature = "testutils"))]
-            Frame::TestContract(id, _) => Ok(id.clone()),
+            Frame::TestContract(tc) => Ok(tc.id.clone()),
         })
     }
 
@@ -775,7 +794,7 @@ impl Host {
                     Frame::ContractVM(vm, _) => &vm.contract_id,
                     Frame::Token(id, _) => id,
                     #[cfg(any(test, feature = "testutils"))]
-                    Frame::TestContract(id, _) => id,
+                    Frame::TestContract(tc) => &tc.id,
                     Frame::HostFunction(_) => continue,
                 };
                 if id == *exist_id {
@@ -789,7 +808,7 @@ impl Host {
         }
 
         // "testutils" is not covered by budget metering.
-        #[cfg(feature = "testutils")]
+        #[cfg(any(test, feature = "testutils"))]
         {
             // This looks a little un-idiomatic, but this avoids maintaining a borrow of
             // self.0.contracts. Implementing it as
@@ -799,9 +818,59 @@ impl Host {
             // maintains a borrow of self.0.contracts, which can cause borrow errors.
             let cfs_option = self.0.contracts.borrow().get(&id).cloned();
             if let Some(cfs) = cfs_option {
-                return self.with_frame(Frame::TestContract(id.clone(), func.clone()), || {
-                    cfs.call(&func, self, args)
-                        .ok_or_else(|| self.err_general("function not found"))
+                let frame = TestContractFrame::new(id.clone(), func.clone());
+                let panic = frame.panic.clone();
+                return self.with_frame(Frame::TestContract(frame), || {
+                    use std::any::Any;
+                    use std::panic::{catch_unwind, set_hook, take_hook, AssertUnwindSafe};
+                    type PanicVal = Box<dyn Any + Send>;
+
+                    // We're directly invoking a native rust contract here,
+                    // which we allow only in local testing scenarios, and we
+                    // want it to behave as close to the way it would behave if
+                    // the contract were actually compiled to WASM and running
+                    // in a VM.
+                    //
+                    // In particular: if the contract function panics, if it
+                    // were WASM it would cause the VM to trap, so we do
+                    // something "as similar as we can" in the native case here,
+                    // catch the native panic and attempt to continue by
+                    // translating the panic back to an error, so that
+                    // `with_frame` will rollback the host to its pre-call state
+                    // (as best it can) and propagate the error to its caller
+                    // (which might be another contract doing try_call).
+                    //
+                    // This is somewhat best-effort, but it's compiled-out when
+                    // building a host for production use, so we're willing to
+                    // be a bit forgiving.
+                    let closure = AssertUnwindSafe(move || cfs.call(&func, self, args));
+                    let existing_panic_hook = take_hook();
+                    set_hook(Box::new(|_| ()));
+                    let res: Result<Option<RawVal>, PanicVal> = catch_unwind(closure);
+                    set_hook(existing_panic_hook);
+                    match res {
+                        Ok(Some(rawval)) => Ok(rawval),
+                        Ok(None) => Err(self.err(
+                            DebugError::general()
+                                .msg("error '{}': calling unknown contract function '{}'")
+                                .arg::<RawVal>(func.into()),
+                        )),
+                        Err(_) => {
+                            // Return an error indicating the contract function
+                            // panicked. If if was a panic generated by a
+                            // CheckedEnv-upgraded HostError, it had its status
+                            // captured by VmCallerCheckedEnv::escalate_error_to_panic:
+                            // fish the Status stored in the frame back out and
+                            // propagate it.
+                            let msg = "caught panic with '{}' in contract function '{}'";
+                            let func: RawVal = func.into();
+                            let mut err = DebugError::general().msg(msg).arg(func);
+                            if let Some(status) = *panic.borrow() {
+                                err = DebugError::new(status).msg(msg).arg(func);
+                            }
+                            Err(self.err(err))
+                        }
+                    }
                 });
             }
         }
@@ -897,7 +966,7 @@ impl Host {
     }
 
     // "testutils" is not covered by budget metering.
-    #[cfg(feature = "testutils")]
+    #[cfg(any(test, feature = "testutils"))]
     pub fn register_test_contract(
         &self,
         contract_id: Object,
@@ -914,7 +983,7 @@ impl Host {
     }
 
     // "testutils" is not covered by budget metering.
-    #[cfg(feature = "testutils")]
+    #[cfg(any(test, feature = "testutils"))]
     pub fn register_test_contract_wasm(
         &self,
         contract_id: Object,
@@ -926,7 +995,7 @@ impl Host {
     }
 
     // "testutils" is not covered by budget metering.
-    #[cfg(feature = "testutils")]
+    #[cfg(any(test, feature = "testutils"))]
     pub fn register_test_contract_token(&self, contract_id: Object) -> Result<(), HostError> {
         self.create_contract_with_id(ScContractCode::Token, contract_id)
     }
@@ -1204,6 +1273,49 @@ impl VmCallerCheckedEnv for Host {
     type VmUserState = Host;
     type Error = HostError;
 
+    // This function is somewhat subtle.
+    //
+    // It exists to allow the client of the (VmCaller)CheckedEnv interface(s) to
+    // essentially _reject_ an error returned by one of the Result-returning
+    // methods on the trait, choosing to panic instead. But doing so in some way
+    // that the trait defines, rather than calling panic in the client.
+    //
+    // The only "client" we expect to _do_ this is the `impl Env for CheckedEnv`
+    // definition, in checked_env.rs, which itself is only used for testing
+    // native contracts, adapting `CheckedEnv` to the non-error-returning `Env`
+    // interface that contracts expect.
+    //
+    // When such a "rejected error" occurs, we do panic, but only after checking
+    // to see if we're in a `TestContract` invocation, and if so storing the
+    // error's Status value in that frame, such that `Host::call_n` above can
+    // recover the Status when it _catches_ the panic and converts it back to an
+    // error.
+    //
+    // It might seem like we ought to `std::panic::panic_any(e)` here, making
+    // the panic carry a `HostError` or `Status` and catching it by dynamic type
+    // inspection in the `call_n` catch logic. The reason we don't do so is that
+    // `panic_any` will not provide a nice printable value to the `PanicInfo`,
+    // it constructs, so when/if the panic makes it to a top-level printout it
+    // will display a relatively ugly message like "thread panicked at Box<dyn
+    // Any>" to stderr, when it is much more useful to the user if we have it
+    // print the result of HostError::Debug, with its glorious status code,
+    // site-of-origin backtrace and debug log.
+    //
+    // To get it to do that, we have to call `panic!()`, not `panic_any`.
+    // Personally I think this is a glaring weakness of `panic_any` but we are
+    // not in a position to improve it.
+    fn escalate_error_to_panic(&self, e: Self::Error) -> ! {
+        #[cfg(any(test, feature = "testutils"))]
+        let _ = self.with_current_frame(|f| {
+            if let Frame::TestContract(frame) = f {
+                *frame.panic.borrow_mut() = Some(e.status);
+            }
+            Ok(())
+        });
+        let escalation = self.err_status_msg(e.status, "escalating error '{}' to panic");
+        panic!("{:?}", escalation)
+    }
+
     // Notes on metering: covered by the components
     fn log_value(&self, _vmcaller: &mut VmCaller<Host>, v: RawVal) -> Result<RawVal, HostError> {
         self.record_debug_event(DebugEvent::new().arg(v))?;
@@ -1245,7 +1357,7 @@ impl VmCallerCheckedEnv for Host {
                 Frame::HostFunction(_) => Ok(InvokerType::Account),
                 Frame::Token(id, _) => Ok(InvokerType::Contract),
                 #[cfg(any(test, feature = "testutils"))]
-                Frame::TestContract(_, _) => Ok(InvokerType::Contract),
+                Frame::TestContract(_) => Ok(InvokerType::Contract),
             },
             // In tests contracts are executed with a single frame.
             // TODO: Investigate this discrepancy: https://github.com/stellar/rs-soroban-env/issues/485.
@@ -1277,7 +1389,7 @@ impl VmCallerCheckedEnv for Host {
                 Frame::HostFunction(_) => Err(self.err_general("invoker is not a contract")),
                 Frame::Token(id, _) => Ok(id.clone()),
                 #[cfg(any(test, feature = "testutils"))]
-                Frame::TestContract(id, _) => Ok(id.clone()), // no metering
+                Frame::TestContract(tc) => Ok(tc.id.clone()), // no metering
             },
             _ => Err(self.err_general("no frames to derive the invoker from")),
         }?;
@@ -2736,8 +2848,8 @@ impl VmCallerCheckedEnv for Host {
                     outer.push_back(self.add_host_object(inner)?.into())?;
                 }
                 #[cfg(any(test, feature = "testutils"))]
-                Frame::TestContract(id, function) => {
-                    let vals = get_host_val_tuple(&id, &function)?;
+                Frame::TestContract(tc) => {
+                    let vals = get_host_val_tuple(&tc.id, &tc.func)?;
                     let inner = MeteredVector::from_array(self.budget_cloned(), [vals.0, vals.1])?;
                     outer.push_back(self.add_host_object(inner)?.into())?;
                 }
@@ -2752,7 +2864,7 @@ impl VmCallerCheckedEnv for Host {
         status: Status,
     ) -> Result<RawVal, Self::Error> {
         if status.is_type(ScStatusType::ContractError) {
-            Err(self.err_status_msg(status, "failing with contract error status code"))
+            Err(self.err_status_msg(status, "failing with contract error status code '{}'"))
         } else {
             Err(self.err_status_msg(
                 ScHostValErrorCode::UnexpectedValType,
```

### soroban-env-host/src/lib.rs
```diff
@@ -44,7 +44,7 @@ pub mod storage;
 #[cfg(test)]
 mod test;
 
-#[cfg(feature = "testutils")]
+#[cfg(any(test, feature = "testutils"))]
 pub use host::ContractFunctionSet;
 pub use host::{metered_map::MeteredOrdMap, Host, HostError, LedgerInfo};
 pub use im_rc;
```

### soroban-env-host/src/test.rs
```diff
@@ -14,7 +14,7 @@ mod vec;
 mod budget_metering;
 #[cfg(feature = "vm")]
 mod complex;
-#[cfg(feature = "testutils")]
+#[cfg(any(test, feature = "testutils"))]
 mod contract_event;
 #[cfg(feature = "vm")]
 mod hostile;
@@ -24,4 +24,5 @@ mod invocation;
 mod lifecycle;
 mod tuple;
 
+#[cfg(any(test, feature = "testutils"))]
 mod token;
```

### soroban-env-host/src/test/invocation.rs
```diff
@@ -75,7 +75,7 @@ fn invoke_cross_contract_with_err() -> Result<(), HostError> {
     assert_eq!(sv.get_payload(), exp_st.to_raw().get_payload());
 
     let events = host.get_events()?;
-    assert_eq!(events.0.len(), 3);
+    assert_eq!(events.0.len(), 4);
     let last_event = events.0.last();
     match last_event {
         Some(HostEvent::Debug(de)) => {
@@ -107,7 +107,7 @@ fn invoke_cross_contract_with_err() -> Result<(), HostError> {
     assert!(HostError::result_matches_err_status(res, code));
 
     let events = host.get_events()?;
-    assert_eq!(events.0.len(), 6);
+    assert_eq!(events.0.len(), 8);
     let last_event = events.0.last();
     match last_event {
         Some(HostEvent::Debug(de)) => {
@@ -186,7 +186,7 @@ fn invoke_cross_contract_indirect_err() -> Result<(), HostError> {
     assert_eq!(status.get_payload(), exp.to_raw().get_payload());
 
     let events = host.get_events()?;
-    assert_eq!(events.0.len(), 4);
+    assert_eq!(events.0.len(), 5);
     let last_event = events.0.last();
     match last_event {
         Some(HostEvent::Debug(de)) => {
@@ -218,7 +218,7 @@ fn invoke_cross_contract_indirect_err() -> Result<(), HostError> {
     assert!(HostError::result_matches_err_status(res, code));
 
     let events = host.get_events()?;
-    assert_eq!(events.0.len(), 8);
+    assert_eq!(events.0.len(), 10);
     let last_event = events.0.last();
     match last_event {
         Some(HostEvent::Debug(de)) => {
```

### soroban-env-host/src/test/token.rs
```diff
@@ -2,7 +2,7 @@ use std::{convert::TryInto, rc::Rc};
 
 use crate::{
     budget::Budget,
-    host::Frame,
+    host::{Frame, TestContractFrame},
     host_vec,
     native_contract::{
         base_types::BigInt,
@@ -252,10 +252,10 @@ impl TokenTest {
         F: FnOnce() -> Result<T, HostError>,
     {
         self.host.with_frame(
-            Frame::TestContract(
+            Frame::TestContract(TestContractFrame::new(
                 Hash(contract_id_bytes.to_array().unwrap()),
                 Symbol::from_str("foo"),
-            ),
+            )),
             || {
                 let res = f();
                 match res {
```

### soroban-env-host/src/vm/dispatch.rs
```diff
@@ -1,4 +1,6 @@
-use crate::{budget::CostType, Host, Object, RawVal, Status, Symbol, VmCaller, VmCallerCheckedEnv};
+use crate::{
+    budget::CostType, Host, HostError, Object, RawVal, Status, Symbol, VmCaller, VmCallerCheckedEnv,
+};
 use soroban_env_common::call_macro_with_all_host_functions;
 use wasmi::core::{FromValue, Trap, TrapCode::UnexpectedSignature, Value};
 
@@ -75,7 +77,16 @@ macro_rules! generate_dispatch_functions {
                     // happens to be a natural switching point for that: we have
                     // conversions to and from both RawVal and i64 / u64 for
                     // wasmi::Value.
-                    let res: Value = host.$fn_id(&mut vmcaller, $(<$type as FromValue>::from_value(Value::I64($arg)).ok_or(UnexpectedSignature)?),*)?.into();
+                    let res: Result<_, HostError> = host.$fn_id(&mut vmcaller, $(<$type as FromValue>::from_value(Value::I64($arg)).ok_or(UnexpectedSignature)?),*);
+                    let res: Value = match res {
+                        Ok(ok) => ok.into(),
+                        Err(hosterr) => {
+                            // We make a new HostError here to capture the escalation event itself.
+                            let escalation: HostError = host.err_status_msg(hosterr.status, "escalating error '{}' to VM trap");
+                            let trap: Trap = escalation.into();
+                            return Err(trap)
+                        }
+                    };
                     if let Value::I64(v) = res {
                         Ok((v,))
                     } else {
```
