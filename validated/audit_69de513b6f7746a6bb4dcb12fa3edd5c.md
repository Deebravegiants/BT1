Audit Report

## Title
Fee-on-transfer / non-standard ERC20 tokens cause XCM holding-register accounting mismatch in `ERC20Transactor` - (File: cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs)

## Summary
`ERC20Transactor` is a `TransactAsset` implementation wired into `asset-hub-westend`'s `AssetTransactors` tuple, letting the XCM executor move arbitrary Solidity ERC20 tokens deployed on `pallet-revive` by calling their `transfer` function. Both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus` credit/treat the operation as fully successful based solely on the `transfer` call's boolean return value, without verifying the actual balance delta at `TransfersCheckingAccount`, so fee-on-transfer, deflationary, or rebasing ERC20 tokens can desynchronize the XCM holding register from the real tokens actually escrowed.

## Finding Description
In `withdraw_asset_with_surplus`, the transactor calls `IERC20::transferCall{to: checking_address, value: amount}` via `pallet_revive::Pallet::<T>::bare_call`, and if the call does not revert and decodes to `true`, it unconditionally credits `AssetsInHolding` with the *requested* `amount` rather than the amount that actually reached `TransfersCheckingAccount` [1](#0-0) [2](#0-1) . The symmetric `deposit_asset_with_surplus` has the same pattern outbound: it transfers `amount` from the checking account to the beneficiary and, as long as `transfer` returns `true`, treats the deposit as fully successful without confirming the beneficiary's balance actually increased by `amount` [3](#0-2) .

Critically, this transactor is confirmed to be live in `asset-hub-westend`'s XCM configuration: `ERC20Transactor` is defined as a type alias parameterized with `assets_common::ERC20Matcher` and `ERC20TransfersCheckingAccount`, and is included as the last element of the `AssetTransactors` tuple, which is assigned to `XcmConfig::AssetTransactor` [4](#0-3) [5](#0-4) . This confirms the transactor is reachable in a live runtime, not a mock/test helper.

The `Matcher` used, `ERC20Matcher`, is defined as `MatchedConvertedConcreteId<H160, u128, IsLocalAccountKey20, AccountKey20ToH160, TryConvertInto>` [6](#0-5) , and `IsLocalAccountKey20` matches *any* local `Location` consisting of a single `AccountKey20` junction [7](#0-6) . This means there is no allow-list: any 20-byte address (i.e., any deployed `pallet-revive` contract address, attacker-controlled or otherwise) is accepted as a valid ERC20 asset for this transactor, confirming the permissionless attack surface described in the report.

The only accounting object used for the credited amount, `Erc20Credit`, is a thin imbalance wrapper around a `u128` with no independent balance verification — it simply tracks whatever amount it is constructed with [8](#0-7) , so there is no secondary safeguard downstream that would catch a mismatch between the requested and actually-transferred amount.

This matches the reported vulnerability class: the code checks only "did the call revert" and "did it return `true`," not the real balance delta, which breaks for tokens implementing fee-on-transfer, rebasing, or burn-on-transfer logic.

## Impact Explanation
Because `AssetsInHolding` is credited with the nominal `amount` rather than the amount actually escrowed in `TransfersCheckingAccount`, a malicious ERC20 contract that charges an internal fee/burn on `transfer` (while still returning `true`) can cause the XCM executor's internal holding register to believe more value is backed by the checking account than actually exists there. Subsequent `deposit_asset_with_surplus` calls against that inflated holding value will attempt to move funds out of `TransfersCheckingAccount` that were never fully deposited, potentially draining balances belonging to unrelated users/assets sharing the same checking account, or causing unpredictable transfer failures once the account's real balance is exhausted. The nominal (not actual) amount also propagates onward through the wider XCM message (fees, reserve calculations, multi-hop transfers), compounding the desync. This is a concrete accounting-integrity bug reachable through a live, non-privileged XCM asset-transactor path in an in-scope Polkadot SDK runtime.

## Likelihood Explanation
Exploitation requires only that an attacker deploy an ERC20 contract with non-standard transfer semantics on `pallet-revive` — a permissionless action available to any account — and then route it through XCM as a fungible asset. The `ERC20Matcher` configuration confirmed in `asset-hub-westend` accepts any local `AccountKey20` location without restriction, so no allow-listing or governance step gates which contracts can be matched. This removes the main uncertainty flagged in the original report (whether the live `Matcher` config restricts this to vetted contracts) — it does not. The attack is repeatable and requires no privileged role, satisfying the requirement that a normal external user can trigger the issue.

## Recommendation
In both `withdraw_asset_with_surplus` and `deposit_asset_with_surplus`, query the `TransfersCheckingAccount`'s (or beneficiary's) ERC20 balance immediately before and after the `transfer` call via a `balanceOf` bare-call, and use the observed balance delta — not the requested `amount` — when constructing `AssetsInHolding` credits or when deciding whether the deposit fully succeeded. If the delta is smaller than requested, either fail the operation (returning any partially-transferred funds accounting appropriately) or credit only the amount actually received.

## Proof of Concept
1. Deploy a Solidity ERC20 contract on `pallet-revive` whose `transfer` function burns/deducts e.g. 10% of `value` internally but still returns `true` on success.
2. Because `ERC20Matcher` (`IsLocalAccountKey20` + `AccountKey20ToH160`) matches any local `AccountKey20` location with no allow-list, this contract's address is automatically accepted as a valid asset ID by `ERC20Transactor::withdraw_asset_with_surplus`/`deposit_asset_with_surplus` in `asset-hub-westend`'s `xcm_config.rs`.
3. Initiate an XCM `WithdrawAsset` for `amount = 1000` of this token from an account holding the token (e.g., via `pallet_xcm`'s local `execute` extrinsic, available to any signed user, or via a reserve-transfer flow that routes through this transactor).
4. `ERC20Transactor::withdraw_asset_with_surplus` calls `transfer(checking_account, 1000)`; the contract actually moves only 900 to the checking account but returns `true`.
5. `AssetsInHolding` is credited with `Erc20Credit(1000)` at line 200 of `erc20_transactor.rs`, even though `TransfersCheckingAccount`'s real ERC20 balance only increased by 900 — an unbacked 100-unit surplus now exists in the executor's internal holding register, which can be deposited to any destination via subsequent XCM instructions, unbacked by real tokens in the checking account.

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L73-107)
```rust
/// A minimal imbalance tracking type that holds an ERC20 token amount.
///
/// This type implements the necessary imbalance accounting traits but does not perform
/// runtime-level balance enforcement. It's used to track ERC20 token amounts within XCM
/// asset holdings, where the actual balance constraints are enforced by the ERC20 smart
/// contract itself rather than the runtime.
struct Erc20Credit(u128);
impl UnsafeConstructorDestructor<u128> for Erc20Credit {
	fn unsafe_clone(&self) -> Box<dyn ImbalanceAccounting<u128>> {
		Box::new(Erc20Credit(self.0))
	}
	fn forget_imbalance(&mut self) -> u128 {
		let amount = self.0;
		self.0 = 0;
		amount
	}
}

impl UnsafeManualAccounting<u128> for Erc20Credit {
	fn saturating_subsume(&mut self, mut other: Box<dyn ImbalanceAccounting<u128>>) {
		let amount = other.forget_imbalance();
		self.0 = self.0.saturating_add(amount);
	}
}

impl ImbalanceAccounting<u128> for Erc20Credit {
	fn amount(&self) -> u128 {
		self.0
	}
	fn saturating_take(&mut self, amount: u128) -> Box<dyn ImbalanceAccounting<u128>> {
		let new = self.0.min(amount);
		self.0 = self.0 - new;
		Box::new(Erc20Credit(new))
	}
}
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L150-169)
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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L253-298)
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

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L429-434)
```rust
impl xcm_executor::Config for XcmConfig {
	type RuntimeCall = RuntimeCall;
	type XcmSender = XcmRouter;
	type XcmEventEmitter = PolkadotXcm;
	type AssetTransactor = AssetTransactors;
	type OriginConverter = XcmOriginToTransactDispatchOrigin;
```

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

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L157-160)
```rust
/// [`xcm_executor::traits::MatchesFungibles`] implementation that matches
/// ERC20 tokens.
pub type ERC20Matcher =
	MatchedConvertedConcreteId<H160, u128, IsLocalAccountKey20, AccountKey20ToH160, TryConvertInto>;
```
