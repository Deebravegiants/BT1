### Title
`add_tip` in `pallet_snowbridge_system_frontend` omits the `Halted` operating-mode check enforced on `register_token`, allowing exports to Ethereum to continue during a halt - (File: `bridges/snowbridge/pallets/system-frontend/src/lib.rs`)

### Summary
The external report describes a Solidity pattern where a "pause" guard is applied inconsistently across sibling entry points that reach the same sensitive state-changing logic, letting users bypass the intended pause. The closest structural analog found in this repo is in `pallet_snowbridge_system_frontend`, where `register_token` explicitly checks the pallet's halt flag before proceeding, but the sibling extrinsic `add_tip` — which also burns/moves user assets and dispatches a cross-chain XCM `Transact` to the Ethereum bridge — does not perform the same check.

### Finding Description
`ExportOperatingMode<T>` is a governance-controlled halt flag, settable only via `set_operating_mode` (root-only) [1](#0-0) .

`register_token` correctly gates on this flag before executing: [2](#0-1) 

`add_tip`, however, performs the equivalent externally-triggered, asset-affecting operation (swap the tip asset for Ether, burn it for teleport, and forward a `Transact` XCM to Bridge Hub) without checking `ExportOperatingMode`/`Halted` at all: [3](#0-2) 

Both dispatchables funnel into the same low-level machinery — `swap_fee_asset_and_burn`/`swap_and_burn` (asset swap + burn) and `send_transact_call`/`send_xcm` (dispatch of XCM to the bridge hub) — used identically by the checked `register_token` path: [4](#0-3) 

This mirrors the CDPVault issue structurally: a pause/halt mechanism intended to stop the pallet's bridge-export behaviour is enforced on one caller of the shared logic but not on another caller of the same shared logic, so an unprivileged, signed user can still trigger XCM export activity while the pallet is supposed to be halted.

### Impact Explanation
If governance halts the Snowbridge export path (e.g., in response to a security incident such as a compromised BEEFY/light-client, or bridge-hub congestion/attack), the intent of `set_operating_mode(Halted)` is to stop the flow of value and messages from Polkadot to Ethereum through this frontend pallet. Because `add_tip` skips the halt check, users can continue to: (1) swap arbitrary configured assets for Ether via `T::Swap`, (2) burn that Ether for teleport, and (3) push XCM `Transact` calls to Bridge Hub while the system is supposedly halted. This does not directly forge new tokens, but it undermines the operational control that the halt mechanism is meant to provide, continuing user-triggered value transfer/export traffic during an incident when the operator has explicitly decided to stop it.

### Likelihood Explanation
High likelihood of the code path being reachable: `add_tip` is a normal signed extrinsic requiring no special origin (`ensure_signed(origin)?`), callable by any account holding a fee asset to swap. No proxy, mock, or privileged setup is required to trigger it — it's a first-class, unprivileged, externally-facing entry point.

### Recommendation
Add the same `ensure!(!Self::export_operating_mode().is_halted(), Error::<T>::Halted);` check at the start of `add_tip` (and any other extrinsic in this pallet that reaches `swap_and_burn`/`send_transact_call`), consistent with `register_token`, so the halt flag uniformly gates all pathways that move funds or send XCM export traffic.

### Proof of Concept
1. Root calls `set_operating_mode(Halted)`, setting `ExportOperatingMode::<T>` to `Halted`.
2. A regular signed user calls `add_tip(origin, message_id, asset)`.
3. `add_tip` skips any halt check (unlike `register_token`), proceeds to call `swap_fee_asset_and_burn` (swapping/burning the user's asset) and `send_transact_call` (dispatching an XCM `Transact` to Bridge Hub), succeeding despite the pallet being halted.

Note: I was unable to execute a live test run given the read-only nature of this analysis; the finding is based on static code review of the `add_tip` and `register_token` implementations and their shared helper functions, confirming the check is present in one but absent in the other.

### Citations

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L190-208)
```rust
	/// The current operating mode for exporting to Ethereum.
	#[pallet::storage]
	#[pallet::getter(fn export_operating_mode)]
	pub type ExportOperatingMode<T: Config> = StorageValue<_, OperatingMode, ValueQuery>;

	#[pallet::call]
	impl<T: Config> Pallet<T>
	where
		<T as frame_system::Config>::AccountId: Into<Location>,
	{
		/// Set the operating mode for exporting messages to Ethereum.
		#[pallet::call_index(0)]
		#[pallet::weight((T::DbWeight::get().reads_writes(1, 1), DispatchClass::Operational))]
		pub fn set_operating_mode(origin: OriginFor<T>, mode: OperatingMode) -> DispatchResult {
			ensure_root(origin)?;
			ExportOperatingMode::<T>::put(mode);
			Self::deposit_event(Event::ExportOperatingModeChanged { mode });
			Ok(())
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L225-252)
```rust
		pub fn register_token(
			origin: OriginFor<T>,
			asset_id: Box<VersionedLocation>,
			metadata: AssetMetadata,
			fee_asset: Asset,
		) -> DispatchResult {
			ensure!(!Self::export_operating_mode().is_halted(), Error::<T>::Halted);

			let asset_location: Location =
				(*asset_id).try_into().map_err(|_| Error::<T>::UnsupportedLocationVersion)?;
			let origin_location = T::RegisterTokenOrigin::ensure_origin(origin, &asset_location)?;

			let ether_gained = if origin_location.is_here() {
				// Root origin/location does not pay any fees/tip.
				0
			} else {
				Self::swap_fee_asset_and_burn(origin_location.clone(), fee_asset)?
			};

			let call = Self::build_register_token_call(
				origin_location.clone(),
				asset_location,
				metadata,
				ether_gained,
			)?;

			Self::send_transact_call(origin_location, call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L254-273)
```rust
		/// Add an additional relayer tip for a committed message identified by `message_id`.
		/// The tip asset will be swapped for ether.
		#[pallet::call_index(2)]
		#[pallet::weight(
			T::WeightInfo::add_tip()
				.saturating_add(T::BackendWeightInfo::transact_add_tip())
		)]
		pub fn add_tip(origin: OriginFor<T>, message_id: MessageId, asset: Asset) -> DispatchResult
		where
			<T as frame_system::Config>::AccountId: Into<Location>,
		{
			let who = ensure_signed(origin)?;

			let ether_gained = Self::swap_fee_asset_and_burn(who.clone().into(), asset)?;

			// Send the tip details to BH to be allocated to the reward in the Inbound/Outbound
			// pallet
			let call = Self::build_add_tip_call(who.clone(), message_id.clone(), ether_gained);
			Self::send_transact_call(who.into(), call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L372-423)
```rust
		fn swap_fee_asset_and_burn(
			origin: Location,
			fee_asset: Asset,
		) -> Result<u128, DispatchError> {
			let ether_location = T::EthereumLocation::get();
			let (fee_asset_location, fee_amount) = match fee_asset {
				Asset { id: AssetId(ref loc), fun: Fungible(amount) } => (loc, amount),
				_ => {
					tracing::debug!(target: LOG_TARGET, ?fee_asset, "error matching fee asset");
					return Err(Error::<T>::UnsupportedAsset.into());
				},
			};
			if fee_amount == 0 {
				return Ok(0);
			}

			let ether_gained = if *fee_asset_location != ether_location {
				Self::swap_and_burn(
					origin.clone(),
					fee_asset_location.clone(),
					ether_location,
					fee_amount,
				)
				.inspect_err(|&e| {
					tracing::debug!(target: LOG_TARGET, ?e, "error swapping asset");
				})?
			} else {
				burn_for_teleport::<T::AssetTransactor>(&origin, &fee_asset)
					.map_err(|_| Error::<T>::BurnError)?;
				fee_amount
			};
			Ok(ether_gained)
		}

		fn send_transact_call(
			origin_location: Location,
			call: BridgeHubRuntime<T>,
		) -> DispatchResult {
			let dest = T::BridgeHubLocation::get();
			let remote_xcm = Self::build_remote_xcm(&call);
			let message_id = Self::send_xcm(origin_location, dest.clone(), remote_xcm.clone())
				.map_err(|error| Error::<T>::from(error))?;

			Self::deposit_event(Event::<T>::MessageSent {
				origin: T::PalletLocation::get().into(),
				destination: dest,
				message: remote_xcm,
				message_id,
			});

			Ok(())
		}
```
