## Title
Missing minimum enforcement on `StateMachineCommitmentCap` allows premature eviction of in-flight state commitments - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`update_commitment_caps` in `pallet-ismp` only validates that a per-chain commitment retention cap is `> 0`, with no minimum tied to the chain's challenge period or expected in-flight message volume. This is the same bug class as the reported `EpochLimit` issue: a low-but-nonzero configuration value is accepted even though values below a safety threshold can cause the pruning logic to delete data still required for correct protocol operation.

### Finding Description
`pallet-ismp` retains verified `StateCommitment`s per state machine in a bounded FIFO queue (`StateCommitmentQueue`/`BoundedStateCommitments`), evicting the oldest entries once the configured cap is exceeded: [1](#0-0) 

The cap itself is set via the admin-only extrinsic `update_commitment_caps`, whose only validation is that the value is nonzero: [2](#0-1) 

However, incoming `Request`/`Response`/`Timeout` messages can only be verified against a state commitment while it still exists in storage and while the configured `challenge_period` has elapsed: [3](#0-2) [4](#0-3) 

Once a height is evicted from `BoundedStateCommitments`, lookups return `StateCommitmentNotFound` and can never be verified against again: [5](#0-4) 

The test suite confirms the eviction mechanics — with a cap of `2`, only the two most-recent heights remain provable and older heights become permanently unverifiable: [6](#0-5) 

Just like the reported `EpochLimit` case (`core/blockchain.go#L1438-L1444`, where any value below 3 could delete data required for chain operation), nothing in `update_commitment_caps` enforces that the retained window covers at least the state machine's `challenge_period` plus a safety margin for relay latency. A well-intentioned admin (or the seeded migration constants themselves, which size caps only against block cadence, not challenge period) can configure a cap that is smaller than the number of state machine updates that occur within one challenge period.

### Impact Explanation
If the cap is set too low relative to how frequently `update_client` advances a chain's commitments, honestly-submitted `Request`/`Response`/`Timeout` messages relayed by ordinary (unprivileged) relayers can permanently fail `StateCommitmentNotFound` even though their challenge period has not elapsed yet — the commitment they need is evicted before it can ever be used to verify membership/non-membership proofs. This makes the affected route "unable to deliver messages" for messages dispatched during that window, and any funds/fees locked pending those message deliveries become permanently stuck (no retry path exists once the commitment height is gone, since `previous_commitment_height`/consensus updates only ever advance forward). This matches the report's medium-risk impact category: a configuration value without an enforced safety minimum silently deletes data required for correct protocol operation.

### Likelihood Explanation
Requires an admin (via `T::AdminOrigin`) to set a cap without realizing it must exceed `challenge_period / average block time` for that chain — an honest misconfiguration, not a malicious admin action, exactly mirroring the original `EpochLimit` report's framing. The docstring for `update_commitment_caps` even encourages sizing caps purely by "finality cadence", never mentioning `challenge_period`, making this misconfiguration plausible in practice.

### Recommendation
Enforce a minimum on `update_commitment_caps` (and on the seeded migration constants in `modules/pallets/ismp/src/migrations.rs`) that is derived from the configured `challenge_period` for that `StateMachineId` divided by the expected block interval, plus a safety margin — analogous to enforcing `EpochLimit >= 3` while still allowing an explicit "unlimited" sentinel if desired. Reject cap updates that would evict commitments still inside their challenge period.

### Proof of Concept
1. Admin calls `create_consensus_client` / `update_consensus_state` setting `challenge_period` to, e.g., 5 minutes for chain X.
2. Admin calls `update_commitment_caps` with `cap = 2` for chain X (passes validation since `2 > 0`).
3. Consensus relayer submits several `update_client` messages in quick succession (each carrying several new `StateCommitment`s for chain X), causing `insert_bounded_state_commitment` to evict older heights per [7](#0-6) .
4. A relayer submits a `Request` message with a proof against a height that was evicted before its 5-minute challenge period elapsed — `validate_state_machine` now fails permanently with `StateCommitmentNotFound`/`ChallengePeriodNotElapsed` can never resolve because the referenced state commitment no longer exists, per [5](#0-4) .
5. The corresponding cross-chain message can never be delivered; any escrowed relayer fee/funds tied to it are permanently stuck.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L490-507)
```rust
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().writes(commitment_caps.len() as u64))]
		#[pallet::call_index(5)]
		pub fn update_commitment_caps(
			origin: OriginFor<T>,
			commitment_caps: BTreeMap<StateMachineId, u32>,
		) -> DispatchResult {
			T::AdminOrigin::ensure_origin(origin)?;

			ensure!(
				commitment_caps.values().all(|cap| *cap > 0),
				Error::<T>::InvalidCommitmentCap
			);
			for (id, cap) in commitment_caps {
				StateMachineCommitmentCap::<T>::insert(id, cap);
			}

			Ok(())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L747-770)
```rust
		pub fn insert_bounded_state_commitment(
			height: StateMachineHeight,
			commitment: StateCommitment,
		) {
			let cap = Self::state_machine_commitment_cap(height.id).max(1) as u64;
			let mut state = CommitmentQueueStates::<T>::get(height.id);

			StateCommitmentQueue::<T>::insert(height.id, state.tail, height.height);
			state.tail += 1;

			let excess = (state.tail - state.head)
				.saturating_sub(cap)
				.min(MAX_COMMITMENT_EVICTIONS_PER_INSERT as u64);
			for _ in 0..excess {
				if let Some(old) = StateCommitmentQueue::<T>::take(height.id, state.head) {
					BoundedStateCommitments::<T>::remove(height.id, old);
					BoundedStateMachineUpdateTime::<T>::remove(height.id, old);
				}
				state.head += 1;
			}

			CommitmentQueueStates::<T>::insert(height.id, state);
			BoundedStateCommitments::<T>::insert(height.id, height.height, commitment);
		}
```

**File:** modules/ismp/core/src/handlers.rs (L104-114)
```rust
pub fn verify_delay_passed<H>(host: &H, proof_height: &StateMachineHeight) -> Result<bool, Error>
where
	H: IsmpHost,
{
	let update_time = host.state_machine_update_time(*proof_height)?;
	let delay_period = host
		.challenge_period(proof_height.id)
		.ok_or(Error::ChallengePeriodNotConfigured { state_machine: proof_height.id })?;
	let current_timestamp = host.timestamp();
	Ok(delay_period.as_secs() == 0 || current_timestamp.saturating_sub(update_time) > delay_period)
}
```

**File:** modules/ismp/core/src/handlers.rs (L121-147)
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
```

**File:** modules/pallets/ismp/src/host.rs (L59-65)
```rust
	fn state_machine_commitment(
		&self,
		height: StateMachineHeight,
	) -> Result<StateCommitment, Error> {
		BoundedStateCommitments::<T>::get(height.id, height.height)
			.ok_or_else(|| Error::StateCommitmentNotFound { height })
	}
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp.rs (L716-776)
```rust
#[test]
fn lowering_the_cap_drains_the_queue_gradually() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		let host = Ismp::default();
		let id = queue_test_state_machine();
		let store = |height: u64| {
			host.store_state_machine_commitment(
				StateMachineHeight { id, height },
				queue_test_commitment(),
			)
			.unwrap();
		};

		pallet_ismp::Pallet::<Test>::update_commitment_caps(
			RuntimeOrigin::root(),
			BTreeMap::from([(id, 8)]),
		)
		.unwrap();
		for height in 1..=8u64 {
			store(height);
		}
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 0, tail: 8 }
		);

		pallet_ismp::Pallet::<Test>::update_commitment_caps(
			RuntimeOrigin::root(),
			BTreeMap::from([(id, 2)]),
		)
		.unwrap();

		// 9 live vs cap 2: only MAX_COMMITMENT_EVICTIONS_PER_INSERT entries are
		// evicted per insertion, so the excess drains over several insertions.
		store(9);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 4, tail: 9 }
		);
		store(10);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 8, tail: 10 }
		);
		store(11);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 9, tail: 11 }
		);
		// At the cap: steady state, one eviction per insertion.
		store(12);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 10, tail: 12 }
		);
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 10 }).is_err());
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 11 }).is_ok());
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 12 }).is_ok());
	})
}
```
