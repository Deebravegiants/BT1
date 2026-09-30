# [?] fix: fix underflow panic (#2276)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2022-10-13
Source: https://github.com/chainflip-io/chainflip-backend/commit/ed4ac642276c57515cac1f6858168f5b979dd238
Type: security-commit

## Details
fix: fix underflow panic (#2276)

## Patch
### state-chain/pallets/cf-validator/src/lib.rs
```diff
@@ -1075,7 +1075,7 @@ impl<T: Config> Pallet<T> {
 
 		let limit = Self::backup_reward_nodes_limit();
 		if limit < backups.len() {
-			backups.select_nth_unstable_by_key(limit - 1, |(_, amount)| Reverse(*amount));
+			backups.select_nth_unstable_by_key(limit, |(_, amount)| Reverse(*amount));
 			backups.truncate(limit);
 		}
 
```
