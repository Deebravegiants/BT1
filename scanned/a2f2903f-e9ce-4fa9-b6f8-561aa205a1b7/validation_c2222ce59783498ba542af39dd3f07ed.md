### Title
`XcmExecuteFilter` and `XcmReserveTransferFilter` are independently enforced, allowing users to bypass a `Nothing` reserve-transfer filter by crafting the equivalent program via `execute` - (File: `polkadot/xcm/pallet-xcm/src/lib.rs`)

### Summary
`Pallet::do_reserve_transfer_assets` (and its helpers `local_reserve_transfer_programs` / `destination_reserve_transfer_programs` / `remote_reserve_transfer_program`) gate the dedicated reserve-transfer extrinsics with `T::XcmReserveTransferFilter::contains(&(origin, assets))`, but the low-level `execute` extrinsic only checks `T::XcmExecuteFilter::contains(&(origin, xcm))`. Since these are two independent `Contains` implementations set by the runtime, a chain that sets `XcmReserveTransferFilter = Nothing` (to explicitly disallow acting as a reserve) while leaving `XcmExecuteFilter = Everything` allows an unprivileged signed user to reconstruct the same `WithdrawAsset`/`DepositReserveAsset` (or `InitiateReserveWithdraw`) program and submit it via `PolkadotXcm::execute`, fully bypassing the intended block.

