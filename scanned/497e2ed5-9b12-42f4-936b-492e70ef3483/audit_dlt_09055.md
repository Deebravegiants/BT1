# [?] fix: Out-of-bounds read in amount-join token address comparison in update_amount_join (#984)

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-04-10
Source: https://github.com/LedgerHQ/app-ethereum/commit/bae8f4587caeb18f6b0773b8a231a5c4fabeaf15
Type: security-commit

## Details
fix: Out-of-bounds read in amount-join token address comparison in update_amount_join (#984)

Co-authored-by: Cerberus Merlin <merlin@cerberus.security>

## Patch
### src/features/sign_message_eip712/ui_logic.c
```diff
@@ -638,6 +638,10 @@ static bool update_amount_join(const uint8_t *data, uint8_t length) {
     }
     switch (ui_ctx->amount.state) {
         case AMOUNT_JOIN_STATE_TOKEN:
+            if (length != ADDRESS_LENGTH) {
+                apdu_response_code = SWO_INCORRECT_DATA;
+                return false;
+            }
             if (token != NULL) {
                 if (memcmp(data, token->address, ADDRESS_LENGTH) != 0) {
                     return false;
```
