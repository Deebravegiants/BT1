### Title
`add_tip` bypasses the operating-mode halt check enforced on `register_token`, allowing bridge operations to continue while Ethereum export is halted - (File: `bridges/snowbridge/pallets/system-frontend/src/lib.rs`)

### Summary
The `pallet-snowbridge-system-frontend` pallet exposes an `ExportOperatingMode` storage flag (`Normal`/`Halted`) that is meant to gate outbound operations toward Ethereum during an emergency. `register_token` explicitly checks this flag before proceeding, but the sibling extrinsic `add_tip` performs the same category of action (swapping/burning an asset and sending a `Transact` XCM to the bridge hub) without any halt check — structurally the same class of bug as the reported RdpxV2Core `redeem()` missing a `whenNotPaused()` guard while other functions (`bond`, `bondWithDelegate`, `withdraw`) enforced it.

### Finding Description
`ExportOperatingMode` is a pallet-level pause flag with `is_halted()`: [1](#0-0) 

In `register_token`, the very first statement enforces the halt: [2](#0-1) 

`add_tip`, however, performs the analogous privileged action — swapping/burning the tip asset and dispatching a `Transact` call to the bridge hub via `send_transact_call` — with no equivalent `ensure!(!Self::export_operating_mode().is_halted(), Error::<T>::Halted)` check: [3](#0-2) 

Both extrinsics ultimately call `send_transact_call`, which builds and dispatches an XCM `Transact` toward `EthereumSystem` on BridgeHub: [4](#0-3) 

This is exactly the same vulnerability class as the RdpxV2Core report: one action-performing entry point checks the pause/halt state, a sibling entry point in the same pallet performing an equally consequential action does not, giving any unprivileged signed account a way to keep interacting with the bridge even while governance has set `ExportOperatingMode::Halted`.

### Impact Explanation
When root sets the mode to `Halted` (via `set_operating_mode`) — presumably in response to an incident on the Ethereum side or a compromised bridge component — the intent is that all non-governance Ethereum-export operations stop. `add_tip` is callable by any signed account, is unaffected by the halt, and can still: swap a user-supplied asset for ether, burn ether for teleport, and dispatch an XCM `Transact` to BridgeHub targeting the (potentially compromised/paused) `EthereumSystem` pallet. This undermines the operator's ability to fully quiesce the export path during an emergency, and could be used to keep generating outbound XCM traffic/asset burns toward a system that operators believed was halted.

### Likelihood Explanation
High for reachability: `add_tip` requires only `ensure_signed(origin)`, no special privilege, and is a normal public extrinsic: [5](#0-4) 
The existing test suite (`add_tip_ether_asset_succeeds`, `add_tip_non_ether_asset_succeeds`) confirms `add_tip` succeeds under default (`Normal`) test conditions, but there is no test exercising `add_tip` while `ExportOperatingMode::Halted` is set — unlike `register_token`, which has an explicit `test_switch_operating_mode` test proving the halt check works for it. This asymmetry in test coverage mirrors the asymmetry in the code itself.

### Recommendation
Add the same halt guard used in `register_token` to `add_tip`:
```rust
pub fn add_tip(origin: OriginFor<T>, message_id: MessageId, asset: Asset) -> DispatchResult {
    ensure!(!Self::export_operating_mode().is_halted(), Error::<T>::Halted);
    let who = ensure_signed(origin)?;
    ...
}
```
and add a regression test analogous to `test_switch_operating_mode` that asserts `add_tip` fails with `Error::<T>::Halted` while the mode is `Halted`.

### Proof of Concept
1. Root calls `set_operating_mode(Halted)` as in `test_switch_operating_mode`: [6](#0-5) 
2. Confirm `register_token` is now blocked with `Error::<T>::Halted` (already proven by the existing test): [7](#0-6) 
3. Call `add_tip` with a signed origin (same setup as `add_tip_ether_asset_succeeds`) while the mode is still `Halted`: [8](#0-7)  — this call is expected to succeed and emit `Event::MessageSent`, proving the halt is bypassed. This scenario is not currently covered by any test in `tests.rs`.

**Caveat:** I was unable to trace how `set_operating_mode`/`ExportOperatingMode` interacts with the runtime-level XCM filters used on the actual BridgeHub runtime (e.g., whether a separate `SafeMode`/`TxPause` configuration on the production runtime independently blocks `add_tip`); this analysis is based solely on the pallet's own logic and unit tests. Runtime integration files for BridgeHub were not indexed in this pass, so I cannot rule out a compensating control at the runtime configuration layer.

### Citations

**File:** bridges/snowbridge/primitives/core/src/operating_mode.rs (L32-36)
```rust
impl BasicOperatingMode {
	pub fn is_halted(&self) -> bool {
		*self == BasicOperatingMode::Halted
	}
}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L225-235)
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
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L261-273)
```rust
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

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L406-423)
```rust
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

**File:** bridges/snowbridge/pallets/system-frontend/src/tests.rs (L114-120)
```rust
fn test_switch_operating_mode() {
	new_test_ext().execute_with(|| {
		assert_ok!(EthereumSystemFrontend::set_operating_mode(
			RawOrigin::Root.into(),
			BasicOperatingMode::Halted,
		));
		let origin_location = Location::new(1, [Parachain(2000)]);
```

**File:** bridges/snowbridge/pallets/system-frontend/src/tests.rs (L132-140)
```rust
		assert_noop!(
			EthereumSystemFrontend::register_token(
				origin.clone(),
				asset_id.clone(),
				asset_metadata.clone(),
				asset.clone(),
			),
			crate::Error::<Test>::Halted
		);
```

**File:** bridges/snowbridge/pallets/system-frontend/src/tests.rs (L150-163)
```rust
fn add_tip_ether_asset_succeeds() {
	new_test_ext().execute_with(|| {
		let who: AccountId = Keyring::Alice.into();
		let message_id = MessageId::Inbound(1);
		let ether_location = Ether::get();
		let tip_amount = 1000;
		let asset = Asset::from((ether_location.clone(), tip_amount));

		assert_ok!(EthereumSystemFrontend::add_tip(
			RuntimeOrigin::signed(who.clone()),
			message_id.clone(),
			asset.clone()
		));

```
