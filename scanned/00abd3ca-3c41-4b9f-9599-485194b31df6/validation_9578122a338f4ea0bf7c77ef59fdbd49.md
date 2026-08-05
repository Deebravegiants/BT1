This confirms the key finding: `ERC20Matcher` (`cumulus/parachains/runtimes/assets/common/src/lib.rs:159-160`) matches **any** location of the form `AccountKey20`, meaning **any Ethereum contract address a user includes in an XCM message is treated as a valid ERC20 asset** — this is permissionless, not governance-gated, per the PRDoc: "asset ids of the form `{parents:0, interior: X1(AccountKey20{key,network})}` will be matched by this transactor and the corresponding `transfer` function will be called in the smart contract whose address is `key`" [1](#0-0) . Any unprivileged user can deploy a fee-on-transfer/deflationary ERC20 contract via `pallet-revive` and reference it in an XCM message.

### Title
Missing balance verification in `ERC20Transactor` allows accounting desync with fee-on-transfer/deflationary ERC20 tokens - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` credit/assume the exact `amount` requested by the XCM message into `AssetsInHolding`, relying solely on the ERC20 `transfer()` call's boolean return value and non-revert status, without checking the checking account's actual balance before/after the transfer [2](#0-1) .

### Finding Description
On withdraw, the code calls `IERC20::transferCall{ to: checking_address, value: amount }` on the arbitrary contract at `asset_id`, and — as long as the call doesn't revert and returns `true` — credits `AssetsInHolding` with the full requested `amount` via `Erc20Credit(amount)`, regardless of what the checking account actually received [3](#0-2) . Any ERC20 contract that burns/fees a portion of `transfer()` (fee-on-transfer, rebasing/deflationary tokens) while still returning `true` will cause the XCM holding register to be over-credited relative to the checking account's real token balance. The matcher (`ERC20Matcher`) accepts any `AccountKey20` location as a valid asset id with no allow-list or governance gate [4](#0-3) , so any user can deploy such a contract via `pallet-revive` and reference it in an XCM program routed through `ERC20Transactor`, which is wired into `AssetTransactors` on Asset Hub Westend [5](#0-4) . The same pattern applies symmetrically to `deposit_asset_with_surplus`, which transfers `amount` from the checking account to the beneficiary without confirming the beneficiary actually received `amount` [6](#0-5) .

### Impact Explanation
Repeated withdraw operations against a fee-on-transfer contract create phantom XCM holding credit that is not backed by real ERC20 balance in the checking account. This holding credit can subsequently be forwarded cross-chain (e.g., reserve-transferred/represented on another chain) or deposited back locally as if fully backed, meaning the checking account's real balance for that asset can become insufficient to satisfy later legitimate withdrawals for the same asset — an accounting/solvency inconsistency purely local to this ERC20 asset class, isolated per contract address (does not affect other assets' accounting).

### Likelihood Explanation
Reaching this path requires no privileged role: any user can (1) deploy a `pallet-revive` contract implementing `IERC20` with a deflationary/fee-on-transfer `transfer()` that still returns `true`, and (2) construct an XCM program referencing that contract address as an `AccountKey20` asset id, which `ERC20Matcher` will accept unconditionally. This is directly analogous to the reported class of "missing balance check before/after transfer" bugs, and mirrors exactly the scenario the external report describes for fee-charging ERC20 transfers.

### Recommendation
In `withdraw_asset_with_surplus`, query the checking account's ERC20 balance immediately before and after the `transfer` call and credit `AssetsInHolding` with the actual observed delta rather than the requested `amount`. Symmetrically, in `deposit_asset_with_surplus`, verify the beneficiary's balance delta matches (or fails/returns the shortfall) rather than assuming success implies exact-amount transfer, consistent with the "check balance before and after transfer" recommendation from the referenced report.

### Proof of Concept
1. Deploy (via `pallet_revive::Pallet::instantiate`) an ERC20-like contract whose `transfer(to, value)` burns/fees e.g. 5% of `value` before crediting `to`, but still returns `true` on success.
2. Craft an XCM `Xcm(vec![WithdrawAsset(asset), ...])` where `asset` is `{ parents: 0, interior: X1(AccountKey20 { key: <contract_address>, network: None }) }` with `fun: Fungible(amount)`.
3. Execute the XCM via `pallet_xcm` from a signed account holding `amount` of the token; observe `ERC20Transactor::withdraw_asset_with_surplus` returns `Erc20Credit(amount)` in the holding register (per lines 197-203) even though the checking account's on-chain ERC20 balance only increased by `amount * 0.95`.
4. Repeating this shows the XCM holding register's cumulative credited amount for this asset diverges from and exceeds the checking account's real ERC20 balance, demonstrable via `balanceOf(checking_account)` vs. sum of credited `amount`s across withdrawals.

### Citations

**File:** prdoc/stable2506/pr_7762.prdoc (L10-14)
```text
      Westend.
      This means asset ids of the form `{ parents: 0, interior: X1(AccountKey20 { key, network }) }` will be
      matched by this transactor and the corresponding `transfer` function will be called in the
      smart contract whose address is `key`.
      If your chain uses `pallet-revive`, you can support ERC20s as well by adding the transactor, which lives
```

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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L248-266)
```rust
		// We need to map the 32 byte beneficiary account to a 20 byte account.
		let eth_address = T::AddressMapper::to_address(&who);
		let address = Address::from(Into::<[u8; 20]>::into(eth_address));
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

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L157-160)
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
