# [M] Not Allowing Owner to Withdraw Any Extra Token in owner_withdraw_token Function

## Summary
Severity: Medium
Chain: Smart contract
Component: AlephZeroAMM
Published: 2024-01-28
Source: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/47
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xa23854063fa86292d03055a0da5fb89ee03634e9728d240b66b2ce0d0b60d371
**Severity:** medium

**Description:**
**Description**\

The `owner_withdraw_token` function enables the owner to withdraw any additional token from the contract. However, the existing implementation restricts the owner from withdrawing extra tokens associated with the `pool_id`. The purpose of this function is to facilitate the withdrawal of extra reward tokens. The current restriction is imposed by the 
`ensure!(self.pool_id != token, FarmError::RewardTokenIsPoolToken);` check.


**Impact**\

The owner should have the ability to withdraw any extra token from the contract, including those linked to the `pool_id`.



**Revised Code File (Optional)**

```diff
         fn owner_withdraw_token(&mut self, token: TokenId) -> Result<(), FarmError> {
             ensure!(self.env().caller() == self.owner, FarmError::CallerNotOwner);
             ensure!(!self.is_active(), FarmError::FarmAlreadyRunning);
-            // Owner should be able to withdraw every token except the pool token.
-            ensure!(self.pool_id != token, FarmError::RewardTokenIsPoolToken);
+            // Owner should be able to withdraw every extra token.
 
             self.update()?;
             let mut token_ref: contract_ref!(PSP22) = token.into();
             let total_balance = token_ref.balance_of(self.env().account_id());
-            let undistributed_balance = if let Some(token_index) =
+            let mut undistributed_balance = if let Some(token_index) =
                 self.reward_tokens.iter().position(|&t| t == token)
             {
                 total_balance.saturating_sub(self.farm_distributed_unclaimed_rewards[token_index])
             } else {
                 total_balance
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/47_
