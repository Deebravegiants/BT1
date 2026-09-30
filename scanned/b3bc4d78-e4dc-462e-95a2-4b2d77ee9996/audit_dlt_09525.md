# [?] Fix overflow multiplication

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2021-12-17
Source: https://github.com/chainflip-io/chainflip-backend/commit/f0283e8612228b2c65bcc89b0b9cac5ff7a25341
Type: security-commit

## Details
Fix overflow multiplication

## Patch
### state-chain/runtime/src/chainflip.rs
```diff
@@ -30,6 +30,7 @@ use sp_runtime::{
 use sp_std::{cmp::min, convert::TryInto, marker::PhantomData, prelude::*};
 
 use sp_io::hashing::twox_128;
+use sp_runtime::helpers_128bit::multiply_by_rational;
 
 impl Chainflip for Runtime {
 	type Call = Call;
@@ -187,7 +188,11 @@ impl RewardDistribution for BackupValidatorEmissions {
 			rewards = rewards
 				.into_iter()
 				.map(|(validator_id, reward)| {
-					(validator_id, (reward * emissions_cap) / total_rewards)
+					(
+						validator_id,
+						multiply_by_rational(reward, emissions_cap, total_rewards)
+							.unwrap_or_default(),
+					)
 				})
 				.collect();
 		}
```
