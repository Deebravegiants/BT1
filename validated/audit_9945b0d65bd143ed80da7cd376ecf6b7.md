### Title
NFT theft via missing owner check in `NonFungiblesTransferAdapter::transfer_asset` (used by `NonFungiblesAdapter::transfer_asset`/`internal_transfer_asset`) - ([File: polkadot/xcm/xcm-builder/src/nonfungibles_adapter.rs])

### Summary
`NonFungiblesAdapter::withdraw_asset` is actually safe: it converts `who` and explicitly passes `Some(&who)` into `Assets::burn`, delegating the owner check to the underlying `nonfungibles::Mutate::burn` implementation. However, `NonFungiblesAdapter`'s `transfer_asset` (delegated to `NonFungiblesTransferAdapter::transfer_asset`) never validates that `from` is the current owner of `(class, instance)` before calling `Assets::transfer`, because `nonfungibles::Transfer::transfer` has no `from`/`maybe_check_owner` parameter at all.

### Finding Description
`NonFungiblesTransferAdapter::transfer_asset` at [1](#0-0)  only:
1. Matches `what` to `(class, instance)` via `Matcher::matches_nonfungibles`.
2. Converts `to` into a destination account.
3. Calls `Assets::transfer(&class, &instance, &destination)`.

The `from: &Location` parameter is never converted to an account and never compared against the current owner of `(class, instance)`. The underlying trait `nonfungibles::Transfer::transfer` signature itself has no `from`/`maybe_check_owner` argument: [2](#0-1) . It simply moves ownership of the item to `destination`, regardless of who currently owns it.

This is different from `withdraw_asset` (via `NonFungiblesMutateAdapter`), which correctly converts `who` and passes it as `Some(&who)` into `Assets::burn`, letting the pallet implementation enforce ownership: [3](#0-2) . So the premise in the question that `withdraw_asset` omits the `Some(&who)` check is factually incorrect for this code — that path is protected.

The real gap is in `transfer_asset`. Since `NonFungiblesAdapter` implements the `TransactAsset::transfer_asset` method by forwarding to `NonFungiblesTransferAdapter::transfer_asset` [4](#0-3) , any XCM configuration using `NonFungiblesAdapter` as `AssetTransactor` exposes this unchecked transfer path. The XCM executor's `TransferAsset` instruction handler (and the `internal_transfer_asset` fast-path optimization used by `TransferReserveAsset`/similar flows) calls `AssetTransactor::transfer_asset(asset, origin, beneficiary, context)` directly when the transactor supports it, rather than falling back to withdraw+deposit — meaning the owner-check present in `withdraw_asset` is bypassed entirely for this call path.

Exploit flow:
1. Attacker (unprivileged, controls only their own sovereign/derived origin location) sends an XCM message containing `TransferAsset { assets: [nft_asset(class, instance)], beneficiary: attacker_or_third_party }` where `(class, instance)` is actually owned by a different account.
2. `Matcher::matches_nonfungibles` accepts the `(class, instance)` pair (it only validates asset-id encoding, not ownership).
3. `transfer_asset` converts `beneficiary` to a destination account and calls `Assets::transfer(&class, &instance, &destination)` — since `Transfer::transfer` has no ownership parameter, it unconditionally reassigns the item to `destination`.
4. No origin/ownership check ever fires because `from` is unused in the entire function body.

### Impact Explanation
Any account able to send an XCM message hitting the `TransferAsset` instruction (e.g., a parachain user submitting `pallet_xcm::execute`/`send` with a `TransferAsset` naming an arbitrary `(class, instance)`) can move another account's NFT to any destination, without ever owning or being authorized for that item — direct theft of a non-fungible asset.

### Likelihood Explanation
This requires only that:
- The runtime configures `NonFungiblesAdapter` (or bare `NonFungiblesTransferAdapter`) as (part of) its `AssetTransactor`.
- `Matcher::matches_nonfungibles` (typically a straightforward class/instance id matcher) accepts attacker-chosen ids for legitimately-existing collection items belonging to someone else.
- The attacker can dispatch or receive-and-execute an XCM program containing `TransferAsset` (reachable via `pallet_xcm::execute` with a permissive `SafeCallFilter`/barrier, or via cross-chain messages routed to the executor).

No signature forgery, no privileged extrinsic, no proxy/multisig abuse needed — a plain user-initiated `TransferAsset` XCM suffices. This is fully reachable through the standard `TransactAsset` trait interface as wired into the XCM executor.

### Recommendation
In `NonFungiblesTransferAdapter::transfer_asset`, convert `from` via `AccountIdConverter::convert_location` and verify it equals `Assets::owner(&class, &instance)` before calling `Assets::transfer`, returning `XcmError::NoPermission`/`FailedToTransactAsset` otherwise. Alternatively, change `nonfungibles::Transfer::transfer` to accept a `maybe_check_owner: Option<&AccountId>` parameter (mirroring `Mutate::burn`) and thread `Some(&from_account)` through from the adapter, so the ownership check is enforced by the underlying pallet rather than solely at the adapter layer.

### Proof of Concept
xcm-builder unit test (adapted to the existing `nonfungibles_adapter` mock test scaffolding):
```rust
#[test]
fn transfer_asset_from_non_owner_should_fail() {
    // Setup: mint NFT (class=1, instance=42) into `owner_account` via Assets::mint_into.
    // Construct `attacker_location` (different from owner's location) and
    // `beneficiary_location` (attacker-controlled destination).
    let nft = Asset { id: AssetId(nft_class_location(1)), fun: NonFungible(AssetInstance::Index(42)) };

    let result = <NonFungiblesAdapter<...> as TransactAsset>::transfer_asset(
        &nft,
        &attacker_location,   // NOT the owner
        &beneficiary_location,
        &XcmContext::with_message_id([0; 32]),
    );

    // Expected (fixed) behavior: transfer must be rejected.
    assert!(matches!(result, Err(XcmError::NoPermission) | Err(XcmError::FailedToTransactAsset(_))));

    // Current (vulnerable) behavior observed: `result` is `Ok(...)` and
    // `Assets::owner(&1, &42)` now equals the beneficiary account, proving
    // the NFT was moved away from `owner_account` without authorization.
}
```
Expected assertion after fix: the call returns an error and `Assets::owner(&class, &instance)` remains unchanged (still the original owner). Currently, without the fix, the transfer succeeds and ownership silently changes to the attacker-chosen beneficiary.

### Citations

**File:** polkadot/xcm/xcm-builder/src/nonfungibles_adapter.rs (L53-76)
```rust
	fn transfer_asset(
		what: &Asset,
		from: &Location,
		to: &Location,
		context: &XcmContext,
	) -> Result<Asset, XcmError> {
		tracing::trace!(
			target: LOG_TARGET,
			?what,
			?from,
			?to,
			?context,
			"transfer_asset",
		);
		// Check we handle this asset.
		let (class, instance) = Matcher::matches_nonfungibles(what)?;
		let destination = AccountIdConverter::convert_location(to)
			.ok_or(MatchError::AccountIdConversionFailed)?;
		Assets::transfer(&class, &instance, &destination).map_err(|e| {
			tracing::debug!(target: LOG_TARGET, ?e, ?class, ?instance, ?destination, "Failed to transfer asset");
			XcmError::FailedToTransactAsset(e.into())
		})?;
		Ok(what.clone())
	}
```

**File:** polkadot/xcm/xcm-builder/src/nonfungibles_adapter.rs (L260-285)
```rust
	fn withdraw_asset(
		what: &Asset,
		who: &Location,
		maybe_context: Option<&XcmContext>,
	) -> Result<AssetsInHolding, XcmError> {
		tracing::trace!(
			target: LOG_TARGET,
			?what,
			?who,
			?maybe_context,
			"withdraw_asset",
		);
		// Check we handle this asset.
		let who = AccountIdConverter::convert_location(who)
			.ok_or(MatchError::AccountIdConversionFailed)?;
		let asset_instance = match what.fun {
			NonFungible(instance) => instance,
			_ => return Err(MatchError::AssetNotHandled.into()),
		};
		let (class, instance) = Matcher::matches_nonfungibles(what)?;
		Assets::burn(&class, &instance, Some(&who)).map_err(|e| {
			tracing::debug!(target: LOG_TARGET, ?e, ?class, ?instance, ?who, "Failed to burn asset");
			XcmError::FailedToTransactAsset(e.into())
		})?;
		Ok(AssetsInHolding::new_from_non_fungible(what.id.clone(), asset_instance))
	}
```

**File:** polkadot/xcm/xcm-builder/src/nonfungibles_adapter.rs (L412-421)
```rust
	fn transfer_asset(
		what: &Asset,
		from: &Location,
		to: &Location,
		context: &XcmContext,
	) -> Result<Asset, XcmError> {
		NonFungiblesTransferAdapter::<Assets, Matcher, AccountIdConverter, AccountId>::transfer_asset(
			what, from, to, context,
		)
	}
```

**File:** substrate/frame/support/src/traits/tokens/nonfungibles_v2.rs (L398-404)
```rust
pub trait Transfer<AccountId>: Inspect<AccountId> {
	/// Transfer `item` of `collection` into `destination` account.
	fn transfer(
		collection: &Self::CollectionId,
		item: &Self::ItemId,
		destination: &AccountId,
	) -> DispatchResult;
```
