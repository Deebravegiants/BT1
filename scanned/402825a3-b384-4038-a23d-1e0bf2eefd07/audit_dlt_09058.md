# [?] fix(network_info): oob read due to integer truncation

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-03-25
Source: https://github.com/LedgerHQ/app-ethereum/commit/a525e4cc4552c524cc99a800d571e822429154c0
Type: security-commit

## Details
fix(network_info): oob read due to integer truncation

## Patch
### src/features/provide_network_info/network_icon.c
```diff
@@ -1,14 +1,16 @@
 #include <stdbool.h>
+#include <stdint.h>
 #include "apdu_constants.h"
 #include "network_info.h"
 #include "write.h"
 #include "tlv_apdu.h"
 #include "app_mem_utils.h"
 #include "ui_utils.h"
 
-#define P2_NETWORK_CONFIG 0x00
-#define P2_NETWORK_ICON   0x01
-#define P2_GET_INFO       0x02
+#define P2_NETWORK_CONFIG        0x00
+#define P2_NETWORK_ICON          0x01
+#define P2_GET_INFO              0x02
+#define NETWORK_ICON_HEADER_SIZE 8U
 
 typedef struct {
     uint16_t received_size;
@@ -31,13 +33,15 @@ static bool check_icon_header(const uint8_t *data, uint16_t length, uint16_t *bu
     uint16_t width = 0;
     uint16_t height = 0;
     uint16_t expected_px = 0;
+    uint32_t payload_size = 0;
+    uint32_t total_size = 0;
 
     // The chunk starts by the Image Header (8 Bytes):
     //   - Width (2 Bytes)
     //   - Height (2 Bytes)
     //   - BPP (1 Byte)
     //   - Img buffer size (3 Bytes)
-    if (length < 8) {
+    if (length < NETWORK_ICON_HEADER_SIZE) {
         PRINTF("NETWORK_ICON header length mismatch (%d)!\n", length);
         return false;
     }
@@ -56,7 +60,15 @@ static bool check_icon_header(const uint8_t *data, uint16_t length, uint16_t *bu
         PRINTF("NETWORK_ICON size mismatch (%dx%d)!\n", width, height);
         return false;
     }
-    *buffer_size = 8 + data[5] + (data[6] << 8) + (data[7] << 16);
+    payload_size =
+        ((uint32_t) data[5]) | (((uint32_t) data[6]) << 8) | (((uint32_t) data[7]) << 16);
+    total_size = NETWORK_ICON_HEADER_SIZE + payload_size;
+    // The icon pipeline tracks buffer sizes as uint16_t, so reject non-representable headers.
+    if (total_size > UINT16_MAX) {
+        PRINTF("NETWORK_ICON length overflow (%lu)!\n", (unsigned long) total_size);
+        return false;
+    }
+    *buffer_size = (uint16_t) total_size;
     return true;
 }
 
```
