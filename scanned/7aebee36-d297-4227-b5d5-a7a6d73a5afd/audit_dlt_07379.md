# [?] fix: Reject ERC-1155 batch transfers whose aggregate quantity overflows

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-05-12
Source: https://github.com/LedgerHQ/app-ethereum/commit/e0b8c65339f5717b0ac9f16fd247f55b1c8df5bc
Type: security-commit

## Details
fix: Reject ERC-1155 batch transfers whose aggregate quantity overflows

The ERC-1155 batch_transfer parser accumulates per-id values into
context->value via add256() to compute the total quantity displayed
on the review screen. add256 wraps on uint256 overflow without
signalling, so a crafted calldata whose values sum past 2^256 would
silently produce a truncated total - a hostile dApp could pair a
benign-looking aggregate with adversarial per-id quantities.

After each accumulation, detect overflow by checking
gt256(&new_value, &context->value): when the running total is now
smaller than the addend, the sum has wrapped. Set the plugin result
to ERROR so the host cannot present a misleading review screen.

(cherry picked from commit 2f24a04bcfa6d4faf0b455d19a59ff10bb380c51)

## Patch
### src/plugins/erc1155/erc1155_provide_parameters.c
```diff
@@ -112,6 +112,15 @@ static void handle_batch_transfer(ethPluginProvideParameter_t *msg, erc1155_cont
             }
             convertUint256BE(context->tokenId, sizeof(context->tokenId), &new_value);
             add256(&context->value, &new_value, &context->value);
+            // Reject crafted batches whose per-id totals wrap uint256. With
+            // the partial sum already stored in context->value, an overflow
+            // would silently misreport the aggregate "total quantity" shown
+            // to the user.
+            if (gt256(&new_value, &context->value)) {
+                PRINTF("Batch transfer aggregate quantity overflow\n");
+                msg->result = ETH_PLUGIN_RESULT_ERROR;
+                break;
+            }
             if (--context->values_array_len == 0) {
                 context->next_param = NONE;
             }
```
