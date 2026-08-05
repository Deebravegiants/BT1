### Title
ERC20Transactor::deposit_asset_with_surplus silently drops all but the first asset from a multi-asset Holding on success - (File: cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs)

### Summary
`ERC20Transactor::deposit_asset_with_surplus` only ever transfers the first fungible asset found in the `AssetsInHolding` it is given and then returns `Ok(surplus)`, discarding any remaining assets in `what` without depositing them or returning them as unspent. Because the XCM executor treats `Ok(...)` from a `TransactAsset` as full and successful consumption of `what`, any additional ERC20-backed assets present in the same `DepositAsset` batch are silently lost with no `AssetTrap` fallback and no error surfaced to the caller.

### Finding Description
The `TransactAsset` contract (both for a single implementor and for the tuple aggregation in `polkadot/xcm/xcm-executor/src/traits/transact_asset.rs`) requires that an implementation either (a) fully deposits everything in `what` and returns `Ok`, or (b) returns the *unconsumed* assets back in the `Err((unspent, error))` tuple so the tuple-of-transactors machinery can try the next transactor, or so the XCM executor can trap the unspent assets via `AssetTrap`. [1](#0-0) 

`ERC20Transactor::deposit_asset_with_surplus` violates this contract. It takes only `what.fungible_assets_iter().next()`, transfers that single asset via the ERC20 `transfer` call, and on success returns `Ok(surplus)` — dropping the rest of `what` entirely instead of returning it as unspent: [2](#0-1) [3](#0-2) 

The only guard against multi-asset input is `defensive_assert!(what.len() == 1, ...)`, which in release/production builds is a no-op (it only panics when defensive-check debug assertions are compiled in) and otherwise behaves as pure pass-through, i.e., it does not stop execution or change behavior in a normal validator/collator runtime. [4](#0-3) 

The comment above the function explicitly documents this as known, intentional behavior ("If multiple assets are present, only the first fungible asset will be deposited and the rest will be silently ignored"), confirming it is not a mocked/hypothetical edge case but an actual code path. [5](#0-4) 

`ERC20Transactor` is composed into the runtime's `AssetTransactors` tuple as the last element: [6](#0-5) 

Exploit flow:
1. An unprivileged actor (e.g., a user initiating a reserve-asset transfer from a chain the target chain trusts as reserve for ERC20-backed assets, or crafting a program executed via `pallet_xcm::execute`/incoming HRMP message with `ReserveAssetDeposited` for two ERC20-mapped assets, `ClearOrigin`, `DepositAsset{assets: Wild(All)/AllCounted(2), beneficiary}`) causes Holding to contain two ERC20-mapped fungible assets (`erc20A`, `erc20B`).
2. The XCM executor processes `DepositAsset`, takes the matching assets out of Holding into a `deposited: AssetsInHolding` set containing both `erc20A` and `erc20B`, and calls the tuple's `deposit_asset_with_surplus(deposited, beneficiary, ...)`.
3. Earlier tuple members (`FungibleTransactor`, `FungiblesTransactor`, `ForeignFungiblesTransactor`, `UniquesTransactor`) don't match ERC20 asset ids via `MatchesFungibles`, so they return `Err(AssetNotFound)` and pass `what` (both assets) unchanged to `ERC20Transactor`.
4. `ERC20Transactor::deposit_asset_with_surplus` takes only the first fungible asset (`erc20A`), successfully transfers it via the ERC20 contract call, and returns `Ok(surplus)` — `erc20B` is dropped from `what` and never returned as unspent.
5. The tuple's `deposit_asset_with_surplus` sees `Ok(...)` from `ERC20Transactor` and short-circuits/returns success for the whole batch, per the tuple semantics documented in `transact_asset.rs`.
6. The XCM executor believes the entire `DepositAsset` batch succeeded; no `AssetTrap` is invoked because no error/unspent assets were ever returned, so `erc20B`'s value is permanently unaccounted for — neither deposited to the beneficiary, nor trapped, nor returned to any origin.

### Impact Explanation
Concrete fund loss: whenever two or more ERC20-backed fungible assets are simultaneously present in Holding at the point `DepositAsset` (with `Wild(All)`/`AllCounted(n)`) is executed, only the first one is actually delivered to the beneficiary; the rest disappear from the system's accounting entirely (not deposited, not trapped, not returned), while the XCM executor and any calling extrinsic/message report success. This matches the scoped impact exactly: silent loss of a deposited asset without triggering the `AssetTrap` fallback.

### Likelihood Explanation
This is trivially reachable by any user who can cause two or more ERC20-backed assets to be simultaneously present in Holding before a `DepositAsset` (or the underlying `deposit_asset_with_surplus`/`transfer_asset_with_surplus` path). Multi-asset reserve transfers, or a crafted local/remote XCM program with two `ReserveAssetDeposited`s of ERC20-mapped assets followed by one `DepositAsset{Wild(All), beneficiary}`, are normal and directly reachable XCM constructs — this does not require any privileged origin, and the `defensive_assert!` provides no real-world protection in production builds. The bug is deterministic and fully repeatable whenever the precondition (2+ ERC20 assets in Holding at deposit time) is met.

### Recommendation
Rewrite `ERC20Transactor::deposit_asset_with_surplus` to either (a) iterate over all matching ERC20 fungible assets in `what`, depositing each and returning `Ok` only once all are successfully transferred, aggregating and returning any that fail/don't match as unspent in the `Err` branch, or (b) if genuinely intended to be single-asset only, reject (`Err((what, XcmError::FailedToTransactAsset(...)))`, returning the untouched `what`) whenever `what.len() != 1`, so the executor traps the assets instead of silently dropping them. Also make the `what.len() == 1` guard a hard, non-optional check (not just `defensive_assert!`) in all build profiles.

### Proof of Concept
xcm-emulator / integration test plan:
1. Configure a test runtime with `AssetTransactors = (..., ERC20Transactor)` and two distinct ERC20 contracts (`erc20A`, `erc20B`) both matched by `assets_common::ERC20Matcher`.
2. Fund the `ERC20TransfersCheckingAccount` with balances of both `erc20A` and `erc20B`.
3. Execute `Xcm([ReserveAssetDeposited(vec![erc20A_asset, erc20B_asset]), ClearOrigin, DepositAsset { assets: Wild(All), beneficiary }])` via `XcmExecutor::execute_xcm` (or `pallet_xcm::execute` from a signed origin, or as an incoming HRMP message from a trusted reserve).
4. Assert:
   - The outcome is `Outcome::Complete` (i.e., no error reported), demonstrating the false-success signal.
   - `beneficiary`'s `erc20A` balance increases by the deposited amount (first asset succeeds).
   - `beneficiary`'s `erc20B` balance is **unchanged** (second asset silently lost).
   - No `AssetTrap` event/storage entry exists for `erc20B` — proving the loss is untracked and unrecoverable, unlike the correct behavior where either both assets are deposited or the whole batch is trapped.

### Citations

**File:** polkadot/xcm/xcm-executor/src/traits/transact_asset.rs (L296-317)
```rust
	fn deposit_asset_with_surplus(
		mut what: AssetsInHolding,
		who: &Location,
		context: Option<&XcmContext>,
	) -> Result<Weight, (AssetsInHolding, XcmError)> {
		for_tuples!( #(
			match Tuple::deposit_asset_with_surplus(what, who, context) {
				Err((unspent, XcmError::AssetNotFound)) | Err((unspent, XcmError::Unimplemented)) => {
					what = unspent;
					// continue
				},
				r => return r,
			}
		)* );
		tracing::trace!(
			target: "xcm::TransactAsset::deposit_asset_with_surplus",
			?what,
			?who,
			?context,
			"did not deposit asset",
		);
		Err((what, XcmError::AssetNotFound))
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L218-243)
```rust
	/// Deposits assets from holding to a beneficiary account via ERC20 transfer.
	///
	/// Note: This implementation only handles a single fungible asset at a time. The
	/// `AssetsInHolding` parameter is required by the `TransactAsset` trait, but callers
	/// should ensure only one asset is passed. If multiple assets are present, only the
	/// first fungible asset will be deposited and the rest will be silently ignored.
	/// The `defensive_assert!` helps catch misuse during development.
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
```

**File:** cumulus/parachains/runtimes/assets/common/src/erc20_transactor.rs (L270-280)
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
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/xcm_config.rs (L239-246)
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
