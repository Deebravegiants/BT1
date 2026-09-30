# [?] fix(utils): re-add trimming of panic message to try_vm_runtime

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2025-09-05
Source: https://github.com/AleoNet/snarkVM-test/commit/c8c9c8db0d0526064cac4fb6a4b3fdb345d2b800
Type: security-commit

## Details
fix(utils): re-add trimming of panic message to try_vm_runtime

## Patch
### utilities/src/vm_error.rs
```diff
@@ -28,10 +28,19 @@ macro_rules! try_vm_runtime {
 
         // Set a custom hook before calling catch_unwind to
         // indicate that the panic was expected and handled.
-        panic::set_hook(Box::new(|e| {
+        panic::set_hook(Box::new(|err| {
             #[cfg(debug_assertions)]
             {
-                let msg = e.to_string().replacen("panicked", "VM safely halted", 1);
+                // Remove all words up to "panicked".
+                let trimmed = err
+                    .to_string()
+                    .split_ascii_whitespace()
+                    .skip_while(|&word| word != "panicked")
+                    .collect::<Vec<&str>>()
+                    .join(" ");
+
+                // Have the message start with "VM safely halted".
+                let msg = trimmed.replacen("panicked", "VM safely halted", 1);
                 eprintln!("{msg}");
             }
         }));
```
