This confirms the vulnerability is real and the open question in the report is resolved: `ERC20Matcher` (`cumulus/parachains/runtimes/assets/common/src/lib.rs` L159-160) is defined as `MatchedConvertedConcreteId<H160, u128, IsLocalAccountKey20, AccountKey20ToH160, TryConvertInto>`, matching any location of the form `(0, [AccountKey20{..}])` via `IsLocalAccountKey20` (L134-139) and `AccountKey20ToH160` (L143-155) — there is no allowlist/registry of vetted contracts. Any address a user provides is accepted, confirmed by `asset-hub-westend/src/xcm_config.rs` wiring `ERC20Transactor` with `assets_common::ERC20Matcher` directly (L221-237).

Audit Report

## Title
Fee-on-transfer / non-standard ERC20 tokens cause accounting mismatch in `ERC20Transactor` - (File: cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs)

## Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` trust the boolean return value of an ERC20 `transfer` call as proof that the exact requested `amount` moved, crediting/debiting the XCM holding register with that unadjusted `amount` without ever measuring the checking account's actual balance delta. Because `ERC20Matcher` accepts any contract address supplied via an `AccountKey20` junction with no allowlist, any unprivileged user can deploy a fee-on-transfer/rebasing ERC20 and immediately exercise this path through `PolkadotXcm::execute`, causing the shared `TransfersCheckingAccount`'s real token balance to silently diverge from what the XCM executor's holding register believes was deposited/withdrawn.

## Finding Description
In `withdraw_asset_with_surplus` (`erc20_transactor.rs` L166-207), the transactor calls `IERC20::transfer(checking_account, amount)` from the user's account and, upon decoding a `true` boolean return, unconditionally credits `AssetsInHolding` with the full requested `amount` via `Erc20Credit(amount)` — no pre/post balance check on the checking account is performed.

Symmetrically, `deposit_asset_with_surplus` (L251-298) instructs the checking account to `transfer(beneficiary, amount)` for the full holding amount and, on a `true` return, simply returns `Ok(surplus)` without verifying the beneficiary actually received `amount`.

The `Matcher` generic (`ERC20Matcher = MatchedConvertedConcreteId<H160, u128, IsLocalAccountKey20, AccountKey20ToH160, TryConvertInto>`, `common/src/lib.rs` L159-160) matches any location shaped `(0, [AccountKey20{..}])` (`IsLocalAccountKey20`, L134-139) and converts the raw key directly to an `H160` contract address (`AccountKey20ToH160`, L143-155) with no registry/allowlist check. This is wired directly into the runtime's `ERC20Transactor` (`asset-hub-westend/src/xcm_config.rs` L221-237), confirming no restriction exists at the runtime-config level — the previously "unresolved" question in the report is answered: arbitrary, attacker-deployable ERC20 contracts can be routed through this transactor.

The existing test `smart_contract_does_not_return_bool_fails` only guards against contracts that fail to return a proper boolean (causing a decode error and safe XCM failure); it does not address a contract that returns `true` but under-delivers tokens due to a fee, which is exactly the accounting-mismatch class described.

## Impact Explanation
Since `TransfersCheckingAccount` is a single shared pool used across all users' withdraw/deposit operations for a given ERC20, a fee-on-transfer token creates a real, persistent shortfall between the checking account's actual on-chain token balance and the cumulative amount the XCM executor's holding logic has credited/debited for that asset. This can starve later legitimate `deposit_asset` operations for the same token (denial of funds to other users) or create an asset-specific insolvency in the checking account. This is a genuine accounting bug in the transactor's fund-custody logic, not a hypothetical concern, since the transferred amount is never reconciled against actual balance changes.

## Likelihood Explanation
Likelihood is high and does not depend on privileged access: `ERC20Matcher` imposes no allowlist, so any unprivileged user can deploy a fee-on-transfer ERC20 contract via `pallet-revive` and immediately submit an XCM message (e.g., via `PolkadotXcm::execute`, mirroring the pattern in the existing `withdraw_and_deposit_erc20s` test) referencing that contract's address as an `AccountKey20` location. The exploit is self-triggerable, repeatable, and requires no victim mistake or special privilege.

## Recommendation
- In `withdraw_asset_with_surplus`, read the checking account's ERC20 balance before and after the `transfer` call and credit `AssetsInHolding` with the actual observed delta instead of the requested `amount`.
- In `deposit_asset_with_surplus`, similarly measure the beneficiary's (or checking account's) balance delta and propagate any shortfall rather than assuming the full `amount` was delivered.
- Alternatively/additionally, restrict `ERC20Matcher` (or add a wrapping check) to a curated, pre-audited registry of ERC20 contracts that are known to be standard-conforming (no fees, no rebasing) before they can be routed through `ERC20Transactor`.

