### Title
Stale state-commitment queue entries let one relayer resubmission cause an extra ("double") eviction that deletes a live, in-window state commitment — (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`ALPINE-CVE-2017-15186` is a double-free: FFmpeg frees the same buffer twice, corrupting memory that a later, legitimate operation still expects to be valid. The reachable analog in Hyperbridge is in `pallet_ismp`'s bounded state-commitment queue: `delete_state_commitment` (invoked when a state commitment is vetoed) intentionally leaves a stale index behind in `StateCommitmentQueue` instead of removing it. When the vetoed height is the *latest* height, the height is reopened and gets re-submitted by an ordinary consensus relayer, creating a **second** queue entry for the same height. The first (stale) entry is later reached by the FIFO eviction cursor and deletes the *live* `BoundedStateCommitments` entry for that height — a commitment that is still within the chain's configured retention cap and that in-flight requests/responses/timeouts may depend on for proof verification. This is structurally the same "double free" defect class: one logical resource (the state commitment slot for a height) ends up subject to two independent free/evict operations, and the second, spurious one destroys state that should still be alive.

### Finding Description
`insert_bounded_state_commitment` appends every stored height to a per-chain FIFO index (`StateCommitmentQueue`) and evicts from the head once the configured cap (`StateMachineCommitmentCap`) is exceeded: [1](#0-0) 

`delete_state_commitment` (used to veto an invalid/fraudulent state commitment) removes the `BoundedStateCommitments`/`BoundedStateMachineUpdateTime` entries but *deliberately* does not locate and remove the corresponding queue index, and resets `LatestStateMachineHeight` back to the previous height when the vetoed height was the latest one: [2](#0-1) 

Because the latest pointer is rolled back, the consensus handler (`update_client`, which only requires `commitment_height.height >= previous_latest_height`) will accept an honest resubmission of that same height from any relayer: [3](#0-2) 

The resubmission creates a fresh queue entry directly behind the stale one left by the veto. When the FIFO eviction cursor reaches the stale entry, it deletes the live commitment for that height — one insertion earlier than it should, and without any way to distinguish "this is a leftover stale index" from "this is the live index." This exact behavior is captured and accepted in the test suite: [4](#0-3) 

### Impact Explanation
The prematurely-evicted state commitment is exactly the artifact that `HandlerV2`/pallet-ismp membership and non-membership proofs are checked against for delivering requests, responses, and timeouts at that height. If pending messages have proofs anchored to that height and it is evicted one insertion earlier than the configured retention window promises, those in-flight messages become unprovable and can never be delivered or timed out through that height — this is a concrete "route unable to deliver messages" condition and can permanently strand escrowed relayer fees/funds tied to those messages if no other height covers the same window. This satisfies the Medium/High bar (unsound retention of state commitments, not merely a resource-only bug), reachable purely through the combination of one veto (an ordinary chain-security action, not "malicious governance") followed by completely ordinary, unprivileged relayer consensus-proof submissions.

### Likelihood Explanation
Triggering the double-eviction requires only: (1) the chain having vetoed an invalid state commitment at what happened to be the *latest* height (an expected, periodically-exercised operational path since vetoing is exactly how consensus fault proofs are handled), and (2) any relayer subsequently submitting a normal consensus proof that re-establishes that height (which is expected/encouraged behavior — the reset is explicitly designed to "re-open that height for honest resubmission"). No malicious actor or governance collusion is needed to trigger the destructive eviction; an honest relayer doing exactly what the protocol wants them to do is enough. The one-insertion-early eviction is deterministic once these two ordinary conditions occur, and the burnt queue slot compounds with every subsequent veto-on-latest-height event, degrading retention over time.

### Recommendation
Track a height→queue-index (or generation counter) so `delete_state_commitment` can invalidate exactly the queue entry it corresponds to instead of leaving a stale duplicate, or tag queue entries with a monotonic "commitment generation" that `insert_bounded_state_commitment`'s eviction path checks before deleting `BoundedStateCommitments`, so it only frees the entry that is still the live one for that height/generation, never a commitment that has since been legitimately re-stored.

### Proof of Concept
The existing regression test demonstrates the full trigger and impact end-to-end: [5](#0-4) 
It shows: store height 10 and 11 → veto height 11 (rolls latest back to 10) → an honest relayer resubmits height 11 (second queue entry created) → the next honest consensus update (height 12) evicts the *live* commitment for height 11 one insertion earlier than the configured cap of 2 should allow, verified by `host.state_machine_commitment(StateMachineHeight { id, height: 11 }).is_err()` immediately after `store(12)`.

### Citations

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

**File:** modules/pallets/ismp/src/host.rs (L194-222)
```rust
	fn delete_state_commitment(&self, height: StateMachineHeight) -> Result<(), Error> {
		// The height's entry in the state commitment queue is deliberately left
		// behind; locating it would mean scanning the queue, which is the per-insert
		// cost the queue exists to avoid. Usually its eviction is a no-op, but when
		// the vetoed height is the latest the reset below re-opens it for honest
		// resubmission, and the resubmitted height gets a *second* queue entry. The
		// stale entry then evicts the live commitment when it reaches the head —
		// one insertion before the live entry would have, since the resubmission
		// lands directly behind its stale twin. So a veto costs that height one
		// insertion of retention and permanently burns one queue slot. Both are
		// negligible against the configured caps; making it exact would need a
		// height -> index map on the insert path.
		BoundedStateCommitments::<T>::remove(height.id, height.height);
		BoundedStateMachineUpdateTime::<T>::remove(height.id, height.height);

		// technically any state commitment can be vetoed,
		// safety check that it's the latest before resetting it.
		if let Some(latest) = LatestStateMachineHeight::<T>::get(height.id) {
			if latest == height.height {
				// Reset back to the initial height to allow for honest updates
				let prev_height =
					PreviousStateMachineHeight::<T>::get(height.id).ok_or_else(|| {
						Error::Custom("Previous state machine height should exist".to_string())
					})?;
				LatestStateMachineHeight::<T>::insert(height.id, prev_height);
			}
		}
		Ok(())
	}
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L58-70)
```rust
			// Only allow heights greater than latest height
			if previous_latest_height > commitment_height.height {
				continue;
			}

			// Skip duplicate states
			if host.state_machine_commitment(state_height).is_ok() {
				continue;
			}

			last_commitment_height = Some(state_height);
			host.store_state_machine_commitment(state_height, commitment_height.commitment)?;
			host.store_state_machine_update_time(state_height, host.timestamp())?;
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp.rs (L829-882)
```rust
// Vetoing the *latest* height resets the latest pointer, which re-opens that height
// for honest resubmission. The resubmission gets a second queue entry, and the stale
// twin ahead of it evicts the live commitment one insertion early. This pins that
// wart: it costs the height one insertion of retention and burns one queue slot,
// which is negligible against the configured caps but is not a no-op.
#[test]
fn vetoed_latest_height_that_is_resubmitted_evicts_one_insertion_early() {
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
			host.store_latest_commitment_height(StateMachineHeight { id, height }).unwrap();
		};

		pallet_ismp::Pallet::<Test>::update_commitment_caps(
			RuntimeOrigin::root(),
			BTreeMap::from([(id, 2)]),
		)
		.unwrap();

		store(10);
		store(11);

		// Vetoing the latest height rolls the latest pointer back to 10, so the
		// consensus handler would accept 11 again: it is not below the latest and
		// its commitment is now absent.
		host.delete_state_commitment(StateMachineHeight { id, height: 11 }).unwrap();
		assert_eq!(host.latest_commitment_height(id).unwrap(), 10);

		store(11);
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 11 }).is_ok());
		// Two queue entries now point at height 11: the stale one and the live one.
		assert_eq!(StateCommitmentQueue::<Test>::get(id, 1), Some(11));
		assert_eq!(StateCommitmentQueue::<Test>::get(id, 2), Some(11));

		// Evicting the stale entry at index 1 deletes the live commitment for 11,
		// one insertion before the entry at index 2 would have.
		store(12);
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 11 }).is_err());
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 12 }).is_ok());
		// The queue still counts index 2 as live, so the burnt slot leaves this
		// chain retaining one fewer commitment than its cap of 2.
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 2, tail: 4 }
		);
		assert_eq!(StateCommitmentQueue::<Test>::get(id, 2), Some(11));
	})
```
