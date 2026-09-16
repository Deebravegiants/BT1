### Title
Relayer loses reward for already-delivered work when governance reduces `OutboundRequestDeliveryReward`/`OutboundConsensusDeliveryReward` after delivery but before claim - ([File: modules/pallets/relayer/src/outbound_request.rs])

### Summary
`pallet-ismp-relayer` pays relayers for delivering hyperbridge-originated requests and mandatory consensus rotations via a two-phase flow: (1) the relayer delivers the message/proof to the destination, and (2) the relayer later submits a claim (`claim_outbound_request_delivery_reward` / `claim_outbound_consensus_delivery_reward`) with a state proof of the delivery receipt. The reward amount is read from live storage (`OutboundRequestDeliveryReward` / `OutboundConsensusDeliveryReward`) at claim time, not fixed at delivery time. If governance changes or zeroes that reward between delivery and claim, the relayer's proof of already-completed work becomes permanently unclaimable — mirroring the reported Sherlock bug class where removing a reward token loses users' already-accrued, unclaimed rewards.

### Finding Description
`process_outbound_request_delivery_claim` reads the reward value live and rejects the claim entirely if it is zero: [1](#0-0) 

The equivalent consensus-delivery path does the same: [2](#0-1) 

Both rewards are updated in place by governance calls that overwrite the storage value with no snapshotting of in-flight deliveries: [3](#0-2) [4](#0-3) 

There is no mechanism that records the reward amount at the time the module/destination was eligible and the relayer actually delivered the message (i.e., when the commitment landed in `RequestCommitments` / when the `NewEpoch` was recorded on the destination). The claim only checks the *current* reward value. Once a relayer has delivered a request or rotation — an action that is irreversible and off-chain-verifiable via `RequestReceipts`/`EvmHost._epochs` — reducing or zeroing the reward before the relayer submits the claim destroys the relayer's ability to ever collect payment for that already-completed, unrepeatable work. Unlike the removed reward-token case in the SherLock report where the state (`accumulatedRewardsPerShare`) is deleted, here the accrual state (idempotency keyed by `commitment`/`(destination,set_id)`) persists, but the payout amount used at claim time is decoupled from delivery time, so the same value-loss outcome occurs: work already performed is retroactively stripped of its promised reward.

The tesseract relayer's own claim pipeline confirms this is meant to be a routine, asynchronous, unprivileged flow — delivery and claim submission happen independently and are explicitly designed to be retried/replayed across relayer restarts: [5](#0-4) 

meaning there is always a real time window, potentially spanning multiple blocks or a relayer restart, during which a governance reward update can race an in-flight, already-completed delivery.

### Impact Explanation
Any relayer who delivers a hyperbridge-originated request or mandatory consensus rotation is entitled to the reward configured at delivery time. If governance lowers or removes that reward before the relayer's claim lands (a routine parameter update, not a malicious act), the relayer's proof of delivery becomes worthless: `OutboundRequestNoRewardConfigured` / `OutboundNoRewardConfigured` will be returned forever for that commitment/rotation, since the work cannot be "re-delivered" to earn under a new reward window. This is a permanent loss of an earned-but-unclaimed reward, directly analogous to the reported issue where removing a reward token loses previously accrued, unclaimed yield. Because relayers are the entities Hyperbridge depends on to shepherd governance/system messages (host-executive updates, intents-coprocessor responses, token-governor messages, BEEFY rotations) across chains, discouraging relayers from picking up this work via unpredictable reward retraction threatens delivery of critical protocol messages.

### Likelihood Explanation
This requires no attacker at all — it is a normal governance operation (adjusting a per-chain/per-module reward, which the docs describe as an expected, recurring parameter) combined with the inherent latency of the two-phase accumulate/claim design (state-proof construction, challenge-period waits, relayer restarts). The tesseract relayer code explicitly plans for claims to be pending across restarts and delays, so the race window is not a rare edge case but a designed-in gap between delivery and claim.

### Recommendation
Snapshot the reward amount at the point the relayer's eligibility is established (e.g., when the request/rotation delivery is durably recorded — `RequestCommitments` insertion or `NewEpoch`/receipt write) rather than reading live governance state at claim time. Concretely, either (a) store the reward-at-delivery keyed by `commitment`/`(destination, set_id)` when the reward is looked up for the first eligible claim window, or (b) apply reward reductions only prospectively (to deliveries/rotations that occur after the update), leaving already-delivered-but-unclaimed work payable at the old rate. At minimum, emit a clear on-chain notice and/or provide a grace-period claim path so relayers with in-flight deliveries are not silently and permanently denied payment when governance updates `OutboundRequestDeliveryReward`/`OutboundConsensusDeliveryReward`.

### Proof of Concept
1. Governance calls `set_outbound_request_delivery_reward(module_id, 1_000)` making `module_id` reward-eligible. [6](#0-5) 
2. A hyperbridge-originated `PostRequest` from `module_id` is dispatched and its commitment lands in `RequestCommitments`.
3. A relayer delivers this request to the destination chain; `RequestReceipts[commitment]` is written on the destination recording the relayer as the deliverer. The relayer's off-chain claim pipeline records this as a pending claim (per `tesseract/messaging/fees/prisma/schema.prisma` `OutboundRequestClaims` model, status "pending").
4. Before the relayer's claim transaction lands, governance calls `set_outbound_request_delivery_reward(module_id, 0)` (e.g. as part of routine reward-schedule maintenance, or turning off incentives for a module going forward).
5. The relayer submits `claim_outbound_request_delivery_reward` with a valid state proof of the `RequestReceipts[commitment]` entry and a valid signature.
6. `process_outbound_request_delivery_claim` reads `OutboundRequestDeliveryReward::<T>::get(&module_id)` = 0 and reverts with `OutboundRequestNoRewardConfigured`. [7](#0-6) 
7. `OutboundRequestsClaimed` was never marked, but the relayer has no way to re-earn a reward for a delivery that has already happened — the reward for this specific, completed piece of work is permanently lost.

### Citations

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

**File:** modules/pallets/relayer/src/outbound_consensus.rs (L174-175)
```rust
		let reward = OutboundConsensusDeliveryReward::<T>::get(destination);
		ensure!(reward > BalanceOf::<T>::default(), Error::<T>::OutboundNoRewardConfigured);
```

**File:** modules/pallets/relayer/src/lib.rs (L399-415)
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
		}
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

**File:** tesseract/messaging/messaging/src/outbound_claim.rs (L16-20)
```rust
//! Periodic task that claims outbound consensus delivery rewards.
//!
//! Each time the relayer delivers a mandatory BEEFY rotation to an EVM destination, the delivery
//! path writes a row to the local DB. This task wakes on a fixed interval, reads those rows,
//! skips anything already claimed on Hyperbridge, and submits the remaining claims in parallel.
```