## Proof of Concept
1. Deploy an ERC20 contract on `pallet-revive` whose `transfer`/`transferFrom` returns `true` but deducts a fee (e.g., burns 5%) so the recipient receives only 95% of the requested amount.
2. As an unprivileged account, submit an XCM message via `PolkadotXcm::execute` containing `withdraw_asset` for this token's `AccountKey20` location, following the pattern in `withdraw_and_deposit_erc20s` (`asset-hub-westend/tests/tests.rs` L1864-1929).
3. Inspect `TransfersCheckingAccount`'s actual ERC20 balance via `Revive as fungibles::Inspect::balance(erc20_address, &checking_account)` before and after — it increases by only 95% of `amount`, while `AssetsInHolding` (and hence any subsequent `deposit_asset` accounting) is based on the full `amount`.
4. Repeat across multiple withdraw/deposit cycles to show the checking account's real balance persistently falls behind the sum of `amount` values credited/debited by the transactor for that asset, eventually causing a legitimate deposit for another user to fail with insufficient checking-account balance. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L166-207)
```rust
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
		// We need to return this surplus for the executor to allow refunding it.
		let surplus = weight_limit.saturating_sub(weight_consumed);
		tracing::trace!(target: "xcm::transactor::erc20::withdraw", ?weight_consumed, ?surplus, ?storage_deposit);
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L251-298)
```rust
		// To deposit, we actually transfer from the checking account to the beneficiary.
		// We do this using the solidity ERC20 interface.
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

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L134-160)
```rust
pub struct IsLocalAccountKey20;
impl Contains<Location> for IsLocalAccountKey20 {
	fn contains(location: &Location) -> bool {
		matches!(location.unpack(), (0, [AccountKey20 { .. }]))
	}
}

/// Fallible converter from a location to a `H160` that matches any location ending with
/// an `AccountKey20` junction.
pub struct AccountKey20ToH160;
impl MaybeEquivalence<Location, H160> for AccountKey20ToH160 {
	fn convert(location: &Location) -> Option<H160> {
		match location.unpack() {
			(0, [AccountKey20 { key, .. }]) => Some((*key).into()),
			_ => None,
		}
	}

	fn convert_back(key: &H160) -> Option<Location> {
		Some(Location::new(0, [AccountKey20 { key: (*key).into(), network: None }]))
	}
}

/// [`xcm_executor::traits::MatchesFungibles`] implementation that matches
/// ERC20 tokens.
pub type ERC20Matcher =
	MatchedConvertedConcreteId<H160, u128, IsLocalAccountKey20, AccountKey20ToH160, TryConvertInto>;
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L221-237)
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
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs (L2019-2073)
```rust
// Here the contract returns a number but because it can be cast to true
// it still succeeds.
#[test]
fn smart_contract_does_not_return_bool_fails() {
	let sender: AccountId = ALICE.into();
	let beneficiary: AccountId = BOB.into();
	let revive_account = pallet_revive::Pallet::<Runtime>::account_id();
	let checking_account =
		asset_hub_westend_runtime::xcm_config::ERC20TransfersCheckingAccount::get();
	let initial_wnd_amount = 10_000_000_000_000u128;

	ExtBuilder::<Runtime>::default().build().execute_with(|| {
		// Bring the revive account to life.
		assert_ok!(Balances::mint_into(&revive_account, initial_wnd_amount));

		// Fund all accounts involved.
		assert_ok!(Balances::mint_into(&sender, initial_wnd_amount));
		assert_ok!(Balances::mint_into(&beneficiary, initial_wnd_amount));
		assert_ok!(Balances::mint_into(&checking_account, initial_wnd_amount));

		// This contract implements the ERC20 interface for `transfer` except it returns a uint256.
		let code = compile_module_with_type("MyTokenFake", FixtureType::Resolc)
			.expect("compile ERC20")
			.0;

		let initial_amount_u256 = U256::from(1_000_000_000_000u128);
		let constructor_data = sol_data::Uint::<256>::abi_encode(&initial_amount_u256);

		let Contract { addr: non_erc20_address, .. } = bare_instantiate(&sender, code)
			.transaction_limits(TransactionLimits::WeightAndDeposit {
				weight_limit: Weight::from_parts(500_000_000_000, 10 * 1024 * 1024),
				deposit_limit: Balance::MAX,
			})
			.data(constructor_data)
			.build_and_unwrap_contract();

		let wnd_amount_for_fees = 1_000_000_000_000u128;
		let erc20_transfer_amount = 100u128;
		let message = Xcm::<RuntimeCall>::builder()
			.withdraw_asset((Parent, wnd_amount_for_fees))
			.pay_fees((Parent, wnd_amount_for_fees))
			.withdraw_asset((
				AccountKey20 { key: non_erc20_address.into(), network: None },
				erc20_transfer_amount,
			))
			.deposit_asset(AllCounted(1), beneficiary.clone())
			.build();
		// Execution fails but doesn't panic.
		assert!(PolkadotXcm::execute(
			RuntimeOrigin::signed(sender.clone()),
			Box::new(VersionedXcm::V5(message)),
			Weight::from_parts(2_500_000_000, 220_000),
		)
		.is_err());
	});
```
