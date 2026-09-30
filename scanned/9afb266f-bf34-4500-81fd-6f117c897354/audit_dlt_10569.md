# [?] fix(core): fix crash when setting wipe code

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-10-10
Source: https://github.com/trezor/trezor-firmware/commit/da76bd501dd1bfefba472a969f213253ac6fc7cf
Type: security-commit

## Details
fix(core): fix crash when setting wipe code

[no changelog]

## Patch
### storage/storage.c
```diff
@@ -1684,12 +1684,12 @@ secbool storage_change_wipe_code(const uint8_t *pin, size_t pin_len,
     return secfalse;
   }
 
+  mpu_mode_t mpu_mode = mpu_reconfig(MPU_MODE_STORAGE);
+
   ui_progress_init(STORAGE_PIN_OP_VERIFY);
   ui_message =
       (pin_len != 0 && wipe_code_len == 0) ? VERIFYING_PIN_MSG : PROCESSING_MSG;
 
-  mpu_mode_t mpu_mode = mpu_reconfig(MPU_MODE_STORAGE);
-
   secbool ret = unlock(pin, pin_len, ext_salt);
   if (sectrue != ret) {
     goto end;
```
