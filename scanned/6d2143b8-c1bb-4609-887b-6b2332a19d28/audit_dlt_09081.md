# [?] fix(core): fix FLASH region overflow on T2T1

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-09-02
Source: https://github.com/trezor/trezor-firmware/commit/7bea7466f171e360d1357c12952df187183e4e8c
Type: security-commit

## Details
fix(core): fix FLASH region overflow on T2T1

Fixes https://github.com/trezor/trezor-firmware/issues/7792.

[no changelog]

## Patch
### core/embed/sys/linker/stm32f4/firmware.ld
```diff
@@ -65,7 +65,7 @@ SECTIONS {
     . = ALIGN(4);
   } >AUX1_RAM
 
-  .buf : ALIGN(4) {
+  .buf (NOLOAD) : ALIGN(4) {
     *(.buf*);
     . = ALIGN(4);
   } >AUX1_RAM
```
