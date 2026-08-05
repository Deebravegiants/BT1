This confirms the code matches the security claim exactly, with no allow-list gate on `ERC20Matcher` and no balance-delta verification in either `withdraw_asset_with_surplus` or `deposit_asset_with_surplus`, both of which credit/transfer the fixed `amount` based solely on the boolean return value of `IERC20::transferCall`. The wiring into `AssetTransactors` on Asset Hub Westend is also confirmed as claimed.

Audit Report

## Title
Missing balance verification in `ERC20Transactor` allows accounting desync with fee-on-transfer/deflationary ERC20 tokens - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

## Summary
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` credit/transfer the exact `amount` requested by the XCM message, relying solely on the ERC20 `transfer()` call's boolean return value and non-revert status, without verifying the checking account's or beneficiary's actual balance delta. [1](#0-0)  Because `ERC20Matcher` accepts any local `AccountKey20` location unconditionally with no allow-list, any user can deploy a fee-on-transfer contract via `pallet-revive` and exploit this path. [2](#0-1) 

## Finding Description
On withdraw, `withdraw_asset_with_surplus` calls `IERC20::transferCall{ to: checking_address, value: amount }` on the arbitrary contract at `asset_id` obtained from `Matcher::matches_fungibles(what)`, and as long as the call does not revert and decodes to `true`, it unconditionally credits `AssetsInHolding` with the full requested `amount` via `Erc20Credit(amount)` — with no query of the checking account's actual balance before/after the call. [1](#0-0)  The matcher used, `ERC20Matcher`, is defined as `MatchedConvertedConcreteId<H160, u128, IsLocalAccountKey20, AccountKey20ToH160, TryConvertInto>`, where `IsLocalAccountKey20` matches any `Location` of the form `(0, [AccountKey20 { .. }])` with no allow-list or governance gate. [3](#0-2)  `ERC20Transactor` is wired into `AssetTransactors` on Asset Hub Westend's `xcm_config.rs`, alongside the other fungible/foreign-fungible transactors, making it reachable from ordinary XCM programs executed by any signed account. [4](#0-3)  The symmetric issue exists in `deposit_asset_with_surplus`, which transfers `amount` from the checking account to the beneficiary and treats a `true` return as full success without verifying the beneficiary's balance delta. [5](#0-4)  A fee-on-transfer/deflationary ERC20 contract that burns or fees a portion of the transferred value while still returning `true` will cause the XCM holding register (or beneficiary balance assumption) to diverge from the real on-chain ERC20 balance actually moved.

## Impact Explanation
Repeated withdraw operations against a fee-on-transfer contract create XCM holding credit not fully backed by the real balance increase in the checking account for that specific ERC20 asset. This divergence is isolated to the individual malicious ERC20 contract's accounting under the `ERC20Transactor`/checking-account model; it does not affect the accounting of `pallet-balances`, `pallet-assets`, or other unrelated asset classes, since the checking account balance for that ERC20 token is a value tracked entirely within the external contract, and the desync is confined to how much of that specific token's supply the pallet believes is backed at the checking account versus what is truly held there.

## Likelihood Explanation
No privileged role is required: any user can deploy a `pallet-revive` contract implementing `IERC20` with a fee-on-transfer/deflationary `transfer()` that still returns `true`, then submit an ordinary XCM program with `WithdrawAsset`/`DepositAsset` referencing that contract's address as an `AccountKey20` asset id, which `ERC20Matcher` accepts unconditionally per `IsLocalAccountKey20`. This is repeatable and requires no victim mistake or unrealistic assumption — it directly follows from the intended, documented behavior of the ERC20 transactor being permissionless for any deployed contract, as also stated in the PRDoc introducing this feature.

## Recommendation
In `withdraw_asset_with_surplus`, query the checking account's ERC20 balance immediately before and after the `transfer` call, and credit `AssetsInHolding` with the observed delta rather than the requested `amount`. Symmetrically, in `deposit_asset_with_surplus`, verify the beneficiary's balance delta matches the requested `amount`, failing/returning the shortfall to the holding register otherwise, rather than assuming a `true` return value implies an exact-amount transfer.

## Proof of Concept
1. Deploy a `pallet-revive` contract implementing `IERC20` whose `transfer(to, value)` burns/fees a percentage of `value` before crediting `to`, but still returns `true` on success.
2. Craft an XCM `Xcm(vec![WithdrawAsset(asset), ...])` where `asset` is `{ parents: 0, interior: X1(AccountKey20 { key: <contract_address>, network: None }) }` with `fun: Fungible(amount)`.
3. Execute the XCM via `pallet_xcm` from a signed account holding `amount` of the token on Asset Hub Westend.
4. Observe `ERC20Transactor::withdraw_asset_with_surplus` returns `Erc20Credit(amount)` in the holding register (per `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs` lines 197-203) even though the checking account's actual `balanceOf` increase is less than `amount`.
5. Repeat to show the cumulative credited amount for this asset diverges from and exceeds the checking account's real ERC20 balance.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L166-207)
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
				} else {
					tracing::debug!(target: "xcm::transactor::erc20::withdraw", "contract transfer failed");
					Err(XcmError::FailedToTransactAsset("ERC20 contract transfer failed"))
				}
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L248-298)
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
