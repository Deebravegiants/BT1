# [?] [verifier] Minor hardening against arithmetic overflow (#505)

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2022-09-26
Source: https://github.com/move-language/move/commit/db9b8cb29607488ba0a84a0f57216de1475c9f40
Type: security-commit

## Details
[verifier] Minor hardening against arithmetic overflow (#505)

* [verifier] Minor hardening against arithmetic overflow

* Update language/move-binary-format/src/check_bounds.rs

Co-authored-by: Meng Xu <72079339+meng-xu-cs@users.noreply.github.com>

* Update language/move-binary-format/src/check_bounds.rs

Co-authored-by: Meng Xu <72079339+meng-xu-cs@users.noreply.github.com>

Co-authored-by: Meng Xu <72079339+meng-xu-cs@users.noreply.github.com>

## Patch
### language/move-binary-format/src/check_bounds.rs
```diff
@@ -324,14 +324,28 @@ impl<'a> BoundsChecker<'a> {
             None => return Ok(()),
         };
 
-        debug_assert!(function_def.function.into_index() < self.view.function_handles().len());
+        if function_def.function.into_index() >= self.view.function_handles().len() {
+            return Err(verification_error(
+                StatusCode::INDEX_OUT_OF_BOUNDS,
+                IndexKind::FunctionDefinition,
+                function_def_idx as TableIndex,
+            ));
+        }
         let function_handle = &self.view.function_handles()[function_def.function.into_index()];
-
-        debug_assert!(function_handle.parameters.into_index() < self.view.signatures().len());
+        if function_handle.parameters.into_index() >= self.view.signatures().len() {
+            return Err(verification_error(
+                StatusCode::INDEX_OUT_OF_BOUNDS,
+                IndexKind::FunctionDefinition,
+                function_def_idx as TableIndex,
+            ));
+        }
         let parameters = &self.view.signatures()[function_handle.parameters.into_index()];
 
         // check if the number of parameters + locals is less than u8::MAX
-        let locals_count = self.get_locals(code_unit)?.len() + parameters.len();
+        let locals_count = self
+            .get_locals(code_unit)?
+            .len()
+            .saturating_add(parameters.len());
 
         if locals_count > (u8::MAX as usize) + 1 {
             return Err(verification_error(
@@ -353,7 +367,8 @@ impl<'a> BoundsChecker<'a> {
         check_bounds_impl(self.view.signatures(), code_unit.locals)?;
 
         let locals = self.get_locals(code_unit)?;
-        let locals_count = locals.len() + parameters.len();
+        // Use saturating add for stability; range checked above
+        let locals_count = locals.len().saturating_add(parameters.len());
 
         // if there are locals check that the type parameters in local signature are in bounds.
         let type_param_count = type_parameters.len();
```

### language/move-vm/transactional-tests/tests/module_publishing/republish_module_skip_compatible_linking_hack_struct.exp
```diff
@@ -1 +1,28 @@
 processed 5 tasks
+
+task 2 'publish'. lines 18-23:
+Error: Unable to publish module '00000000000000000000000000000042::A'. Got VMError: {
+    major_status: BACKWARD_INCOMPATIBLE_MODULE_UPDATE,
+    sub_status: None,
+    location: undefined,
+    indices: [],
+    offsets: [],
+}
+
+task 3 'publish'. lines 25-45:
+Error: Unable to publish module '00000000000000000000000000000042::A'. Got VMError: {
+    major_status: BACKWARD_INCOMPATIBLE_MODULE_UPDATE,
+    sub_status: None,
+    location: undefined,
+    indices: [],
+    offsets: [],
+}
+
+task 4 'run'. lines 47-47:
+Error: Function execution failed with VMError: {
+    major_status: FUNCTION_RESOLUTION_FAILURE,
+    sub_status: None,
+    location: undefined,
+    indices: [],
+    offsets: [],
+}
```
