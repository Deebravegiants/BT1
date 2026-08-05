## Analysis: Fee-on-Transfer / Non-Standard ERC20 Analog in `ERC20Transactor`

The reported vulnerability class (unaccounted transfer fees breaking the "amount requested == amount actually moved" invariant) has a direct analog in the Polkadot SDK's `ERC20Transactor`, which bridges XCM asset transfers to arbitrary ERC20 contracts running under `pallet-revive`.

### Title
Unverified ERC20 transfer amounts allow fee-on-transfer/rebasing tokens to desynchronize XCM holding credits from actual checking-account balance - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` invoke a token's `IERC20::transfer` and only check the boolean success return value, then unconditionally mint an `AssetsInHolding` credit (or assume a deposit succeeded) for the exact `amount` requested — never verifying the actual balance delta of the `TransfersCheckingAccount`.

### Finding Description
In `withdraw_asset_with_surplus`, the transactor calls `transfer(checking_address, amount)` on the ERC20 contract identified by the location's `AccountKey20` and, if the call returns `true`, mints `Erc20Credit(amount)` into the XCM holding regardless of how many tokens the checking account actually received [1](#0-0) . The standard ERC20 `transfer` ABI only returns a success boolean; it says nothing about the amount actually credited. Fee-on-transfer, rebasing, or otherwise non-standard tokens can return `true` while crediting the recipient (`checking_address`) less than `amount`.

Symmetrically, `deposit_asset_with_surplus` transfers `amount` from the checking account to the beneficiary and treats a `true` return as full success [2](#0-1) , again without confirming the beneficiary's balance actually increased by `amount`.

The `ERC20Matcher` used to decide which locations/contracts this transactor handles matches **any** location of the form `(0, [AccountKey20 { key, .. }])` — i.e., any deployed contract address, with no whitelist [3](#0-2) . Since `pallet-revive` contract deployment is permissionless, any user can deploy a fee-on-transfer or otherwise non-conformant ERC20 contract and immediately have it recognized by this transactor in `AssetTransactors` on Asset Hub Westend [4](#0-3) .

This is the same root cause pattern as the external report: the protocol assumes `transfer(amount)` moves exactly `amount`, and never reconciles the "vault" (here, `ERC20TransfersCheckingAccount`) balance before/after against the credit it issues into the XCM system.

### Impact Explanation
Every successful withdraw against a fee-on-transfer/rebasing ERC20 mints an `AssetsInHolding`/`Erc20Credit` value larger than what is actually locked in the checking account. Over repeated withdraw operations, the checking account balance for that asset drifts below the sum of credits that have been (or will be) represented elsewhere in the XCM program (e.g., deposited to a different local beneficiary, or forwarded in a reserve-transfer to a remote chain that mints a derivative 1:1 against the "locked" amount). This breaks the same `balance[before] == balance[after]` reserve-backing invariant flagged in the original report, and can eventually cause deposit/redemption failures (later users unable to withdraw the full backing) once the shortfall surfaces — a systemic accounting/backing risk, not merely a cosmetic balance display bug.

### Likelihood Explanation
Reachable by any unprivileged user: `pallet-revive` contract deployment and XCM local execution (`pallet_xcm::execute`) are both available to ordinary accounts, and the `ERC20Matcher` imposes no allow-list on which contract addresses are treated as valid ERC20 assets by this transactor. An attacker (or even an unaware integrator) only needs to reference a non-standard ERC20 contract address via an `AccountKey20` location in an XCM program that exercises `WithdrawAsset`/`DepositAsset` through `ERC20Transactor`.

### Recommendation
After each `transfer` call in `withdraw_asset_with_surplus`/`deposit_asset_with_surplus`, read back the checking/beneficiary account's actual `balanceOf` delta (or require/verify a `Transfer` event amount) and mint/return an `AssetsInHolding` credit reflecting the *actual* amount moved rather than the requested `amount`. Alternatively, restrict `ERC20Matcher` to an explicitly whitelisted set of verified standard-conformant ERC20 contracts, consistent with the "whitelisted tokens only" mitigation the original report's client relied on.

### Proof of Concept
1. Deploy a minimal ERC20-like contract via `pallet-revive` whose `transfer` function deducts 1% and burns it, but still returns `true`.
2. Use `pallet_xcm::execute` with a program: `WithdrawAsset` for this contract's `AccountKey20` location, amount `100`, followed by `DepositAsset` to a different local beneficiary.
3. Observe: `ERC20Transactor::withdraw_asset_with_surplus` mints `Erc20Credit(100)` [5](#0-4)  even though the checking account's `balanceOf` only increased by `99`. The subsequent `deposit_asset_with_surplus` attempts to move `100` out of the checking account [6](#0-5) , which will fail once the checking account's real balance is insufficient — demonstrating the checking account is under-collateralized relative to credits already issued for prior successful operations.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L166-203)
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L251-280)
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L157-161)
```rust
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
