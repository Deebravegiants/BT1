# [?] Fix override of panic hook during cross-contract testing (#620)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2023-01-18
Source: https://github.com/stellar/rs-soroban-env/commit/d803b0922d1d9eb4d3cfde5e6d574c7776c23388
Type: security-commit

## Details
Fix override of panic hook during cross-contract testing (#620)

* Fix override of panic hook during cross-contract testing

* Don't mention recursion in call_with_suppressed_panic_hook

Co-authored-by: Graydon Hoare <graydon@pobox.com>

## Patch
### soroban-env-host/src/host.rs
```diff
@@ -824,7 +824,7 @@ impl Host {
                 let panic = frame.panic.clone();
                 return self.with_frame(Frame::TestContract(frame), || {
                     use std::any::Any;
-                    use std::panic::{catch_unwind, set_hook, take_hook, AssertUnwindSafe};
+                    use std::panic::AssertUnwindSafe;
                     use crate::xdr::ScUnknownErrorCode;
                     type PanicVal = Box<dyn Any + Send>;
 
@@ -847,10 +847,7 @@ impl Host {
                     // building a host for production use, so we're willing to
                     // be a bit forgiving.
                     let closure = AssertUnwindSafe(move || cfs.call(&func, self, args));
-                    let existing_panic_hook = take_hook();
-                    set_hook(Box::new(|_| ()));
-                    let res: Result<Option<RawVal>, PanicVal> = catch_unwind(closure);
-                    set_hook(existing_panic_hook);
+                    let res: Result<Option<RawVal>, PanicVal> = testutils::call_with_suppressed_panic_hook(closure);
                     match res {
                         Ok(Some(rawval)) => Ok(rawval),
                         Ok(None) => Err(self.err(
@@ -2272,3 +2269,64 @@ impl VmCallerCheckedEnv for Host {
         Ok(().into())
     }
 }
+
+#[cfg(any(test, feature = "testutils"))]
+mod testutils {
+    use crate::RawVal;
+    use std::any::Any;
+    use std::cell::Cell;
+    use std::panic::UnwindSafe;
+    use std::panic::{catch_unwind, set_hook, take_hook};
+    use std::sync::Once;
+
+    type PanicVal = Box<dyn Any + Send>;
+
+    /// Catch panics while suppressing the default panic hook that prints to the
+    /// console.
+    ///
+    /// For the purposes of test reporting we don't want every panicking (but
+    /// caught) contract call to print to the console. This requires overriding
+    /// the panic hook, a global resource. This is an awkward thing to do with
+    /// tests running in parallel.
+    ///
+    /// This function lazily performs a one-time wrapping of the existing panic
+    /// hook. It then uses a thread local variable to track contract call depth.
+    /// If a panick occurs during a contract call the original hook is not
+    /// called, otherwise it is called.
+    pub fn call_with_suppressed_panic_hook<C>(closure: C) -> Result<Option<RawVal>, PanicVal>
+    where
+        C: FnOnce() -> Option<RawVal> + UnwindSafe,
+    {
+        thread_local! {
+            static TEST_CONTRACT_CALL_COUNT: Cell<u64> = Cell::new(0);
+        }
+
+        static WRAP_PANIC_HOOK: Once = Once::new();
+
+        WRAP_PANIC_HOOK.call_once(|| {
+            let existing_panic_hook = take_hook();
+            set_hook(Box::new(move |info| {
+                let calling_test_contract = TEST_CONTRACT_CALL_COUNT.with(|c| c.get() != 0);
+                if !calling_test_contract {
+                    existing_panic_hook(info)
+                }
+            }))
+        });
+
+        TEST_CONTRACT_CALL_COUNT.with(|c| {
+            let old_count = c.get();
+            let new_count = old_count.checked_add(1).expect("overflow");
+            c.set(new_count);
+        });
+
+        let res: Result<Option<RawVal>, PanicVal> = catch_unwind(closure);
+
+        TEST_CONTRACT_CALL_COUNT.with(|c| {
+            let old_count = c.get();
+            let new_count = old_count.checked_sub(1).expect("overflow");
+            c.set(new_count);
+        });
+
+        res
+    }
+}
```
