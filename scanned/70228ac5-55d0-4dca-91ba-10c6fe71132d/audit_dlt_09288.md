# [?] fix(tui): always restore terminal state during panic unwinding (#14965)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-06-02
Source: https://github.com/foundry-rs/foundry/commit/404283cba65040a4a0e053ae5e1e6953e0f0f8e9
Type: security-commit

## Details
fix(tui): always restore terminal state during panic unwinding (#14965)

Co-authored-by: Mablr <59505383+mablr@users.noreply.github.com>

## Patch
### crates/tui/src/lib.rs
```diff
@@ -178,6 +178,11 @@ impl<B: Backend + Write> TerminalGuard<B> {
     }
 
     fn restore(&mut self) {
+        // Always restore terminal state on drop, even during panic unwinding.
+        // The panic hook installed in `setup()` may be replaced by external code,
+        // so `Drop` must not rely on it as the sole cleanup path.
+        Self::half_restore(self.terminal.backend_mut());
+
         if !panicking() {
             let _ = take_hook();
             let prev = self.hook.take().unwrap();
@@ -186,8 +191,6 @@ impl<B: Backend + Write> TerminalGuard<B> {
                 Err(_) => unreachable!("`self.hook` is not the only reference to the panic hook"),
             };
             set_hook(prev);
-
-            Self::half_restore(self.terminal.backend_mut());
         }
 
         let _ = self.terminal.show_cursor();
```
