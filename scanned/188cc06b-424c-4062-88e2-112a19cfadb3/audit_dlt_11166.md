# [?] fix(core,assembly): replace unsound ptr::read in panic recovery (#2934)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-04-07
Source: https://github.com/0xMiden/miden-vm/commit/012a74eecb3f27bb5f9034f852dabfbc388d28bc
Type: security-commit

## Details
fix(core,assembly): replace unsound ptr::read in panic recovery (#2934)

Replace unsafe ptr::read with safe *err unbox in the downcast::<std::io::Error>() arm of catch_unwind panic recovery. The ptr::read performed a bitwise copy out of the Box while the Box was still dropped at end of scope, causing potential UB via double-drop. This patch removes the unsafe block entirely.

Closes #2814

Co-authored-by: François Garillot <4142+huitseeker@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -7,6 +7,7 @@
 - Reverted the `MainTrace` typed row storage change that caused a large `blake3_1to1` trace-building regression ([#2949](https://github.com/0xMiden/miden-vm/pull/2949)).
 #### Bug Fixes
 
+- Replaced unsound `ptr::read` with safe unbox in panic recovery, removing UB from potential double-drop ([#2934](https://github.com/0xMiden/miden-vm/pull/2934)).
 - Reverted `InvokeKind::ProcRef` back to `InvokeKind::Exec` in `visit_mut_procref` and added an explanatory comment (#2893).
 - Fixed the release dry-run publish cycle between `miden-air` and `miden-ace-codegen`, and preserved leaf-only DAG imports with explicit snapshots ([#2931](https://github.com/0xMiden/miden-vm/pull/2931)).
 
```

### core/src/program/mod.rs
```diff
@@ -155,13 +155,10 @@ impl Program {
             },
             Err(err) => Err(err),
         })
-        .map_err(|p| {
-            match p.downcast::<std::io::Error>() {
-                // SAFETY: It is guaranteed to be safe to read Box<std::io::Error>
-                Ok(err) => unsafe { core::ptr::read(&*err) },
-                // Propagate unknown panics
-                Err(err) => std::panic::resume_unwind(err),
-            }
+        .map_err(|p| match p.downcast::<std::io::Error>() {
+            Ok(err) => *err,
+            // Propagate unknown panics
+            Err(err) => std::panic::resume_unwind(err),
         })?
     }
 }
```

### crates/assembly-syntax/src/library/mod.rs
```diff
@@ -421,12 +421,9 @@ impl Library {
             self.write_into(&mut file);
             Ok(())
         })
-        .map_err(|p| {
-            match p.downcast::<std::io::Error>() {
-                // SAFETY: It is guaranteed safe to read Box<std::io::Error>
-                Ok(err) => unsafe { core::ptr::read(&*err) },
-                Err(err) => std::panic::resume_unwind(err),
-            }
+        .map_err(|p| match p.downcast::<std::io::Error>() {
+            Ok(err) => *err,
+            Err(err) => std::panic::resume_unwind(err),
         })?
     }
 
```
