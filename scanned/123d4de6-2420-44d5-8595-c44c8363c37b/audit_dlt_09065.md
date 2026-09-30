# [?] fix potential oob writes

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2024-04-12
Source: https://github.com/LedgerHQ/app-ethereum/commit/5b905fe47fafe70d755010ac8377bc85d1d96f81
Type: security-commit

## Details
fix potential oob writes

## Patch
### src_common/common_utils.c
```diff
@@ -199,8 +199,11 @@ bool amountToString(const uint8_t *amount,
     uint8_t amount_len = strnlen(tmp_buffer, sizeof(tmp_buffer));
     uint8_t ticker_len = strnlen(ticker, MAX_TICKER_LEN);
 
-    memcpy(out_buffer, ticker, MIN(out_buffer_size, ticker_len));
     if (ticker_len > 0) {
+        if (out_buffer_size <= ticker_len + 1) {
+            return false;
+        }
+        memcpy(out_buffer, ticker, ticker_len);
         out_buffer[ticker_len++] = ' ';
     }
 
```
