Confirmed: `process_outbound_consensus_delivery_claim` at `modules/pallets/relayer/src/outbound_consensus.rs:174-175` reads `OutboundConsensusDeliveryReward::<T>::get(destination)` **at claim time**, not a value snapshotted when the relayer actually performed the delivery. This is structurally identical to the Sherlock finding: the "reward rate" is a single live governance-controlled parameter, and a relayer's entitlement is only realized against whatever that parameter currently holds — there is no per-delivery locked/accrued amount recorded when the qualifying work (mandatory rotation delivery, attested by `EvmHost._epochs[set_id]`) actually happened.

### Title
Unclaimed outbound-delivery rewards are permanently lost if governance lowers/removes the reward after the qualifying delivery but before the relayer claims - (File: modules/pallets/relayer/src/outbound_consensus.rs, modules/pallets/relayer/src/outbound_request.rs)

### Summary
`pallet-ismp-relayer` pays relayers for delivering mandatory BEEFY consensus rotations (`claim_outbound_consensus_delivery_reward`) and hyperbridge-originated requests (`claim_outbound_request_delivery_reward`). Both claims are two-phase: (1) the relayer performs the delivery on-chain (an event visible immediately, e.g. `EvmHost._epochs[set_id]` being set, or `RequestReceipts[commitment]` on the destination), and (2) at some later time the relayer submits a claim with a state proof of that delivery to actually collect the reward. The reward amount paid out is read from the *current* value of `OutboundConsensusDeliveryReward`/`OutboundRequestDeliveryReward` at claim time, not a value fixed at delivery time.

### Finding Description
In `process_outbound_consensus_delivery_claim`: [1](#0-0) 
the reward is looked up live via `OutboundConsensusDeliveryReward::<T>::get(destination)` and rejected with `OutboundNoRewardConfigured` if it is zero. The same pattern is documented for the request-delivery claim: [2](#0-1)  "Allowlist lookup. `reward = OutboundRequestDeliveryReward::<T>::get(module_id)`. If zero, reject." Both reward maps are mutated in place by an unrestricted "update" extrinsic that has no awareness of deliveries that already occurred and are simply awaiting a claim: [3](#0-2) [4](#0-3) 

This is the same root cause as the reported `SingleSidedLiquidityVault` bug: the protocol tracks "reward eligibility" as a single live/global rate rather than snapshotting the amount owed at the moment the qualifying work was verifiably done on-chain. A relayer can win the "delivery race" (deliver a mandatory rotation, or a hyperbridge-originated request) and be entitled to a reward the moment the on-chain attribution slot (`EvmHost._epochs[set_id]` / `RequestReceipts[commitment]`) is populated, but that entitlement is not persisted anywhere — it only exists implicitly as "current reward map value × not yet in the claimed-idempotency set." If the reward for that destination/module is lowered or zeroed before the relayer's claim lands (competing block inclusion, network delay, relayer downtime, or simply governance turning off a program), the relayer permanently loses the reward for work already performed: the claim either reverts with `OutboundNoRewardConfigured`/`OutboundRequestNoRewardConfigured`, or silently pays out the new (lower) amount instead of what was promised when the delivery happened. Because `OutboundConsensusRotationsClaimed`/`OutboundRequestsClaimed` only track "claimed or not", there is no way to retroactively recover the original amount even if governance restores the reward later — the value fetched at that later time is whatever it currently is, not what it was at delivery time.

### Impact Explanation
A relayer who has already performed the incentivized on-chain work (delivering a rotation or a hyperbridge-originated request to the destination, which itself costs real gas) can have their earned reward reduced to zero or an arbitrary lower amount purely by a config update racing their claim transaction. This is a direct, permanent loss of promised relayer compensation for completed work — funds the relayer economically relied on when deciding to perform (and pay gas for) the delivery. Given rewards are paid from the treasury `PalletId` account and the claim is otherwise fully verified (state proof + signature), the only missing piece is amount-locking at the time of qualifying work, matching the Medium-severity pattern in the original report.

### Likelihood Explanation
This does not require any malicious actor: it can occur any time governance recalibrates `OutboundConsensusDeliveryReward` or `OutboundRequestDeliveryReward` (a routine, expected maintenance action — the docs describe these as tunable, per-chain/per-module knobs) while any relayer has an in-flight, unclaimed delivery. Given delivery and claim are separated by consensus-proof latency, challenge periods, and relayer-side background task scheduling (`tesseract/messaging/messaging/src/outbound_claim.rs`), there is a realistic window during which an in-flight reward can be invalidated by a routine parameter update.

### Recommendation
Snapshot the reward amount at the moment the qualifying delivery event is durably recorded (e.g., store `(destination, set_id) -> reward_at_delivery` or `(module_id) -> reward_at_dispatch` alongside/instead of only an idempotency flag), and pay out that snapshotted amount on claim rather than re-reading the live reward map. Alternatively, require the reward-update extrinsic to only take effect for deliveries whose attribution slot is populated after the update, and reference the previous stored reward value for anything already delivered/verifiable before the update landed.

### Citations

**File:** modules/pallets/relayer/src/outbound_consensus.rs (L174-186)
```rust
		let reward = OutboundConsensusDeliveryReward::<T>::get(destination);
		ensure!(reward > BalanceOf::<T>::default(), Error::<T>::OutboundNoRewardConfigured);

		let treasury: T::AccountId =
			<T as Config>::TreasuryPalletId::get().into_account_truncating();
		let payee_account: T::AccountId = payee.into();
		<<T as pallet_ismp::Config>::Currency as Mutate<T::AccountId>>::transfer(
			&treasury,
			&payee_account,
			reward,
			Preservation::Preserve,
		)
		.map_err(|_| Error::<T>::OutboundRewardTransferFailed)?;
```

**File:** docs/outbound-request-incentivization.md (L126-126)
```markdown
6. **Allowlist lookup.** `reward = OutboundRequestDeliveryReward::<T>::get(module_id)`. If zero, reject. This is the only place the allowlist is enforced; governance enables a module by setting a non-zero reward.
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
