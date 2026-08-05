### Title
ERC20 Asset Transactor blindly trusts declared transfer amount instead of verifying actual balance delta, breaking accounting for fee-on-transfer/rebasing ERC20 tokens - (File: `cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs`)

### Summary
The `ERC20Transactor` used to bridge XCM fungible-asset semantics onto `pallet-revive` ERC20 contracts assumes that an ERC20 `transfer()` call always moves exactly the requested `amount`. It never checks the actual token balance before/after the call. Any user can deploy an arbitrary ERC20 contract and have it treated as a first-class XCM fungible asset (no allow-list/registration gate), so a rebasing or fee-on-transfer ERC20 will desynchronize the XCM-side "credit" tracked in `AssetsInHolding` from the real balance actually held by the `TransfersCheckingAccount`, exactly analogous to the Cork Protocol M-6 finding where rebasing `Ra`/`Pa` balances diverge from the state-tracked accounting.

### Finding Description
`withdraw_asset_with_surplus` withdraws tokens from a user by calling ERC20 `transfer(checking_address, amount)` and then unconditionally mints an `Erc20Credit(amount)` into the XCM holding register, using the *requested* `amount`, not the amount actually received by the checking account: [1](#0-0) 

Symmetrically, `deposit_asset_with_surplus` calls ERC20 `transfer(beneficiary, amount)` from the checking account using the amount taken from holding, again without verifying the checking account's actual balance or the beneficiary's actual received amount: [2](#0-1) 

The `Erc20Credit` type used for imbalance accounting is a "minimal imbalance tracking type" that explicitly does not enforce real balance constraints — the comment says the actual balance constraints are enforced by the ERC20 contract itself, but the code never re-derives the credited amount from an actual balance check: [3](#0-2) 

Critically, there is no gatekeeping on which ERC20 contracts can be used this way. The matcher for this transactor, `ERC20Matcher`, matches *any* local `AccountKey20` location with no allow-list or issuance-based check (unlike `TrustBackedAssets`/`ForeignAssets`, which require registration and a non-zero-issuance check): [4](#0-3) [5](#0-4) 

This is the same root-cause pattern as the Cork Protocol report: the protocol's internal accounting (state-tracked `Ra`/`Pa` balances in Cork; `Erc20Credit` amount in holding here) assumes a 1:1, exact-transfer token model and never syncs with the token's real balance semantics, which breaks for tokens with rebasing or fee-on-transfer behavior.

### Impact Explanation
Any user can deploy their own ERC20 contract via `pallet-revive` whose `transfer()` implements a fee-on-transfer or rebase mechanism (e.g., deducting a percentage on each transfer, or where balances fluctuate independent of transfer calls). When such a token is referenced in an XCM program:
- On `withdraw_asset_with_surplus`, the checking account receives less than `amount`, yet the XCM holding register is credited with the full nominal `amount`. That inflated credit can then be deposited to any beneficiary (including cross-chain via further XCM instructions), effectively minting XCM-recognized value not actually backed by the checking account's real balance.
- Because the `TransfersCheckingAccount` is shared across all users of a given ERC20 asset, this creates an insolvency in the shared checking account: subsequent legitimate depositors may find the checking account under-collateralized, causing `deposit_asset_with_surplus` calls to fail (denial of service) or, if the ERC20 allows it, to succeed while draining balance backing other users' claims (loss of funds for other holders of the same asset).

### Likelihood Explanation
High for any registered ERC20 that has non-standard transfer semantics, and reachable by an unprivileged user because:
- No permissioning/registration is required for an address to be treated as a valid ERC20 XCM asset — `ERC20Matcher`/`IsLocalAccountKey20` matches any `AccountKey20` location.
- Any user can deploy an arbitrary contract to `pallet-revive` and immediately use it through XCM `WithdrawAsset`/`DepositAsset` instructions targeting their own contract address.
- No off-chain governance step (like asset registration in `pallet-assets`) gates this pathway.

### Recommendation
`ERC20Transactor::withdraw_asset_with_surplus` and `deposit_asset_with_surplus` should read the ERC20 `balanceOf` of the relevant account before and after the `transfer` call and credit/debit `AssetsInHolding` with the actual observed balance delta, rather than trusting the caller-specified `amount`. Alternatively, explicitly document and enforce (e.g., via an allow-list of vetted ERC20 contracts) that only standard, non-rebasing, non-fee-on-transfer ERC20 tokens can be registered for use with this transactor.

### Proof of Concept
1. Deploy an ERC20 contract via `pallet-revive` whose `transfer(to, amount)` deducts a 5% fee, sending `amount * 0.95` to `to` and burning/redirecting the remainder, while still returning `true` and encoding the call so `abi_decode_returns_validate` reports success.
2. Craft an XCM program with `WithdrawAsset` for `{ parents: 0, interior: [AccountKey20 { key: <contract address> }] }` with amount `X` from the attacker's own account — matched unconditionally by `ERC20Matcher`/`IsLocalAccountKey20` (`cumulus/parachains/runtimes/assets/common/src/lib.rs:132-161`).
3. `withdraw_asset_with_surplus` (`erc20_transactor.rs:150-216`) transfers nominal `X` to `TransfersCheckingAccount`, but the checking account's real ERC20 balance only increases by `0.95 * X`; the XCM holding register nevertheless credits `Erc20Credit(X)`.
4. Follow with `DepositAsset` to a second (attacker-controlled) beneficiary for amount `X`; `deposit_asset_with_surplus` (`erc20_transactor.rs:225-306`) instructs the checking account to transfer `X` out, which either fails once accumulated shortfall exceeds available balance (DoS for all users of that asset) or succeeds by spending balance that should have backed other users' deposits (fund loss for other holders), demonstrating the accounting/state mismatch driven by non-standard ERC20 transfer semantics.

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

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L159-203)
```rust
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L225-266)
```rust
	fn deposit_asset_with_surplus(
		what: AssetsInHolding,
		who: &Location,
		_context: Option<&XcmContext>,
	) -> Result<Weight, (AssetsInHolding, XcmError)> {
		tracing::trace!(
			target: "xcm::transactor::erc20::deposit",
			?what, ?who,
		);
		defensive_assert!(what.len() == 1, "Trying to deposit more than one asset!");
		// Check we handle this asset.
		let maybe = what
			.fungible_assets_iter()
			.next()
			.and_then(|asset| Matcher::matches_fungibles(&asset).ok());
		let (asset_contract_id, amount) = match maybe {
			Some(inner) => inner,
			None => return Err((what, MatchError::AssetNotHandled.into())),
		};
		let who = match AccountIdConverter::convert_location(who) {
			Some(inner) => inner,
			None => return Err((what, MatchError::AccountIdConversionFailed.into())),
		};
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L132-161)
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

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L177-246)
```rust
pub type ForeignFungiblesTransactor = FungiblesAdapter<
	// Use this fungibles implementation:
	ForeignAssets,
	// Use this currency when it is a fungible asset matching the given location or name:
	ForeignAssetsConvertedConcreteId,
	// Convert an XCM Location into a local account id:
	LocationToAccountId,
	// Our chain's account ID type (we can't get away without mentioning it explicitly):
	AccountId,
	// We don't need to check teleports here.
	NoChecking,
	// The account to use for tracking teleports.
	CheckingAccount,
>;

/// `AssetId`/`Balance` converter for `PoolAssets`.
pub type PoolAssetsConvertedConcreteId =
	assets_common::PoolAssetsConvertedConcreteId<PoolAssetsPalletLocation, Balance>;

/// Means for transacting asset conversion pool assets on this chain.
pub type PoolFungiblesTransactor = FungiblesAdapter<
	// Use this fungibles implementation:
	PoolAssets,
	// Use this currency when it is a fungible asset matching the given location or name:
	PoolAssetsConvertedConcreteId,
	// Convert an XCM Location into a local account id:
	LocationToAccountId,
	// Our chain's account ID type (we can't get away without mentioning it explicitly):
	AccountId,
	// We only want to allow teleports of known assets. We use non-zero issuance as an indication
	// that this asset is known.
	LocalMint<parachains_common::impls::NonZeroIssuance<AccountId, PoolAssets>>,
	// The account to use for tracking teleports.
	CheckingAccount,
>;

parameter_types! {
	/// Taken from the real gas and deposits of a standard ERC20 transfer call.
	pub const ERC20TransferGasLimit: Weight = Weight::from_parts(500_000_000_000, 10 * 1024 * 1024);
	pub const ERC20TransferStorageDepositLimit: Balance = 10_200_000_000;
	pub ERC20TransfersCheckingAccount: AccountId = PalletId(*b"py/revch").into_account_truncating();
	pub DapBufferAccount: AccountId = pallet_dap::Pallet::<Runtime>::buffer_account();
}

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
