### Title
`ismp-arbitrum` pallet permanently trusts a state machine once registered — no removal/disable path for `SupportedStateMachines` - ([File: modules/ismp/clients/ismp-arbitrum/src/pallet.rs])

### Summary
The `pallet-ismp-arbitrum` consensus-client pallet exposes exactly one privileged call, `set_rollup_core_address`, which both binds a rollup-core contract address to a `StateMachineId` and unconditionally flips that state machine's entry in `SupportedStateMachines` to `true`. Unlike the sibling GRANDPA and parachain consensus-client pallets in the same codebase, which both ship paired `add_*`/`remove_*` extrinsics, this pallet has no `remove_state_machine`, `disable_state_machine`, or any other call that can clear a `SupportedStateMachines` entry once set.

### Finding Description
`set_rollup_core_address` is the only dispatchable in the pallet: [1](#0-0) 

It writes to two storage maps:
- `StateMachinesRollupCoreAddresses<T>` — the L1 rollup-core contract address trusted for that Arbitrum state machine's consensus proofs.
- `SupportedStateMachines<T>` — `insert(state_machine_id.state_id, true)`, an append-only allow-flag with no corresponding `false`/`remove` path anywhere in the pallet.

This `SupportedStateMachines` flag is load-bearing for the consensus client itself: `ConsensusClient::state_machine` gates whether a given `StateMachine` is accepted as a valid client for state-proof verification purely on `contains_key`: [2](#0-1) 

and `verify_consensus` looks up the trusted `rollup_core_address` for the state machine and, if present, proceeds to verify whichever consensus proof variant (`ArbitrumOrbit` or `ArbitrumBold`) was submitted against that address: [3](#0-2) 

Once a state machine is admitted this way, `AdminOrigin` retains the ability to *re-point* the rollup-core address (via another `set_rollup_core_address` call, which just overwrites `StateMachinesRollupCoreAddresses`), but has no way to fully revoke the chain: there is no call that removes the `SupportedStateMachines` entry or the `StateMachinesRollupCoreAddresses` entry. Compare this to the pallet's sibling consensus clients in the same module tree, which explicitly support disabling a previously-trusted source:

- GRANDPA client ships both `add_state_machines` and `remove_state_machines`: [4](#0-3) 
- Parachain client ships both `add_parachain` and `remove_parachain`: [5](#0-4) 

The Arbitrum client is the outlier: it is architecturally identical (an admin-gated allowlist feeding a consensus verifier) but omits the removal half entirely.

### Impact Explanation
`SupportedStateMachines` and `StateMachinesRollupCoreAddresses` function exactly like the reported `addSafeAddress()` allowlist: an admin decision to trust a source is permanent and cannot be walked back through the pallet's own interface. If an Arbitrum Orbit/BoLD deployment that was once admitted is later deprecated, migrated to a different rollup contract that governance does not want to keep trusting, found to have a compromised/buggy `RollupCore`, or simply should be retired from the protocol, `AdminOrigin` has no on-chain mechanism to stop `verify_consensus` from continuing to accept and act on consensus proofs referencing that state machine — `state_machine()` will keep reporting it as supported forever, and the only "fix" available is overwriting the rollup-core address (not disabling the entry), which does not help if the intent is to fully cut the chain off. This is a one-way trust escalation in a consensus-verification code path that other, structurally identical clients in the same repo correctly guard against with a removal extrinsic — meeting the "unsound state commitment" / permanent-trust class of impact from the analog report.

### Likelihood Explanation
Likelihood is moderate-to-high over the life of the protocol: L2 rollup contracts are routinely upgraded/migrated (e.g., Arbitrum's BoLD upgrade itself, which this pallet explicitly models as a second consensus type), and governance needs a way to deprecate a previously-supported Orbit/BoLD chain or rollup-core address without a runtime upgrade. Any operational need to disable a chain (compromise, decommission, wrong address bound, chain sunset) currently has no on-chain remedy short of a pallet code change and forkless runtime upgrade, which the fishermen-blacklist mechanism in the same file only partially covers (it blacklists specific claim hashes, not the whole state machine).

### Recommendation
Add a governance-gated `remove_state_machine` (and/or `disable_rollup_core_address`) extrinsic to `pallet-ismp-arbitrum`, mirroring `remove_state_machines`/`remove_parachain` in the GRANDPA/parachain clients: clear the `SupportedStateMachines` entry and, ideally, the associated `StateMachinesRollupCoreAddresses` entry, emitting a corresponding event (e.g. `StateMachineRemoved`) for observability. This restores parity between the Arbitrum consensus client and its sibling clients and gives governance a real path to revoke trust from a compromised or deprecated Arbitrum deployment.

### Proof of Concept
1. `AdminOrigin` calls `set_rollup_core_address(state_machine_id, rollup_core_address)` to onboard an Arbitrum Orbit/BoLD chain — `StateMachinesRollupCoreAddresses` is set and `SupportedStateMachines::insert(state_id, true)` runs (`modules/ismp/clients/ismp-arbitrum/src/pallet.rs:82-104`).
2. Time passes; the bound `rollup_core_address`'s contract is later found compromised, deprecated, or governance decides the chain should no longer be trusted for consensus proofs.
3. `AdminOrigin` searches the pallet's call surface for a way to revoke trust — there is only `set_rollup_core_address` (which can only rebind to a *different* address, not disable), no `remove_state_machine`/`remove_rollup_core_address` exists.
4. `verify_consensus` (`modules/ismp/clients/ismp-arbitrum/src/lib.rs:130-217`) and `state_machine()` (`:236-242`) continue to treat the chain as fully supported and will verify/accept any well-formed consensus proof against whichever address is currently bound, with no on-chain way to shut this down short of a runtime upgrade — reproducing the "can add but never remove" defect from the referenced report in a consensus-trust context.

### Citations

**File:** modules/ismp/clients/ismp-arbitrum/src/pallet.rs (L77-105)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Sets the new roll up core address
		#[pallet::call_index(0)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(1, 1))]
		pub fn set_rollup_core_address(
			origin: OriginFor<T>,
			state_machine_id: StateMachineId,
			rollup_core_address: H160,
		) -> DispatchResult {
			<T as Config>::AdminOrigin::ensure_origin(origin)?;

			StateMachinesRollupCoreAddresses::<T>::mutate(
				state_machine_id.clone(),
				|maybe_address| {
					*maybe_address = Some(rollup_core_address);
				},
			);

			SupportedStateMachines::<T>::insert(state_machine_id.state_id, true);

			Self::deposit_event(Event::<T>::StateMachinesRollupCoreAddress {
				state_machine_id,
				rollup_core_address,
			});

			Ok(())
		}
	}
```

**File:** modules/ismp/clients/ismp-arbitrum/src/lib.rs (L130-155)
```rust
		if let Some(rollup_core_address) =
			Pallet::<T>::state_machines_rollup_core_addresses(state_machine_id)
		{
			match proof {
				ArbitrumConsensusProof::ArbitrumOrbit(proof) => {
					// Derive the unified claim hash and refuse blacklisted entries before the
					// heavy proof verification.
					let state_hash = get_state_hash::<H>(
						proof.global_state,
						proof.machine_status,
						proof.inbox_max_count,
					);
					let claim = orbit_claim_hash::<H>(state_hash, proof.node_number);
					if <T as pallet::Config>::FishermanBlacklist::is_arbitrum_claim_blacklisted(
						state_machine_id,
						claim,
					) {
						return Err(ArbitrumError::ClaimBlacklisted(claim).into());
					}

					let state = verify_arbitrum_payload::<H>(
						proof,
						state_root,
						rollup_core_address,
						consensus_state_id.clone(),
					)?;
```

**File:** modules/ismp/clients/ismp-arbitrum/src/lib.rs (L236-242)
```rust
	fn state_machine(&self, id: StateMachine) -> Result<Box<dyn StateMachineClient>, Error> {
		if SupportedStateMachines::<T>::contains_key(id) {
			Ok(Box::new(<EvmStateMachine<H, T>>::default()))
		} else {
			Err(ArbitrumError::UnsupportedStateMachine(id).into())
		}
	}
```

**File:** modules/ismp/clients/grandpa/src/lib.rs (L96-134)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Add some a state machine to the list of supported state machines
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::add_state_machines(new_state_machines.len() as u32))]
		pub fn add_state_machines(
			origin: OriginFor<T>,
			new_state_machines: Vec<AddStateMachine>,
		) -> DispatchResult {
			T::RootOrigin::ensure_origin(origin)?;

			let state_machines =
				new_state_machines.iter().map(|a| a.state_machine.clone()).collect();
			for AddStateMachine { state_machine, slot_duration } in new_state_machines {
				SupportedStateMachines::<T>::insert(state_machine, slot_duration);
			}

			Self::deposit_event(Event::StateMachineAdded { state_machines });

			Ok(())
		}

		/// Remove a state machine from the list of supported state machines
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::remove_state_machines(state_machines.len() as u32))]
		pub fn remove_state_machines(
			origin: OriginFor<T>,
			state_machines: Vec<StateMachine>,
		) -> DispatchResult {
			T::RootOrigin::ensure_origin(origin)?;

			for state_machine in state_machines.clone() {
				SupportedStateMachines::<T>::remove(state_machine)
			}

			Self::deposit_event(Event::StateMachineRemoved { state_machines });

			Ok(())
		}
```

**File:** modules/ismp/clients/parachain/client/src/lib.rs (L158-200)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Add some new parachains to the parachains whitelist
		#[pallet::call_index(1)]
		#[pallet::weight(<T as pallet::Config>::WeightInfo::add_parachain(para_ids.len() as u32))]
		pub fn add_parachain(origin: OriginFor<T>, para_ids: Vec<ParachainData>) -> DispatchResult {
			T::RootOrigin::ensure_origin(origin)?;
			let host = <T::IsmpHost>::default();
			for para in &para_ids {
				let state_id = match host.host_state_machine() {
					StateMachine::Kusama(_) => StateMachine::Kusama(para.id),
					StateMachine::Polkadot(_) => StateMachine::Polkadot(para.id),
					_ => continue,
				};
				Parachains::<T>::insert(para.id, ());
				let _ = host.store_challenge_period(
					StateMachineId {
						state_id,
						consensus_state_id: parachain_consensus_state_id(host.host_state_machine()),
					},
					0,
				);
			}

			Self::deposit_event(Event::ParachainsAdded { para_ids });

			Ok(())
		}

		/// Removes some parachains from the parachains whitelist
		#[pallet::call_index(2)]
		#[pallet::weight(<T as pallet::Config>::WeightInfo::remove_parachain(para_ids.len() as u32))]
		pub fn remove_parachain(origin: OriginFor<T>, para_ids: Vec<u32>) -> DispatchResult {
			T::RootOrigin::ensure_origin(origin)?;
			for id in &para_ids {
				Parachains::<T>::remove(id);
				SlotDurations::<T>::remove(id);
			}

			Self::deposit_event(Event::ParachainsRemoved { para_ids });

			Ok(())
		}
```
