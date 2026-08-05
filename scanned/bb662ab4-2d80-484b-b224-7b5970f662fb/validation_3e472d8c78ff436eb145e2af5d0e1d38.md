## Analysis

The reported bug is a Solidity-side "no-bool-return ERC-20" incompatibility (`IERC20.approve()` reverting when the callee returns no data, as is the case for Tether-style/USDT0 tokens). Searching the Rust codebase, the closest structural analog is not `pallet-assets` (which has already been hardened for ERC-20 semantics, see `pallet_11279`/`pallet_12196` prdocs) but the code in `pallet-revive`/Cumulus that bridges XCM to actual Solidity ERC-20 contracts and strictly ABI-decodes their return values.

Two candidate call sites were found:

1. `substrate/frame/revive/src/impl_fungibles.rs` `burn_from`/`mint_into` (lines 191-192, 229-230) use `bool::abi_decode_validate(&return_value.data).expect("Failed to ABI decode")` [1](#0-0) . This would panic outright on a non-bool-returning ERC-20. However, this entire module is gated by `#![cfg(any(feature = "std", feature = "runtime-benchmarks", test))]` and its own doc comment states "This is only meant for tests since gas limits are not taken into account" [2](#0-1) . It is **not compiled into a production runtime**, so it is disqualified per the "no reachable attacker-controlled entry path" rule.

2. `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`, the production `ERC20Transactor` used as an XCM `TransactAsset` implementation for bridging ERC-20 tokens through `pallet-revive`. Both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus` ABI-encode an `IERC20::transferCall`, execute it via `bare_call`, and then decode the return with `IERC20::transferCall::abi_decode_returns_validate(&return_value.data)` [3](#0-2) [4](#0-3) . Unlike the Solidity bug, decode failure here is handled gracefully (mapped to `XcmError::FailedToTransactAsset`, not a panic), but any ERC-20 contract that (like Tether/USDT0) returns no boolean from `transfer()` will make `withdraw_asset` and `deposit_asset` **unconditionally fail** for that asset — every XCM message trying to move it reverts with "ERC20 contract result couldn't decode". This requires the asset to already be configured/matched by `Matcher::matches_fungibles` (a governance/config decision, analogous to a vault already listing USDT0 as a supported asset in the original report), but once configured, any unprivileged user's ordinary XCM transfer of that asset is permanently unusable — the same "always reverts / permanently bricked" impact class as the original finding, just realized via a returned XCM error rather than an ABI-decode panic.

Given the ambiguity of whether the disqualification rule "trusted-role compromise required" applies to the *initial configuration* step (which is not attacker action, just as USDT0 being a supported vault asset wasn't attacker-caused in the original report) versus the actual triggering action (an ordinary user's XCM transfer, which is unprivileged), I present this as the closest, but lower-confidence, analog:

### Title
ERC20Transactor XCM asset transfers permanently fail for non-bool-returning ERC-20 tokens (e.g. USDT/USDT0-style contracts) - (File: cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` strictly ABI-decode the `bool` return of `IERC20::transferCall` via `abi_decode_returns_validate`. Any ERC-20 contract that returns no data on success (the historical Tether/USDT-style non-compliant pattern referenced in the source report) causes decoding to fail on every single transfer, permanently disabling XCM-based transfers for that asset.

### Finding Description
Both transactor functions call `bare_call` against the ERC-20 contract and then run:
```rust
IERC20::transferCall::abi_decode_returns_validate(&return_value.data)
``` [4](#0-3) 
If the contract executes successfully but returns empty calldata (no `bool`), this decode call errors, and the transactor maps that to `XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")` for both withdraw and deposit paths [5](#0-4) . There is no fallback treating empty return data as success (the "safe ERC-20" pattern recommended in the source report).

### Impact Explanation
If a parachain runtime configures `Matcher` to route a non-bool-returning ERC-20 (mirroring Tether's historical/`USDT0` behavior) through `ERC20Transactor`, then **every** `withdraw_asset`/`deposit_asset` XCM operation for that token will fail unconditionally — the asset becomes permanently untransactable through XCM. This mirrors the original report's "always reverts, DoS for the entire lifecycle" impact, though realized as a graceful XCM error rather than a panic/revert.

### Likelihood Explanation
Low-to-moderate. The failure is only reachable once a runtime's asset registration/config (a privileged/governance action) matches a non-standard ERC-20 to this transactor — an unprivileged user cannot introduce the vulnerable asset themselves, they can only trigger the (already broken) transfer path for an asset that governance chose to list. This weakens the finding relative to the source report, where the vulnerable code path was reachable purely through normal owner operations on an already-supported asset.

### Recommendation
Mirror the `TransferTokenHelper.safeTokenApprove()` pattern from the report: treat empty return data as success (only fail the decode if data is present and decodes to `false`, or if data is present with wrong length), i.e. replace the strict `abi_decode_returns_validate` with logic equivalent to:
```rust
if return_value.data.is_empty() { /* treat as success */ }
else { /* decode bool, check truthiness */ }
```
This should be applied to both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus` in `erc20_transactor.rs`.

### Proof of Concept
1. Deploy (or configure via governance) an ERC-20 contract on `pallet-revive` whose `transfer()` implementation does not return a `bool` (empty return data), mirroring Tether's non-standard `transfer`/`approve`.
2. Register this contract as a `Matcher`-recognized fungible asset for `ERC20Transactor`.
3. Submit any XCM message that withdraws or deposits this asset (e.g., a reserve transfer).
4. `bare_call` succeeds and does not revert, but `abi_decode_returns_validate` fails on the empty return data, causing `XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")` for every subsequent attempt — permanent DoS of that asset's XCM transferability.

### Citations

**File:** substrate/frame/revive/src/impl_fungibles.rs (L18-25)
```rust
//! Implementation of the `fungibles::*` family of traits for `pallet-revive`.
//!
//! This is meant to allow ERC20 tokens stored on this pallet to be used with
//! the fungibles traits.
//! This is only meant for tests since gas limits are not taken into account,
//! the feature flags make sure of that.

#![cfg(any(feature = "std", feature = "runtime-benchmarks", test))]
```

**File:** substrate/frame/revive/src/impl_fungibles.rs (L187-199)
```rust
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L185-215)
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
		} else {
			tracing::debug!(target: "xcm::transactor::erc20::withdraw", ?result, "Error");
			// This error could've been duplicate smart contract, out of gas, etc.
			// If the issue is gas, there's nothing the user can change in the XCM
			// that will make this work since there's a hardcoded gas limit.
			Err(XcmError::FailedToTransactAsset("ERC20 contract execution errored"))
		}
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L276-297)
```rust
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
```
