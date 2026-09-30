# [?] Fix out-of-bounds read on TLV parser

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2024-09-26
Source: https://github.com/LedgerHQ/app-ethereum/commit/d1a3b6af0184b3a94cb36b2f45fcc30ec299eb4f
Type: security-commit

## Details
Fix out-of-bounds read on TLV parser

## Patch
### src_features/provideTrustedName/cmd_provide_trusted_name.c
```diff
@@ -809,7 +809,8 @@ static bool parse_tlv(const s_tlv_payload *payload,
                 break;
 
             case TLV_VALUE:
-                if (offset >= payload->size) {
+                if ((offset + data.length) > payload->size) {
+                    PRINTF("Error: value would go beyond the TLV payload!\n");
                     return false;
                 }
                 data.value = &payload->buf[offset];
@@ -833,6 +834,10 @@ static bool parse_tlv(const s_tlv_payload *payload,
                 return false;
         }
     }
+    if (step != TLV_TAG) {
+        PRINTF("Error: unexpected data at the end of the TLV payload!\n");
+        return false;
+    }
     return verify_struct(trusted_name_info);
 }
 
```
