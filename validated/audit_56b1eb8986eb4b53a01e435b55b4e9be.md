Based on my research, I found a valid analog of the same vulnerability class (accounting based on a *requested* transfer amount instead of the *actual* balance delta) in the `ERC20Transactor` used for XCM asset transfers on Asset Hub, which integrates arbitrary user-deployed ERC20 contracts via `pallet-revive`.

### Title
Inconsistent balance accounting in `ERC20Transactor` XCM asset transfers allows fee-on-transfer/deflationary ERC20 tokens to create unbacked XCM holding credit - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` moves ERC20 tokens into XCM's asset holding by calling the token's `transfer()` function and, if the call returns `true`, unconditionally credits the XCM holding with the *requested* `amount` — the same value passed to `transfer()` — rather than the actual balance delta observed at the checking account. This mirrors exactly the root cause described in the external Morpheus report: recording the amount an operation was *called with* instead of the amount that *actually moved*.

### Finding Description
`Matcher::matches_fungibles(what)` extracts `(asset_id, amount)` from the XCM asset descriptor, and `withdraw_asset_with_surplus` transfers `amount` from the user to `TransfersCheckingAccount` via a raw ERC20 `transfer()` call [1](#0-0) . It only inspects the boolean return value of `transfer()`; on `true` it creates `AssetsInHolding::new_from_fungible_credit(what.id.clone(), Box::new(Erc20Credit(amount)))` using the originally requested `amount`, with no verification that the checking account's balance actually increased by that much [2](#0-1) . The symmetric `deposit_asset_with_surplus` similarly just calls `transfer()` for the credited `amount` and trusts the boolean return, again without checking the actual balance change at the recipient [3](#0-2) .

Unlike the internal FRAME `pallet-assets`/`pallet-balances` ledgers — where `decrease_balance`/`increase_balance` compute and return the *actual* amount debited/credited from internal storage [4](#0-3)  — the ERC20 asset class here relies entirely on an external, arbitrary, user-deployed contract's self-reported success flag, with no balance-before/balance-after check analogous to `DepositPool::_stake()` in the Morpheus report.

`ERC20Transactor` is wired into Asset Hub Westend's live `AssetTransactors` XCM configuration [5](#0-4) , and the existing test suite confirms that *any* signed account can permissionlessly instantiate an arbitrary contract via `pallet-revive` and immediately use it as an ERC20 asset in XCM `withdraw_asset`/`deposit_asset` instructions [6](#0-5) . There is no allowlist of trusted ERC20 contracts — the matcher only requires the contract to expose an ERC20-shaped interface — meaning an attacker fully controls the token's `transfer()` semantics (e.g., implementing a fee-on-transfer / deflationary token that returns `true` while moving less than `amount` to the checking account).

### Impact Explanation
An attacker who deploys a malicious ERC20 contract that returns `true` from `transfer()` while moving less than the requested `amount` (fee-on-transfer, deflationary burn, or rounding-based rebasing logic) causes `withdraw_asset_with_surplus` to mint phantom XCM holding balance not backed by real tokens sitting in `TransfersCheckingAccount`. This phantom balance can then be deposited to a beneficiary via `deposit_asset_with_surplus`, which will attempt to `transfer()` the full unbacked `amount` out of the checking account. Since the checking account never received that much, either:
- The deposit-side `transfer()` fails/reverts if the malicious contract enforces its own accounting, causing legitimate XCM programs and unrelated future transfers of the same malicious asset to fail (denial of service for that asset class), or
- If the malicious contract's internal accounting doesn't independently verify checking-account balance (e.g., it just tracks total supply loosely), the attacker can extract more value than they deposited, draining the checking account's real balance of that token relative to what other participants believe is credited — a direct accounting/value-extraction bug for an unprivileged, permissionless actor.

This differs from the FRAME-native pallets (`pallet-balances`, `pallet-assets`), which are immune to this class of bug because they use internal ledger `try_mutate` operations that always report the actual delta.

### Likelihood Explanation
High for an attacker willing to deploy a custom contract: `pallet-revive` contract deployment and XCM `withdraw_asset`/`transact` execution are both permissionless operations available to any signed account on Asset Hub, as demonstrated directly by the existing `withdraw_and_deposit_erc20s` test which deploys an arbitrary compiled contract and immediately exercises it through `ERC20Transactor` [7](#0-6) . No special privilege or trusted role is required — only writing a Solidity/ink! contract with non-standard transfer accounting.

### Recommendation
In `withdraw_asset_with_surplus` and `deposit_asset_with_surplus`, read the checking-account's/beneficiary's ERC20 `balanceOf` before and after the `transfer()` call and use the observed delta (not the requested `amount`) both when constructing `Erc20Credit` and when validating success, mirroring the balance-before/balance-after pattern already used elsewhere for non-standard tokens. Reverting or reducing the credited amount to the actual delta closes the discrepancy window entirely.

### Proof of Concept
Conceptually reproducible by extending the existing `withdraw_and_deposit_erc20s` test [8](#0-7) : replace `MyToken` with a fee-on-transfer variant whose `transfer()` implementation deducts e.g. 1% before crediting the recipient but still returns `true`. Executing the same `withdraw_asset`/`deposit_asset` XCM program would show `Erc20Credit(amount)` reflecting the full requested `amount` while `IERC20::balanceOf(checking_account)` only increased by `amount * 0.99`, then a subsequent `deposit_asset_with_surplus` for the full recorded `amount` would fail or, in a looser-accounting contract, drain more from the checking account than it actually holds.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L159-181)
```rust
		let (asset_id, amount) = Matcher::matches_fungibles(what)?;
		let who = AccountIdConverter::convert_location(who)
			.ok_or(MatchError::AccountIdConversionFailed)?;
		// We need to map the 32 byte checking account to a 20 byte account.
		let checking_account_eth = T::AddressMapper::to_address(&TransfersCheckingAccount::get());
		let checking_address = Address::from(Into::<[u8; 20]>::into(checking_account_eth));
		let weight_limit = WeightLimit::get();
		// To withdraw, we actually transfer to the checking account.
		// We do this using the solidity ERC20 interface.
		let data =
			IERC20::transferCall { to: checking_address, value: EU256::from(amount) }.abi_encode();
		let ContractResult { result, weight_consumed, storage_deposit, .. } =
			pallet_revive::Pallet::<T>::bare_call(
				OriginFor::<T>::signed(who.clone()),
				asset_id,
				U256::zero(),
				TransactionLimits::WeightAndDeposit {
					weight_limit,
					deposit_limit: StorageDepositLimit::get(),
				},
				data,
				&ExecConfig::new_substrate_tx(),
			);
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L185-208)
```rust
		if let Ok(return_value) = result {
			tracing::trace!(target: "xcm::transactor::erc20::withdraw", ?return_value, "Return value by withdraw_asset");
			if return_value.did_revert() {
				tracing::debug!(target: "xcm::transactor::erc20::withdraw", "ERC20 contract reverted");
				Err(XcmError::FailedToTransactAsset("ERC20 contract reverted"))
			} else {
				let is_success = IERC20::transferCall::abi_decode_returns_validate(&return_value.data).map_err(|error| {
					tracing::debug!(target: "xcm::transactor::erc20::withdraw", ?error, "ERC20 contract result couldn't decode");
					XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")
				})?;
				if is_success {
					tracing::trace!(target: "xcm::transactor::erc20::withdraw", "ERC20 contract was successful");
					Ok((
						AssetsInHolding::new_from_fungible_credit(
							what.id.clone(),
							Box::new(Erc20Credit(amount)),
						),
						surplus,
					))
				} else {
					tracing::debug!(target: "xcm::transactor::erc20::withdraw", "contract transfer failed");
					Err(XcmError::FailedToTransactAsset("ERC20 contract transfer failed"))
				}
			}
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L253-298)
```rust
		let data = IERC20::transferCall { to: address, value: EU256::from(amount) }.abi_encode();
		let weight_limit = WeightLimit::get();
		let ContractResult { result, weight_consumed, storage_deposit, .. } =
			pallet_revive::Pallet::<T>::bare_call(
				OriginFor::<T>::signed(TransfersCheckingAccount::get()),
				asset_contract_id,
				U256::zero(),
				TransactionLimits::WeightAndDeposit {
					weight_limit,
					deposit_limit: StorageDepositLimit::get(),
				},
				data,
				&ExecConfig::new_substrate_tx(),
			);
		// We need to return this surplus for the executor to allow refunding it.
		let surplus = weight_limit.saturating_sub(weight_consumed);
		tracing::trace!(target: "xcm::transactor::erc20::deposit", ?weight_consumed, ?surplus, ?storage_deposit);
		if let Ok(return_value) = result {
			tracing::trace!(target: "xcm::transactor::erc20::deposit", ?return_value, "Return value");
			if return_value.did_revert() {
				tracing::debug!(target: "xcm::transactor::erc20::deposit", "Contract reverted");
				Err((what, XcmError::FailedToTransactAsset("ERC20 contract reverted")))
			} else {
				match IERC20::transferCall::abi_decode_returns_validate(&return_value.data) {
					Ok(true) => {
						tracing::trace!(target: "xcm::transactor::erc20::deposit", "ERC20 contract was successful");
						Ok(surplus)
					},
					Ok(false) => {
						tracing::debug!(target: "xcm::transactor::erc20::deposit", "contract transfer failed");
						Err((
							what,
							XcmError::FailedToTransactAsset("ERC20 contract transfer failed"),
						))
					},
					Err(error) => {
						tracing::debug!(target: "xcm::transactor::erc20::deposit", ?error, "ERC20 contract result couldn't decode");
						Err((
							what,
							XcmError::FailedToTransactAsset(
								"ERC20 contract result couldn't decode",
							),
						))
					},
				}
			}
```

**File:** substrate/frame/assets/src/functions.rs (L570-620)
```rust
	pub(super) fn decrease_balance(
		id: T::AssetId,
		target: &T::AccountId,
		amount: T::Balance,
		f: DebitFlags,
		check: impl FnOnce(
			T::Balance,
			&mut AssetDetails<T::Balance, T::AccountId, DepositBalanceOf<T, I>>,
		) -> DispatchResult,
	) -> Result<T::Balance, DispatchError> {
		if amount.is_zero() {
			return Ok(amount);
		}

		let details = Asset::<T, I>::get(&id).ok_or(Error::<T, I>::Unknown)?;
		ensure!(details.status == AssetStatus::Live, Error::<T, I>::AssetNotLive);

		let actual = Self::prep_debit(id.clone(), target, amount, f)?;
		let mut target_died: Option<DeadConsequence> = None;

		Asset::<T, I>::try_mutate(&id, |maybe_details| -> DispatchResult {
			let details = maybe_details.as_mut().ok_or(Error::<T, I>::Unknown)?;
			check(actual, details)?;

			Account::<T, I>::try_mutate(&id, target, |maybe_account| -> DispatchResult {
				let mut account = maybe_account.take().ok_or(Error::<T, I>::NoAccount)?;
				debug_assert!(account.balance >= actual, "checked in prep; qed");

				// Make the debit.
				account.balance = account.balance.saturating_sub(actual);
				if account.balance < details.min_balance {
					debug_assert!(account.balance.is_zero(), "checked in prep; qed");
					Self::ensure_account_can_die(id.clone(), target)?;
					target_died = Some(Self::dead_account(target, details, &account.reason, false));
					if let Some(Remove) = target_died {
						return Ok(());
					}
				};
				*maybe_account = Some(account);
				Ok(())
			})?;

			Ok(())
		})?;

		// Execute hook outside of `mutate`.
		if let Some(Remove) = target_died {
			T::Freezer::died(id.clone(), target);
			T::Holder::died(id, target);
		}
		Ok(actual)
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L221-246)
```rust
/// Transactor for ERC20 tokens.
pub type ERC20Transactor = assets_common::ERC20Transactor<
	// We need this for accessing pallet-revive.
	Runtime,
	// The matcher for smart contracts.
	assets_common::ERC20Matcher,
	// How to convert from a location to an account id.
	LocationToAccountId,
	// The maximum gas that can be used by a standard ERC20 transfer.
	ERC20TransferGasLimit,
	// The maximum storage deposit that can be used by a standard ERC20 transfer.
	ERC20TransferStorageDepositLimit,
	// We're generic over this so we can't escape specifying it.
	AccountId,
	// Checking account for ERC20 transfers.
	ERC20TransfersCheckingAccount,
>;

/// Means for transacting assets on this chain.
pub type AssetTransactors = (
	FungibleTransactor,
	FungiblesTransactor,
	ForeignFungiblesTransactor,
	UniquesTransactor,
	ERC20Transactor,
);
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs (L1864-1929)
```rust
#[test]
fn withdraw_and_deposit_erc20s() {
	let sender: AccountId = ALICE.into();
	let beneficiary: AccountId = BOB.into();
	let revive_account = pallet_revive::Pallet::<Runtime>::account_id();
	let checking_account =
		asset_hub_westend_runtime::xcm_config::ERC20TransfersCheckingAccount::get();
	let initial_wnd_amount = 100_000_000_000_000_000u128;
	sp_tracing::init_for_tests();

	ExtBuilder::<Runtime>::default().build().execute_with(|| {
		// Bring the revive account to life.
		assert_ok!(Balances::mint_into(&revive_account, initial_wnd_amount));
		// Fund all accounts involved.
		assert_ok!(Balances::mint_into(&sender, initial_wnd_amount));
		assert_ok!(Balances::mint_into(&beneficiary, initial_wnd_amount));
		assert_ok!(Balances::mint_into(&checking_account, initial_wnd_amount));

		let code = compile_module_with_type("MyToken", FixtureType::Resolc)
			.expect("compile ERC20")
			.0;

		let initial_amount_u256 = U256::from(1_000_000_000_000u128);
		let constructor_data = sol_data::Uint::<256>::abi_encode(&initial_amount_u256);
		let Contract { addr: erc20_address, .. } = bare_instantiate(&sender, code)
			.transaction_limits(TransactionLimits::WeightAndDeposit {
				weight_limit: Weight::from_parts(500_000_000_000, 10 * 1024 * 1024),
				deposit_limit: Balance::MAX,
			})
			.data(constructor_data)
			.build_and_unwrap_contract();

		let sender_balance_before = <Balances as fungible::Inspect<_>>::balance(&sender);

		let erc20_transfer_amount = 100u128;
		let wnd_amount_for_fees = 10_000_000_000_000u128;
		// Actual XCM to execute locally.
		let message = Xcm::<RuntimeCall>::builder()
			.withdraw_asset((Parent, wnd_amount_for_fees))
			.pay_fees((Parent, wnd_amount_for_fees))
			.withdraw_asset((
				AccountKey20 { key: erc20_address.into(), network: None },
				erc20_transfer_amount,
			))
			.deposit_asset(AllCounted(1), beneficiary.clone())
			.refund_surplus()
			.deposit_asset(AllCounted(1), sender.clone())
			.build();
		assert_ok!(PolkadotXcm::execute(
			RuntimeOrigin::signed(sender.clone()),
			Box::new(VersionedXcm::V5(message)),
			Weight::from_parts(600_000_000_000, 15 * 1024 * 1024),
		));

		// Revive is not taking any fees.
		let sender_balance_after = <Balances as fungible::Inspect<_>>::balance(&sender);
		// Balance after is larger than the difference between balance before and transferred
		// amount because of the refund.
		assert!(sender_balance_after > sender_balance_before - wnd_amount_for_fees);

		// Beneficiary receives the ERC20.
		let beneficiary_amount =
			<Revive as fungibles::Inspect<_>>::balance(erc20_address, &beneficiary);
		assert_eq!(beneficiary_amount, erc20_transfer_amount);
	});
}
```
