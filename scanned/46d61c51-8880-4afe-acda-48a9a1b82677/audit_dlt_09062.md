# [?] Fix potential out-of-bounds read by up to 2 bytes during TLV parsing

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2024-11-27
Source: https://github.com/LedgerHQ/app-ethereum/commit/51bc8b25a9230c713355d35e5f3b5cea5b9a3c33
Type: security-commit

## Details
Fix potential out-of-bounds read by up to 2 bytes during TLV parsing

## Patch
### src_features/provideDynamicNetwork/network_dynamic.c
```diff
@@ -493,6 +493,10 @@ static uint16_t parse_tlv(const uint8_t *data, uint8_t length) {
     cx_sha256_init(&sig_ctx.hash_ctx);
     // handle TLV payload
     while (offset != length) {
+        if ((offset + 2) > length) {
+            sw = APDU_RESPONSE_INVALID_DATA;
+            break;
+        }
         tag_start_off = offset;
         field_tag = data[offset++];
         field_len = data[offset++];
```
