### Title
Sync-committee consensus client cannot remove a stale or compromised L2 consensus / state machine entry once added - (File: modules/ismp/clients/sync-committee/src/pallet.rs)

### Summary
The `ismp-sync-committee` pallet exposes `add_l2_consensus` and `add_state_machine` to let `AdminOrigin` register additional L2 state machines (Arbitrum Orbit, OP Stack, etc.) under the sync-committee consensus client, but provides no corresponding removal extrinsic. Every other consensus-client whitelist pallet in the codebase (`ismp-grandpa`, `ismp-parachain`, `ismp-tendermint`) ships a matching `remove_*` call; the sync-committee pallet is the exception, mirroring exactly the "add without remove" bug class from the referenced Kairos report.

### Finding Description
`add_l2_consensus` writes an `L2Consensus` entry (an L1 contract address such as a dispute-game factory, L2 oracle, or rollup core address) into the consensus state's `l2_consensus` map and unconditionally sets `SupportedStatemachines::<T, I>::insert(state_machine_id.state_id, true)`: [1](#0-0) 

`add_state_machine` similarly only ever inserts into `SupportedStatemachines`: [2](#0-1) 

There is no `remove_l2_consensus` / `remove_state_machine` call in this pallet — confirmed by the absence of any `remove` call index and by contrast with the sibling consensus-client pallets, which explicitly pair add/remove: [3](#0-2) [4](#0-3) [5](#0-4) 

The consensus client itself gates all future state-machine verification purely on whether the entry is `true` in `SupportedStatemachines`: [6](#0-5) 

Once an L2 is registered, its `L2Consensus` entry (the trusted on-chain address used to validate that L2's state root, e.g. an OP Stack dispute-game factory or Arbitrum rollup core contract) is permanently baked into consensus state and the whitelist flag can never be cleared. If that registered contract is later deprecated, migrated, or its ownership/upgradeability is compromised (a routine occurrence for L2 fault-proof/rollup contracts), there is no on-chain mechanism to revoke trust in that L2 — the only remedy is decommissioning the entire sync-committee consensus client, which would also break every other unrelated L2/state machine relying on the same client.

### Impact Explanation
Because `state_machine()` returns `Ok` for any state machine that was ever added, `verify_consensus` continues to accept and forward `StateCommitmentHeight`s derived from that L2's now-stale or compromised `L2Consensus` contract indefinitely. If the underlying L1 contract governing that L2's finality (dispute-game factory, L2 oracle, rollup core) becomes untrustworthy, hyperbridge has no way to stop trusting state proofs sourced from it, resulting in a permanently unrevocable trust relationship. This can enable unsound state commitments to keep being accepted for that state machine — a route that cannot be shut down without disabling a shared, non-fungible consensus client entirely, in contradiction to the "least privilege" and "incident response" expectations built into every other consensus whitelist in this codebase (grandpa, tendermint, parachain).

### Likelihood Explanation
This is not a hypothetical: L2 rollup/fault-proof contracts (dispute game factories, L2 oracles) are routinely upgraded or migrated by their own governance, and Hyperbridge's admin has no lever to react by revoking trust in a superseded or compromised address once whitelisted. Given the codebase explicitly builds `remove_*` counterparts for every other consensus-client whitelist (an intentional design pattern), the missing removal path here is a genuine gap rather than a deliberate immutability choice, and directly matches the reported bug class.

### Recommendation
Add `remove_l2_consensus` / `remove_state_machine` extrinsics to `modules/ismp/clients/sync-committee/src/pallet.rs`, gated by the same `AdminOrigin`, that clear the entry from `SupportedStatemachines` and remove/replace the corresponding `L2Consensus` entry in the stored `ConsensusState`, mirroring the `add_state_machines`/`remove_state_machines` pattern already implemented in `ismp-grandpa`.

### Proof of Concept
1. Admin calls `add_l2_consensus(state_machine_id = Evm(OPTIMISM), l2_consensus = OpFaultProofGames(factory_addr, [...]))`, whitelisting Optimism under the sync-committee client.
2. Optimism governance later migrates/upgrades `factory_addr` to a new contract, or the existing factory's admin key is compromised.
3. There is no `remove_l2_consensus` call available; the entry `SupportedStatemachines::<T,I>::get(Evm(OPTIMISM)) == true` cannot be cleared.
4. `state_machine()` in `beacon_client.rs` keeps returning `Ok(Box::new(EvmStateMachine))` for Optimism forever, and `verify_consensus` keeps deriving/forwarding `StateCommitmentHeight`s tied to the old/compromised `L2Consensus` configuration, since the only stored consensus-state field that can be updated is via another `add_l2_consensus` call (which merely overwrites the map entry but never disables the state machine or forces reverification of the outstanding trust link) — the admin's only remaining lever is decommissioning the entire consensus client shared by all other L2s.

### Citations

**File:** modules/ismp/clients/sync-committee/src/pallet.rs (L71-98)
```rust
		/// Add a new l2 consensus to the sync committee consensus state
		#[pallet::call_index(0)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(1, 2))]
		pub fn add_l2_consensus(
			origin: OriginFor<T>,
			state_machine_id: StateMachineId,
			l2_consensus: L2Consensus,
		) -> DispatchResult {
			<T as Config<I>>::AdminOrigin::ensure_origin(origin)?;

			let host = <T as Config<I>>::IsmpHost::default();
			let StateMachineId { consensus_state_id, state_id: state_machine } = state_machine_id;

			let encoded_consensus_state = host
				.consensus_state(consensus_state_id)
				.map_err(|_| Error::<T, I>::ErrorFetchingConsensusState)?;
			let mut consensus_state: ConsensusState =
				codec::Decode::decode(&mut &encoded_consensus_state[..])
					.map_err(|_| Error::<T, I>::ErrorDecodingConsensusState)?;

			consensus_state.l2_consensus.insert(state_machine, l2_consensus);
			SupportedStatemachines::<T, I>::insert(state_machine_id.state_id, true);

			let encoded_consensus_state = consensus_state.encode();
			host.store_consensus_state(consensus_state_id, encoded_consensus_state)
				.map_err(|_| Error::<T, I>::ErrorStoringConsensusState)?;
			Ok(())
		}
```

**File:** modules/ismp/clients/sync-committee/src/pallet.rs (L100-110)
```rust
		/// Add a new state machine
		#[pallet::call_index(1)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads(1))]
		pub fn add_state_machine(
			origin: OriginFor<T>,
			state_machine_id: StateMachineId,
		) -> DispatchResult {
			<T as Config<I>>::AdminOrigin::ensure_origin(origin)?;
			SupportedStatemachines::<T, I>::insert(state_machine_id.state_id, true);
			Ok(())
		}
```

**File:** modules/ismp/clients/grandpa/src/lib.rs (L96-135)
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
	}
```

**File:** modules/ismp/clients/tendermint/src/pallet.rs (L49-85)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Add a Tendermint state machine support entry
		#[pallet::call_index(0)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(1, 1))]
		pub fn set_supported_state_machine(
			origin: OriginFor<T>,
			state_machine: StateMachine,
			supported: bool,
		) -> DispatchResult {
			<T as Config>::AdminOrigin::ensure_origin(origin)?;

			SupportedStateMachines::<T>::insert(state_machine, supported);
			Self::deposit_event(Event::<T>::StateMachineSupportUpdated {
				state_machine,
				supported,
			});
			Ok(())
		}

		/// Remove a Tendermint state machine support entry
		#[pallet::call_index(1)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(1, 1))]
		pub fn remove_supported_state_machine(
			origin: OriginFor<T>,
			state_machine: StateMachine,
		) -> DispatchResult {
			<T as Config>::AdminOrigin::ensure_origin(origin)?;

			SupportedStateMachines::<T>::remove(state_machine);
			Self::deposit_event(Event::<T>::StateMachineSupportUpdated {
				state_machine,
				supported: false,
			});
			Ok(())
		}
	}
```

**File:** modules/ismp/clients/parachain/client/src/lib.rs (L159-200)
```rust
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

**File:** modules/ismp/clients/sync-committee/src/beacon_client.rs (L150-160)
```rust
	fn consensus_client_id(&self) -> ConsensusClientId {
		C::ID
	}

	fn state_machine(&self, id: StateMachine) -> Result<Box<dyn StateMachineClient>, Error> {
		if SupportedStatemachines::<T, I>::contains_key(id) {
			Ok(Box::new(<EvmStateMachine<H, T>>::default()))
		} else {
			Err(SyncCommitteeError::UnsupportedStateMachine.into())
		}
	}
```
