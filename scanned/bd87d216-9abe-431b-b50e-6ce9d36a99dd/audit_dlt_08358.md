# [?] prevent the VM from crashing due to trying to drop a local stack with references

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2022-11-09
Source: https://github.com/move-language/move/commit/39f7784d95827085e9680a020130da3c95daa942
Type: security-commit

## Details
prevent the VM from crashing due to trying to drop a local stack with references

## Patch
### language/move-vm/runtime/src/interpreter.rs
```diff
@@ -133,15 +133,14 @@ impl Interpreter {
                     .map_err(|err| self.maybe_core_dump(err, &current_frame))?;
             match exit_code {
                 ExitCode::Return => {
+                    let non_ref_vals = current_frame
+                        .locals
+                        .drop_all_values()
+                        .map(|(_idx, val)| val);
+
                     // TODO: Check if the error location is set correctly.
                     gas_meter
-                        .charge_drop_frame(
-                            current_frame
-                                .locals
-                                .into_values()
-                                .map_err(|e| self.set_location(e))?
-                                .map(|(_idx, val)| val),
-                        )
+                        .charge_drop_frame(non_ref_vals.into_iter())
                         .map_err(|e| self.set_location(e))?;
 
                     if let Some(frame) = self.call_stack.pop() {
```

### language/move-vm/transactional-tests/tests/references/drop_ref.exp
```diff
@@ -0,0 +1 @@
+processed 1 task
```

### language/move-vm/transactional-tests/tests/references/drop_ref.mvir
```diff
@@ -0,0 +1,9 @@
+//# run --signers 0x1
+main(account: signer) {
+    let u: u64;
+    let u_ref: &u64;
+label b0:
+    u = 10;
+    u_ref = freeze(&mut u);
+    return;
+}
\ No newline at end of file
```

### language/move-vm/types/src/values/values_impl.rs
```diff
@@ -1022,14 +1022,26 @@ impl Locals {
         Ok(())
     }
 
-    pub fn into_values(self) -> PartialVMResult<impl Iterator<Item = (usize, Value)>> {
-        Ok(take_unique_ownership(self.0)?
-            .into_iter()
-            .enumerate()
-            .flat_map(|(idx, val)| match &val {
-                ValueImpl::Invalid => None,
-                _ => Some((idx, Value(val))),
-            }))
+    /// Drop all Move values onto a different Vec to avoid leaking memory.
+    /// References are excluded since they may point to invalid data.
+    pub fn drop_all_values(&mut self) -> impl Iterator<Item = (usize, Value)> {
+        let mut locals = self.0.borrow_mut();
+        let mut res = vec![];
+
+        for idx in 0..locals.len() {
+            match &locals[idx] {
+                ValueImpl::Invalid => (),
+                ValueImpl::ContainerRef(_) | ValueImpl::IndexedRef(_) => {
+                    locals[idx] = ValueImpl::Invalid;
+                }
+                _ => res.push((
+                    idx,
+                    Value(std::mem::replace(&mut locals[idx], ValueImpl::Invalid)),
+                )),
+            }
+        }
+
+        res.into_iter()
     }
 }
 
```
