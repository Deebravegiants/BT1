# [?] add integration test to ensure add liquidty shares it nos exploitable

## Summary
Severity: Unknown
Chain: Hydration
Component: galacticcouncil/hydration-node
Published: 2025-10-06
Source: https://github.com/galacticcouncil/hydration-node/commit/1ce3a8161fe49cbb464f32650b94ff304c069288
Type: security-commit

## Details
add integration test to ensure add liquidty shares it nos exploitable

## Patch
### integration-tests/src/aave_router.rs
```diff
@@ -36,10 +36,11 @@ use pallet_liquidation::BorrowingContract;
 use pallet_route_executor::TradeExecution;
 use primitives::Balance;
 use sp_runtime::traits::Zero;
-use sp_runtime::DispatchResult;
+use sp_runtime::{DispatchError, DispatchResult};
 use sp_runtime::FixedU128;
 use sp_runtime::Permill;
 use sp_runtime::TransactionOutcome;
+use pallet_stableswap::MAX_ASSETS_IN_POOL;
 
 pub const PATH_TO_SNAPSHOT: &str = "evm-snapshot/SNAPSHOT";
 const RUNTIME_API_CALLER: EvmAddress = sp_core::H160(hex!("82db570265c37be24caf5bc943428a6848c3e9a6"));
@@ -906,3 +907,109 @@ mod transfer_atoken {
 		})
 	}
 }
+
+pub mod stableswap_with_atoken {
+	use hydradx_runtime::{RuntimeOrigin, Stableswap};
+	use super::*;
+
+	#[test]
+	fn add_liquidity_shares_should_not_work_when_user_has_not_enough_atoken_balance() {
+		crate::aave_router::with_atoken(|| {
+			let ed = 1000;
+			AssetRegistry::update(
+				hydradx_runtime::RuntimeOrigin::root(),
+				crate::aave_router::ADOT,
+				None,
+				None,
+				Some(ed),
+				None,
+				None,
+				None,
+				None,
+				None,
+			)
+				.unwrap();
+
+			let alice_all_balance = Currencies::free_balance(crate::aave_router::ADOT, &ALICE.into());
+			let adot_asset_id = HydraErc20Mapping::asset_address(crate::aave_router::ADOT);
+
+			let (pool_id, _,_) = init_stableswap_with_atoken().unwrap();
+
+			let alice_adot_balance = Currencies::free_balance(ADOT, &ALICE.into());
+			assert_eq!(alice_adot_balance, 1001);
+
+			//Should fail as alice has not enough asset to provide liquidity
+			assert_noop!(Stableswap::add_liquidity_shares(RuntimeOrigin::signed(ALICE.into()),pool_id, 666_000_000_000_000_000_000,ADOT, u128::MAX),  Other("evm:0x4e487b710000000000000000000000000000000000000000000000000000000000000011"));
+		})
+	}
+}
+
+pub fn init_stableswap_with_atoken() -> Result<(AssetId, AssetId, AssetId), DispatchError> {
+	let initial_liquidity = 1_000_000_000_000_000_000_000u128;
+
+	let mut initial: Vec<AssetAmount<<Runtime as pallet_stableswap::Config>::AssetId>> = vec![];
+	let mut asset_ids: Vec<<Runtime as pallet_stableswap::Config>::AssetId> = Vec::new();
+	//Add an asset
+	let name: Vec<u8> = 10i32.to_ne_bytes().to_vec();
+	let asset_id = AssetRegistry::register_sufficient_asset(
+		None,
+		Some(name.try_into().unwrap()),
+		AssetKind::Token,
+		1u128,
+		Some(b"xDUM".to_vec().try_into().unwrap()),
+		Some(18u8),
+		None,
+		None,
+	)?;
+
+	asset_ids.push(asset_id);
+	Currencies::update_balance(
+		RuntimeOrigin::root(),
+		AccountId::from(BOB),
+		asset_id,
+		initial_liquidity as i128,
+	)?;
+	initial.push(AssetAmount::new(asset_id, initial_liquidity));
+
+	//Add atoken
+	asset_ids.push(ADOT);
+	let initial_adot_liquidity = Currencies::free_balance(crate::aave_router::ADOT, &ALICE.into()) - 1001;
+	//assert_eq!(initial_adot_liquidity, 999999999990000);
+	initial.push(AssetAmount::new(ADOT, initial_adot_liquidity));
+	Currencies::transfer(RuntimeOrigin::signed(ALICE.into()), AccountId::from(BOB), ADOT, initial_adot_liquidity)?;
+	assert_eq!( Currencies::free_balance(crate::aave_router::ADOT, &ALICE.into()), 1001);
+
+	//
+	let pool_id = AssetRegistry::register_sufficient_asset(
+		None,
+		Some(b"pool".to_vec().try_into().unwrap()),
+		AssetKind::Token,
+		1u128,
+		None,
+		None,
+		None,
+		None,
+	)?;
+
+	let amplification = 100u16;
+	let fee = Permill::from_percent(1);
+
+	let asset_in: AssetId = *asset_ids.last().unwrap();
+	let asset_out: AssetId = *asset_ids.first().unwrap();
+
+	Stableswap::create_pool(
+		RuntimeOrigin::root(),
+		pool_id,
+		BoundedVec::truncate_from(asset_ids),
+		amplification,
+		fee,
+	)?;
+
+	Stableswap::add_liquidity(
+		RuntimeOrigin::signed(BOB.into()),
+		pool_id,
+		BoundedVec::truncate_from(initial),
+	)?;
+
+	Ok((pool_id, asset_in, asset_out))
+}
\ No newline at end of file
```
