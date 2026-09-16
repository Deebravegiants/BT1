### Title
`update_cost_per_block` retroactively repricing unrewarded consensus block spans lets a relayer drain the treasury - ([File: modules/pallets/consensus-incentives/src/impls.rs])

### Summary
`pallet-consensus-incentives` pays relayers `(latest_height - baseline) * StateMachinesCostPerBlock` for delivering a `ConsensusMessage` that advances a state machine's verified height. The per-block rate is fetched at the moment the reward is computed rather than being tied to the point in time the corresponding blocks were actually verified. Because the rate update (`update_cost_per_block`) never accrues/settles the pending unpaid span first, any backlog of already-finalized-but-unrewarded blocks gets priced at whatever the *new* rate is when the next relayer submits a proof — exactly the same bug class as the Ion Protocol `updateInterestRateModule` finding, where a new module is applied to interest that accrued under the old one.

### Finding Description
Reward accounting is watermark-based: `LastRewardedHeight` tracks the highest height already paid for, and `calculate_reward` computes the unpaid span from that watermark to the freshly confirmed `latest_commitment_height`: [1](#0-0) 

The rate itself is read live from storage with no linkage to when the underlying blocks were verified: [2](#0-1) 

`update_cost_per_block` is a simple `mutate` of `StateMachinesCostPerBlock` with no call to settle/flush any pending unrewarded span (no equivalent of "accrue interest" before changing the rate, and no reset of `LastRewardedHeight` to the current height): [3](#0-2) 

Consequence: if a state machine's remote height has advanced (state commitments already stored, e.g. via prior consensus updates or relayer submissions) without yet triggering a `ConsensusMessage`-driven `on_executed` reward pass, and governance then raises `cost_per_block` (a routine operational parameter change, not malicious governance), the very next relayer to submit any consensus proof collects `(latest_height - baseline) * NEW_rate` for the *entire* backlog span — priced at the new, higher rate — even though that backlog accrued while the old (lower) rate was in effect. This is functionally identical to the Ion Protocol IRM issue: `_calculateRewardAndDebtDistributionForIlk` applies the newly-assigned module to a `block.timestamp - ilk.lastRateUpdate` span that predates the assignment, because `updateInterestRateModule` doesn't call `_accrueInterest` first.

The reward path is reachable by an ordinary, unprivileged relayer: `on_executed` is invoked by `pallet-ismp`'s message-execution pipeline (`FeeHandler::on_executed`, wired from `handle_unsigned`/consensus-message handling) after any relayer delivers a signed consensus proof — no special permission is required to trigger the payout calculation, only to change the rate. [4](#0-3) 

### Impact Explanation
A relayer can receive a payout sized by a backlog of blocks multiplied by a rate that was never in effect while those blocks were verified. If governance increases `cost_per_block` (e.g., to reflect higher operating costs on a fast-growing chain) while a multi-thousand-block unrewarded span exists, the first relayer to submit any qualifying proof extracts treasury funds far in excess of what was budgeted/intended for that historical span — a direct, unbacked drain of the `TreasuryAccount` funds (both the token transfer and the matching reputation mint). This is a concrete loss-of-funds condition for the protocol treasury, triggerable by a single unprivileged consensus-message submission timed around a routine rate update.

### Likelihood Explanation
Likelihood is low-to-moderate: it requires (a) an unrewarded backlog to exist (plausible any time a chain is momentarily inactive, newly onboarded, or between reward-eligible messages) and (b) a `cost_per_block` change while that backlog is outstanding. Because rate changes are a normal, expected governance operation (not a compromise), and relayers can simply watch for such updates and immediately submit a pending proof to capture the mispriced backlog, an opportunistic (but otherwise honest) relayer can reliably exploit this whenever the conditions align — mirroring the acknowledged-but-accepted nature of the original Ion Protocol finding, except here the counterparty is an ordinary relayer rather than the protocol's own admin reverting a broken module.

### Recommendation
Before committing a new `cost_per_block` in `update_cost_per_block`, settle the pending span at the *old* rate (mirroring "accrue interest before changing the rate module"): compute and pay/reserve the reward for `latest_commitment_height - LastRewardedHeight` using the current rate, and advance `LastRewardedHeight` to `latest_commitment_height`, before writing the new rate into `StateMachinesCostPerBlock`. Alternatively, snapshot `LastRewardedHeight` to the current `latest_commitment_height` at the moment of a rate change (forfeiting the backlog reward rather than mispricing it), ensuring the new rate only ever applies to blocks confirmed after the update.

### Proof of Concept
1. State machine `X` has consensus commitments verified up to height `H_backlog` (e.g., via `store_state_machine_commitment`/`store_latest_commitment_height`), but no `ConsensusMessage`-triggered `on_executed` reward pass has run since `LastRewardedHeight` was last set (or it was never set, defaulting to `previous_commitment_height`), leaving a large `(H_backlog - baseline)` span unpaid.
2. Governance calls `update_cost_per_block(state_machine_id, new_high_rate)` — a routine, non-malicious parameter update, analogous to the Ion Protocol admin calling `updateInterestRateModule`.
3. Any relayer submits a normal signed `ConsensusMessage` for state machine `X` (even one that only advances the height slightly further, to `H_backlog + 1`), which reaches `pallet-ismp`'s `handle_unsigned` and fires `FeeHandler::on_executed`.
4. `calculate_reward` computes `reward = (latest_height - baseline) * new_high_rate`, covering the entire backlog `(H_backlog - baseline)` at the new rate instead of the rate(s) actually in force while those blocks were verified, transferring an inflated amount from `TreasuryAccount` to the relayer (test scaffolding for the reward/watermark mechanics is visible in `modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs:121-219`, which demonstrates how `LastRewardedHeight` and block-span rewards are computed and would need to be extended to show the rate-change timing).

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L46-75)
```rust
		if let Some(block_cost) = StateMachinesCostPerBlock::<T>::get(state_machine_id) {
			let reward = Self::calculate_reward(&state_machine_id, block_cost)?;

			if reward.is_zero() {
				return Ok(());
			}

			T::Currency::transfer(
				&T::TreasuryAccount::get().into_account_truncating(),
				&relayer_account,
				reward,
				Preservation::Expendable,
			)
			.map_err(|_| Error::<T>::RewardTransferFailed)?;

			Self::deposit_event(Event::<T>::RelayerRewarded {
				relayer: relayer_account.clone(),
				amount: reward,
				state_machine_height,
			});

			T::ReputationAsset::mint_into(&relayer_account, reward.saturated_into())
				.map_err(|_| Error::<T>::ReputationMintFailed)?;

			LastRewardedHeight::<T>::mutate(state_machine_id, |watermark| {
				*watermark = Some(watermark.unwrap_or_default().max(state_machine_height.height));
			});
		}
		Ok(())
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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L104-157)
```rust
impl<T: Config> FeeHandler for Pallet<T>
where
	<T as frame_system::Config>::AccountId: From<[u8; 32]>,
{
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
