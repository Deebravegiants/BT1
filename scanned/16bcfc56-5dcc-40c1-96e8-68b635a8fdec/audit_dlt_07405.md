# [?] fix(cli): don't panic on a non-UTF-8 command-line argument (#16645)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-04
Source: https://github.com/foundry-rs/foundry/commit/94bbd59a0da5668efb7bd3f99f87b5e5c94bfa10
Type: security-commit

## Details
fix(cli): don't panic on a non-UTF-8 command-line argument (#16645)

GlobalArgs::check_markdown_help is the first statement executed in every
binary's entry point (cast, forge, anvil, chisel), before clap ever parses
argv. It used std::env::args(), which is documented to panic if any argument
isn't valid Unicode, so a single non-UTF-8 byte on the command line crashed
all four binaries with a raw panic instead of a usage error.

Switch to std::env::args_os(), which yields OsString instead of panicking.
OsString's PartialEq<str> impl means the existing comparisons against string
literals need no other changes.

Verified against a built cast/forge binary: the same non-UTF-8 argument now
produces a clean clap usage error (exit code 2) instead of an unrecovered
panic (exit code 101), for both the trivial case and the (correctly
unaffected) case where the bad argument follows a '--' separator.

Adds a regression test invoking the actual cast binary with a raw non-UTF-8
byte argument, proven via real red-before-green (fails with the actual panic
on unfixed code, passes after the fix).

Co-authored-by: DaniPopes <57450786+DaniPopes@users.noreply.github.com>

## Patch
### .changelog/nonutf8-arg-panic.md
```diff
@@ -0,0 +1,8 @@
+---
+cast: patch
+forge: patch
+anvil: patch
+chisel: patch
+---
+
+Fix all four binaries panicking on a non-UTF-8 command-line argument
```

### crates/cast/tests/cli/main.rs
```diff
@@ -85,6 +85,30 @@ Build Profile: [..]
 "#]]);
 });
 
+// tests that a non-UTF-8 command-line argument produces a clean error instead of an unrecovered
+// panic in `GlobalArgs::check_markdown_help` (which used to call `std::env::args()`, documented to
+// panic on invalid Unicode, as the very first statement of every binary's entry point)
+#[cfg(unix)]
+casttest!(non_utf8_argument_does_not_panic, |prj, _cmd| {
+    use std::os::unix::ffi::OsStrExt;
+
+    let bad_arg = std::ffi::OsStr::from_bytes(&[0xff]);
+    let output = prj.cast_bin().arg(bad_arg).output().unwrap();
+
+    assert_ne!(
+        output.status.code(),
+        Some(101),
+        "a non-UTF-8 argument must not cause an unrecovered panic (exit code 101); got status {:?}, stderr: {}",
+        output.status,
+        String::from_utf8_lossy(&output.stderr)
+    );
+    let stderr = String::from_utf8_lossy(&output.stderr);
+    assert!(
+        !stderr.contains("panicked at"),
+        "a non-UTF-8 argument must not panic; stderr: {stderr}"
+    );
+});
+
 // tests `--help` is printed to std out
 casttest!(print_help, |_prj, cmd| {
     cmd.arg("--help").assert_success().stdout_eq(str![[r#"
```

### crates/cli/src/opts/global.rs
```diff
@@ -61,7 +61,7 @@ impl GlobalArgs {
     /// This must be called **before** parsing arguments, since commands with required
     /// subcommands would fail parsing before the flag is checked.
     pub fn check_markdown_help<C: clap::CommandFactory>() {
-        if std::env::args().take_while(|a| a != "--").any(|a| a == "--markdown-help") {
+        if std::env::args_os().take_while(|a| a != "--").any(|a| a == "--markdown-help") {
             // Pre-parse: `Shell` is not initialized yet, so `sh_*` is unavailable.
             foundry_cli_markdown::print_help_markdown::<C>();
             std::process::exit(0);
```
