Audit Report

## Title
Unprotected AMM swap with no slippage/minimum-output check in `add_tip` / `register_token` enables price-manipulation of Ether accounting - (File: `bridges/snowbridge/pallets/system-frontend/src/lib.rs`)

## Summary
`swap_and_burn` in the `snowbridge-pallet-system-frontend` pallet swaps a caller-supplied tip/fee asset for Ether via `T::Swap::swap_exact_tokens_for_tokens` (backed by `pallet-asset-conversion`) with `amount_out_min` hard-coded to `None`, disabling all slippage protection. This function is reachable from the unprivileged, signed extrinsic `add_tip` and the origin-gated `register_token`, both of which forward the resulting `ether_gained` to the Ethereum side as the basis for relayer reward/fee accounting, making that figure manipulable via same-block AMM price manipulation.

## Finding Description
`swap_and_burn` executes the token conversion with no minimum-output bound: [1](#0-0) . This is directly confirmed in the code — the comment "No minimum amount required" at line 305 accurately reflects that `None` is passed for `amount_out_min`.

This is reachable from two entry points:
- `add_tip`, callable by any signed account, swaps a caller-supplied `asset` for Ether via `swap_fee_asset_and_burn` and forwards `ether_gained` to the `AddTip` transact call for reward accounting on BridgeHub/Ethereum: [2](#0-1) .
- `register_token`, using `T::RegisterTokenOrigin::ensure_origin` gating (any origin that owns the asset location, i.e., not root-restricted for non-`here` origins), which similarly swaps `fee_asset` for Ether before embedding `ether_gained` into the dispatched `RegisterToken` call: [3](#0-2) .

`pallet-asset-conversion`'s `do_swap_exact_tokens_for_tokens` does support and correctly enforce an `amount_out_min` guard when provided (`Error::ProvidedMinimumNotSufficientForSwap`), confirmed by the guard logic and existing unit test `swap_should_not_work_if_too_much_slippage`: [4](#0-3) [5](#0-4) . This confirms the guard exists in the underlying pallet but is deliberately bypassed by `system-frontend` passing `None`, so the swap always executes at whatever spot price the pool offers at call time.

Because `T::Swap` resolves to the permissionless, publicly tradable `AssetConversion` pool for `(tip_asset, ether)`, and pool creation/liquidity in `pallet-asset-conversion` is not gated to privileged accounts, an attacker who controls the timing of their own `add_tip`/`register_token` call can bracket it with their own trades against the same pool (e.g., via `utility.batch_all` for atomicity) to move the spot price immediately before the tip swap and reverse it afterward, inflating the reported `ether_gained` for a fixed nominal `tip_amount`/`fee_amount`. This is a self-sandwich attack against an AMM used as an unguarded price source for cross-chain fee/reward accounting — a well-established DeFi vulnerability pattern (missing slippage bound doubling as a manipulable oracle).

## Impact Explanation
`ether_gained` is not merely internal bookkeeping — it is embedded in the `EthereumSystemCall::AddTip`/`RegisterToken` transact calls dispatched to BridgeHub/Ethereum, forming the basis for relayer reward and registration-fee accounting: [6](#0-5) . An attacker manipulating the pool price during the swap extracts real Ether from the pool's liquidity providers (since the burned/teleported Ether is genuinely destroyed from the pool and cannot be recovered by the attacker), while reporting a distorted, inflated fee/reward value on the Ethereum side relative to fair-market pricing. This is a legitimate accounting-integrity impact affecting LPs of the relevant `AssetConversion` pool and the correctness of cross-chain reward/fee data, though it is bounded by pool depth, LP fees on the bracketing trades, and requires the attacker to fund the price-moving legs.

## Likelihood Explanation
Both `add_tip` (any signed account, no admin gating) and `register_token` (gated only by asset ownership, not by economic privilege) are realistically reachable by an unprivileged user, and `pallet-asset-conversion` pools are permissionless and tradable by anyone. Atomic bracketing of trades is achievable via `utility.batch_all` in the same extrinsic, or same-block ordering. The main constraint on profitability is pool liquidity depth and AMM fees on the two extra bracketing trades, which limits the attack's economic attractiveness for well-liquidated pools but remains fully feasible for thin/attacker-seeded pools.

## Recommendation
Add an explicit `amount_out_min` parameter to `add_tip`/`register_token` (or compute one internally via `AssetConversionApi::quote_price_exact_tokens_for_tokens` with an acceptable tolerance) and pass it through to `T::Swap::swap_exact_tokens_for_tokens` in `swap_and_burn`, instead of hard-coding `None`.

## Proof of Concept
1. Attacker identifies/creates the `AssetConversion` pool for `(tip_asset, EthereumLocation)`.
2. In a single `utility.batch_all` transaction, the attacker:
   a. Swaps Ether into the pool via `pallet_asset_conversion::Pallet::swap_exact_tokens_for_tokens`, cheapening Ether relative to `tip_asset` in the pool reserves.
   b. Calls `SystemFrontend::add_tip(message_id, asset)` with `tip_asset`; since `swap_and_burn` passes `amount_out_min: None`, the swap executes at the manipulated price, yielding an inflated `ether_gained` that is burned and reported to BridgeHub/Ethereum.
   c. Reverses the initial trade to restore the pool price, recovering most of the capital from step (a) minus AMM fees.
3. Compare the `ether_gained` reported in the `MessageSent`/`SwapExecuted` events against the fair-market quote obtained via `quote_price_exact_tokens_for_tokens` immediately before the manipulation to demonstrate the discrepancy, and verify the pool's Ether reserve loss exceeds what a fair-price swap of `tip_amount` would produce.

### Citations

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L56-68)
```rust
/// Call indices for dispatchables within `snowbridge-pallet-system-v2`
#[derive(Encode, Decode, Debug, PartialEq, Clone, TypeInfo)]
pub enum EthereumSystemCall<T: frame_system::Config> {
	#[codec(index = 2)]
	RegisterToken {
		sender: Box<VersionedLocation>,
		asset_id: Box<VersionedLocation>,
		metadata: AssetMetadata,
		amount: u128,
	},
	#[codec(index = 3)]
	AddTip { sender: AccountIdOf<T>, message_id: MessageId, amount: u128 },
}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L225-252)
```rust
		pub fn register_token(
			origin: OriginFor<T>,
			asset_id: Box<VersionedLocation>,
			metadata: AssetMetadata,
			fee_asset: Asset,
		) -> DispatchResult {
			ensure!(!Self::export_operating_mode().is_halted(), Error::<T>::Halted);

			let asset_location: Location =
				(*asset_id).try_into().map_err(|_| Error::<T>::UnsupportedLocationVersion)?;
			let origin_location = T::RegisterTokenOrigin::ensure_origin(origin, &asset_location)?;

			let ether_gained = if origin_location.is_here() {
				// Root origin/location does not pay any fees/tip.
				0
			} else {
				Self::swap_fee_asset_and_burn(origin_location.clone(), fee_asset)?
			};

			let call = Self::build_register_token_call(
				origin_location.clone(),
				asset_location,
				metadata,
				ether_gained,
			)?;

			Self::send_transact_call(origin_location, call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L261-273)
```rust
		pub fn add_tip(origin: OriginFor<T>, message_id: MessageId, asset: Asset) -> DispatchResult
		where
			<T as frame_system::Config>::AccountId: Into<Location>,
		{
			let who = ensure_signed(origin)?;

			let ether_gained = Self::swap_fee_asset_and_burn(who.clone().into(), asset)?;

			// Send the tip details to BH to be allocated to the reward in the Inbound/Outbound
			// pallet
			let call = Self::build_add_tip_call(who.clone(), message_id.clone(), ether_gained);
			Self::send_transact_call(who.into(), call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L301-308)
```rust
			let ether_gained = T::Swap::swap_exact_tokens_for_tokens(
				who.clone(),
				swap_path,
				tip_amount,
				None, // No minimum amount required
				who,
				true,
			)?;
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L988-1002)
```rust
			ensure!(amount_in > Zero::zero(), Error::<T>::ZeroAmount);
			if let Some(amount_out_min) = amount_out_min {
				ensure!(amount_out_min > Zero::zero(), Error::<T>::ZeroAmount);
			}

			Self::validate_swap_path(&path)?;
			let path = Self::balance_path_from_amount_in(amount_in, path)?;

			let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
			if let Some(amount_out_min) = amount_out_min {
				ensure!(
					amount_out >= amount_out_min,
					Error::<T>::ProvidedMinimumNotSufficientForSwap
				);
			}
```

**File:** substrate/frame/asset-conversion/src/tests.rs (L1565-1613)
```rust
#[test]
fn swap_should_not_work_if_too_much_slippage() {
	new_test_ext().execute_with(|| {
		let user = 1;
		let token_1 = NativeOrWithId::Native;
		let token_2 = NativeOrWithId::WithId(2);

		create_tokens(user, vec![token_2.clone()]);
		assert_ok!(AssetConversion::create_pool(
			RuntimeOrigin::signed(user),
			Box::new(token_1.clone()),
			Box::new(token_2.clone())
		));

		assert_ok!(Balances::force_set_balance(
			RuntimeOrigin::root(),
			user,
			10000 + get_native_ed()
		));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(user), 2, user, 1000));

		let liquidity1 = 10000;
		let liquidity2 = 200;

		assert_ok!(AssetConversion::add_liquidity(
			RuntimeOrigin::signed(user),
			Box::new(token_1.clone()),
			Box::new(token_2.clone()),
			liquidity1,
			liquidity2,
			1,
			1,
			user,
		));

		let exchange_amount = 100;

		assert_noop!(
			AssetConversion::swap_exact_tokens_for_tokens(
				RuntimeOrigin::signed(user),
				bvec![token_2.clone(), token_1.clone()],
				exchange_amount, // amount_in
				4000,            // amount_out_min
				user,
				false,
			),
			Error::<Test>::ProvidedMinimumNotSufficientForSwap
		);
	});
```
