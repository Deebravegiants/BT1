# [?] fix: avoid deadlock in nested shell calls (#9245)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-11-01
Source: https://github.com/foundry-rs/foundry/commit/ea11082555e15f899a8bb9102890f3c2f7713cb8
Type: security-commit

## Details
fix: avoid deadlock in nested shell calls (#9245)

* fix: avoid deadlock in nested shell calls

* cleanup

## Patch
### crates/common/src/io/macros.rs
```diff
@@ -132,15 +132,23 @@ macro_rules! sh_eprintln {
 #[macro_export]
 macro_rules! __sh_dispatch {
     ($f:ident $fmt:literal $($args:tt)*) => {
-        $crate::Shell::$f(&mut *$crate::Shell::get(), ::core::format_args!($fmt $($args)*))
+        $crate::__sh_dispatch!(@impl $f &mut *$crate::Shell::get(), $fmt $($args)*)
     };
 
     ($f:ident $shell:expr, $($args:tt)*) => {
-        $crate::Shell::$f($shell, ::core::format_args!($($args)*))
+        $crate::__sh_dispatch!(@impl $f $shell, $($args)*)
     };
 
     ($f:ident $($args:tt)*) => {
-        $crate::Shell::$f(&mut *$crate::Shell::get(), ::core::format_args!($($args)*))
+        $crate::__sh_dispatch!(@impl $f &mut *$crate::Shell::get(), $($args)*)
+    };
+
+    // Ensure that the global shell lock is held for as little time as possible.
+    // Also avoids deadlocks in case of nested calls.
+    (@impl $f:ident $shell:expr, $($args:tt)*) => {
+        match ::core::format_args!($($args)*) {
+            fmt => $crate::Shell::$f($shell, fmt),
+        }
     };
 }
 
@@ -168,6 +176,11 @@ mod tests {
         sh_eprintln!("eprintln")?;
         sh_eprintln!("eprintln {}", "arg")?;
 
+        sh_println!("{:?}", {
+            sh_println!("hi")?;
+            "nested"
+        })?;
+
         Ok(())
     }
 
```

### crates/common/src/io/shell.rs
```diff
@@ -186,9 +186,9 @@ impl Shell {
         }
     }
 
-    /// Get a static reference to the global shell.
+    /// Acquire a lock to the global shell.
     ///
-    /// Initializes the global shell with the default values if it has not been set yet.
+    /// Initializes it with the default values if it has not been set yet.
     pub fn get() -> impl DerefMut<Target = Self> + 'static {
         GLOBAL_SHELL.get_or_init(Default::default).lock().unwrap_or_else(PoisonError::into_inner)
     }
@@ -200,10 +200,9 @@ impl Shell {
     /// Panics if the global shell has already been set.
     #[track_caller]
     pub fn set(self) {
-        if GLOBAL_SHELL.get().is_some() {
-            panic!("attempted to set global shell twice");
-        }
-        GLOBAL_SHELL.get_or_init(|| Mutex::new(self));
+        GLOBAL_SHELL
+            .set(Mutex::new(self))
+            .unwrap_or_else(|_| panic!("attempted to set global shell twice"))
     }
 
     /// Sets whether the next print should clear the current line and returns the previous value.
```
