## Analog Vulnerability Found

The reported ERC4626 pattern — trusting a return value instead of verifying the real balance delta — has a direct analog in this repository's `ERC20Transactor`, used to bridge `pallet-revive` ERC-20 contracts into XCM's `AssetsInHolding` accounting.

### Title
Trusting unchecked ERC20 `transfer()` return values in `ERC20Transactor` causes phantom asset accounting - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` credit/debit XCM's `AssetsInHolding` based purely on the boolean return value of an ERC20 `transfer()` call to/from an internal `TransfersCheckingAccount`, without ever verifying the actual `balanceOf` delta of that account.

### Finding Description
On withdraw, the transactor calls `transfer(checking_address, amount)` on the asset's ERC20 contract and, if `abi_decode_returns_validate` yields `Ok(true)`, unconditionally mints `AssetsInHolding` credit for the full requested `amount` via `Erc20Credit(amount)`: [1](#0-0) 

On deposit, the same pattern is used — the transactor trusts `Ok(true)` from the beneficiary transfer and reports success/surplus without checking that the beneficiary's real balance actually increased: [2](#0-1) 

This is registered in Asset Hub Westend as one of the standard `AssetTransactors` handling any ERC20 whose address appears as an `AccountKey20` interior junction, per the feature PRDoc: any ERC20 contract address can be referenced from XCM, matched by `assets_common::ERC20Matcher`, with no separate governance-gated registration step required beyond the contract existing on-chain via `pallet-revive`: [3](#0-2) 

Unlike the codebase's own `pallet-asset-conversion` precompile tests, which explicitly assert that balance deltas match the decoded return values (the "correct" pattern the original report recommends): [4](#0-3) 

`erc20_transactor.rs` never performs this balance-delta check.

### Impact Explanation
Any ERC20 contract with non-standard transfer semantics — fee-on-transfer, rebasing, deflationary, or otherwise return-value-lying tokens — will cause the `TransfersCheckingAccount`'s real token balance to drift out of sync with the sum of `AssetsInHolding` credits the runtime believes exist. Because `Erc20Credit`'s accounting is a purely internal counter (per its own doc comment, "the actual balance constraints are enforced by the ERC20 smart contract itself rather than the runtime"), repeated withdraw/deposit cycles on such a token will progressively overstate holdings relative to the checking account's real balance. This can manifest as: (a) legitimate users' later deposits/withdrawals failing once the checking account's real balance is exhausted (denial of service), or (b) early users extracting more real value than they deposited at the expense of later users — the same "unfairly affects users' positions" outcome described in the original report, since the checking account functions like a shared vault/pool for that ERC20 across all XCM participants.

### Likelihood Explanation
Reaching this code requires only that some ERC20 contract with non-conforming transfer behavior be referenced via its `AccountKey20` location in an XCM program — no privileged registration or governance action is needed per the transactor's design (any deployed contract address matches). Fee-on-transfer and rebasing tokens are common in the wider ERC20 ecosystem, making this a realistic occurrence rather than a purely theoretical one, though it is somewhat mitigated by requiring an unusual/malicious token to actually be used through this specific transactor.

### Recommendation
Verify actual balance deltas of the `TransfersCheckingAccount` (and beneficiary, for deposits) via `balanceOf` before and after the `transfer()` call, and use the observed delta — not the trusted return value — as the credited/debited `AssetsInHolding` amount, mirroring the balance-delta-check pattern already used in `substrate/frame/asset-conversion/precompiles/src/tests.rs`.

### Proof of Concept
1. Deploy (or reference) an ERC20 contract via `pallet-revive` on Asset Hub Westend whose `transfer()` always returns `true` but delivers less than `value` (fee-on-transfer) to the recipient.
2. Submit an XCM program with `WithdrawAsset` referencing this token's `AccountKey20` location for amount `N`; `ERC20Transactor::withdraw_asset_with_surplus` credits `AssetsInHolding` with the full `N` even though the `TransfersCheckingAccount`'s real balance only increased by `N - fee`.
3. Repeat withdraw/deposit cycles (e.g. via other users' legitimate XCM transfers of the same token) until the checking account's real balance is less than the sum of outstanding phantom credits — subsequent legitimate `deposit_asset_with_surplus` calls for other users will begin failing once the checking account cannot cover the overstated total, or an attacker who withdraws first captures more than their fair share of the account's dwindling real balance.

**Uncertainty:** I could not find, within the indexed portion of the codebase, a bridge from `ERC20Transactor`'s `Erc20Credit` into `pallet-asset-conversion` pools (the `SingleAssetExchangeAdapter`/`ExchangeAsset` path operates on `fungibles::Balanced` assets like `Assets`/`ForeignAssets`, not directly on raw `pallet-revive` ERC20 balances), so I cannot confirm this phantom-accounting issue propagates into shared liquidity pools — the concrete impact is scoped to the `TransfersCheckingAccount`'s own solvency for that specific ERC20 token, not necessarily broader protocol assets. Given the size limits on indexing, there may be additional integration points (e.g. in `pallet-dap` or other Asset Hub configuration) I was unable to fully inspect; a full-repository review via a Devin session would be needed to conclusively rule out a wider blast radius.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L191-203)
```rust
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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L270-280)
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

**File:** substrate/frame/asset-conversion/precompiles/src/tests.rs (L136-146)
```rust
		let swapper_asset1_after =
			<NativeAndAssets as Inspect<u64>>::balance(NativeOrWithId::WithId(1), &swapper);
		assert_eq!(swapper_asset1_before - swapper_asset1_after, 100);

		let recipient_native_after =
			<NativeAndAssets as Inspect<u64>>::balance(NativeOrWithId::Native, &recipient);
		assert_eq!(
			U256::from(recipient_native_after - recipient_native_before),
			amount_out,
			"received amount must match return value"
		);
```
