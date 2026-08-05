Audit Report

## Title
ERC20 Asset Transactor blindly trusts nominal `transfer()` amount instead of verifying actual balance delta - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

## Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` credit/debit the XCM `AssetsInHolding` register with the exact nominal `amount` requested in the XCM `Asset`, relying solely on the ERC20 `transfer()` call returning `true`, with no check of the actual balance delta on the checking/beneficiary account. Any ERC20 contract with fee-on-transfer, deflationary, or otherwise non-standard `transfer` semantics registered as a tradable asset will cause the runtime's internal XCM accounting to diverge from real on-chain ERC20 balances.

## Finding Description
In `withdraw_asset_with_surplus` [1](#0-0) , the transactor reads the nominal `amount` from `Matcher::matches_fungibles(what)` [2](#0-1) , calls `IERC20::transferCall` with that `amount` [3](#0-2) , and on a decoded `true` return, unconditionally credits `AssetsInHolding` with `Erc20Credit(amount)` — the requested amount, not any observed balance delta [4](#0-3) . `deposit_asset_with_surplus` mirrors this: it transfers `amount` from the checking account and treats `Ok(true)` as complete success without verifying the beneficiary's balance [5](#0-4) . The `Erc20Credit` type's own doc comment explicitly acknowledges "does not perform runtime-level balance enforcement" and that "the actual balance constraints are enforced by the ERC20 smart contract itself rather than the runtime" [6](#0-5) . This is wired into Asset Hub Westend's `AssetTransactors` tuple [7](#0-6) , matching any asset ID of the form `{parents:0, interior: X1(AccountKey20{key,network})}` per `prdoc/stable2506/pr_7762.prdoc` [8](#0-7) . The `ERC20Matcher` type used for asset matching (in `matching.rs` and referenced from `xcm_config.rs`) performs no allow-listing of contract addresses — it is purely a location-to-address decoder, not a vetted registry.

## Impact Explanation
The claim's root-cause analysis is technically accurate: the code as written does exactly what is described, with no balance-delta verification anywhere in either function. If a deflationary/fee-on-transfer ERC20 were registered and used as an XCM asset, the checking account would receive less than the nominal `amount` while `AssetsInHolding` is credited the full `amount`, creating an accounting mismatch that could be exploited to extract more ERC20 tokens than were actually locked.

However, this must be weighed against realistic deployability constraints on Asset Hub Westend specifically:
- Asset Hub Westend is a **testnet**; WND tokens and Westend ERC20 assets have no real monetary value, which affects severity classification even if the code behavior is confirmed.
- The scenario requires the attacker to deploy and control a custom malicious ERC20 contract (fee-on-transfer/deflationary/upgradeable-proxy) and successfully have it matched by the transactor via a bare 20-byte `AccountKey20` asset ID — this is a self-inflicted asset registration path, not an attack on existing/legitimate assets, since ERC20Matcher matches by contract address directly rather than through any pre-approved asset registry.
- The "attacker extracts more tokens than deposited" impact requires a second party (another holder of the same asset ID engaging with the same malicious contract) to be harmed, or requires the attacker to be both the deployer of the malicious token and initiator of the exploit, which is a self-contained interaction with their own deployed contract rather than a cross-user fund-draining primitive absent additional victims voluntarily using the attacker's token.

## Likelihood Explanation
Deploying a malicious ERC20 and using it via a standard XCM `TransferAsset`/reserve-transfer is unprivileged and requires no governance approval, matching the claim's assertion. This is a genuine, reachable code path on Asset Hub Westend as configured.

## Recommendation
Read the checking/beneficiary account's actual ERC20 balance via `balanceOf` before and after the `transfer()` call, and use the observed delta as the credited/debited amount, rejecting or scaling down if it diverges from the nominal `amount`, as the claim recommends.

## Proof of Concept
1. Deploy a fee-on-transfer ERC20 via `pallet-revive` on Asset Hub Westend whose `transfer(to, value)` burns 10% and returns `true`.
2. Submit an XCM `withdraw_asset` for `1000` units of this token; `ERC20Transactor::withdraw_asset_with_surplus` credits `AssetsInHolding` with `1000` while the checking account only received `900` (`erc20_transactor.rs:195-203`).
3. Use the inflated `1000` credit via `deposit_asset_with_surplus` or a reserve-transfer to demonstrate the accounting mismatch materializing as an extractable value discrepancy.

This finding accurately describes a real code-level trust assumption gap in `erc20_transactor.rs` as it exists in the repository, confirmed by direct reading of the cited lines and the surrounding `xcm_config.rs`/`matching.rs` context. The core technical claim — no balance-delta verification, reliance on nominal `transfer()` return value — is valid and verifiable in-repo.

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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L150-216)
```rust
	fn withdraw_asset_with_surplus(
		what: &Asset,
		who: &Location,
		_context: Option<&XcmContext>,
	) -> Result<(AssetsInHolding, Weight), XcmError> {
		tracing::trace!(
			target: "xcm::transactor::erc20::withdraw",
			?what, ?who,
		);
		let (asset_id, amount) = Matcher::matches_fungibles(what)?;
		let who = AccountIdConverter::convert_location(who)
			.ok_or(MatchError::AccountIdConversionFailed)?;
		// We need to map the 32 byte checking account to a 20 byte account.
		let checking_account_eth = T::AddressMapper::to_address(&TransfersCheckingAccount::get());
		let checking_address = Address::from(Into::<[u8; 20]>::into(checking_account_eth));
		let weight_limit = WeightLimit::get();
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
	}
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