### Finding Description
- `Config::XcmExecuteFilter` and `Config::XcmReserveTransferFilter` are declared as two separate, independently-configured associated types on `pallet_xcm::Config` (`polkadot/xcm/pallet-xcm/src/lib.rs:282` and `:292`).
- The `execute` extrinsic path only enforces `XcmExecuteFilter`: [1](#0-0) 
- The dedicated reserve-transfer path enforces `XcmReserveTransferFilter` in multiple helper functions before building the program, e.g. `do_reserve_transfer_assets`: [2](#0-1) 
and `local_reserve_transfer_programs` (the "local-reserve" case, where this chain becomes the reserve for a destination's assets): [3](#0-2) 
- Several shipped runtimes deliberately set `XcmReserveTransferFilter = Nothing` while `XcmExecuteFilter = Everything`, explicitly to prevent the chain from being used as a reserve, e.g. Bridge Hub Rococo/Westend and Collectives Westend: [4](#0-3) [5](#0-4) 
- Critically, the underlying `XcmExecutor` instruction handlers do **not** replicate the `XcmReserveTransferFilter` semantics. `DepositReserveAsset` (the "this chain becomes the reserve" instruction) has no `IsReserve`/filter gate at all — it just moves holdings into the destination's sovereign account and forwards the message: [6](#0-5) 
`InitiateReserveWithdraw`/`WithdrawAsset`-driven remote-reserve withdrawals are gated only by `Config::IsReserve` (a *different*, asset-trust check, unrelated to `XcmReserveTransferFilter`): [7](#0-6) 
- On Bridge Hub Rococo/Westend, `IsReserve = ()` (nothing is a trusted reserve) so remote-reserve-withdraw-style bypass is blocked by `IsReserve`, but this is coincidental — it protects against trusting a *foreign* reserve, not against *this chain* becoming a reserve via `DepositReserveAsset`, which has no equivalent barrier check. The `Barrier` (e.g. `WithComputedOrigin<(AllowTopLevelPaidExecutionFrom<Everything>, ...)>`) only gates *who* may execute and whether fees are paid — it is structurally origin/fee-based, not semantically aware of "reserve transfer" as a category, so it does not substitute for `XcmReserveTransferFilter`: [8](#0-7) 

Because of this gap, a signed user calling `PolkadotXcm::execute(origin, Xcm(vec![WithdrawAsset(local_assets), DepositReserveAsset{assets: Wild(All), dest, xcm}]), Weight::MAX)` on a chain configured with `XcmReserveTransferFilter = Nothing` but `XcmExecuteFilter = Everything` and `AllowTopLevelPaidExecutionFrom<Everything>` in its Barrier will have the local-reserve-style transfer executed, because none of `XcmExecuteFilter`, the `Barrier`, or `IsReserve` block `DepositReserveAsset` semantically the way `XcmReserveTransferFilter` was intended to.

### Impact Explanation
The scoped impact is a filter bypass: governance's decision to disable reserve-transfer functionality on a given chain (expressed via `XcmReserveTransferFilter = Nothing`, e.g. "this parachain is not meant as a reserve location") can be circumvented by unprivileged users through the `execute` extrinsic, as long as `XcmExecuteFilter` permits general execution (which is the common production configuration, since `execute` is meant for local reserve/teleport receive flows). This does not directly duplicate or steal assets (accounting inside `DepositReserveAsset`/`WithdrawAsset` is correct — the user spends their own local assets to accomplish it), but it defeats an intended architectural/governance control meant to prevent the chain from acting as an asset reserve, which can have downstream trust and accounting implications for destination chains that did not expect this chain to be a valid reserve for the transferred asset.

### Likelihood Explanation
Feasible and fully user-controlled: it requires only a signed origin able to satisfy `ExecuteXcmOrigin` (any local account under `SignedToAccountId32`), sufficient asset balance, and a runtime where `XcmExecuteFilter` is permissive (`Everything`, the common case) while `XcmReserveTransferFilter = Nothing`. This exact combination exists in-repo today (Bridge Hub Rococo/Westend, Collectives Westend). The only mitigating factor observed is `IsReserve = ()` on Bridge Hub, which blocks the *remote-reserve-withdraw* variant, but does not block the *local-reserve* (`DepositReserveAsset`) variant, since no check gates that instruction. Full confirmation that `DepositReserveAsset` succeeds unblocked on these specific runtimes (i.e., that the Barrier's `AllowTopLevelPaidExecutionFrom<Everything>` accepts a `WithdrawAsset`+`DepositReserveAsset` program from a signed local origin) was not independently executed/tested here — this should be validated with the emulator test below.

### Recommendation
Enforce `XcmReserveTransferFilter` semantics at the `XcmExecutor` level (or equivalently, add a check in `execute`) so that instructions equivalent to reserve transfers (`DepositReserveAsset`, `InitiateReserveWithdraw`, and `InitiateTransfer` with reserve-deposit/reserve-withdraw asset filters) are also subject to the same origin/asset `Contains` check as the dedicated `reserve_transfer_assets`/`transfer_assets` extrinsics, regardless of entry point (`execute` vs dedicated extrinsic). Alternatively, document explicitly that `XcmReserveTransferFilter = Nothing` provides no security guarantee unless `XcmExecuteFilter` is also restricted to disallow raw reserve-transfer-shaped programs, and audit/tighten `XcmExecuteFilter` on affected production runtimes (Bridge Hub Rococo/Westend, Collectives Westend, etc.) to reject such programs.

### Proof of Concept
xcm-emulator/integration test (using the existing test harness style at `cumulus/parachains/integration-tests/emulated/tests/assets/asset-hub-westend/src/tests/reserve_transfer.rs`), targeted at Bridge Hub Rococo or Westend:
1. Confirm `BridgeHubWestend`'s `pallet_xcm::Config::XcmReserveTransferFilter = Nothing` and `XcmExecuteFilter = Everything` (already true per `xcm_config.rs`).
2. Call the dedicated extrinsic:
```rust
let result = BridgeHubWestend::execute_with(|| {
    <BridgeHubWestend as BridgeHubWestendPallet>::PolkadotXcm::reserve_transfer_assets(
        signed_origin.clone(), bx!(dest.into()), bx!(beneficiary.into()), bx!(assets.into()), 0, Unlimited,
    )
});
assert_err!(result, ... Error::Filtered ...); // blocked by XcmReserveTransferFilter = Nothing
```
3. Construct and submit the equivalent low-level program via `execute`:
```rust
let xcm: Xcm<bridge_hub_westend_runtime::RuntimeCall> = Xcm(vec![
    WithdrawAsset(assets.clone().into()),
    DepositReserveAsset { assets: Wild(All), dest: dest.clone(), xcm: Xcm(vec![
        DepositAsset { assets: Wild(All), beneficiary },
    ])},
]);
let result = BridgeHubWestend::execute_with(|| {
    <BridgeHubWestend as BridgeHubWestendPallet>::PolkadotXcm::execute(
        signed_origin, bx!(VersionedXcm::from(xcm)), Weight::MAX,
    )
});
assert_ok!(result); // expected to succeed despite XcmReserveTransferFilter = Nothing
```
4. Assert the sender's local balance decreased and a `ReserveAssetDeposited`/onward XCM was queued to `dest`, proving the reserve-transfer effect occurred despite the dedicated filter blocking it — demonstrating the bypass.

### Citations

**File:** polkadot/xcm/pallet-xcm/src/lib.rs (L358-378)
```rust
			let outcome = (|| {
				let origin_location = T::ExecuteXcmOrigin::ensure_origin(origin)?;
				let mut hash = message.using_encoded(sp_io::hashing::blake2_256);
				let message = (*message).try_into().map_err(|()| {
					tracing::debug!(
						target: "xcm::pallet_xcm::execute", id=?hash,
						"Failed to convert VersionedXcm to Xcm",
					);
					Error::<T>::BadVersion
				})?;
				let value = (origin_location, message);
				ensure!(T::XcmExecuteFilter::contains(&value), Error::<T>::Filtered);
				let (origin_location, message) = value;
				Ok(T::XcmExecutor::prepare_and_execute(
					origin_location,
					message,
					&mut hash,
					max_weight,
					max_weight,
				))
			})()
```

**File:** polkadot/xcm/pallet-xcm/src/lib.rs (L2072-2074)
```rust
		ensure!(assets.len() <= MAX_ASSETS_FOR_TRANSFER, Error::<T>::TooManyAssets);
		let value = (origin_location, assets.into_inner());
		ensure!(T::XcmReserveTransferFilter::contains(&value), Error::<T>::Filtered);
```

**File:** polkadot/xcm/pallet-xcm/src/lib.rs (L2436-2457)
```rust
		let value = (origin, assets);
		ensure!(T::XcmReserveTransferFilter::contains(&value), Error::<T>::Filtered);
		let (_, assets) = value;

		// max assets is `assets` (+ potentially separately handled fee)
		let max_assets =
			assets.len() as u32 + if matches!(&fees, FeesHandling::Batched { .. }) { 0 } else { 1 };
		let assets: Assets = assets.into();
		let context = T::UniversalLocation::get();
		let mut reanchored_assets = assets.clone();
		reanchored_assets
			.reanchor(&dest, &context)
			.map_err(|e| {
				tracing::error!(target: "xcm::pallet_xcm::local_reserve_transfer_programs", ?e, ?dest, ?context, "Failed to re-anchor assets");
				Error::<T>::CannotReanchor
			})?;

		// XCM instructions to be executed on local chain
		let mut local_execute_xcm = Xcm(vec![
			// locally move `assets` to `dest`s local sovereign account
			TransferAsset { assets, beneficiary: dest.clone() },
		]);
```

**File:** cumulus/parachains/runtimes/bridge-hubs/bridge-hub-rococo/src/xcm_config.rs (L134-165)
```rust
pub type Barrier = TrailingSetTopicAsId<
	DenyThenTry<
		DenyRecursively<DenyReserveTransferToRelayChain>,
		(
			// Allow local users to buy weight credit.
			TakeWeightCredit,
			// Expected responses are OK.
			AllowKnownQueryResponses<PolkadotXcm>,
			WithComputedOrigin<
				(
					// If the message is one that immediately attempts to pay for execution, then
					// allow it.
					AllowTopLevelPaidExecutionFrom<Everything>,
					// Parent, its pluralities (i.e. governance bodies), relay treasury pallet
					// and sibling People get free execution.
					AllowExplicitUnpaidExecutionFrom<(
						ParentOrParentsPlurality,
						Equals<RelayTreasuryLocation>,
						Equals<SiblingPeople>,
						Equals<AssetHubRococoLocation>,
					)>,
					// Subscriptions for version tracking are OK.
					AllowSubscriptionsFrom<ParentRelayOrSiblingParachains>,
					// HRMP notifications from the relay chain are OK.
					AllowHrmpNotificationsFromRelayChain,
				),
				UniversalLocation,
				ConstU32<8>,
			>,
		),
	>,
>;
```

**File:** cumulus/parachains/runtimes/bridge-hubs/bridge-hub-rococo/src/xcm_config.rs (L258-269)
```rust
impl pallet_xcm::Config for Runtime {
	type RuntimeEvent = RuntimeEvent;
	type XcmRouter = XcmRouter;
	// We want to disallow users sending (arbitrary) XCMs from this chain.
	type SendXcmOrigin = EnsureXcmOrigin<RuntimeOrigin, ()>;
	// We support local origins dispatching XCM executions.
	type ExecuteXcmOrigin = EnsureXcmOrigin<RuntimeOrigin, LocalOriginToLocation>;
	type XcmExecuteFilter = Everything;
	type XcmExecutor = XcmExecutor<XcmConfig>;
	type XcmTeleportFilter = Everything;
	// This parachain is not meant as a reserve location.
	type XcmReserveTransferFilter = Nothing;
```

**File:** cumulus/parachains/runtimes/collectives/collectives-westend/src/xcm_config.rs (L304-314)
```rust
impl pallet_xcm::Config for Runtime {
	type RuntimeEvent = RuntimeEvent;
	// We only allow the Fellows to send messages.
	type SendXcmOrigin = EnsureXcmOrigin<RuntimeOrigin, FellowsToPlurality>;
	type XcmRouter = XcmRouter;
	// We support local origins dispatching XCM executions.
	type ExecuteXcmOrigin = EnsureXcmOrigin<RuntimeOrigin, LocalOriginToLocation>;
	type XcmExecuteFilter = Everything;
	type XcmExecutor = XcmExecutor<XcmConfig>;
	type XcmTeleportFilter = Everything;
	type XcmReserveTransferFilter = Nothing; // This parachain is not meant as a reserve location.
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L764-777)
```rust
	fn do_reserve_withdraw_assets(
		assets: AssetsInHolding,
		failed_bin: &mut AssetsInHolding,
		reserve: &Location,
		remote_xcm: &mut Vec<Instruction<()>>,
	) -> Result<Assets, XcmError> {
		// Must ensure that we recognise the assets as being managed by the destination.
		#[cfg(not(any(test, feature = "runtime-benchmarks")))]
		for asset in assets.assets_iter() {
			ensure!(
				Config::IsReserve::contains(&asset, &reserve),
				XcmError::UntrustedReserveLocation
			);
		}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L1203-1232)
```rust
			DepositReserveAsset { assets, dest, xcm } => {
				self.transactional_process(|self_ref| {
					let mut assets = self_ref.holding.saturating_take(assets);
					// When not using `PayFees`, nor `JIT_WITHDRAW`, delivery fees are paid from
					// transferred assets.
					let maybe_delivery_fee_from_assets = if self_ref.fees.is_empty() && !self_ref.fees_mode.jit_withdraw {
						// Deduct and return the part of `assets` that shall be used for delivery fees.
						self_ref.take_delivery_fee_from_assets(&mut assets, &dest, FeeReason::DepositReserveAsset, &xcm)?
					} else {
						None
					};
					let mut message = Vec::with_capacity(xcm.len() + 2);
					tracing::trace!(target: "xcm::DepositReserveAsset", ?assets, "Assets except delivery fee");
					Self::do_reserve_deposit_assets(
						assets,
						&dest,
						&mut message,
						Some(&self_ref.context),
					)?;
					// clear origin for subsequent custom instructions
					message.push(ClearOrigin);
					// append custom instructions
					message.extend(xcm.0.into_iter());
					if let Some(delivery_fee) = maybe_delivery_fee_from_assets {
						// Put back delivery_fee in holding register to be charged by XcmSender.
						self_ref.holding.subsume_assets(delivery_fee);
					}
					self_ref.send(dest, Xcm(message), FeeReason::DepositReserveAsset)?;
					Ok(())
				})
```
