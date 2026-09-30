# [?] fix(core/bootloader): fix codec v1 overflow issues

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-03-26
Source: https://github.com/trezor/trezor-firmware/commit/eebd2e5e2d4f3ca3e0728a76337d66a54fc96229
Type: security-commit

## Details
fix(core/bootloader): fix codec v1 overflow issues

[no changelog]

## Patch
### core/embed/projects/bootloader/wire/codec_v1.c
```diff
@@ -49,8 +49,9 @@ secbool codec_parse_header(const uint8_t *buf, uint16_t *msg_id,
   if (buf[0] != '?' || buf[1] != '#' || buf[2] != '#') {
     return secfalse;
   }
-  *msg_id = (buf[3] << 8) + buf[4];
-  *msg_size = (buf[5] << 24) + (buf[6] << 16) + (buf[7] << 8) + buf[8];
+  *msg_id = ((uint16_t)buf[3] << 8) | buf[4];
+  *msg_size = ((uint32_t)buf[5] << 24) | ((uint32_t)buf[6] << 16) |
+              ((uint32_t)buf[7] << 8) | buf[8];
   return sectrue;
 }
 
@@ -170,6 +171,10 @@ static bool read(pb_istream_t *stream, uint8_t *buf, size_t count) {
 
   size_t packet_size = state->iface->rx_packet_size;
 
+  if (packet_size <= MSG_HEADER2_LEN) {
+    return false;
+  }
+
   size_t read = 0;
   // while we have data left
   while (read < count) {
@@ -224,12 +229,17 @@ void codec_flush(wire_iface_t *iface, uint32_t msg_size, uint8_t *buf) {
 
   size_t packet_size = iface->rx_packet_size;
 
+  if (packet_size <= MSG_HEADER1_LEN) {
+    return;
+  }
+
   if (msg_size > (packet_size - MSG_HEADER1_LEN)) {
     // calculate how many blocks need to be read to drain the message (rounded
-    // up to not leave any behind)
-    remaining_chunks = (msg_size - (packet_size - MSG_HEADER1_LEN) +
-                        ((packet_size - MSG_HEADER2_LEN) - 1)) /
-                       (packet_size - MSG_HEADER2_LEN);
+    // up to not leave any behind); use uint64_t to avoid 32-bit wrap for large
+    // attacker-supplied msg_size values
+    uint64_t num = (uint64_t)msg_size - (packet_size - MSG_HEADER1_LEN) +
+                   (packet_size - MSG_HEADER2_LEN - 1);
+    remaining_chunks = (int)(num / (packet_size - MSG_HEADER2_LEN));
   }
 
   for (int i = 0; i < remaining_chunks; i++) {
```
