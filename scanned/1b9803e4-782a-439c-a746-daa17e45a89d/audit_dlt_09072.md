# [?] Fix stack overflow with long APDUs

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2022-03-24
Source: https://github.com/LedgerHQ/app-ethereum/commit/e57bc93c6976db400b004d38da1e2a6eeec25dad
Type: security-commit

## Details
Fix stack overflow with long APDUs

## Patch
### src_features/signMessageEIP712/entrypoint.c
```diff
@@ -594,7 +594,7 @@ void    init_heap(void)
 
 int     main(void)
 {
-    uint8_t         buf[256];
+    uint8_t         buf[260]; // 4 bytes APDU header + 256 bytes payload
     uint16_t        idx;
     int             state;
     uint8_t         payload_size = 0;
```
