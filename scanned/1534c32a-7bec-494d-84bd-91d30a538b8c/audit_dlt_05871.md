# [?] fix(zk_toolbox): Do not panic if mint is not successful (#2973)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-09-26
Source: https://github.com/matter-labs/zksync-era/commit/57b99d4fc906ae7ab5532ea23a069b34a2ee7c02
Type: security-commit

## Details
fix(zk_toolbox): Do not panic if mint is not successful (#2973)

## What ❔

Use governor for minting process and do not panic if minting is not
successful

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
@@ -10,7 +10,7 @@ use ethers::{
 };
 use types::TokenInfo;
 
-use crate::wallets::Wallet;
+use crate::{logger, wallets::Wallet};
 
 pub fn create_ethers_client(
     private_key: H256,
@@ -103,13 +103,12 @@ pub async fn mint_token(
 
     let mut pending_txs = vec![];
     for call in &pending_calls {
-        pending_txs.push(
-            call.send()
-                .await?
-                // It's safe to set such low number of confirmations and low interval for localhost
-                .confirmations(3)
-                .interval(Duration::from_millis(30)),
-        );
+        let call = call.send().await;
+        match call {
+            // It's safe to set such low number of confirmations and low interval for localhost
+            Ok(call) => pending_txs.push(call.confirmations(3).interval(Duration::from_millis(30))),
+            Err(e) => logger::error(format!("Minting is not successful {e}")),
+        }
     }
 
     futures::future::join_all(pending_txs).await;
```

### zk_toolbox/crates/zk_inception/src/commands/chain/common.rs
```diff
@@ -111,7 +111,7 @@ pub async fn mint_base_token(
         let amount = AMOUNT_FOR_DISTRIBUTION_TO_WALLETS * base_token.nominator as u128
             / base_token.denominator as u128;
         common::ethereum::mint_token(
-            wallets.operator,
+            wallets.governor,
             base_token.address,
             addresses,
             l1_rpc_url,
```
