## Analog Vulnerability Found

### Title
Emergency-pause (`pallet-tx-pause` / `pallet-safe-mode`) can be bypassed for NFT/asset transfers via XCM asset-transactor adapters - (`File: polkadot/xcm/xcm-builder/src/nonfungibles_adapter.rs`)

### Summary
The LensHub finding is a "missing modifier on one transfer path" bug: `whenNotPaused` was enforced on every *external* function, but the internal ERC-721 transfer hook was not, so governance's emergency pause could not stop NFT transfers. Substrate's analog to `whenNotPaused` is `pallet_tx_pause`/`pallet_safe_mode`, which work by filtering `RuntimeCall`s at `Dispatchable::dispatch` time. The same class of gap exists here: XCM's non‑fungible asset-transactor adapters call the underlying `Transfer`/`Mutate` trait methods on pallets such as `pallet-nfts`/`pallet-uniques` **directly**, never going through `Dispatchable::dispatch`, so they are invisible to `TxPause`/`SafeMode`.

### Finding Description
Substrate's pause primitives only intercept calls made through the standard extrinsic dispatch path:

- `RuntimeCall::dispatch` checks `OriginTrait::filter_call` (built from `frame_system::Config::BaseCallFilter`, which `pallet_tx_pause`/`pallet_safe_mode` compose into) before performing the actual mutation: [1](#0-0) 
- `pallet_tx_pause` stores a `PausedCalls` map keyed by `(pallet_name, call_name)` and is enforced purely through this `Contains<RuntimeCall>` filter: [2](#0-1) 
- A real runtime configuration shows exactly the "pause everything except a whitelist" pattern used for incident response: [3](#0-2) 

However, `pallet-nfts`'s own transfer logic has **no** pause/global-halt check at all — only per-item/per-collection lock settings: [4](#0-3) . Governance-level pausing is expected to be enforced entirely at the dispatch layer (via `TxPause`/`SafeMode` pausing the `Nfts::transfer` call).

The `Transfer` trait implementation that XCM uses to move NFTs calls `do_transfer` directly, with no filter check: [5](#0-4) 

XCM's asset-transactor adapters invoke this trait method directly from `transfer_asset`, completely outside `Dispatchable::dispatch`: [6](#0-5) [7](#0-6) 

Notably, the XCM executor's own `Transact` instruction handler *does* explicitly filter dispatched calls through `Config::SafeCallFilter` before calling `Config::CallDispatcher::dispatch`: [8](#0-7) . This proves the pattern is known and applied to `Transact`, but the same protection was never wired into `TransferAsset`/`DepositAsset`/`WithdrawAsset` handling for non‑fungibles (or fungibles) — exactly the asymmetry described in the LensHub report ("all *external* functions have the modifier... the transfer function doesn't").

Inbound XCM messages are processed by `pallet_message_queue`/`cumulus_pallet_xcmp_queue` via `ProcessXcmMessage`, which calls `XcmExecutor::execute` directly rather than through the extrinsic pipeline: [9](#0-8) [10](#0-9) . So even a paused chain keeps servicing inbound XCM messages, and any `TransferAsset`/`ReserveAssetDeposited`/`ReceiveTeleportedAsset` instruction touching an NFT collection reaches `do_transfer` unfiltered.

### Impact Explanation
If a runtime's governance pauses `Nfts::transfer` (or `Uniques::transfer`) via `pallet_tx_pause`, or activates `pallet_safe_mode`, in response to an incident (e.g. a compromised account holding valuable NFTs, or an exploit in a marketplace pallet), an attacker who already controls the affected NFT can still move it out of governance's reach by routing the transfer through an XCM reserve-transfer/teleport to another chain — the `NonFungiblesAdapter`/`NonFungibleAdapter::transfer_asset` path never checks `TxPause`/`SafeMode` state. This defeats the entire purpose of the emergency pause, identical in effect to the cited LensHub scenario (governance wants to halt NFT transfers but cannot, because one transfer path was left unguarded).

### Likelihood Explanation
This requires: (1) a runtime configuring `pallet-nfts`/`pallet-uniques` (or an equivalent non-fungible implementation) as a `TransactAsset` behind `NonFungibleAdapter`/`NonFungiblesAdapter` for cross-chain NFT transfer support, and (2) `pallet_xcm`'s public extrinsics (`limited_reserve_transfer_assets`, `transfer_assets`, etc.) or inbound XCM from another chain being available to move that asset class. Any unprivileged holder of the NFT can trigger this the moment governance pauses only the plain `Nfts::transfer` extrinsic — which is the natural, minimal-blast-radius incident response, making the bypass realistic rather than purely theoretical.

### Recommendation
Add an explicit pause/filter check inside the shared `Transfer`/`Mutate` non-fungible(s) trait implementations (or inside the XCM adapters themselves) that consults the same authority `TxPause`/`SafeMode` use, mirroring the `SafeCallFilter` check already performed for the `Transact` instruction in `xcm-executor/src/lib.rs`. Alternatively, document and enforce that any pause/safe-mode intended to halt asset transfers must also disable the relevant `TransactAsset` adapters/XCM instructions for that asset class, not just the extrinsic call.

### Proof of Concept
1. Configure a runtime with `pallet-nfts` and `NonFungiblesAdapter`/`NonFungibleAdapter` wired as `TransactAsset` for XCM (as is standard for NFT-enabled system/parachains).
2. Governance detects an incident and pauses `Nfts::transfer` via `TxPause::pause(origin, ("Nfts","transfer"))`, or activates `pallet_safe_mode`.
3. Confirm `Nfts::transfer` extrinsic now fails with `CallFiltered` (matches existing test pattern in `substrate/frame/tx-pause/src/tests.rs::can_pause_specific_call`).
4. The NFT owner instead calls `pallet_xcm::limited_reserve_transfer_assets` (or an inbound XCM message from another chain triggers `WithdrawAsset`/`DepositAsset`/`TransferAsset`) targeting the same collection/item.
5. Observe that `NonFungiblesAdapter::transfer_asset` → `pallet_nfts::Pallet::transfer` (trait impl) → `do_transfer` succeeds, moving the NFT despite the active pause/safe-mode — demonstrating the bypass.

### Citations

**File:** substrate/frame/support/procedural/src/construct_runtime/expand/call.rs (L169-183)
```rust
		impl #scrate::__private::Dispatchable for RuntimeCall {
			type RuntimeOrigin = RuntimeOrigin;
			type Config = RuntimeCall;
			type Info = #scrate::dispatch::DispatchInfo;
			type PostInfo = #scrate::dispatch::PostDispatchInfo;
			fn dispatch(self, origin: RuntimeOrigin) -> #scrate::dispatch::DispatchResultWithPostInfo {
				if !<Self::RuntimeOrigin as #scrate::traits::OriginTrait>::filter_call(&origin, &self) {
					return ::core::result::Result::Err(
						#system_path::Error::<#runtime>::CallFiltered.into()
					);
				}

				#scrate::traits::UnfilteredDispatchable::dispatch_bypass_filter(self, origin)
			}
		}
```

**File:** substrate/frame/tx-pause/src/lib.rs (L279-288)
```rust
impl<T: pallet::Config> Contains<<T as frame_system::Config>::RuntimeCall> for Pallet<T>
where
	<T as frame_system::Config>::RuntimeCall: GetCallMetadata,
{
	/// Return whether the call is allowed to be dispatched.
	fn contains(call: &<T as frame_system::Config>::RuntimeCall) -> bool {
		let CallMetadata { pallet_name, function_name } = call.get_call_metadata();
		!Pallet::<T>::is_paused_unbound(pallet_name.into(), function_name.into())
	}
}
```

**File:** substrate/bin/node/runtime/src/lib.rs (L247-268)
```rust
/// Calls that can bypass the safe-mode pallet.
pub struct SafeModeWhitelistedCalls;
impl Contains<RuntimeCall> for SafeModeWhitelistedCalls {
	fn contains(call: &RuntimeCall) -> bool {
		match call {
			RuntimeCall::System(_) | RuntimeCall::SafeMode(_) | RuntimeCall::TxPause(_) => true,
			_ => false,
		}
	}
}

/// Calls that cannot be paused by the tx-pause pallet.
pub struct TxPauseWhitelistedCalls;
/// Whitelist `Balances::transfer_keep_alive`, all others are pauseable.
impl Contains<RuntimeCallNameOf<Runtime>> for TxPauseWhitelistedCalls {
	fn contains(full_name: &RuntimeCallNameOf<Runtime>) -> bool {
		match (full_name.0.as_slice(), full_name.1.as_slice()) {
			(b"Balances", b"transfer_keep_alive") => true,
			_ => false,
		}
	}
}
```

**File:** substrate/frame/nfts/src/features/transfer.rs (L46-80)
```rust
	pub fn do_transfer(
		collection: T::CollectionId,
		item: T::ItemId,
		dest: T::AccountId,
		with_details: impl FnOnce(
			&CollectionDetailsFor<T, I>,
			&mut ItemDetailsFor<T, I>,
		) -> DispatchResult,
	) -> DispatchResult {
		// Retrieve collection details.
		let collection_details =
			Collection::<T, I>::get(&collection).ok_or(Error::<T, I>::UnknownCollection)?;

		// Ensure the item is not locked.
		ensure!(!T::Locker::is_locked(collection, item), Error::<T, I>::ItemLocked);

		// Ensure the item is not transfer disabled on the system level attribute.
		ensure!(
			!Self::has_system_attribute(&collection, &item, PalletAttributes::TransferDisabled)?,
			Error::<T, I>::ItemLocked
		);

		// Retrieve collection config and check if items are transferable.
		let collection_config = Self::get_collection_config(&collection)?;
		ensure!(
			collection_config.is_setting_enabled(CollectionSetting::TransferableItems),
			Error::<T, I>::ItemsNonTransferable
		);

		// Retrieve item config and check if the item is transferable.
		let item_config = Self::get_item_config(&collection, &item)?;
		ensure!(
			item_config.is_setting_enabled(ItemSetting::Transferable),
			Error::<T, I>::ItemLocked
		);
```

**File:** substrate/frame/nfts/src/impl_nonfungibles.rs (L412-419)
```rust
impl<T: Config<I>, I: 'static> Transfer<T::AccountId> for Pallet<T, I> {
	fn transfer(
		collection: &Self::CollectionId,
		item: &Self::ItemId,
		destination: &T::AccountId,
	) -> DispatchResult {
		Self::do_transfer(*collection, *item, destination.clone(), |_, _| Ok(()))
	}
```

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

**File:** polkadot/xcm/xcm-builder/src/nonfungible_adapter.rs (L50-73)
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
		let instance = Matcher::matches_nonfungible(what).ok_or(MatchError::AssetNotHandled)?;
		let destination = AccountIdConverter::convert_location(to)
			.ok_or(MatchError::AccountIdConversionFailed)?;
		NonFungible::transfer(&instance, &destination).map_err(|e| {
			tracing::debug!(target: LOG_TARGET, ?e, ?instance, ?destination, "Failed to transfer non-fungible asset");
			XcmError::FailedToTransactAsset(e.into())
		})?;
		Ok(what.clone())
	}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L1096-1133)
```rust
					target: "xcm::process_instruction::transact",
					?call,
					"Processing call",
				);

				if !Config::SafeCallFilter::contains(&message_call) {
					tracing::trace!(
						target: "xcm::process_instruction::transact",
						"Call filtered by `SafeCallFilter`",
					);

					return Err(XcmError::NoPermission)
				}

				let dispatch_origin =
					Config::OriginConverter::convert_origin(origin.clone(), origin_kind).map_err(
						|_| {
							tracing::trace!(
								target: "xcm::process_instruction::transact",
								?origin,
								?origin_kind,
								"Failed to convert origin to a local origin."
							);

							XcmError::BadOrigin
						},
					)?;

				tracing::trace!(
					target: "xcm::process_instruction::transact",
					origin = ?dispatch_origin,
					call = ?message_call,
					"Dispatching call with origin",
				);

				let weight = message_call.get_dispatch_info().call_weight;
				let maybe_actual_weight =
					match Config::CallDispatcher::dispatch(message_call, dispatch_origin) {
```

**File:** polkadot/xcm/xcm-builder/src/process_xcm_message.rs (L35-99)
```rust
impl<
		MessageOrigin: Into<Location> + FullCodec + MaxEncodedLen + Clone + Eq + PartialEq + TypeInfo + Debug,
		XcmExecutor: ExecuteXcm<Call>,
		Call: Decode + GetDispatchInfo,
	> ProcessMessage for ProcessXcmMessage<MessageOrigin, XcmExecutor, Call>
{
	type Origin = MessageOrigin;

	/// Process the given message, using no more than the remaining `weight` to do so.
	fn process_message(
		message: &[u8],
		origin: Self::Origin,
		meter: &mut WeightMeter,
		id: &mut XcmHash,
	) -> Result<bool, ProcessMessageError> {
		let versioned_message = VersionedXcm::<Call>::decode_all_with_depth_limit(
			MAX_XCM_DECODE_DEPTH,
			&mut &message[..],
		)
		.map_err(|e| {
			tracing::trace!(
				target: LOG_TARGET,
				?e,
				"`VersionedXcm` failed to decode",
			);

			ProcessMessageError::Corrupt
		})?;
		let message = Xcm::<Call>::try_from(versioned_message).map_err(|_| {
			tracing::trace!(
				target: LOG_TARGET,
				"Failed to convert `VersionedXcm` into `xcm::prelude::Xcm`!",
			);

			ProcessMessageError::Unsupported
		})?;
		let pre = XcmExecutor::prepare(message, Weight::MAX).map_err(|_| {
			tracing::trace!(
				target: LOG_TARGET,
				"Failed to prepare message.",
			);

			ProcessMessageError::Unsupported
		})?;
		// The worst-case weight:
		let required = pre.weight_of();
		if !meter.can_consume(required) {
			tracing::trace!(
				target: LOG_TARGET,
				"Xcm required {required} more than remaining {}",
				meter.remaining(),
			);

			return Err(ProcessMessageError::Overweight(required));
		}

		let (consumed, result) = match XcmExecutor::execute(origin.into(), pre, id, Weight::zero())
		{
			Outcome::Complete { used } => {
				tracing::trace!(
					target: LOG_TARGET,
					"XCM message execution complete, used weight: {used}",
				);
				(used, Ok(true))
			},
```

**File:** cumulus/parachains/runtimes/people/people-westend/src/lib.rs (L326-347)
```rust
impl pallet_message_queue::Config for Runtime {
	type RuntimeEvent = RuntimeEvent;
	#[cfg(feature = "runtime-benchmarks")]
	type MessageProcessor = pallet_message_queue::mock_helpers::NoopMessageProcessor<
		cumulus_primitives_core::AggregateMessageOrigin,
	>;
	#[cfg(not(feature = "runtime-benchmarks"))]
	type MessageProcessor = xcm_builder::ProcessXcmMessage<
		AggregateMessageOrigin,
		xcm_executor::XcmExecutor<XcmConfig>,
		RuntimeCall,
	>;
	type Size = u32;
	// The XCMP queue pallet is only ever able to handle the `Sibling(ParaId)` origin:
	type QueueChangeHandler = NarrowOriginToSibling<XcmpQueue>;
	type QueuePausedQuery = NarrowOriginToSibling<XcmpQueue>;
	type HeapSize = sp_core::ConstU32<{ 103 * 1024 }>;
	type MaxStale = sp_core::ConstU32<8>;
	type ServiceWeight = MessageQueueServiceWeight;
	type IdleMaxServiceWeight = MessageQueueServiceWeight;
	type WeightInfo = weights::pallet_message_queue::WeightInfo<Runtime>;
}
```
