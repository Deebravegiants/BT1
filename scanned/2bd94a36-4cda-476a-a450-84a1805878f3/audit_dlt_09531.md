# [?] Merge pull request #410 from chainflip-io/fix/reputation-genesis-panic

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2021-08-18
Source: https://github.com/chainflip-io/chainflip-backend/commit/d2b5ae1ae3c2bdc3b079eb77eb33ca129ef7b219
Type: security-commit

## Details
Merge pull request #410 from chainflip-io/fix/reputation-genesis-panic

Add accrual ratio to genesis

## Patch
### state-chain/node/src/chain_spec.rs
```diff
@@ -5,8 +5,8 @@ use sp_finality_grandpa::AuthorityId as GrandpaId;
 use sp_runtime::traits::{IdentifyAccount, Verify};
 use state_chain_runtime::{
 	opaque::SessionKeys, AccountId, AuctionConfig, AuraConfig, EmissionsConfig, FlipBalance,
-	FlipConfig, GenesisConfig, GrandpaConfig, SessionConfig, Signature, StakingConfig, SudoConfig,
-	SystemConfig, ValidatorConfig, DAYS, WASM_BINARY,
+	FlipConfig, GenesisConfig, GrandpaConfig, ReputationConfig, SessionConfig, Signature,
+	StakingConfig, SudoConfig, SystemConfig, ValidatorConfig, DAYS, WASM_BINARY,
 };
 
 // The URL for the telemetry server.
@@ -29,6 +29,11 @@ const BLOCK_EMISSIONS: FlipBalance = {
 	ANNUAL_INFLATION / 365 * DAYS as u128
 };
 
+// Number of blocks to be online to accrue a point
+pub const ACCRUAL_BLOCKS: u32 = 2500;
+// Number of accrual points
+pub const ACCRUAL_POINTS: i32 = 1;
+
 /// Specialized `ChainSpec`. This is a specialization of the general Substrate ChainSpec type.
 pub type ChainSpec = sc_service::GenericChainSpec<GenesisConfig>;
 
@@ -351,7 +356,9 @@ fn testnet_genesis(
 			emission_per_block: BLOCK_EMISSIONS,
 			..Default::default()
 		}),
-		pallet_cf_reputation: Some(Default::default()),
+		pallet_cf_reputation: Some(ReputationConfig {
+			accrual_ratio: (ACCRUAL_POINTS, ACCRUAL_BLOCKS),
+		}),
 	}
 }
 
```
