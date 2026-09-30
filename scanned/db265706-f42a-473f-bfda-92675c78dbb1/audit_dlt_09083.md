# [?] fix(core): centralize rust panic handler in sys crate

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-08-24
Source: https://github.com/trezor/trezor-firmware/commit/20c6666aeab4d75c7c496efdc056df3d325f5e27
Type: security-commit

## Details
fix(core): centralize rust panic handler in sys crate

[no changelog]

## Patch
### core/embed/projects/boardloader/src/main.rs
```diff
@@ -1,7 +1,5 @@
 #![no_std]
 #![no_main]
 
-#[panic_handler]
-fn panic(_info: &core::panic::PanicInfo) -> ! {
-    loop {}
-}
+// force pull in Rust generated symbols (incl. the panic handler)
+use sys as _;
```

### core/embed/projects/bootloader_ci/src/main.rs
```diff
@@ -1,7 +1,5 @@
 #![no_std]
 #![no_main]
 
-#[panic_handler]
-fn panic(_info: &core::panic::PanicInfo) -> ! {
-    loop {}
-}
+// force pull in Rust generated symbols (incl. the panic handler)
+use sys as _;
```

### core/embed/projects/secmon/src/main.rs
```diff
@@ -1,7 +1,5 @@
 #![no_std]
 #![no_main]
 
-#[panic_handler]
-fn panic(_info: &core::panic::PanicInfo) -> ! {
-    loop {}
-}
+// force pull in Rust generated symbols (incl. the panic handler)
+use sys as _;
```

### core/embed/rust/src/lib.rs
```diff
@@ -59,40 +59,6 @@ mod bootloader;
 #[macro_use]
 extern crate rtl;
 
-#[cfg(feature = "debug")]
-#[cfg(not(test))]
-#[panic_handler]
-/// More detailed panic handling. The difference against
-/// default `panic` below is that this "debug" version
-/// takes around 10 kB more space in the flash region.
-fn panic_debug(panic_info: &core::panic::PanicInfo) -> ! {
-    // Filling at least the file and line information, if available.
-    // TODO: find out how to display message from panic_info.message()
-    let msg = panic_info.message().as_str().unwrap_or("rs");
-    if let Some(location) = panic_info.location() {
-        rtl::system_exit_fatal(msg, location.file(), location.line());
-    } else {
-        rtl::system_exit_fatal(msg, "", 0);
-    }
-}
-
-#[cfg(not(feature = "debug"))]
-#[cfg(not(test))]
-#[cfg(any(not(feature = "test"), feature = "clippy"))]
-#[panic_handler]
-/// Default panic handling. Not showing any details - thus saving flash space.
-fn panic(_info: &core::panic::PanicInfo) -> ! {
-    // TODO: as of Rust 1.63 / nightly 2022-08, ignoring the `_info` parameter does
-    // not help with saving flash space -- the `fmt` machinery still gets
-    // compiled in. We can avoid that by using unstable Cargo arguments:
-    //   -Zbuild-std=core -Zbuild-std-features=panic_immediate_abort
-    // Doing that will compile every panic!() to a single udf instruction which
-    // raises a Hard Fault on hardware.
-    //
-    // Otherwise, use `unwrap!` macro from trezorhal.
-    fatal_error!("rs");
-}
-
 #[cfg(not(target_arch = "arm"))]
 #[cfg(not(test))]
 #[cfg(any(not(feature = "test"), feature = "clippy"))]
```

### core/embed/sys/src/lib.rs
```diff
@@ -3,6 +3,13 @@
 mod ffi;
 
 pub mod irq;
+
+// Compiled out for host-side unit tests, where std provides the handler.
+// Cargo builds test targets and their dependencies with `panic = "unwind"`;
+// all firmware and emulator profiles use `abort` or `immediate-abort`.
+#[cfg(not(panic = "unwind"))]
+mod panic;
+
 #[cfg(feature = "dbg_console")]
 pub mod syslog;
 
```

### core/embed/sys/src/panic.rs
```diff
@@ -0,0 +1,15 @@
+/// Panic handler shared by all binaries that link `sys`.
+///
+/// Only debug builds ever reach it - the release profile uses
+/// `panic = "immediate-abort"`, which compiles every panic to an abort
+/// instruction without referencing the handler, so it gets stripped there.
+#[panic_handler]
+fn panic(panic_info: &core::panic::PanicInfo) -> ! {
+    // Filling at least the file and line information, if available.
+    let msg = panic_info.message().as_str().unwrap_or("rs");
+    if let Some(location) = panic_info.location() {
+        rtl::system_exit_fatal(msg, location.file(), location.line());
+    } else {
+        rtl::system_exit_fatal(msg, "", 0);
+    }
+}
```
