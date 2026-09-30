# [?] fix(zk_toolbox): Do not panic during mint (#2658)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-08-14
Source: https://github.com/matter-labs/zksync-era/commit/1a8ee90d9d6578492806bd0a337ef203db32f6c9
Type: security-commit

## Details
fix(zk_toolbox): Do not panic during mint (#2658)

## What ❔

<!-- What are the changes this PR brings about? -->
<!-- Example: This PR adds a PR template to the repo. -->
<!-- (For bigger PRs adding more context is appreciated) -->

## Why ❔

<!-- Why are these changes done? What goal do they contribute to? What
are the principles behind them? -->
<!-- Example: PR templates ensure PR reviewers, observers, and future
iterators are in context about the evolution of repos. -->

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [ ] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [ ] Code has been formatted via `zk fmt` and `zk lint`.

Signed-off-by: Danil <deniallugo@gmail.com>

## Patch
### zk_toolbox/crates/common/src/ethereum.rs
```diff
@@ -9,7 +9,7 @@ use ethers::{
     types::{Address, TransactionRequest, H256},
 };
 
-use crate::wallets::Wallet;
+use crate::{logger, wallets::Wallet};
 
 pub fn create_ethers_client(
     private_key: H256,
@@ -79,15 +79,26 @@ pub async fn mint_token(
     let contract = TokenContract::new(token_address, client);
     // contract
     for address in addresses {
-        contract
-            .mint(address, amount.into())
-            .send()
-            .await?
-            // It's safe to set such low number of confirmations and low interval for localhost
-            .confirmations(1)
-            .interval(Duration::from_millis(30))
-            .await?;
+        if let Err(err) = mint(&contract, address, amount).await {
+            logger::warn(format!("Failed to mint {err}"))
+        }
     }
 
     Ok(())
 }
+
+async fn mint<T: Middleware + 'static>(
+    contract: &TokenContract<T>,
+    address: Address,
+    amount: u128,
+) -> anyhow::Result<()> {
+    contract
+        .mint(address, amount.into())
+        .send()
+        .await?
+        // It's safe to set such low number of confirmations and low interval for localhost
+        .confirmations(1)
+        .interval(Duration::from_millis(30))
+        .await?;
+    Ok(())
+}
```
