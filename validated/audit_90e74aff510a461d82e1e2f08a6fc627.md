This confirms a genuine, in-scope analog to the Polkaswap finding, live in `asset-hub-westend-runtime` via `ERC20Transactor` (added per `prdoc/stable2506/pr_7762.prdoc`).

### Title
ERC20 Asset Transactor blindly trusts nominal `transfer()` amount instead of verifying actual balance delta - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` credit/debit the XCM `AssetsInHolding` register with the exact nominal `amount` requested in the XCM `Asset`, based solely on the ERC20 `transfer()` call returning `true`. Neither function checks the token's actual balance before/after the call. Any ERC20 contract registered as a tradable asset (matched by `assets_common::ERC20Matcher` on Asset Hub Westend, wired in `cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs:222-246`) that implements fee-on-transfer, deflationary, or otherwise non-standard `transfer` semantics (including via a proxy upgrade, matching the original Polkaswap report's exact scenario) will cause the runtime's internal XCM accounting to diverge from the real on-chain ERC20 balance.

### Finding Description
In `withdraw_asset_with_surplus` (`cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs:150-216`), the transactor:
1. Reads the requested `amount` from the XCM `Asset` via `Matcher::matches_fungibles(what)` [1](#0-0) .
2. Calls `IERC20::transferCall { to: checking_address, value: EU256::from(amount) }` on the arbitrary registered contract [2](#0-1) .
3. On a decoded `true` return value, unconditionally mints `AssetsInHolding::new_from_fungible_credit(what.id.clone(), Box::new(Erc20Credit(amount)))` — crediting the *requested* `amount`, not the amount actually received by the checking account [3](#0-2) .

Symmetrically, `deposit_asset_with_surplus` (lines 225-306) transfers `amount` out of the checking account and treats `Ok(true)` as full success, again without verifying the beneficiary actually received `amount` [4](#0-3) .

The `Erc20Credit` imbalance type itself documents this design gap explicitly: "This type implements the necessary imbalance accounting traits but does not perform runtime-level balance enforcement... the actual balance constraints are enforced by the ERC20 smart contract itself rather than the runtime" [5](#0-4) . This is precisely the trust assumption the Polkaswap/Trail of Bits report flags as unsafe: the runtime assumes `transfer(amount)` moves exactly `amount`, with no tracking of upgradeable/proxy contract semantics changes and no pause mechanism for such tokens.

This transactor is live in the `AssetTransactors` tuple on Asset Hub Westend [6](#0-5) , matching any asset ID of the form `{parents:0, interior: X1(AccountKey20{key,network})}` as an ERC20 contract address, per `prdoc/stable2506/pr_7762.prdoc` [7](#0-6) . There is no allow-list, no upgrade/proxy detection, and no governance approval gate before an ERC20 becomes usable in XCM transfers — any user can deploy or use an ERC20 contract via `pallet-revive` and immediately move it through XCM.

### Impact Explanation
If a deflationary/fee-on-transfer (or upgraded-to-deflationary proxy) ERC20 is used as an XCM asset:
- On `withdraw_asset_with_surplus`, the checking account receives less than `amount`, but the XCM executor's holding register is credited the full nominal `amount`. That inflated `AssetsInHolding` value can then be reserve-transferred/deposited elsewhere (e.g., minted as a foreign asset on another chain, or deposited to a beneficiary via `deposit_asset_with_surplus`), letting an attacker extract more ERC20 tokens than were actually locked in the checking account — directly mirroring the Polkaswap "attacker receives more tokens than deposited" exploit.
- Repeated cycles can drain the checking account's real ERC20 balance while inflated claims persist in the XCM system, causing accounting insolvency and fund loss for other holders of the same asset ID.

### Likelihood Explanation
No privileged role is required. Any user can:
1. Deploy (or already control) an ERC20 contract via `pallet-revive` that is deflationary, fee-on-transfer, or a proxy that can later be upgraded to such semantics.
2. Use it in a normal XCM `TransferAsset`/reserve-transfer through `PolkadotXcm`, which is a standard unprivileged extrinsic path on Asset Hub Westend.
3. Trigger the accounting mismatch on the very first transfer — no governance approval or allow-listing step currently gates which ERC20 contracts can be used with this transactor.

### Recommendation
Do not trust the nominal `amount` from the ERC20 `transfer()` return value. Before crediting/debiting `AssetsInHolding`, read the checking/beneficiary account's actual balance via `balanceOf` before and after the call and use the observed delta as the credited/debited amount (reject or scale down if it differs from `amount`). Longer term, maintain an explicit allow-list of vetted, non-upgradeable ERC20 contracts eligible for this transactor, and re-verify/pause an asset if its bytecode or proxy implementation changes, consistent with the original report's recommendation for automated upgrade tracking and consensus-gated re-approval.

### Proof of Concept
1. Deploy an ERC20 contract via `pallet-revive` on Asset Hub Westend whose `transfer(to, value)` burns 10% of `value` and only moves 90% to `to`, but still returns `true`.
2. Send an XCM that withdraws `1000` units of this token from account `A` via `ERC20Transactor::withdraw_asset_with_surplus`: the checking account's real ERC20 balance increases by only `900`, but `AssetsInHolding` is credited `1000` (`erc20_transactor.rs:195-203`).
3. Use that `1000`-credited holding to have `deposit_asset_with_surplus` pay out `1000` units to beneficiary `B` (or reserve-transfer `1000` to a remote chain as a foreign asset). The checking account only ever received `900`, so this either drains the checking account for other users' funds or fails silently while the remote chain records `1000` as backed, creating a lasting accounting mismatch — the same "receive more tokens than deposited" outcome described in the original Polkaswap report.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L73-78)
```rust
/// A minimal imbalance tracking type that holds an ERC20 token amount.
///
/// This type implements the necessary imbalance accounting traits but does not perform
/// runtime-level balance enforcement. It's used to track ERC20 token amounts within XCM
/// asset holdings, where the actual balance constraints are enforced by the ERC20 smart
/// contract itself rather than the runtime.
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L159-159)
```rust
		let (asset_id, amount) = Matcher::matches_fungibles(what)?;
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L166-169)
```rust
		// To withdraw, we actually transfer to the checking account.
		// We do this using the solidity ERC20 interface.
		let data =
			IERC20::transferCall { to: checking_address, value: EU256::from(amount) }.abi_encode();
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L195-203)
```rust
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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L253-280)
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
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L240-246)
```rust
pub type AssetTransactors = (
	FungibleTransactor,
	FungiblesTransactor,
	ForeignFungiblesTransactor,
	UniquesTransactor,
	ERC20Transactor,
);
```

**File:** prdoc/stable2506/pr_7762.prdoc (L8-14)
```text
    description: |
      This PR introduces an Asset Transactor for dealing with ERC20 tokens and adds it to Asset Hub
      Westend.
      This means asset ids of the form `{ parents: 0, interior: X1(AccountKey20 { key, network }) }` will be
      matched by this transactor and the corresponding `transfer` function will be called in the
      smart contract whose address is `key`.
      If your chain uses `pallet-revive`, you can support ERC20s as well by adding the transactor, which lives
```
