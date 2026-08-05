Audit Report

## Title
ERC20 Asset Transactor blindly trusts declared transfer amount instead of verifying actual balance delta, breaking accounting for fee-on-transfer/rebasing ERC20 tokens - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

## Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` credit/debit the XCM `AssetsInHolding` register using the caller-declared `amount` passed to the ERC20 `transfer()` call, rather than verifying the actual balance change on the `TransfersCheckingAccount`. Because `ERC20Matcher`/`IsLocalAccountKey20` matches any local `AccountKey20` location without any registration or allow-list gate, an unprivileged user can deploy a non-standard (fee-on-transfer or rebasing) ERC20 contract via `pallet-revive` and use it through this transactor to desynchronize XCM-tracked "credit" from the real balance held by the shared checking account.

## Finding Description
In `withdraw_asset_with_surplus`, the transactor calls ERC20 `transfer(checking_address, amount)` and, upon a successful (non-reverted, `true`-returning) call, unconditionally credits `AssetsInHolding` with `Erc20Credit(amount)` using the requested `amount` rather than the amount actually received by the checking account: [1](#0-0) . Symmetrically, `deposit_asset_with_surplus` instructs the checking account to `transfer(beneficiary, amount)` using the amount taken from holding, again without checking the checking account's real balance before/after or the beneficiary's actually received amount: [2](#0-1) .

The `Erc20Credit` imbalance type explicitly documents that it performs no runtime-level balance enforcement, relying entirely on the ERC20 contract to do so — but the transactor never re-derives the credited/debited amount from an actual balance check: [3](#0-2) .

Critically, there is no allow-list gating which ERC20 contracts are eligible: `ERC20Matcher` is built on `IsLocalAccountKey20`, which matches *any* local `AccountKey20` location unconditionally: [4](#0-3) . This is confirmed by the feature's own PR description, which states the transactor matches any asset id of the form `{ parents: 0, interior: X1(AccountKey20 { key, network }) }` and calls `transfer` on whatever contract address `key` refers to — with no registration step. The transactor is wired into `AssetTransactors` on Asset Hub Westend: [5](#0-4) .

The only checks performed are on the call's success/revert status and ABI-decoded boolean return value — not on the actual token balance delta: [6](#0-5) .

## Impact Explanation
A user can deploy a fee-on-transfer or rebasing ERC20 contract via `pallet-revive` and reference it in an XCM program targeting their own contract address. On withdraw, the checking account receives less than the nominal `amount` (or a rebasing balance fluctuates independent of the transfer), yet the XCM holding register is credited the full nominal `amount`. Since the `TransfersCheckingAccount` is shared across *all* users of a given ERC20 asset (a single `PalletId`-derived account per runtime, not per-asset or per-user), this creates a real accounting divergence in that shared account: subsequent legitimate depositors of the same asset can experience `deposit_asset_with_surplus` failures (DoS) once the shortfall exceeds the account's actual balance, or funds backing other users' claims can be spent, causing loss for other holders of that same asset. This is an unprivileged-triggerable in-scope accounting/insolvency issue for the ERC20 transactor introduced on Asset Hub Westend.

## Likelihood Explanation
High. No permissioning, registration, or allow-list step exists between deploying an arbitrary ERC20 contract on `pallet-revive` and having that contract's address usable as a first-class XCM fungible asset via `WithdrawAsset`/`DepositAsset` — `ERC20Matcher` unconditionally matches any `AccountKey20` location. Contrast this with `ForeignAssets`/`PoolAssets` transactors, which gate on registration or non-zero-issuance checks. An attacker only needs to instantiate a contract and submit a `PolkadotXcm::execute` call referencing it, both reachable by any signed account, as demonstrated by the existing test `withdraw_and_deposit_erc20s` in `asset-hub-westend/tests/tests.rs`, which exercises exactly this withdraw/deposit flow for arbitrary user-deployed ERC20 contracts.

## Recommendation
Modify `withdraw_asset_with_surplus` and `deposit_asset_with_surplus` to read the ERC20 `balanceOf` of the relevant account before and after the `transfer` call, and credit/debit `AssetsInHolding` using the actual observed balance delta instead of the caller-declared `amount`. Alternatively, restrict the `ERC20Matcher`/checking account mechanism to a vetted allow-list of standard, non-rebasing, non-fee-on-transfer ERC20 contracts, analogous to the registration/issuance gating used for `TrustBackedAssets`/`ForeignAssets`.

## Proof of Concept
1. Deploy a fee-on-transfer ERC20 contract via `pallet-revive` whose `transfer(to, amount)` sends only `0.95 * amount` to `to` while still returning `true`.
2. Submit an XCM program (via `PolkadotXcm::execute`, callable by any signed account, as in the existing `withdraw_and_deposit_erc20s` test) with `WithdrawAsset` for `{ parents: 0, interior: [AccountKey20 { key: <contract address> }] }` for amount `X`, matched unconditionally by `IsLocalAccountKey20`/`ERC20Matcher`.
3. `withdraw_asset_with_surplus` transfers nominal `X` to `ERC20TransfersCheckingAccount`, but the checking account's real balance only increases by `0.95X`; the XCM holding register is nevertheless credited `Erc20Credit(X)`.
4. Follow with `DepositAsset` to a beneficiary for amount `X`; `deposit_asset_with_surplus` instructs the checking account to transfer out `X`, exceeding what it actually received, demonstrating the accounting mismatch and its effect on the shared checking account across all holders of that ERC20 asset.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L73-79)
```rust
/// A minimal imbalance tracking type that holds an ERC20 token amount.
///
/// This type implements the necessary imbalance accounting traits but does not perform
/// runtime-level balance enforcement. It's used to track ERC20 token amounts within XCM
/// asset holdings, where the actual balance constraints are enforced by the ERC20 smart
/// contract itself rather than the runtime.
struct Erc20Credit(u128);
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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L251-266)
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L132-160)
```rust
/// `Contains<Location>` implementation that matches locations with no parents,
/// a `PalletInstance` and an `AccountKey20` junction.
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
