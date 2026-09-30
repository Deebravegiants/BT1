# [?] fix(core): memory corruption on emulator init

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2024-10-22
Source: https://github.com/trezor/trezor-firmware/commit/87aab69644815c897fa0f86e879905be2eac83c2
Type: security-commit

## Details
fix(core): memory corruption on emulator init

Found by AddressSanitizer.

## Patch
### core/embed/trezorhal/unix/systimer.c
```diff
@@ -38,7 +38,7 @@ void systimer_init(void) {
     return;
   }
 
-  memset(&drv, 0, sizeof(systimer_driver_t));
+  memset(drv, 0, sizeof(systimer_driver_t));
   drv->initialized = true;
 }
 
```
