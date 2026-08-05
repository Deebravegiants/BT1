Audit Report

## Title
Trusting unchecked ERC20 `transfer()` return values in `ERC20Transactor` causes phantom asset accounting - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

## Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` credit/debit XCM's `AssetsInHolding` based purely on the boolean return value of an ERC20 `transfer()` call to/from an internal `TransfersCheckingAccount`, without verifying the actual `balanceOf` delta of that account. This confirmed pattern allows non-standard ERC20 tokens (fee-on-transfer, rebasing) to desynchronize real on-chain balances from the runtime's internal `AssetsInHolding` accounting.

## Finding Description
On withdraw, the transactor calls `IERC20::transferCall` on the asset contract targeting `checking_address`, and upon `Ok(true)` from `abi_decode_returns_validate`, unconditionally mints `Erc20Credit(amount)` for the requested `amount` regardless of what the `TransfersCheckingAccount` actually received: [1](#0-0) . Symmetrically, on deposit, the transactor transfers from `TransfersCheckingAccount` to the beneficiary and treats `Ok(true)` as full success without confirming the beneficiary's real balance increased by `amount`: [2](#0-1) . The `Erc20Credit` type's own doc comment acknowledges this is a "minimal imbalance tracking type" that does not perform runtime-level balance enforcement, relying entirely on the ERC20 contract's own accounting: [3](#0-2) . This transactor is wired into Asset Hub Westend's `AssetTransactors` tuple, so it is live and reachable for any XCM program referencing an ERC20 asset: [4](#0-3) .

## Impact Explanation
For fee-on-transfer, rebasing, or otherwise non-conforming ERC20 tokens, the `TransfersCheckingAccount`'s real balance can drift from the sum of `Erc20Credit` amounts the runtime believes were deposited/withdrawn. Since this is limited to the single shared `TransfersCheckingAccount` used by this specific transactor for that specific ERC20 token, the blast radius is that account's own solvency for cycles of withdraw/deposit through XCM, potentially resulting in a denial of service for later users or a shift of value among users interacting with that token via this path. However, the credit is transient — `AssetsInHolding` is a per-XCM-instruction accounting object that only lives for the duration of executing the message; it isn't a persistent ledger balance a user "owns" across time. The actual value transferred out via `deposit_asset_with_surplus` is still bounded by what the ERC20 contract itself allows the `TransfersCheckingAccount` to send, so the ERC20 contract's own state constrains the real value that can leave the checking account. The exploit is entirely dependent on voluntarily using a malicious/non-standard ERC20 contract through the transactor — a normal, standard-conforming ERC20 (the vast majority, and any token registered normally) is entirely unaffected, since standard ERC20 transfers move exactly `amount` and return `true` only on full success.

## Likelihood Explanation
Triggering this requires an ERC20 contract with non-conforming transfer semantics (fee-on-transfer/rebasing) to be deployed via `pallet-revive` and referenced by its `AccountKey20` location in an XCM program — this is possible without governance, but requires deliberate use of a specific malicious/non-standard contract, which is a real but narrow precondition. This lands in the same territory the SDK's own SECURITY.md exclusion list flags: impacts requiring "basic economic" assumptions about third-party token behavior, and impacts that don't demonstrate concrete loss beyond a single non-standard token's own checking account. The report itself acknowledges uncertainty about whether this propagates beyond the checking account's own solvency into any pool or wider protocol asset, and could not confirm a bridge into `pallet-asset-conversion` liquidity pools.

## Recommendation
Verify the actual balance delta of the `TransfersCheckingAccount` (for withdraw) and the beneficiary (for deposit) via `balanceOf` calls before and after the `transfer()` call, and use the observed delta rather than the trusted return value as the credited/debited `AssetsInHolding` amount, following the balance-delta-check pattern in `substrate/frame/asset-conversion/precompiles/src/tests.rs`.

## Proof of Concept
1. Deploy an ERC20 contract via `pallet-revive` whose `transfer()` always returns `true` but delivers less than `value` to the recipient (fee-on-transfer).
2. Submit an XCM program with `WithdrawAsset` referencing this token's `AccountKey20` location for amount `N`; `withdraw_asset_with_surplus` credits `AssetsInHolding` with the full `N` even though `TransfersCheckingAccount`'s real balance only increased by `N - fee`.
3. Repeat withdraw/deposit cycles until the checking account's real balance is insufficient to cover subsequent legitimate `deposit_asset_with_surplus` calls, demonstrating DoS/value-drift scoped to that token's checking account.

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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L276-280)
```rust
				match IERC20::transferCall::abi_decode_returns_validate(&return_value.data) {
					Ok(true) => {
						tracing::trace!(target: "xcm::transactor::erc20::deposit", "ERC20 contract was successful");
						Ok(surplus)
					},
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L238-246)
```rust

/// Means for transacting assets on this chain.
pub type AssetTransactors = (
	FungibleTransactor,
	FungiblesTransactor,
	ForeignFungiblesTransactor,
	UniquesTransactor,
	ERC20Transactor,
);
```
