# [?] Fix feesToString buffer overflow

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2022-08-09
Source: https://github.com/LedgerHQ/app-ethereum/commit/d3840079123bdc7dd91317731c1fabd29ea91515
Type: security-commit

## Details
Fix feesToString buffer overflow

## Patch
### src_features/signTx/logic_signTx.c
```diff
@@ -231,15 +231,26 @@ static void feesToString(uint256_t *rawFee, char *displayBuffer, uint32_t displa
     i = 0;
     tickerOffset = 0;
     memset(displayBuffer, 0, displayBufferSize);
+
     while (feeTicker[tickerOffset]) {
+        if ((uint32_t) tickerOffset >= displayBufferSize) {
+            break;
+        }
+
         displayBuffer[tickerOffset] = feeTicker[tickerOffset];
         tickerOffset++;
     }
     while (G_io_apdu_buffer[i]) {
+        if ((uint32_t) (tickerOffset) + i >= displayBufferSize) {
+            break;
+        }
         displayBuffer[tickerOffset + i] = G_io_apdu_buffer[i];
         i++;
     }
-    displayBuffer[tickerOffset + i] = '\0';
+
+    if ((uint32_t) (tickerOffset) + i < displayBufferSize) {
+        displayBuffer[tickerOffset + i] = '\0';
+    }
 }
 
 // Compute the fees, transform it to a string, prepend a ticker to it and copy everything to
```
