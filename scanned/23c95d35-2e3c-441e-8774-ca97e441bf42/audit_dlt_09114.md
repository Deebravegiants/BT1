# [?] fix(emulator): fix emulator crash on MacOS

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2024-10-30
Source: https://github.com/trezor/trezor-firmware/commit/8bc3890639b92aa54bcc62b6cdf2a162b41eeff2
Type: security-commit

## Details
fix(emulator): fix emulator crash on MacOS

[no changelog]

## Patch
### core/embed/lib/error_handling.c
```diff
@@ -23,7 +23,11 @@
 #include "error_handling.h"
 #include "system.h"
 
+#ifndef TREZOR_EMULATOR
+// Stack check guard value set in startup code.
+// This is used if stack protection is enabled.
 uint32_t __stack_chk_guard = 0;
+#endif
 
 // Calls to this function are inserted by the compiler
 // when stack protection is enabled.
```
