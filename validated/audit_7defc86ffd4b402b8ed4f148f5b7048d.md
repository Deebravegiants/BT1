I have enough context to write the final analog finding.

### Title
Flat, uniform `OutboundConsensusDeliveryReward` / `StateMachinesCostPerBlock` incentives that ignore per-destination delivery cost let governance-set rewards leak treasury value on cheap routes and strand expensive routes without delivery - (File: `modules/pallets/relayer/src/lib.rs`, `modules/pallets/relayer/src/outbound_consensus.rs`, `modules/pallets/consensus-incentives/src/lib.rs`)

### Summary
Hyperbridge pays relayers a single, governance-configured reward per destination for delivering mandatory consensus (authority-set rotation) proofs — `OutboundConsensusDeliveryReward` keyed only by `StateMachine` [1](#0-0)  — and a single per-block reward for inbound consensus relaying — `StateMachinesCostPerBlock` keyed only by `StateMachineId` [2](#0-1) . Exactly as the referenced report describes for AMM incentive pools of differing risk, these two flat reward maps must be manually and correctly calibrated per destination chain even though the real cost of delivering a proof (destination gas price, calldata size, state-proof verification complexity) varies enormously between chains. There is no on-chain mechanism tying the configured reward to actual delivery cost.

### Finding Description
`OutboundConsensusDeliveryReward` is a flat `StorageMap<StateMachine, BalanceOf<T>>` set only by governance and paid out unconditionally once a relayer proves delivery via `process_outbound_consensus_delivery_claim` [3](#0-2) . Similarly, `StateMachinesCostPerBlock` pays `(LatestHeight - PreviousHeight) * CostPerBlock` from the treasury for every consensus update on a chain, with `CostPerBlock` set once per state machine via `update_cost_per_block` [4](#0-3)  and applied identically regardless of how expensive or urgent that chain's updates actually are [5](#0-4) .

Neither reward map has any structural tie to the destination chain's real cost profile. Documentation confirms the reward exists specifically "to offset the gas cost of keeping that chain's on-chain Hyperbridge consensus client current" and that "without this incentive, destinations that see infrequent user traffic would be unprofitable to keep up to date" [6](#0-5) . This is the exact incentive-mismatch bug class in the referenced report: a single incentive value applied across pools/routes of materially different risk/cost, when the correct design requires the incentive to scale with that risk/cost. Because the constant is set once by governance and left uniform, any destination whose delivery cost is under-priced relative to its configured reward silently drains the treasury on every rotation/update (relayers are indifferent to how the chain compares — they simply pursue the highest-margin route), while any destination whose delivery cost is under-compensated becomes economically irrational for any relayer to service, so it never receives the mandatory authority-set rotation. Per the docs, an EVM destination's on-chain consensus client "falls behind and stops accepting Hyperbridge proofs altogether" once it misses a rotation [7](#0-6) , permanently freezing message delivery for that route until governance manually intervenes and top-ups/patches the constant.

### Impact Explanation
- Chains with an over-priced flat reward relative to actual delivery gas cost leak Hyperbridge treasury `$BRIDGE` funds to relayers indefinitely, with no automatic correction mechanism — a systemic value leak identical in mechanism to the referenced report's "protocol leaks value."
- Chains with an under-priced flat reward relative to actual delivery cost become unprofitable to service. No unprivileged relayer will submit the mandatory rotation, so the destination's on-chain client falls behind and the route becomes permanently unable to accept or verify further Hyperbridge state (a frozen, undeliverable route) until governance manually raises the constant — which is itself a slow, discrete, per-chain governance action that does not automatically track gas-price volatility.
- Both outcomes are reachable purely by an unprivileged relayer choosing which destination(s) to service based on the mismatch between the fixed reward and the real cost, with zero code-level defenses against either failure mode.

### Likelihood Explanation
Gas prices, calldata size for state/consensus proofs, and destination congestion vary continuously and can diverge sharply between EVM destinations (e.g., an L1 vs. a rollup, or a chain undergoing a gas-price spike). Since `OutboundConsensusDeliveryReward` and `StateMachinesCostPerBlock` are static values requiring a privileged extrinsic to update, any drift between the configured constant and real-world cost is virtually guaranteed over time and across the growing set of destinations, mirroring exactly the "developers must carefully choose incentive amounts per pool/route" caveat raised in the referenced report.

### Recommendation
Do not rely on a single flat, manually-set reward per destination/state machine. Either (a) derive the reward dynamically from an on-chain or oracle-fed estimate of the destination's current gas price and proof size, (b) require the reward to be re-validated/re-calibrated on a bounded cadence with alerts when observed relayer delivery cost diverges from the configured value, or (c) document explicitly (as Sushi ultimately did) that governance must proactively and continuously monitor per-chain gas costs and keep `OutboundConsensusDeliveryReward` / `StateMachinesCostPerBlock` tightly tracked to them, with monitoring/alerting for chains whose configured reward has drifted from real delivery cost in either direction.

### Proof of Concept
1. Governance sets `OutboundConsensusDeliveryReward[ChainA] = X` and `OutboundConsensusDeliveryReward[ChainB] = X` (same flat value) because both are EVM destinations, without accounting for ChainA's calldata-heavy proof verification being 10x more expensive in gas than ChainB's.
2. Gas prices later shift: ChainA's actual delivery cost rises above `X`, ChainB's stays well below `X`.
3. Rational relayers stop submitting ChainA's mandatory authority-set rotations (unprofitable) while continuing to submit ChainB's, over-earning the difference (`X` − real cost) from the treasury every single rotation via `process_outbound_consensus_delivery_claim` [3](#0-2) .
4. ChainA's on-chain `EvmHost` consensus client falls behind the current authority set and, per the documented behavior, "stops accepting Hyperbridge proofs altogether" [7](#0-6)  — the route to ChainA is now undeliverable — while the treasury continues bleeding funds to relayers servicing ChainB at an inflated margin.

### Citations

**File:** modules/pallets/relayer/src/lib.rs (L152-159)
```rust
	/// Per-destination reward, in the runtime's [`Config::Currency`], paid to
	/// the relayer that delivers a mandatory (authority-set rotation)
	/// consensus proof to that destination. `0` (the default) means rewards
	/// are off for the chain.
	#[pallet::storage]
	#[pallet::getter(fn outbound_consensus_delivery_reward)]
	pub type OutboundConsensusDeliveryReward<T: Config> =
		StorageMap<_, Blake2_128Concat, StateMachine, BalanceOf<T>, ValueQuery>;
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

**File:** docs/content/developers/explore/relayers.mdx (L181-190)
```text
- **Authority-set rotations (mandatory).** When the Hyperbridge
  validator set rotates, every destination chain must be notified or
  its on-chain client will fall behind and stop accepting Hyperbridge
  proofs altogether. The outbound task always propagates these, even
  if there are no messages targeting that chain.
- **Messaging-only proofs (opportunistic).** When an accepted proof
  carries no authority-set change, the relayer skips destinations
  with no pending messages, avoiding gas on chains that gain nothing
  from the update.

```

**File:** docs/content/developers/explore/relayers.mdx (L211-224)
```text
## Mandatory consensus proof rewards (EVM chains)

When the outbound task delivers an authority-set rotation (a
*mandatory* consensus proof) to an EVM destination, the destination
chain pays the relayer a reward on top of whatever messaging incentives
travel in the same transaction. This offsets the gas cost of keeping
that chain's on-chain Hyperbridge consensus client current even when
no user message would otherwise justify the delivery.

Tesseract claims this reward automatically in the background after a
successful mandatory consensus proof delivery — operators do not need
to take any extra action. Without this incentive, destinations that
see infrequent user traffic would be unprofitable to keep up to date;
with it, every EVM destination stays current.
```
