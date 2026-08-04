## Analog Found: ERC20Transactor decodes bool return without accounting for the state change that already occurred

### Title
Non-standard ERC20 tokens (no bool return) cause `ERC20Transactor` to lose track of already-transferred funds during XCM asset transacting - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` call an arbitrary ERC20-like `pallet_revive` contract's `transfer` function via `bare_call`, then require the returned data to ABI-decode as a `bool` (`IERC20::transferCall::abi_decode_returns_validate`). This is the exact same class of bug as the reported issue: some ERC20 implementations (like mainnet USDT) execute the transfer successfully but return no data at all, causing the boolean decode to fail even though the state-changing transfer already completed on-chain.

### Finding Description
The transactor is registered as one of the `AssetTransactors` for asset ids of the form `AccountKey20` (i.e. any smart-contract address), as documented in [1](#0-0) , and wired into the runtime in [2](#0-1) . Because the asset id is derived directly from the contract's `H160` address (via `ERC20Matcher`) rather than from a curated allow-list, any deployed `pallet_revive` contract exposing an ERC20-shaped interface can be used as the underlying asset for this transactor.

In `withdraw_asset_with_surplus`, the transfer to the checking account is executed via `pallet_revive::Pallet::<T>::bare_call` — a real, state-changing call — before the return value is inspected: [3](#0-2) 

If the call does not revert but also does not return ABI-encoded boolean data (e.g. a USDT-style non-compliant `transfer`/similar), `abi_decode_returns_validate` fails and the function returns `Err(XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode"))` — even though the tokens have already physically moved to the checking account: [4](#0-3) 

The identical pattern exists in `deposit_asset_with_surplus`, where funds are transferred from the checking account to the beneficiary and the same decode-or-fail logic is applied after the transfer already executed: [5](#0-4) 

This mirrors the reported root cause precisely: the SDK code, like the audited Solidity contracts, assumes ERC20 `transfer`/`approve`-style calls always return a decodable `bool`, and treats a failure to decode that value as if the underlying operation failed — without accounting for the fact that the operation's state effects (the token transfer) have already been committed.

### Impact Explanation
When `withdraw_asset_with_surplus` returns an `Err` after the underlying `transfer` to the checking account already succeeded, the XCM executor believes the withdrawal failed and does not credit any `AssetsInHolding` for the amount (`Erc20Credit`) — but the sender's tokens are gone, moved into `TransfersCheckingAccount`. This is a direct loss-of-funds/accounting desync: the user's balance decreased on the ERC20 contract, yet the XCM program proceeds (or aborts) with no corresponding holding register credit, and no automatic mechanism recovers the tokens from the checking account. Symmetrically, in `deposit_asset_with_surplus`, if the transfer from the checking account to the beneficiary succeeds but fails to decode, the XCM executor treats the deposit as failed (returning `what` back to the caller/trap) while the beneficiary has already received the tokens — the same units could then be considered "trapped assets" and reprocessed, risking double-crediting.

### Likelihood Explanation
This is realistically triggerable, not merely theoretical: the ERC20 asset id space is any `AccountKey20` (`pallet_revive` contract address), so an unprivileged user can deploy or use an existing non-standard ERC20 contract (mirroring real-world tokens like USDT that do not return `bool` from `transfer`) and register/reference it as the asset in an XCM program that invokes this transactor. No privileged origin is required — any user constructing an XCM message that withdraws/deposits such a token through `ERC20Transactor` hits this path.

### Recommendation
Do not treat a failed ABI decode of the return data as equivalent to "the operation reverted." When `return_value.did_revert()` is `false` but the return data is empty or fails to decode as `bool`, treat the call as successful (matching common "SafeERC20"-style handling: empty return data on a non-reverting call is accepted as success), only treating an explicit `Ok(false)` decoded return as a genuine transfer failure. This should be applied to both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus` in `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`.

### Proof of Concept
1. Deploy a `pallet_revive` contract implementing `transfer(address,uint256)` that performs the balance mutation but returns no data (mimicking mainnet USDT semantics), matching the `IERC20` interface used by [6](#0-5) .
2. Register/derive this contract's address as an XCM asset id (`AccountKey20`) matched by `ERC20Matcher`, as configured in [7](#0-6) .
3. Submit an XCM program that calls `WithdrawAsset` for this asset from a user account, triggering `ERC20Transactor::withdraw_asset_with_surplus`.
4. Observe: the underlying `transfer` to `TransfersCheckingAccount` succeeds (funds move), but `IERC20::transferCall::abi_decode_returns_validate` fails on the empty return data at [8](#0-7) , causing `Err(XcmError::FailedToTransactAsset(...))` to propagate while the user's balance has already been debited with no compensating holding-register credit.

### Citations

**File:** prdoc/stable2506/pr_7762.prdoc (L9-15)
```text
      This PR introduces an Asset Transactor for dealing with ERC20 tokens and adds it to Asset Hub
      Westend.
      This means asset ids of the form `{ parents: 0, interior: X1(AccountKey20 { key, network }) }` will be
      matched by this transactor and the corresponding `transfer` function will be called in the
      smart contract whose address is `key`.
      If your chain uses `pallet-revive`, you can support ERC20s as well by adding the transactor, which lives
      in `assets-common`.
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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L166-194)
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

**File:** substrate/primitives/ethereum-standards/src/IERC20.sol (L41-46)
```text
    /// @dev Moves a `value` amount of tokens from the caller's account to `to`.
    ///
    /// Returns a boolean value indicating whether the operation succeeded.
    ///
    /// Emits a {Transfer} event.
    function transfer(address to, uint256 value) external returns (bool);
```
