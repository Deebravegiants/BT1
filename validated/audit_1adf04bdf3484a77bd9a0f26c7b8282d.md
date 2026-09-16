### Title
`remove_state_machines` / `remove_parachain` / `remove_supported_state_machine` deregister a consensus-client source chain without checking in-flight requests, permanently stranding messages and their attached relayer fees - ([File: modules/ismp/clients/grandpa/src/lib.rs], [File: modules/ismp/clients/parachain/client/src/lib.rs], [File: modules/ismp/clients/tendermint/src/pallet.rs])

### Summary
Several ISMP consensus-client pallets expose an admin-gated "remove" call that deletes a source state machine from the whitelist that gates acceptance of new consensus/state proofs for that chain. None of these removal paths check whether there are still undelivered/unfinalized ISMP requests or responses originating from (or destined to) that state machine that depend on future state-commitment updates to be provable. This mirrors the `removePlugin` bug class in the report: a registration is deleted with no check for outstanding claims tied to it.

### Finding Description
`pallet-ismp-grandpa::remove_state_machines` simply removes the entry from `SupportedStateMachines` and emits an event, with no check of pending message state: [1](#0-0) 

The analogous `remove_parachain` call in the parachain consensus client removes `Parachains` and `SlotDurations` entries the same way: [2](#0-1) 

And the Tendermint pallet's `remove_supported_state_machine` does the same: [3](#0-2) 

Once a state machine is removed from the whitelist, `validate_state_machine` in ISMP core will reject any new consensus/state proof for that chain because `consensus_client_id`/`state_machine` resolution depends on it being recognized: [4](#0-3) 

Any request or response that was dispatched but not yet delivered because the destination has not yet observed a sufficiently high finalized state commitment for the source chain becomes permanently undeliverable the moment governance removes that state machine — relayers can no longer submit new state proofs for it, so the message can never clear its challenge period and be executed on the destination, and any fee escrowed for its delivery (tracked per-`StateMachine` in `pallet-ismp-relayer::Fees`) can never be earned/claimed by a relayer for that in-flight batch. This is the same failure mode the source report flags: removal of a registration entity with no check for "valid claims" tied to it, resulting in funds/messages that can no longer be settled.

### Impact Explanation
This produces a route that can no longer deliver messages for any request/response still in flight at removal time — one of the explicitly accepted impact categories ("a route unable to deliver messages"). Because delivery is what unlocks relayer-fee accumulation (`pallet-ismp-relayer::accumulate_fees`/`Fees` storage) and application-level effects (`onAccept`/`onGetResponse`), in-flight funds and application state become permanently stuck if the associated state machine is deregistered before those messages clear. This is reachable by ordinary users/relayers who dispatched or are relaying messages through a route that a later, unrelated governance action turns off — they have no way to force delivery once the whitelist entry is gone.

### Likelihood Explanation
Likelihood is moderate: it requires a privileged (`RootOrigin`/`AdminOrigin`) removal call, which the "malicious-governance" exclusion in principle discounts, but the bug class here is not about malicious governance — it is about *legitimate* governance operations (deprecating a stale/compromised/migrating chain) that are objectively reachable and expected to occur over the protocol's life, and the code gives operators no warning or blocking mechanism when in-flight requests exist. Docs even describe removal as a normal, reversible administrative action ("They can always be re-added"), which somewhat mitigates severity since re-adding restores provability for pending heights that haven't expired their challenge/unbonding period — but if the unbonding/challenge window elapses first, or if the consensus state itself is discarded, the freeze becomes effectively permanent.

### Recommendation
Before removing a state machine from any of these whitelists, check whether there are pending (undelivered, non-timed-out) requests/responses associated with that state machine, and either block the removal, or provide a dedicated draining/timeout path so in-flight messages can still be finalized after removal (e.g., only reject *new* dispatches or *new* consensus updates before the last committed height, rather than immediately rejecting all future proofs including those needed to prove already-committed-but-undelivered messages).

### Proof of Concept
1. A user dispatches a `PostRequest` from chain `A` (a GRANDPA-tracked solochain) to chain `B`, paying a relayer fee.
2. Chain `B`'s host has not yet received a sufficiently aged (past-challenge-period) state commitment for chain `A` covering the block containing this request.
3. Governance (`RootOrigin`) calls `remove_state_machines` (or `remove_parachain`/`remove_supported_state_machine`) removing chain `A` from the whitelist, e.g. as part of unrelated chain deprecation. [1](#0-0) 
4. Any subsequent GRANDPA consensus proof submission for chain `A` is rejected because `consensus_client_id`/whitelist lookups no longer resolve it (`validate_state_machine`). [4](#0-3) 
5. The pending request from step 1 can never be proven/delivered on chain `B`; the relayer who would have delivered it can never accumulate the associated fee, and if the application locked funds pending delivery, those funds are stuck as well.

### Citations

**File:** modules/ismp/clients/grandpa/src/lib.rs (L118-134)
```rust
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

**File:** modules/ismp/clients/parachain/client/src/lib.rs (L187-200)
```rust
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

**File:** modules/ismp/clients/tendermint/src/pallet.rs (L69-84)
```rust
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
```

**File:** modules/ismp/core/src/handlers.rs (L121-148)
```rust
pub fn validate_state_machine<H>(
	host: &H,
	proof_height: StateMachineHeight,
) -> Result<Box<dyn StateMachineClient>, Error>
where
	H: IsmpHost,
{
	// Ensure consensus client is not frozen
	let consensus_client_id = host.consensus_client_id(proof_height.id.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized {
			consensus_state_id: proof_height.id.consensus_state_id,
		},
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	// Ensure client is not frozen
	host.is_consensus_client_frozen(proof_height.id.consensus_state_id)?;

	// Ensure delay period has elapsed
	if !verify_delay_passed(host, &proof_height)? {
		return Err(Error::ChallengePeriodNotElapsed {
			state_machine_id: proof_height.id,
			current_time: host.timestamp(),
			update_time: host.state_machine_update_time(proof_height)?,
		});
	}

	consensus_client.state_machine(proof_height.id.state_id)
}
```
