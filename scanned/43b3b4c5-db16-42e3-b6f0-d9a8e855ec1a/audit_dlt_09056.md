# [?] fix: Out-of-bounds read on zero-length int8 EIP-712 fields during display formatting

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-04-09
Source: https://github.com/LedgerHQ/app-ethereum/commit/f8420a9cf5a470a5375a034b396d2606e909b765
Type: security-commit

## Details
fix: Out-of-bounds read on zero-length int8 EIP-712 fields during display formatting

## Patch
### src/features/sign_message_eip712/ui_logic.c
```diff
@@ -477,6 +477,10 @@ static bool ui_712_format_int(const uint8_t *data,
     if (!first) {
         return false;
     }
+    if (length < 1) {
+        apdu_response_code = SWO_INCORRECT_DATA;
+        return false;
+    }
     if (length > field_ptr->type_size) {
         apdu_response_code = SWO_INCORRECT_DATA;
         return false;
@@ -506,6 +510,10 @@ static bool ui_712_format_int(const uint8_t *data,
             snprintf(strings.tmp.tmp, sizeof(strings.tmp.tmp), "%d", value16);
             break;
         case 8:
+            if (length != sizeof(int8_t)) {
+                apdu_response_code = SWO_INCORRECT_DATA;
+                return false;
+            }
             value8 = (int8_t) data[0];
             snprintf(strings.tmp.tmp, sizeof(strings.tmp.tmp), "%d", value8);
             break;
```
