# [M] Any token account owned by delegate can be used

## Summary
Severity: Medium
Contest weight: 0.0806
Dataset id: 5384
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Different delegate_token_account can be used here as long as the mint is expected and the delegate is the owner of the account. One can change ownership of their token account to set the delegate and use this account with Lingo's program. This ends up with fees being collected in multiple different token accounts (liquidity fragmentation).

## Recommendation
Prefer using the associated token account for the delegate, as only one token account is expected to be used here:
diff --git a/programs/transfer_hook/src/context/fee_claim_back.rs b/programs/transfer_hook/src/context/fee_claim_back.rs
index 706711a..0800543 100644
--- a/programs/transfer_hook/src/context/fee_claim_back.rs
+++ b/programs/transfer_hook/src/context/fee_claim_back.rs
@@ -35,8 +35,8 @@ pub struct FeeClaimBack<'info> {
