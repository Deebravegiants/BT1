### Title
`burn_from`/`mint_into` in `pallet-revive`'s `fungibles::Mutate` impl ignore `Precision`, causing `BestEffort` withdrawals to fail instead of partially succeeding - ([File: substrate/frame/revive/src/impl_fungibles.rs])

### Summary
`Pallet<T>`'s override of `fungibles::Mutate::burn_from` and `mint_into` (lines 162-241) discards the `Preservation`, `Precision`, and `Fortitude` parameters entirely, always issuing an `IERC20::transferCall` for the *exact* `amount` requested. This breaks the documented contract of `Precision::BestEffort`, which callers such as `xcm_builder::FungiblesAdapter` rely on to allow partial burns instead of failing outright.

### Finding Description
The default trait implementation of `burn_from` in `substrate/frame/support/src/traits/tokens/fungibles/regular.rs` (lines 282-303) computes `actual = reducible_balance(...).min(amount)`, and only errors with `TokenError::FundsUnavailable` if `actual != amount && precision != BestEffort`. This is the documented semantic: with `BestEffort`, a caller with insufficient balance should get a partial burn (`Ok(actual < amount)`) rather than an error.

`pallet-revive`'s override at [1](#0-0)  completely bypasses this logic: it takes `_: Preservation, _: Precision, _: Fortitude` and never reads them. It always constructs an ERC20 `transferCall` for the full requested `amount`: [2](#0-1) 

If the underlying ERC20 contract's balance is less than `amount`, the `transfer` will revert or return `false` (per standard ERC20 semantics), and the function returns `Err("Contract reverted")` or `Err("Contract transfer failed")` at lines 189/197 — regardless of whether the caller specified `Precision::BestEffort`. There is no fallback to clamp `amount` to the actual balance and retry with a smaller transfer.

