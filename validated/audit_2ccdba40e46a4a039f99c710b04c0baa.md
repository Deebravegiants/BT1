This confirms the analog clearly. Both `OutboundConsensusDeliveryReward` and `OutboundRequestDeliveryReward` are read fresh at claim time (`OutboundConsensusDeliveryReward::<T>::get(destination)` at [1](#0-0) , `OutboundRequestDeliveryReward::<T>::get(&module_id)` at [2](#0-1) ), while the relayer's costly on-chain work (delivering the consensus proof or the request) happens earlier, unattributed to any locked-in reward value.

### Title
Relayer delivery rewards are read at claim time, not locked at dispatch time, exposing relayers to fee changes after work is done - (File: `modules/pallets/relayer/src/outbound_consensus.rs`, `modules/pallets/relayer/src/outbound_request.rs`)

### Summary
`OutboundConsensusDeliveryReward` and `OutboundRequestDeliveryReward` are per-destination/per-module reward amounts governance can update at any time via `set_outbound_consensus_delivery_reward` and `set_outbound_request_delivery_reward` [3](#0-2) [4](#0-3) . A relayer decides to deliver a hyperbridge-originated consensus rotation or POST request based on the reward value visible at delivery time, but the actual payout is computed by reading the storage value fresh at claim time — after the relayer has already spent gas delivering to the destination and waited for the destination state commitment to land back on Hyperbridge. If the reward is reduced (or zeroed) in that interval, the relayer is paid less than what motivated the delivery, or the claim reverts entirely with `OutboundNoRewardConfigured` / `OutboundRequestNoRewardConfigured`.

### Finding Description
The claim-processing functions look up the reward by key at verification time, not at the time the underlying request/rotation was dispatched:

- `process_outbound_consensus_delivery_claim` reads `OutboundConsensusDeliveryReward::<T>::get(destination)` only after performing the full state-proof and signature verification pipeline, and reverts with `OutboundNoRewardConfigured` if it is now zero [1](#0-0) .
- `process_outbound_request_delivery_claim` reads `OutboundRequestDeliveryReward::<T>::get(&module_id)` similarly, before the rest of the proof pipeline, but still strictly after the request was dispatched and delivered [5](#0-4) .

Both rewards are freely mutable by governance at any block via a simple storage insert, with no linkage back to the block/state at which the underlying request or consensus rotation was originally dispatched [3](#0-2) [4](#0-3) . There is no snapshotting of the reward amount at dispatch time (e.g., stored alongside the commitment in `RequestCommitments`), and the design doc itself confirms the reward is "decoupled from the dispatch path and paid out at claim time against a destination state proof" [6](#0-5) .

This is structurally identical to the reported `buyFee`/`sellFee` issue: a value that determines counterparty compensation is mutable between the moment an unprivileged actor commits to an action (listing creation / message delivery) and the moment that compensation is actually realized (purchase / reward claim), with the realized value taken from current state rather than the value in effect when the actor committed resources.

### Impact Explanation
An unprivileged relayer that delivers a hyperbridge-originated consensus rotation or system request incurs real, non-refundable destination-chain gas costs and must wait out the challenge period before it can claim. If governance lowers or zeroes the reward for that `state_machine` (or `module_id`) during that window — which can span the full consensus challenge period — the relayer's claim either pays a reduced amount or reverts with `OutboundNoRewardConfigured`/`OutboundRequestNoRewardConfigured`, permanently forfeiting the expected compensation for work already performed and gas already spent. This directly parallels the "Financial Discrepancies for Sellers" impact in the reference report: the relayer "receives less [reward] than anticipated" purely due to a state change that occurred after their commitment, with no mechanism to lock in the rate they acted on.

### Likelihood Explanation
The reward values are explicitly designed to be governance-tunable ("Governance-set per-chain reward" / "Governance-set per-`module_id` reward") [7](#0-6) [8](#0-7) , meaning routine economic rebalancing (not just malicious action) will periodically change these values while claims from prior deliveries are still in flight, given the delivery-to-claim window necessarily spans a state-commitment wait plus challenge period.

### Recommendation
Snapshot the applicable reward at dispatch time and store it alongside the request/rotation commitment (analogous to how `FeeMetadata` already stores `fee` alongside `RequestCommitments`), and have the claim pipeline pay out the snapshotted value rather than re-reading current governance state. Alternatively, apply reward changes only to requests/rotations dispatched after the change takes effect, e.g. by keying reward lookups on the dispatch block height with a delayed-activation window.

### Proof of Concept
1. Governance sets `OutboundRequestDeliveryReward[module_id] = R1` via `set_outbound_request_delivery_reward` [9](#0-8) .
2. A pallet (e.g. host-executive) dispatches a hyperbridge-originated `PostRequest` with `from = module_id` [10](#0-9) .
3. An unprivileged relayer observes reward `R1`, spends gas delivering the request to the destination chain, and begins waiting for the destination state commitment plus challenge period.
4. Before the relayer submits `claim_outbound_request_delivery_reward`, governance calls `set_outbound_request_delivery_reward(module_id, 0)` (or a lower amount) — a normal, non-malicious governance operation.
5. The relayer submits `claim_outbound_request_delivery_reward`; `process_outbound_request_delivery_claim` reads `OutboundRequestDeliveryReward::<T>::get(&module_id)` at that moment, sees `0`, and rejects the claim with `OutboundRequestNoRewardConfigured` [11](#0-10) , or receives a lower reward than the one that motivated the delivery — despite having already fully performed the delivery.

### Citations

**File:** modules/pallets/relayer/src/outbound_consensus.rs (L174-175)
```rust
		let reward = OutboundConsensusDeliveryReward::<T>::get(destination);
		ensure!(reward > BalanceOf::<T>::default(), Error::<T>::OutboundNoRewardConfigured);
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L143-149)
```rust
		let module_id: BoundedVec<u8, ModuleIdBound> = request
			.from
			.clone()
			.try_into()
			.map_err(|_| Error::<T>::OutboundRequestModuleIdTooLong)?;
		let reward = OutboundRequestDeliveryReward::<T>::get(&module_id);
		ensure!(reward > BalanceOf::<T>::default(), Error::<T>::OutboundRequestNoRewardConfigured);
```

**File:** modules/pallets/relayer/src/lib.rs (L399-414)
```rust
		/// Governance-set per-chain reward for delivering mandatory consensus
		/// proofs to that destination.
		#[pallet::call_index(4)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(0, 1))]
		pub fn set_outbound_consensus_delivery_reward(
			origin: OriginFor<T>,
			state_machine: StateMachine,
			amount: BalanceOf<T>,
		) -> DispatchResult {
			T::RelayerOrigin::ensure_origin(origin)?;
			OutboundConsensusDeliveryReward::<T>::insert(state_machine, amount);
			Self::deposit_event(Event::OutboundConsensusDeliveryRewardUpdated {
				state_machine,
				new_reward: amount,
			});
			Ok(())
```

**File:** modules/pallets/relayer/src/lib.rs (L433-450)
```rust
		/// Governance-set per-`module_id` reward for delivering a
		/// hyperbridge-originated request from that module. Setting
		/// `amount = 0` removes the module from the allowlist.
		#[pallet::call_index(6)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(0, 1))]
		pub fn set_outbound_request_delivery_reward(
			origin: OriginFor<T>,
			module_id: BoundedVec<u8, ModuleIdBound>,
			amount: BalanceOf<T>,
		) -> DispatchResult {
			T::RelayerOrigin::ensure_origin(origin)?;
			OutboundRequestDeliveryReward::<T>::insert(&module_id, amount);
			Self::deposit_event(Event::OutboundRequestDeliveryRewardUpdated {
				module_id,
				new_reward: amount,
			});
			Ok(())
		}
```

**File:** docs/outbound-request-incentivization.md (L19-21)
```markdown
This is structurally identical to the existing `claim_outbound_consensus_delivery_reward` (see `modules/pallets/relayer/src/outbound_consensus.rs`) on the consensus side. The request claim lives in its own `modules/pallets/relayer/src/outbound_request.rs` module that mirrors it: swap "consensus rotation delivered" for "request delivered," key the reward storage by `module_id`, and have the relayer ship the full `PostRequest` in the claim so the pallet can hash it on chain.

No changes to pallet-hyperbridge or to any of the system-message dispatch sites. The reward is decoupled from the dispatch path and paid out at claim time against a destination state proof.
```

**File:** modules/pallets/host-executive/src/lib.rs (L225-231)
```rust
			let dispatcher = <T as Config>::IsmpHost::default();
			dispatcher
				.dispatch_request(
					DispatchRequest::Post(post),
					FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() },
				)
				.map_err(|_| Error::<T>::DispatchFailed)?;
```
