# [?] fix(nordic): fix crashes on disconnect events

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-04-10
Source: https://github.com/trezor/trezor-firmware/commit/2aafdd40b4d7a1b1d6d09f2c5ed088ac1a5e4014
Type: security-commit

## Details
fix(nordic): fix crashes on disconnect events

[no changelog]

## Patch
### nordic/trezor/trezor-ble/src/ble/connection.c
```diff
@@ -62,13 +62,11 @@ void connected(struct bt_conn *conn, uint8_t err) {
 void disconnected(struct bt_conn *conn, uint8_t reason) {
   char addr[BT_ADDR_LE_STR_LEN];
 
-  bt_addr_le_to_str(bt_conn_get_dst(conn), addr, sizeof(addr));
-
-  LOG_INF("Disconnected: %s (reason %u)", addr, reason);
-
   pairing_reset();
 
   if (current_conn) {
+    bt_addr_le_to_str(bt_conn_get_dst(conn), addr, sizeof(addr));
+    LOG_INF("Disconnected: %s (reason %u)", addr, reason);
     bt_conn_unref(current_conn);
     current_conn = NULL;
   }
@@ -104,6 +102,7 @@ void connection_disconnect(void) {
     LOG_INF("Remotely disconnected");
     bt_conn_disconnect(current_conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
     bt_conn_unref(current_conn);
+    current_conn = NULL;
   }
 }
 
```
