# [?] fix(core): fix kernel crash when ext app fault

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-01-14
Source: https://github.com/trezor/trezor-firmware/commit/e79f97afeb0421bc29d539365a471de176d75f9b
Type: security-commit

## Details
fix(core): fix kernel crash when ext app fault

[no changelog]

## Patch
### core/embed/sys/task/stm32/systask.c
```diff
@@ -487,7 +487,14 @@ static uint32_t get_return_addr(bool secure, bool privileged, uint32_t sp) {
   }
 #endif
 
-  return *ret_addr;
+  // We checked that ret_addr is valid, but kernel/secmon need not
+  // to have access to the entire memory region where the stack resides =>
+  // MPU temporarily to read the return address.
+  mpu_mode_t mode = mpu_reconfig(MPU_MODE_DISABLED);
+  uint32_t addr = *ret_addr;
+  mpu_restore(mode);
+
+  return addr;
 }
 
 // Terminate active task from fault/exception handler
```
