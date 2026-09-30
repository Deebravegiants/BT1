# [?] fix(core/bootloader): fix overflow wipe progress calculation

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-06-25
Source: https://github.com/trezor/trezor-firmware/commit/a2596ef28de8465c9f00e670a3a13a42029d2b8c
Type: security-commit

## Details
fix(core/bootloader): fix overflow wipe progress calculation

[no changelog]

## Patch
### core/embed/projects/bootloader/bootui.c
```diff
@@ -147,7 +147,7 @@ confirm_result_t ui_screen_wipe_confirm(void) { return screen_wipe_confirm(); }
 void ui_screen_wipe(void) { screen_wipe_progress(0, true); }
 
 void ui_screen_wipe_progress(int pos, int len) {
-  screen_wipe_progress(1000 * pos / len, false);
+  screen_wipe_progress((int16_t)(1000 * (int64_t)pos / len), false);
 }
 
 // done UI
```
