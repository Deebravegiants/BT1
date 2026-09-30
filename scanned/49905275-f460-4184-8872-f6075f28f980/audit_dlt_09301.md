# [?] fix: Shell deadlock 2 (#11535)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-09-03
Source: https://github.com/foundry-rs/foundry/commit/a1534da6e572f4bbfe2f6bd7ac4c6bedd25dc2ea
Type: security-commit

## Details
fix: Shell deadlock 2 (#11535)

* test: shell deadlock 2

* fix it

## Patch
### crates/common/src/io/macros.rs
```diff
@@ -146,7 +146,7 @@ macro_rules! __sh_dispatch {
     // Ensure that the global shell lock is held for as little time as possible.
     // Also avoids deadlocks in case of nested calls.
     (@impl $f:ident $shell:expr, $($args:tt)*) => {
-        match ::core::format_args!($($args)*) {
+        match format!($($args)*) {
             fmt => $crate::Shell::$f($shell, fmt),
         }
     };
@@ -178,7 +178,10 @@ mod tests {
 
         sh_println!("{:?}", {
             sh_println!("hi")?;
-            "nested"
+            solar::data_structures::fmt::from_fn(|f| {
+                let _ = sh_println!("even more nested");
+                write!(f, "hi 2")
+            })
         })?;
 
         Ok(())
```