Symmetrically, `mint_into` at lines 205-241 has no `Precision` parameter at all in this override (mismatching the trait's default single-`Precision::Exact` semantics used via `increase_balance`), but since this override replaces the whole `mint_into` provided method rather than `increase_balance`, it cannot honor differing precision behavior expected by higher-level trait consumers that assume `mint_into`'s failure/success semantics come from `increase_balance`+`Exact`. This is a secondary/lesser issue since `mint_into` itself takes no `Precision` argument in the trait — the primary bug is `burn_from`.

The code comment explicitly states this override exists to support `xcm_builder::FungiblesAdapter` (lines 158-160), which is a real, reachable, unprivileged path: an XCM message causing an asset withdrawal (e.g. `WithdrawAsset`/`TransferAsset` executed via `FungiblesAdapter::withdraw_asset`) can invoke `Mutate::burn_from` with `Precision::BestEffort` in some adapter configurations, expecting a partial burn instead of a hard failure.

### Impact Explanation
For a caller (including XCM executor logic via `FungiblesAdapter`, or any pallet using `fungibles::Mutate<T>` against a `pallet-revive` ERC20 asset) that invokes `burn_from(asset, who, amount, _, Precision::BestEffort, _)` expecting `Ok(actual_burned)` when the account balance is less than `amount`, this implementation instead returns `Err`. This is a denial-of-service / contract-violation on a documented trait guarantee: an operation that should succeed with a lesser amount fails entirely. Conversely, there is no scenario here where more than the actual (available or requested) balance is burned — the underlying ERC20 `transfer` call itself cannot move more than the sender's balance, so no fund duplication/theft is possible; the concrete impact is limited to unexpected `Err` on legitimate BestEffort semantics (denial of a partial burn/withdrawal), not fund loss or over-burning.

### Likelihood Explanation
This is deterministically reproducible whenever: (1) an asset is a `pallet-revive` ERC20 (`H160` asset id) integrated with `fungibles::Mutate`, (2) a caller/consumer (e.g. `FungiblesAdapter` configured to use this pallet as the `fungibles::Mutate` implementation for XCM reserve/teleport asset handling) calls `burn_from` with `Precision::BestEffort`, and (3) the target account's ERC20 balance is less than the requested `amount`. No special privileges are needed to trigger it; any account with an ERC20 balance less than the withdrawal amount can present this via an XCM asset-withdrawal path or a direct call to `fungibles::Mutate::burn_from`.

### Recommendation
In `Pallet<T>::burn_from`, honor `Precision`: before issuing the `transferCall`, query the current ERC20 balance via `Inspect::balance`, and if `precision == Precision::BestEffort`, clamp `amount` to `min(amount, balance)` before constructing `IERC20::transferCall`. If `precision == Precision::Exact`, keep current behavior (fail if balance insufficient). Also consider honoring `Preservation`/`Fortitude` if the ERC20 exposes any minimum-balance semantics, or explicitly document that these are no-ops for ERC20 assets (which have no minimum-balance concept per `minimum_balance` returning `1`).

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/impl_fungibles.rs` test module:
```rust
#[test]
fn burn_from_best_effort_should_partially_succeed() {
    ExtBuilder::default().existential_deposit(1).build().execute_with(|| {
        let _ = <<Test as Config>::Currency as fungible::Mutate<_>>::set_balance(&ALICE, 1_000_000);
        let code = compile_module_with_type("MyToken", FixtureType::Resolc).unwrap().0.to_vec();
        let amount = 1000;
        // Mint ALICE only `amount` (not amount * 2)
        let constructor_data = sol_data::Uint::<256>::abi_encode(&(EU256::from(amount)));
        let Contract { addr, .. } = BareInstantiateBuilder::<Test>::bare_instantiate(
            RuntimeOrigin::signed(ALICE),
            Code::Upload(code),
        )
        .data(constructor_data)
        .build_and_unwrap_contract();

        assert_eq!(<Contracts as fungibles::Inspect<_>>::balance(addr, &ALICE), amount);

        // Attempt to burn MORE than the balance, with BestEffort precision.
        let requested = amount * 2;
        let result = <Contracts as fungibles::Mutate<_>>::burn_from(
            addr,
            &ALICE,
            requested,
            Preservation::Expendable,
            Precision::BestEffort,
            Fortitude::Polite,
        );

        // Documented BestEffort contract: should return Ok(<= amount available), NOT Err.
        assert!(result.is_ok(), "BestEffort burn_from unexpectedly returned Err: {:?}", result);
        let burned = result.unwrap();
        assert!(burned <= amount, "burned more than available balance");
        assert_eq!(<Contracts as fungibles::Inspect<_>>::balance(addr, &ALICE), amount - burned);
    });
}
```
Expected current behavior (bug confirmed): the assertion `result.is_ok()` fails because the underlying `IERC20::transferCall` reverts/returns `false` for `requested > balance`, causing `Err("Contract reverted")` or `Err("Contract transfer failed")` instead of `Ok(amount)` as required by `Precision::BestEffort`.

### Citations

**File:** substrate/frame/revive/src/impl_fungibles.rs (L162-169)
```rust
	fn burn_from(
		asset_id: Self::AssetId,
		who: &T::AccountId,
		amount: Self::Balance,
		_: Preservation,
		_: Precision,
		_: Fortitude,
	) -> Result<Self::Balance, DispatchError> {
```

**File:** substrate/frame/revive/src/impl_fungibles.rs (L170-203)
```rust
		let checking_account_eth = T::AddressMapper::to_address(&Self::checking_account());
		let checking_address = Address::from(Into::<[u8; 20]>::into(checking_account_eth));
		let data =
			IERC20::transferCall { to: checking_address, value: EU256::from(amount) }.abi_encode();
		let ContractResult { result, weight_consumed, .. } = Self::bare_call(
			OriginFor::<T>::signed(who.clone()),
			asset_id,
			U256::zero(),
			TransactionLimits::WeightAndDeposit {
				weight_limit: WEIGHT_LIMIT,
				deposit_limit:
					<<T as pallet::Config>::Currency as fungible::Inspect<_>>::total_issuance(),
			},
			data,
			&ExecConfig::new_substrate_tx(),
		);
		log::trace!(target: "whatiwant", "{weight_consumed}");
		if let Ok(return_value) = result {
			if return_value.did_revert() {
				Err("Contract reverted".into())
			} else {
				let is_success =
					bool::abi_decode_validate(&return_value.data).expect("Failed to ABI decode");
				if is_success {
					let balance = <Self as fungibles::Inspect<_>>::balance(asset_id, who);
					Ok(balance)
				} else {
					Err("Contract transfer failed".into())
				}
			}
		} else {
			Err("Contract out of gas".into())
		}
	}
```
