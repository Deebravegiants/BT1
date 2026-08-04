## Analysis: ERC20-backed XCM asset transactor trusts unverified `transfer()` return value (analog of Sherlock M-01)

The Sherlock bug is a classic "trust the requested amount, not the actual balance delta" accounting flaw. I found a structurally identical pattern in the ERC20 XCM asset transactor added to Asset Hub, where the internal XCM bookkeeping (`AssetsInHolding`) is populated using the *requested* transfer amount rather than a verified balance change, and — critically — the assets eligible for this treatment are **not curated at all**, unlike Sherlock's admin-vetted whitelist.

### Title
Unverified/unauthenticated ERC20 accounting in `ERC20Transactor` allows non-standard tokens to desynchronize XCM holding bookkeeping - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` move ERC20 tokens by calling the token's Solidity `transfer()` function and treat a `true` boolean return as proof that exactly `amount` moved. The XCM holding register (`AssetsInHolding`/`Erc20Credit`) is then credited/debited with the *requested* `amount`, never the actual balance delta. Any AccountKey20-shaped `Location` is accepted as a valid "asset" with no allow-list, so any unprivileged user can permissionlessly deploy a non-standard ERC20 (fee-on-transfer, rebasing, or one that unconditionally returns `true`) via `pallet-revive` and immediately reference it from XCM.

### Finding Description
`ERC20Matcher` (and the `Contains<Location>` gate it uses) match *any* local `AccountKey20` location as a valid fungible asset id, with no registry/curation check: [1](#0-0) 

`withdraw_asset_with_surplus` withdraws by calling `IERC20::transfer` to the checking account and, on a `true` return, unconditionally constructs holding credit equal to the requested `amount` — not the observed balance change: [2](#0-1) 

`deposit_asset_with_surplus` mirrors this on the deposit side, transferring `amount` from the checking account and trusting the boolean return without verifying the beneficiary's balance actually increased by `amount`: [3](#0-2) 

This is the exact root cause pattern from the Sherlock report: the system's internal bookkeeping (here, XCM's `AssetsInHolding`/`Erc20Credit` imbalance tracker, introduced by the imbalance-accounting refactor) assumes the external token contract behaves like a "standard" ERC20 where `transfer(amount)` moves exactly `amount`. Because `pallet-revive` contract deployment is permissionless and the matcher performs no allow-listing, an attacker can supply their own malicious/non-standard token contract and directly control the semantics of `transfer()` — e.g., always return `true` without moving balance, or apply a fee/rebase — causing the XCM-side accounting to diverge from real token custody at the `TransfersCheckingAccount`.

### Impact Explanation
The confirmed, code-level impact is a bookkeeping desynchronization between the ERC20 contract's real balances and the XCM `AssetsInHolding` credit created for the operation — the same invariant break judged Medium in the original Sherlock report. Whether this escalates to direct value theft depends on whether the fictitious holding credit can be converted into value outside the attacker's own worthless token (e.g., via a reserve-based cross-chain transfer where a destination parachain mints a wrapped representation trusting Asset Hub's "reserve" bookkeeping for that asset id, or via any AMM/pool pallet that accepts the ERC20 location as tradeable collateral). I was not able to confirm within the available context whether `pallet-asset-conversion` on Asset Hub Westend currently permits `AccountKey20` ERC20 locations as poolable assets, or whether a destination chain treats this ERC20 as reserve-backed for cross-chain minting — these would be the concrete value-extraction sinks, and their existence should be verified before treating this as more than a local accounting inconsistency. Absent such a sink, impact is limited to the attacker manipulating accounting entirely within assets they themselves define (low real-world value), analogous to Sherlock's own sponsor argument that severity depends on whether "standard" tokens are curated — and here there is explicitly **no curation at all**, which is a materially worse posture than the original Sherlock system.

### Likelihood Explanation
High reachability, uncertain exploitability: any unprivileged account can deploy a contract via `pallet-revive` (no permission required) and submit an XCM program (`pallet_xcm::execute`, permissionless for signed origins) referencing that contract's address as an asset location — both preconditions are trivially satisfiable by an unprivileged attacker, as demonstrated by the existing test suite exercising exactly this contract-address-as-asset-id pattern (`smart_contract_does_not_return_bool_fails`, `non_existent_erc20_will_error`, etc. in `cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs`). However, I could not confirm an unprivileged, reachable path that turns the resulting fictional holding credit into real, transferable value beyond the attacker's own token contract; without that confirmed sink, this should be treated as a state-integrity/accounting-invariant issue rather than a proven fund-theft vulnerability.

### Recommendation
- Require the transactor to read the actual balance of the source/destination account (`balanceOf`) before and after the `transfer()` call and use the observed delta as the `AssetsInHolding` amount, rather than trusting the requested `amount` — mirroring the "check actual balance change" mitigation cited in the original Sherlock report.
- Alternatively/additionally, gate which `AccountKey20` locations are eligible to be used as XCM assets behind an explicit, governance-curated allow-list rather than accepting any syntactically valid `AccountKey20` location.
- Audit downstream consumers (asset-conversion pools, reserve-transfer/bridging configuration) to confirm none of them treat ERC20-backed holding credits as fungible collateral without the same balance-delta verification.

### Proof of Concept
1. As any unprivileged account, deploy a Solidity-compatible contract via `pallet-revive` implementing `IERC20` whose `transfer()` always returns `true` without actually debiting the caller's internal balance (or applies a fee/rebase on transfer).
2. Submit `pallet_xcm::execute` with an XCM program: `WithdrawAsset((AccountKey20 { key: <malicious_contract> }, amount: X))`, using the attacker's own signed origin.
3. Observe (per the existing pattern verified in `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs:185-208`) that `ERC20Transactor::withdraw_asset_with_surplus` credits `AssetsInHolding` with `Erc20Credit(X)` purely because the malicious contract returned `true`, regardless of whether the `TransfersCheckingAccount` actually received `X` tokens.
4. Chain a `DepositAsset`/reserve-transfer instruction in the same XCM program and confirm the holding credit of `X` is spent as if it were fully backed, with no on-chain check that the checking account's real ERC20 balance changed by `X`.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L132-159)
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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L270-298)
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
```
