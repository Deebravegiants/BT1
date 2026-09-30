# [?] fix(nordic/ble): fix stack overflow crash

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-09-19
Source: https://github.com/trezor/trezor-firmware/commit/9935c83c66b66e05f080f4b02b499f17c03806fa
Type: security-commit

## Details
fix(nordic/ble): fix stack overflow crash

[no changelog]

## Patch
### nordic/trezor/trezor-ble/src/ble/advertising.c
```diff
@@ -169,7 +169,11 @@ void advertising_start(bool wl, bool user_disconnect, uint8_t color,
   /* Fill second element for the name */
   advertising_data[1].type = BT_DATA_NAME_COMPLETE;
   advertising_data[1].data_len = name_len;
-  advertising_data[1].data = (const uint8_t *)name;
+
+  static char adv_name[BLE_ADV_NAME_LEN + 1] = {0};
+  memset(adv_name, 0, BLE_ADV_NAME_LEN + 1);
+  memcpy(adv_name, name, name_len);
+  advertising_data[1].data = (const uint8_t *)adv_name;
 
   char gap_name[BLE_ADV_NAME_LEN + 1] = {0};
   memcpy(gap_name, name, name_len);
```

### nordic/trezor/trezor-ble/src/ble/ble_management.c
```diff
@@ -253,5 +253,5 @@ void ble_management_thread(void) {
   }
 }
 
-K_THREAD_DEFINE(ble_management_thread_id, CONFIG_DEFAULT_THREAD_STACK_SIZE,
-                ble_management_thread, NULL, NULL, NULL, 7, 0, 0);
+K_THREAD_DEFINE(ble_management_thread_id, 2048, ble_management_thread, NULL,
+                NULL, NULL, 7, 0, 0);
```
