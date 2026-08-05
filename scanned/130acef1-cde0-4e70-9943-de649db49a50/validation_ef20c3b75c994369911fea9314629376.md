### Title
`deposit_asset_with_surplus` trusts unverified ERC20 `transfer` return value, allowing attacker-controlled contracts to break checking-account/XCM-holding invariant - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor::deposit_asset_with_surplus` calls an arbitrary ERC20 contract's `transfer` via `pallet_revive::Pallet::bare_call` and treats the operation as fully successful solely based on the ABI-decoded boolean return value, never verifying that `ERC20TransfersCheckingAccount`'s on-chain balance actually decreased by `amount`. Because `assets_common::ERC20Matcher` matches *any* local `AccountKey20` location as a valid fungible asset with no registry/allow-list gate, an attacker can deploy and register (via matching, not privileged registration) a malicious ERC20 contract whose `transfer()` unconditionally returns `true` while performing no or partial value movement, causing the XCM executor to consider the deposit complete (no trap, no revert) while the checking account's real balance is left inconsistent with holding accounting.

### Finding Description
`deposit_asset_with_surplus` builds an `IERC20::transferCall` for `amount` from `ERC20TransfersCheckingAccount` to the beneficiary and dispatches it with `pallet_revive::Pallet::<T>::bare_call`: [1](#0-0) 

The only checks performed on the result are "did it revert" and "did it ABI-decode to `true`": [2](#0-1) 

There is no read of the checking account's balance before/after the call, and no cross-check that the contract's internal ledger for `ERC20TransfersCheckingAccount` actually decreased by `amount`. Since the transferred contract is entirely attacker-authored Solidity/PVM bytecode (called via `bare_call`), the attacker fully controls what `transfer()` does internally — it can simply return `true` while moving 0 or partial value, or even credit the beneficiary through a different internal mechanism unrelated to the checking account's balance.

Critically, there is no privileged registration gate preventing an attacker from getting their own contract matched by the transactor: `ERC20Matcher` matches *any* asset whose `AssetId` location is `(0, [AccountKey20 { .. }])`, with no allow-list: [3](#0-2) 

This differs fundamentally from `ForeignAssets`/`TrustBackedAssets`, which are gated by `pallet_assets` ownership/reserve configuration and the `TrustedReserves`/`TrustedTeleporters` XCM executor config seen in the runtime (`asset-hub-westend`/`asset-hub-rococo` `xcm_config.rs`). Those filters operate on `Location`-identified assets registered in `pallet_assets`; they do not gate the ERC20 `H160` matcher path at all, since the `AssetTransactors` tuple simply tries each transactor and `ERC20Transactor`/`ERC20Matcher` accepts any local `AccountKey20` id.

Exploit flow:
1. Attacker deploys `MaliciousERC20` implementing `transfer(address,uint256)` to always `return true` without decreasing the caller's tracked balance (or only decreasing it by a token amount smaller than requested).
2. Attacker triggers an XCM program (e.g., via `pallet_xcm::execute` locally, or a reserve-transfer/teleport instruction sequence) that results in `WithdrawAsset`/`DepositAsset` for asset id `(0, [AccountKey20 { key: MaliciousERC20_address }])` with amount `X`, routed through `ERC20Transactor`.
3. On `withdraw_asset_with_surplus`, the malicious contract can similarly fake success without real balance movement, letting the attacker credit `AssetsInHolding` with `X` without any real backing ever landing in `ERC20TransfersCheckingAccount` — see the identical unguarded pattern at `withdraw_asset_with_surplus`: [4](#0-3) 
4. On `deposit_asset_with_surplus`, using the same contract, the attacker can make the "checking account -> beneficiary" `transfer` call return `true` while retaining (or even duplicating) balance in the contract's internal ledger for the beneficiary, decoupling the ERC20 view from what the XCM executor believes was delivered from holding.
5. Because the executor only inspects the decoded boolean, `Ok(surplus)` is returned, the asset is dropped from `AssetsInHolding` as "delivered" (not trapped, no error), completing the XCM program successfully despite the checking account's real balance not moving by `amount`.

None of the runtime's XCM safeguards (`Barrier`, `IsReserve`/`TrustedReserves`, `IsTeleporter`/`TrustedTeleporters`) mitigate this, because those gates apply to `Location`-identified assets tracked by `pallet_assets`, not to the `H160`/`AccountKey20`-matched ERC20 path, which has no analogous registry check.

### Impact Explanation
This breaks the invariant that XCM holding/asset accounting must mirror actual on-chain ERC20 balance changes of `ERC20TransfersCheckingAccount`. An attacker who fully controls the target contract's `transfer` logic can make the runtime believe assets were correctly moved (withdrawn into or deposited out of the checking account) when they were not, enabling unbacked asset accounting on the XCM side while the EVM/ERC20 ledger diverges — a double-spend/mint-from-nothing primitive scoped specifically to ERC20-backed XCM asset flows through this transactor.

### Likelihood Explanation
Fully feasible and repeatable by any unprivileged user: deploying an arbitrary ERC20 contract via `pallet_revive` requires no special permission, and `ERC20Matcher` accepts any `AccountKey20` location as a matched asset with no allow-list or registration step gating the ERC20 transactor path. The attack only requires the attacker to author standard malicious Solidity/PVM `transfer` logic and issue a local or cross-chain XCM instruction referencing their contract's address as the asset id.

### Recommendation
Before returning `Ok(surplus)` (and similarly in `withdraw_asset_with_surplus`), read `ERC20TransfersCheckingAccount`'s ERC20 balance via a `balanceOf` call immediately before and after the `bare_call` to `transfer`, and require the observed delta to equal exactly `amount`; treat any mismatch (even with a `true` return) as `XcmError::FailedToTransactAsset`. Alternatively, gate which ERC20 contracts can be matched by `ERC20Matcher`/used with `ERC20Transactor` behind an explicit runtime-governed allow-list/registry, analogous to `pallet_assets`' owner-configured trusted reserves, so arbitrary attacker-deployed contracts cannot be used as XCM-recognized assets at all.

### Proof of Concept
Rust integration test (mock runtime with `pallet_revive` + `ERC20Transactor`):
1. Deploy `MaliciousERC20` with `transfer()` hard-coded to `return true` and never decrement the caller's balance mapping.
2. Fund `ERC20TransfersCheckingAccount` conceptually to `amount = X` in the contract's storage (or skip, to model zero-value transfer).
3. Record `MaliciousERC20.balanceOf(ERC20TransfersCheckingAccount)` = `B0`.
4. Call `ERC20Transactor::deposit_asset_with_surplus(AssetsInHolding{X of MaliciousERC20}, beneficiary_location, None)`.
5. Assert: `result.is_ok()` (current buggy behavior) yet `MaliciousERC20.balanceOf(ERC20TransfersCheckingAccount)` is unchanged (`B0`), and `MaliciousERC20.balanceOf(beneficiary)` did not increase by `X` — proving the XCM-reported success diverges from actual ERC20 accounting.
6. Expected fixed behavior: the call should return `Err((what, XcmError::FailedToTransactAsset(..)))` because the balance delta check fails, keeping the asset trapped/refunded instead of falsely credited.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L185-207)
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L253-266)
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L270-287)
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
