This confirms the critical detail the researcher couldn't verify: `ERC20Matcher` is defined as `MatchedConvertedConcreteId<H160, u128, IsLocalAccountKey20, AccountKey20ToH160, TryConvertInto>` [1](#0-0)  where `IsLocalAccountKey20` matches any `Location` of the form `(0, [AccountKey20 { .. }])` [2](#0-1) , and `AccountKey20ToH160` converts that junction's raw `key` field directly into the target contract's `H160` address with no registry lookup [3](#0-2) . The associated PR description confirms this design intent: "asset ids of the form `{ parents: 0, interior: X1(AccountKey20 { key, network }) }` will be matched by this transactor and the corresponding `transfer` function will be called in the smart contract whose address is `key`" — i.e. there is no separate governance-gated registration step; the XCM asset `Location` itself directly encodes the arbitrary target contract address.

This resolves the uncertainty the original report flagged: since the contract address is embedded directly in the `Location`/asset id matched by `Matcher` rather than looked up from a privileged registry, any unprivileged user constructing/executing an XCM program that references an `AccountKey20` asset pointing at a non-standard ERC20 contract (e.g., a USDT-style contract with no `bool` return on `transfer()`) can trigger the vulnerable decode path without any governance action.

The underlying code behavior matches the claim exactly: both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus` call `bare_call` then strictly require `IERC20::transferCall::abi_decode_returns_validate(&return_value.data)` to succeed, converting any decode error (including the empty-return-data case from non-standard ERC20 tokens) into `XcmError::FailedToTransactAsset` [4](#0-3) [5](#0-4) . There is no fallback treating empty return data as success (SafeERC20-style semantics), confirming the claimed missing guard.

---

Audit Report

## Title
`ERC20Transactor` strictly ABI-decodes `bool` from `transfer()`, breaking XCM deposit/withdraw for non-standard ERC20 tokens (USDT-class) - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

## Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` call `transfer()` on an arbitrary ERC20 contract via `pallet_revive::Pallet::<T>::bare_call`, then require the returned data to strictly ABI-decode as `bool` via `IERC20::transferCall::abi_decode_returns_validate`. Non-standard ERC20 tokens (e.g., mainnet USDT) return no data from `transfer()`, so this decode fails and the entire XCM transfer is rejected with `XcmError::FailedToTransactAsset`, even though the underlying on-chain transfer succeeded.

## Finding Description
Both functions perform a `bare_call` to the target contract and, when the call did not revert, unconditionally attempt `IERC20::transferCall::abi_decode_returns_validate(&return_value.data)`; any decode error (including one caused by empty return data) is mapped to `Err(XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode"))` on withdraw, and the analogous `Err((what, XcmError::FailedToTransactAsset(...)))` on deposit. [4](#0-3) [5](#0-4) 

Crucially, the ERC20 contract address is not resolved through any privileged registry: `ERC20Matcher` directly converts the `AccountKey20 { key, .. }` junction of the XCM asset `Location` into the target `H160` contract address [6](#0-5) , matching any local `AccountKey20` location [2](#0-1) . This design is confirmed by the feature's own PR documentation, which states the corresponding `transfer` function is called on "the smart contract whose address is `key`" — i.e., the asset id itself is the contract address, with no governance-gated onboarding step. Consequently, any unprivileged user who can construct/execute an XCM program can select an arbitrary deployed ERC20 contract (including a non-standard, no-return-value one) as the target of a `withdraw_asset_with_surplus`/`deposit_asset_with_surplus` call.

## Impact Explanation
Any user-controlled XCM asset `Location` with an `AccountKey20` junction pointing at a non-standard ERC20 contract (no `bool` return on `transfer()`) will unconditionally fail `withdraw_asset_with_surplus`/`deposit_asset_with_surplus`, producing `XcmError::FailedToTransactAsset` even though the on-chain transfer succeeded. This is a denial of service for legitimate cross-consensus transfers of any such asset through this transactor — a real and foreseeable scenario given that USDT-style non-compliant tokens are widely deployed.

## Likelihood Explanation
High feasibility: since the target contract address is derived directly from the asset `Location`'s `AccountKey20` junction rather than a governance-controlled registry, an unprivileged user constructing an XCM program referencing a deployed non-standard ERC20 contract can trigger this path without any privileged onboarding step, for any contract deployed via `pallet-revive`.

## Recommendation
Adopt SafeERC20-style semantics in both functions: when the call did not revert, treat empty `return_value.data` as success, and only require a strict `bool` decode when return data is non-empty (treating an explicit `false` decode as failure). Apply this consistently to both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus`.

## Proof of Concept
1. Deploy via `pallet-revive` a minimal ERC20-like contract whose `transfer(address,uint256)` updates balances but returns no data (mirroring mainnet USDT).
2. Construct an XCM asset `Location` of the form `(0, [AccountKey20 { key: <contract_address>, network }])`, which `ERC20Matcher`/`IsLocalAccountKey20` will match directly to that contract address.
3. Submit an XCM program invoking `withdraw_asset_with_surplus`/`deposit_asset_with_surplus` for that asset (e.g., a deposit to a beneficiary).
4. Observe `bare_call` succeeds (`did_revert()` is `false`) but `return_value.data` is empty; `IERC20::transferCall::abi_decode_returns_validate` fails, producing `XcmError::FailedToTransactAsset("ERC20 contract result couldn't decode")` despite the underlying transfer having succeeded, permanently blocking XCM transfers for that asset.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L132-139)
```rust
/// `Contains<Location>` implementation that matches locations with no parents,
/// a `PalletInstance` and an `AccountKey20` junction.
pub struct IsLocalAccountKey20;
impl Contains<Location> for IsLocalAccountKey20 {
	fn contains(location: &Location) -> bool {
		matches!(location.unpack(), (0, [AccountKey20 { .. }]))
	}
}
```

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L141-160)
```rust
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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L270-305)
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
		} else {
			tracing::debug!(target: "xcm::transactor::erc20::deposit", ?result, "Error");
			// This error could've been duplicate smart contract, out of gas, etc.
			// If the issue is gas, there's nothing the user can change in the XCM
			// that will make this work since there's a hardcoded gas limit.
			Err((what, XcmError::FailedToTransactAsset("ERC20 contract execution errored")))
		}
```
