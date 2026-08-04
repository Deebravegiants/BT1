### Title
ERC20 Asset Transactor assumes exact-amount ERC20 `transfer()` semantics, breaking accounting for fee-on-transfer/rebasing tokens - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
The `ERC20Transactor` used as an XCM `TransactAsset` implementation for ERC20 assets deployed via `pallet-revive` moves tokens through a shared `TransfersCheckingAccount` using the standard `IERC20::transfer` call, and blindly assumes that the `amount` requested equals the `amount` actually credited/debited on both sides of the transfer. This mirrors the Axelar `TokenHandler` `LOCK_UNLOCK` pattern (`takeToken`/`giveToken`) flagged in the referenced report: any ERC20 whose balance changes are not a strict 1:1 function of transferred `amount` (fee-on-transfer, deflationary burn-on-transfer, or rebasing tokens) will desynchronize the tracked `amount` from the token contract's real balance changes.

### Finding Description
`withdraw_asset_with_surplus` locks tokens by calling the ERC20's `transfer(checking_address, amount)` from the user's account to `TransfersCheckingAccount`, and on success unconditionally constructs an `AssetsInHolding` credit for the full requested `amount`: [1](#0-0) 

`deposit_asset_with_surplus` later moves tokens out of the same `TransfersCheckingAccount` to the beneficiary by again calling `transfer(address, amount)` for that same nominal `amount`, with no re-check of the checking account's actual token balance before/after: [2](#0-1) 

Neither function reads the ERC20's `balanceOf` before and after the transfer to determine the *actual* amount moved — they trust the caller-supplied `amount` parameter and the boolean return value of `transfer()`. This is functionally identical to Axelar's `TokenHandler.takeToken`/`giveToken`, which likewise perform `safeTransferFrom(from, tokenManager, amount)` and `safeTransferFrom(tokenManager, to, amount)` without verifying that `amount` sent equals `amount` received — the exact root cause identified in the external report's Sub-section 1.

Because `TransfersCheckingAccount` is a single pooled account (shared across all ERC20 assets/messages routed through this transactor), any token that:
- charges a fee/burns on transfer (checking account receives less than `amount` credited), or
- rebases its balance out-of-band between the `withdraw` and later `deposit` calls (which, for reserve-based multi-hop or asynchronous XCM flows, are not guaranteed to be in the same atomic call),

will cause the checking account's real ERC20 balance to diverge from the sum of `amount`s the runtime believes it holds.

### Impact Explanation
- If the checking account's real balance is lower than the sum of tracked/nominal amounts (due to fee-on-transfer/deflationary/negative-rebase tokens), a subsequent `deposit_asset_with_surplus` for another (unrelated) pending transfer through the same checking account can fail because the ERC20 `transfer` call reverts or returns `false` for insufficient balance — causing funds routed through that asset to become stuck/untransferable, analogous to the `checked_sub` revert / stuck-funds scenario in Sub-section 2 of the report.
- If the token is instead of the type that increases balance without altering per-account accounting semantics (positive rebase) after locking but before releasing, the pooled excess is not reflected in any single user's credited `amount`, meaning value can leak or become unaccounted-for surplus sitting in the checking account, similar to the value-leakage scenario in Sub-section 1.
- Because `TransfersCheckingAccount` is shared, an issue with one non-standard ERC20 asset can affect the ability to process transfers of that same asset for unrelated users, since insufficient checking-account balance blocks any deposit of that asset regardless of which transfer it originates from.

### Likelihood Explanation
Likelihood depends entirely on which ERC20 contracts get registered/matched by `Matcher: MatchesFungibles` for use with this transactor. `ERC20Transactor` is wired into `asset-hub-westend`'s XCM configuration [3](#0-2) , meaning it is a live, reachable code path for XCM asset transfers of pallet-revive-deployed ERC20 tokens, not a mocked/test-only helper. Any unprivileged user who registers or uses a fee-on-transfer or rebasing ERC20 contract through this transactor can trigger the divergence; no privileged role is required to reach the vulnerable code path, only to have such a token registered in the asset matcher, which is a governance/registration action but the *exploitation* itself is available to any user interacting with such a token afterward.

### Recommendation
Do not assume `transfer(amount)` produces an exact `amount` balance delta. Either:
1. Measure `balanceOf(checking_account)` before and after `transfer` in `withdraw_asset_with_surplus`, and credit `AssetsInHolding` with the *actual* delta observed rather than the requested `amount`; similarly measure the beneficiary's actual received delta in `deposit_asset_with_surplus` and only report success/mint outbound message data for the amount actually delivered.
2. Alternatively, explicitly document/enforce (at the `MatchesFungibles`/asset registration layer) that only strictly standard-conforming ERC20s (no fee-on-transfer, no rebasing) may be matched for use with `ERC20Transactor`, and reject registration of tokens that do not satisfy an invariant check (e.g., a pre-flight balance-delta test at registration time).

### Proof of Concept
1. Deploy (or have a user register) an ERC20 contract via `pallet-revive` that implements a 1% fee-on-transfer (fee burned) or a positive/negative rebase mechanism, and get it matched by the runtime's `MatchesFungibles` configuration for `ERC20Transactor`.
2. User A initiates an XCM transfer of `amount = 1000` of this token. `withdraw_asset_with_surplus` calls `transfer(checking_account, 1000)`; due to the fee, the checking account's real balance only increases by `990`. The function still returns an `AssetsInHolding` credit of `1000`: [4](#0-3) 
3. When `deposit_asset_with_surplus` is later invoked to release the credited `1000` to the destination beneficiary, it calls `transfer(beneficiary, 1000)` from the checking account, but the checking account only has `990` (plus whatever residual/pooled balance exists from other pending transfers). If the checking account is otherwise near-empty, this `transfer` reverts/returns `false`, causing `Err((what, XcmError::FailedToTransactAsset(...)))`: [5](#0-4) 
4. The transfer fails or, if the checking account had a surplus buffer from other users' funds, it succeeds by silently consuming another user's locked balance, breaking the 1:1 accounting invariant the runtime otherwise relies on for asset transactors.

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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L270-286)
```rust
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
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L1-1)
```rust
// Copyright (C) Parity Technologies (UK) Ltd.
```
