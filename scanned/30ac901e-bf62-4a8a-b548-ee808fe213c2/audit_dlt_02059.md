# [?] fix(core): prevent overflow in storage UI callback

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-05-04
Source: https://github.com/trezor/trezor-firmware/commit/9a709303880a8224f1e4f35558f1a4813536f320
Type: security-commit

## Details
fix(core): prevent overflow in storage UI callback

- this PR makes sure that the reported `wait` argument (in seconds) does
not underflows to "4294967 seconds"
- this can ocassionaly happen in animated loader

[no changelog]

## Patch
### storage/storage.c
```diff
@@ -496,8 +496,11 @@ static secbool ui_progress(void) {
   ui_next_update = now + MIN_PROGRESS_UPDATE_MS;
   uint32_t ui_elapsed = now - ui_begin;
 
+  // Prevent overflow when the total time is underestimated.
+  int32_t diff = (int32_t)ui_total - (int32_t)ui_elapsed;
+  if (diff < 0) diff = 0;
   // Round the remaining time to the nearest second.
-  uint32_t ui_rem_sec = (ui_total - ui_elapsed + 500) / 1000;
+  uint32_t ui_rem_sec = (diff + 500) / 1000;
 
 #ifndef TREZOR_EMULATOR
   uint32_t progress = 0;
```
