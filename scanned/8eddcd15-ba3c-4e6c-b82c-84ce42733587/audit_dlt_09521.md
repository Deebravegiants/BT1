# [?] fix: don't panic on missing author (#2770)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2023-01-27
Source: https://github.com/chainflip-io/chainflip-backend/commit/00b8450e1777fb6ebaa342af61f5171623e22562
Type: security-commit

## Details
fix: don't panic on missing author (#2770)

## Patch
### state-chain/runtime/src/chainflip.rs
```diff
@@ -60,7 +60,7 @@ use frame_support::{
 };
 
 use pallet_cf_validator::PercentageRange;
-use sp_runtime::traits::{UniqueSaturatedFrom, UniqueSaturatedInto};
+use sp_runtime::traits::{BlockNumberProvider, UniqueSaturatedFrom, UniqueSaturatedInto};
 use sp_std::prelude::*;
 
 use backup_node_rewards::calculate_backup_rewards;
@@ -205,10 +205,11 @@ impl RewardsDistribution for BlockAuthorRewardDistribution {
 	fn distribute() {
 		let reward_amount = Emissions::current_authority_emission_per_block();
 		if reward_amount != 0 {
-			// TODO: Check if it's ok to panic here.
-			let current_block_author =
-				Authorship::author().expect("A block without an author is invalid.");
-			Flip::settle(&current_block_author, Self::Issuance::mint(reward_amount).into());
+			if let Some(current_block_author) = Authorship::author() {
+				Flip::settle(&current_block_author, Self::Issuance::mint(reward_amount).into());
+			} else {
+				log::warn!("No block author for block {}.", System::current_block_number());
+			}
 		}
 	}
 }
```
