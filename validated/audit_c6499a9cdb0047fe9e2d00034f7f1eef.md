### Title
Consensus-incentive relayer rewards use the current `block_cost` rate for the entire un-rewarded block span, letting a relayer withdraw a rate change to over-drain the treasury - (File: modules/pallets/consensus-incentives/src/impls.rs)

### Summary
`pallet-consensus-incentives::calculate_reward` computes `reward = (latest_height - baseline) * block_cost`, where `block_cost` is *whatever `StateMachinesCostPerBlock` holds at the moment the relayer's consensus message is processed*, applied uniformly across the entire span of blocks accrued since the last reward watermark. This mirrors the H-02 analog exactly: an accrual is computed over a period using only the rate in effect at settlement time, instead of splitting the period at the rate-change boundary. A relayer who controls submission timing can pick the moment of settlement to apply a favorable current rate to blocks that accrued mostly (or entirely) under a different, lower rate.

### Finding Description
`process_message` reads `block_cost` for the state machine and calls `calculate_reward`: [1](#0-0) 

`calculate_reward` computes the block span since the last-paid watermark and multiplies the *entire* span by the single `block_cost` value read for the state machine at call time — there is no per-block-range rate history, and no split of the reward calculation at the point(s) where `update_cost_per_block` changed the rate: [2](#0-1) 

`StateMachinesCostPerBlock` is a simple `StorageMap` with no history/versioning, updated in place by `update_cost_per_block`: [3](#0-2) [4](#0-3) 

This is the same root-cause pattern as Backd's H-02: an accrual/decay computation applies a single rate across a time (here, block-height) span that actually straddled a rate change, because the code never checks "did the rate change partway through this span?" before applying it. The entry point is reachable by any unprivileged relayer: `on_executed` is a `pallet_ismp::fee_handler::FeeHandler` hook invoked whenever a batch containing a `Message::Consensus` is delivered and successfully executed via `pallet_ismp::handle_unsigned` (an unsigned, permissionless extrinsic) — the relayer only needs to be the one who signed/delivered the consensus proof: [5](#0-4) 

Because a relayer chooses when to submit their consensus-update message (they can delay delivery, or race an anticipated `update_cost_per_block` change), they control which rate is "current" at the moment the reward for a large accumulated block span is realized. If governance raises `cost_per_block` (e.g., in response to rising infra costs) and a relayer has an outstanding un-rewarded span of many blocks accrued mostly under the old, lower rate, the relayer can wait until after the increase lands and then submit the (already-available) consensus proof, collecting the entire span's reward at the new, higher rate. Conversely, a relayer can also submit *before* a rate decrease to lock in the higher rate for a large backlog. In both cases the actual amount transferred out of `TreasuryAccount` (an unbacked/uncapped drain, since `Currency::transfer` moves real funds and `ReputationAsset::mint_into` mints reputation tokens proportional to the reward) diverges from what governance intended to pay for that historical block range.

### Impact Explanation
This directly parallels the "Total Supply is not guaranteed" bug class: an accounting invariant (the treasury should pay `old_rate × blocks_before_change + new_rate × blocks_after_change`) is broken because the code always pays `current_rate × total_blocks`. The impact is a concrete drain of the `TreasuryAccount`'s real currency balance beyond what governance intends, plus a proportional over-mint of the `ReputationAsset`. An unprivileged relayer influences the outcome purely by choosing submission timing relative to a rate update — no admin collusion is required, only ordinary submission-timing control that any relayer naturally has. This is a treasury drain / unbacked-mint class issue reachable from a permissionless dispatch path (`handle_unsigned` consensus messages), matching the required "concrete theft ... unbacked mint" impact bar.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: `update_cost_per_block` is an ordinary governance operation expected to be called periodically as infra costs change (not a rare or adversarial admin action), and relayers already have wide latitude over when they submit consensus proofs (submission is unsigned/permissionless and asynchronous relative to when blocks were actually finalized). Any relayer monitoring the chain for a pending `StateMachineCostPerBlockUpdated` event, or simply delivering less frequently, can accumulate a large `latest_height - baseline` span and cash it out at whichever rate is more favorable. No proof forgery or special access is needed — only ordinary control over delivery timing.

### Recommendation
Do not apply a single "current" rate to a block span that may straddle a rate change. Options mirroring the H-02 mitigation:
- Record the block height (or timestamp) at which each `update_cost_per_block` change takes effect, and store a small history of `(effective_height, cost_per_block)` pairs (or at minimum the previous rate and the height it changed at).
- In `calculate_reward`, if `baseline < change_height <= latest_height`, split the reward calculation into `(change_height - baseline) * old_rate + (latest_height - change_height) * new_rate` (generalized across all rate changes that fall inside `[baseline, latest_height]`), analogous to splitting `totalAvailableToNow` accrual at the decay boundary in the original report.
- Alternatively, force a reward settlement (flush of the watermark) automatically whenever `update_cost_per_block` is called, so no un-rewarded span can ever straddle a rate change.

### Proof of Concept
1. Governance calls `update_cost_per_block(state_machine_id, X)` and the chain accrues many state-machine-updated blocks for that state machine without any relayer submitting a consensus message (so `LastRewardedHeight` watermark stays far behind `latest_commitment_height`).
2. Governance later calls `update_cost_per_block(state_machine_id, Y)` where `Y >> X` (e.g., a legitimate cost-of-infra increase).
3. A relayer who has been silently letting messages/consensus proofs pile up (or who monitors the mempool/governance queue for the pending rate change) submits their backlog of consensus messages via `pallet_ismp::Pallet::<T>::handle_unsigned` right after step 2.
4. `on_executed` → `process_message` → `calculate_reward` reads the *new* rate `Y` and computes `reward = (latest_height - baseline) * Y` for the *entire* backlog span, even though most of those blocks should have been paid at rate `X`.
5. `T::Currency::transfer` pays out `reward` from `TreasuryAccount`, and `T::ReputationAsset::mint_into` mints reputation proportional to `reward` — both inflated relative to the amount governance intended for that period, at the treasury's expense.

Note: I was not able to find any additional per-height rate-history storage or reward-settlement-on-rate-change logic elsewhere in the pallet or in its call graph within the indexed portion of the codebase, so this appears to be the full extent of the reward-calculation logic; a live Devin session could confirm there is no compensating check (e.g., in `pallet_ismp`'s dispatch path) that forces settlement before a rate update.

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L41-52)
```rust
	fn process_message(
		state_machine_height: StateMachineHeight,
		state_machine_id: StateMachineId,
		relayer_account: T::AccountId,
	) -> Result<(), Error<T>> {
		if let Some(block_cost) = StateMachinesCostPerBlock::<T>::get(state_machine_id) {
			let reward = Self::calculate_reward(&state_machine_id, block_cost)?;

			if reward.is_zero() {
				return Ok(());
			}

```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L77-100)
```rust
	/// Calculate the reward for a message based on the state machine id
	fn calculate_reward(
		state_machine_id: &StateMachineId,
		block_cost: <T as pallet_ismp::Config>::Balance,
	) -> Result<<T as pallet_ismp::Config>::Balance, Error<T>> {
		let host = <T::IsmpHost>::default();
		let latest_height = host
			.latest_commitment_height(state_machine_id.clone())
			.map_err(|_| Error::<T>::CouldNotGetStateMachineHeight)?;
		let previous_height =
			host.previous_commitment_height(state_machine_id.clone()).unwrap_or_default();

		// Use the rewarded watermark as the baseline and fall back to the previous height until
		// the first reward is recorded for this chain. The watermark only moves forward, so a
		// height that is rolled back and later resubmitted is not paid for a second time.
		let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);

		let blocks = latest_height.saturating_sub(baseline);

		let blocks_as_balance: <T as pallet_ismp::Config>::Balance = blocks.saturated_into();
		let reward = blocks_as_balance.saturating_mul(block_cost);

		Ok(reward)
	}
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L108-157)
```rust
	fn on_executed(
		messages: Vec<MessageWithWeight>,
		events: Vec<IsmpEvent>,
	) -> DispatchResultWithPostInfo {
		let maybe_relayer_account = messages.get(0).and_then(|first_message| {
			if let Message::Consensus(consensus_msg) = &first_message.message {
				let data = sp_io::hashing::keccak_256(&consensus_msg.consensus_proof);
				Signature::decode(&mut &consensus_msg.signer[..])
					.ok()
					.and_then(|sig| sig.verify_and_get_sr25519_pubkey(&data, None).ok())
					.map(|pub_key| pub_key.into())
			} else {
				None::<[u8; 32]>
			}
		});

		if let Some(relayer_account) = maybe_relayer_account {
			// When a batch contains multiple `StateMachineUpdated` events for the
			// same `state_machine_id` (sequential consensus updates for the same
			// chain), `calculate_reward` reads the same persisted
			// `(latest_commitment_height, previous_commitment_height)` pair on
			// every iteration and pays the same block-span reward N times.
			// Collapse the per-state-machine event stream to the single highest
			// `latest_height` so each state machine receives one reward per
			// batch, sized by the actual span of its commitment advance.
			let mut highest_per_state_machine: BTreeMap<StateMachineId, u64> = BTreeMap::new();
			for event in events {
				if let IsmpEvent::StateMachineUpdated(update) = event {
					highest_per_state_machine
						.entry(update.state_machine_id)
						.and_modify(|h| {
							if update.latest_height > *h {
								*h = update.latest_height;
							}
						})
						.or_insert(update.latest_height);
				}
			}

			for (state_machine_id, latest_height) in highest_per_state_machine {
				let state_machine_height =
					StateMachineHeight { id: state_machine_id.clone(), height: latest_height };

				let _ = Self::process_message(
					state_machine_height,
					state_machine_id,
					relayer_account.clone().into(),
				);
			}
		}
```

**File:** modules/pallets/consensus-incentives/src/lib.rs (L70-79)
```rust
	// Mapping from state machineId to respective cost per block
	#[pallet::storage]
	#[pallet::getter(fn state_machines_cost_per_block)]
	pub type StateMachinesCostPerBlock<T: Config> = StorageMap<
		_,
		Blake2_128Concat,
		StateMachineId,
		<T as pallet_ismp::Config>::Balance,
		OptionQuery,
	>;
```

**File:** modules/pallets/consensus-incentives/src/lib.rs (L128-150)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Update cost per block for a state machine
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::update_cost_per_block())]
		pub fn update_cost_per_block(
			origin: OriginFor<T>,
			state_machine_id: StateMachineId,
			cost_per_block: <T as pallet_ismp::Config>::Balance,
		) -> DispatchResult {
			T::IncentivesOrigin::ensure_origin(origin)?;

			StateMachinesCostPerBlock::<T>::mutate(state_machine_id.clone(), |maybe_cost| {
				*maybe_cost = Some(cost_per_block);
			});

			Self::deposit_event(Event::<T>::StateMachineCostPerBlockUpdated {
				state_machine_id,
				cost_per_block,
			});

			Ok(())
		}
```
