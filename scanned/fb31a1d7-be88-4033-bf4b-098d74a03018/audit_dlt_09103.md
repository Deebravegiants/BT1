# [?] fix(core): fix integer overflow in storage

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-09-29
Source: https://github.com/trezor/trezor-firmware/commit/56755da9abd1d948987f587c4b9186594668f3e1
Type: security-commit

## Details
fix(core): fix integer overflow in storage

[no changelog]

## Patch
### storage/norcow_blockwise.h
```diff
@@ -274,7 +274,7 @@ secbool norcow_update_bytes(const uint16_t key, const uint8_t *data,
   }
 
   uint16_t tmp_len = len;
-  uint16_t flash_offset = sector_offset + norcow_write_buffer_flashed;
+  uint32_t flash_offset = sector_offset + norcow_write_buffer_flashed;
 
   ensure(flash_unlock_write(), NULL);
   while (tmp_len > 0) {
```
