### Title
Unconditional zero-amount ERC20 `transfer()` call in `pallet_revive`'s `fungibles::Mutate` implementation can revert on tokens that disallow zero-value transfers - (`substrate/frame/revive/src/impl_fungibles.rs`)

### Summary
`pallet_revive` implements the FRAME `fungibles::Mutate` trait (`burn_from` / `mint_into`) by making a bare contract call into the underlying ERC20 contract's `transfer()` function. Neither function short-circuits when `amount == 0`; both unconditionally construct an ABI-encoded `transferCall` and execute it via `Self::bare_call`. This mirrors the Notional pattern where a deposit/redeem is forwarded to an external money-market contract without checking that the amount is non-zero first.

### Finding Description
`burn_from` and `mint_into` are the two methods the pallet overrides "to be used in `xcm_builder::FungiblesAdapter`" per the code comment: [1](#0-0) 

Both implementations build a `IERC20::transferCall{ to, value: EU256::from(amount) }` and dispatch it with `Self::bare_call(...)` regardless of whether `amount` is zero: [2](#0-1) 

If the target ERC20 contract is a "weird" token that reverts on zero-value transfers (a well-documented ERC20 behavior class, exactly the same category cited in the Notional report — `d-xo/weird-erc20#revert-on-zero-value-transfers`), then any caller of `fungibles::Mutate::burn_from`/`mint_into` with `amount == 0` will see the call fail and propagate an error ("Contract reverted"), even though semantically burning/minting zero should be a no-op.

This differs from the "safe" pattern used elsewhere in the same codebase — e.g. `pallet_balances`' `Currency::burn`/`issue` explicitly no-op on `amount.is_zero()`: [3](#0-2) 

and `pallet_revive`'s own native balance `transfer` function explicitly treats zero value as a no-op: [4](#0-3) 

The `impl_fungibles.rs` ERC20-adapter path breaks this same convention that the rest of the codebase (including the custom `pallet-psm`, whose `redeem` extrinsic explicitly guards fee/burn/transfer calls with `if !x.is_zero()`) follows: [5](#0-4) 

### Impact Explanation
Because this `fungibles::Mutate` implementation is documented to back `xcm_builder::FungiblesAdapter`, any XCM instruction (e.g. `WithdrawAsset`/`DepositAsset` handling, or fee/asset transfers computed to a zero remainder after prior processing) that ends up calling `burn_from`/`mint_into` with a zero amount against an ERC20-asset registered through `pallet_revive` will cause the surrounding dispatch/XCM execution to fail unexpectedly. This is a denial-of-service against otherwise-valid operations rather than a fund-loss bug, but it can make specific asset transfers/rebalances permanently un-executable when interacting with contracts that reject zero-value transfers, exactly the "stuck with a suboptimal state, can't move funds" impact described in the source report.

### Likelihood Explanation
Reaching a zero-value `burn_from`/`mint_into` call is plausible without any privileged role: it only requires (a) an ERC20 asset registered through `pallet_revive`'s fungibles bridge whose contract reverts on zero transfers, and (b) any code path (XCM instruction processing, multi-asset batch operations, or any other `fungibles::Mutate` consumer) that can compute an amount of zero for one of the assets in a batch — e.g., a partial fee/asset split that legitimately rounds to zero for one leg. This does not require a mocked/simulated environment since the transfer call is a real bare contract execution.

### Recommendation
Add an early-return no-op for `amount.is_zero()` at the top of both `burn_from` and `mint_into` in `substrate/frame/revive/src/impl_fungibles.rs`, mirroring the pattern already used in `impl_currency.rs`'s `burn`/`issue` and `exec.rs`'s `transfer`, so that zero-amount operations never reach the underlying ERC20 contract call.

### Proof of Concept
1. Deploy/register an ERC20 contract via `pallet_revive` whose `transfer()` implementation reverts when `value == 0` (a legal, documented ERC20 behavior).
2. Invoke any code path that calls `<Pallet<T> as fungibles::Mutate<_>>::mint_into(asset_id, who, 0)` or `burn_from(asset_id, who, 0, ...)` — for example, through `xcm_builder::FungiblesAdapter` processing an XCM message where the computed transfer amount for this asset is zero.
3. Observe that `Self::bare_call` executes `transferCall{ value: 0 }` against the contract, the contract reverts, and `mint_into`/`burn_from` returns `Err("Contract reverted")`, causing the enclosing extrinsic/XCM execution to fail instead of treating the zero-amount operation as a no-op.

### Citations

**File:** substrate/frame/revive/src/impl_fungibles.rs (L158-203)
```rust
// We implement `fungibles::Mutate` to override `burn_from` and `mint_to`.
//
// These functions are used in [`xcm_builder::FungiblesAdapter`].
impl<T: Config> fungibles::Mutate<<T as frame_system::Config>::AccountId> for Pallet<T> {
	fn burn_from(
		asset_id: Self::AssetId,
		who: &T::AccountId,
		amount: Self::Balance,
		_: Preservation,
		_: Precision,
		_: Fortitude,
	) -> Result<Self::Balance, DispatchError> {
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

**File:** substrate/frame/revive/src/impl_fungibles.rs (L205-241)
```rust
	fn mint_into(
		asset_id: Self::AssetId,
		who: &T::AccountId,
		amount: Self::Balance,
	) -> Result<Self::Balance, DispatchError> {
		let eth_address = T::AddressMapper::to_address(who);
		let address = Address::from(Into::<[u8; 20]>::into(eth_address));
		let data = IERC20::transferCall { to: address, value: EU256::from(amount) }.abi_encode();
		let ContractResult { result, .. } = Self::bare_call(
			OriginFor::<T>::signed(Self::checking_account()),
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

**File:** substrate/frame/balances/src/impl_currency.rs (L336-351)
```rust
	// Burn funds from the total issuance, returning a positive imbalance for the amount burned.
	// Is a no-op if amount to be burned is zero.
	fn burn(mut amount: Self::Balance) -> Self::PositiveImbalance {
		if amount.is_zero() {
			return PositiveImbalance::zero();
		}
		<TotalIssuance<T, I>>::mutate(|issued| {
			*issued = issued.checked_sub(&amount).unwrap_or_else(|| {
				amount = *issued;
				Zero::zero()
			});
		});

		Pallet::<T, I>::deposit_event(Event::<T, I>::Rescinded { amount });
		PositiveImbalance::new(amount)
	}
```

**File:** substrate/frame/revive/src/exec.rs (L1711-1736)
```rust
	/// Transfer some funds from `from` to `to`.
	///
	/// This is a no-op for zero `value`, avoiding events to be emitted for zero balance transfers.
	///
	/// If the destination account does not exist, it is pulled into existence by transferring the
	/// ED from `origin` to the new account. The total amount transferred to `to` will be ED +
	/// `value`. This makes the ED fully transparent for contracts.
	/// The ED transfer is executed atomically with the actual transfer, avoiding the possibility of
	/// the ED transfer succeeding but the actual transfer failing. In other words, if the `to` does
	/// not exist, the transfer does fail and nothing will be sent to `to` if either `origin` can
	/// not provide the ED or transferring `value` from `from` to `to` fails.
	/// Note: This will also fail if `origin` is root.
	fn transfer<S: State>(
		origin: &Origin<T>,
		from: &T::AccountId,
		to: &T::AccountId,
		value: U256,
		preservation: Preservation,
		meter: &mut ResourceMeter<T, S>,
		exec_config: &ExecConfig<T>,
	) -> DispatchResult {
		let value = BalanceWithDust::<BalanceOf<T>>::from_value::<T>(value)
			.map_err(|_| Error::<T>::BalanceConversionFailed)?;
		if value.is_zero() {
			return Ok(());
		}
```

**File:** substrate/frame/psm/src/lib.rs (L857-887)
```rust
			if !fee.is_zero() {
				T::Fungibles::transfer(
					internal_asset.clone(),
					&who,
					&info.fee_destination,
					fee,
					Preservation::Expendable,
				)?;
			}

			if !effective_internal_net.is_zero() {
				T::Fungibles::burn_from(
					internal_asset.clone(),
					&who,
					effective_internal_net,
					Preservation::Expendable,
					Precision::Exact,
					Fortitude::Polite,
				)?;
			}

			let psm_account = Self::psm_account(&internal_asset);
			if !external_out.is_zero() {
				T::Fungibles::transfer(
					external_asset.clone(),
					&psm_account,
					&who,
					external_out,
					Preservation::Expendable,
				)?;
			}
```
