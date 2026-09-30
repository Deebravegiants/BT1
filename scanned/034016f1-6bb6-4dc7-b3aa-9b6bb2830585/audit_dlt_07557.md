# [?] - fix "attempt to subtract with overflow" issue (#2445)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-program-library
Published: 2021-09-22
Source: https://github.com/solana-labs/solana-program-library/commit/11a36d9bd15bc0fad1b3b7e7c8d4bfa28c416684
Type: security-commit

## Details
- fix "attempt to subtract with overflow" issue (#2445)

* - fix "attempt to subtract with overflow" issue

* Update stake-pool/cli/src/main.rs

Co-authored-by: Jon Cinque <jon.cinque@gmail.com>

* Update stake-pool/cli/src/main.rs

Co-authored-by: Jon Cinque <jon.cinque@gmail.com>

* - run cargo fmt on it

Co-authored-by: Jon Cinque <jon.cinque@gmail.com>

## Patch
### stake-pool/cli/src/main.rs
```diff
@@ -1104,9 +1104,11 @@ fn prepare_withdraw_accounts(
         if lamports <= min_balance {
             continue;
         }
+
         let available_for_withdrawal = stake_pool
-            .calc_lamports_withdraw_amount(lamports - *MIN_STAKE_BALANCE)
+            .calc_lamports_withdraw_amount(lamports.saturating_sub(*MIN_STAKE_BALANCE))
             .unwrap();
+
         let pool_amount = u64::min(available_for_withdrawal, remaining_amount);
 
         // Those accounts will be withdrawn completely with `claim` instruction
@@ -1187,9 +1189,13 @@ fn command_withdraw(
             stake_pool_address,
         );
         let stake_account = config.rpc_client.get_account(&stake_account_address)?;
+
         let available_for_withdrawal = stake_pool
-            .calc_lamports_withdraw_amount(stake_account.lamports - *MIN_STAKE_BALANCE)
+            .calc_lamports_withdraw_amount(
+                stake_account.lamports.saturating_sub(*MIN_STAKE_BALANCE),
+            )
             .unwrap();
+
         if available_for_withdrawal < pool_amount {
             return Err(format!(
                 "Not enough lamports available for withdrawal from {}, {} asked, {} available",
```
