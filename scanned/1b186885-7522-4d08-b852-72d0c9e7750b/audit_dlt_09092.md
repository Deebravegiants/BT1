# [?] fix(core): prevent NFC driver crash on repeated deinitialization

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-04-28
Source: https://github.com/trezor/trezor-firmware/commit/c856ba57d746c30852ac39b6337d3b2c0d9c5a69
Type: security-commit

## Details
fix(core): prevent NFC driver crash on repeated deinitialization

[no changelog]

## Patch
### core/embed/io/nfc/st25/nfc.c
```diff
@@ -262,7 +262,9 @@ void nfc_deinit(void) {
     drv->rfal_initialized = false;
   }
 
-  HAL_SPI_DeInit(&drv->hspi);
+  if (drv->hspi.Instance != NULL) {
+    HAL_SPI_DeInit(&drv->hspi);
+  }
 
   HAL_GPIO_DeInit(NFC_SPI_MISO_PORT, NFC_SPI_MISO_PIN);
   HAL_GPIO_DeInit(NFC_SPI_MOSI_PORT, NFC_SPI_MOSI_PIN);
```
