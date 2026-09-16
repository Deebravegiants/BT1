Confirmed: `modules/ismp/core/src/handlers/response.rs:72` requires `get.height == proof.height.height` exactly, and `pallet_state_coprocessor::handle_get_requests` (`modules/pallets/state-coprocessor/src/impls.rs:107`) enforces the same exact-height match. Combined with the tested-and-acknowledged fact that a vetoed non-latest `StateCommitment` height can never be resubmitted (`modules/pallets/testsuite/src/tests/pallet_ismp.rs:778-827`, `vetoed_height_that_cannot_be_resubmitted_evicts_as_a_noop`), this gives a concrete, permanent freeze path for GET requests pinned to that height.

### Title
Permanent freeze of in-flight GET requests when their exact-height state commitment is vetoed by a fisherman - (File: `modules/ismp/core/src/handlers/consensus.rs`, `modules/pallets/ismp/src/host.rs`, `modules/ismp/core/src/handlers/response.rs`, `modules/pallets/state-coprocessor/src/impls.rs`)

### Summary
`GetRequest`s pin the exact height of the destination-chain state they need proven (`GetRequest::height`), and both response-handling paths reject any proof whose height doesn't exactly equal that value. Fishermen may legitimately veto (delete) a state-machine commitment for any height, including one that is not the chain's current latest height. Once a non-latest height's commitment is deleted, `update_client`'s "only allow heights greater than latest height" rule permanently prevents that exact height from ever being re-submitted by consensus updates. Any pending `GetRequest` requiring proof at that exact height can then never be answered — a permanent liveness/fund-freeze failure, not merely a temporary one as in the original Optimism report.

### Finding Description
`update_client` in `modules/ismp/core/src/handlers/consensus.rs:51-71` only stores a new state commitment for a height if it is strictly greater than the previously recorded latest height for that state machine: [1](#0-0) 

`delete_state_commitment` (`modules/pallets/ismp/src/host.rs:194-222`) removes the commitment and, only if the vetoed height *was* the latest, rolls the latest pointer back to allow resubmission: [2](#0-1) 

If the vetoed height is *not* the latest (i.e., a lower/older height was fraudulent while a newer height has already been accepted — a completely normal fishermen scenario), the latest pointer is left untouched. Consequently, any future consensus proof that tries to (re)commit that exact height is skipped by the `previous_latest_height > commitment_height.height { continue; }` guard, permanently leaving that height's commitment absent. This is explicitly reproduced and acknowledged in the test suite: [3](#0-2) 

Vetoing is deliberately proof-free and can be triggered by a single collator for any commitment "ideally still in its challenge period": [4](#0-3) 

The impact surfaces in the `GetRequest` response flow, which is the only ISMP message type that requires an *exact* height match rather than "any later/available height." Both the router handler and the coprocessor pallet enforce `get.height == proof.height.height`: [5](#0-4) [6](#0-5) 

If a fisherman legitimately vetoes the destination-chain state commitment at the exact non-latest height a `GetRequest` targets (e.g., because that particular height's commitment was indeed fraudulent, while the chain has already progressed to a later verified height), the request can never be serviced: no future consensus update can ever re-populate that specific height, and no other height satisfies the exact-match requirement.

### Impact Explanation
This permanently freezes any in-flight `GetRequest` (and its escrowed relayer fee / dependent application state) whose pinned height's commitment is vetoed while not being the latest height. Unlike ordinary `PostRequest`/`PostResponse` delivery, which can be re-proven against any later MMR/overlay root, `GetRequest` responses have no fallback height to retry against — the route is permanently unable to deliver the message, matching the "route unable to deliver messages" / "permanent freezing of funds" acceptance criteria. This can occur purely as a side effect of correct fisherman behavior (vetoing a genuinely fraudulent, non-latest state commitment), not only via a malicious collator.

### Likelihood Explanation
The precondition — a fisherman vetoing a non-latest height — is a designed, expected part of the protocol's fraud-detection flow (any single authorized collator can veto without proof, per the `veto_state_commitment` extrinsic), and is independent of whether any `GetRequest` currently targets that height. Given active cross-chain GET traffic and periodic fisherman activity, a collision between an in-flight `GetRequest`'s pinned height and a vetoed non-latest height is a realistic, low-effort-to-trigger scenario (it can even happen accidentally, without any adversarial intent).

### Recommendation
When `delete_state_commitment` removes a non-latest height, either (a) allow a future consensus update to re-populate that exact height even though it is below the current latest (e.g., track vetoed-but-reopenable heights separately from "duplicate, already-correct" heights), or (b) relax the `GetRequest` response path to accept a proof at any height ≥ `GetRequest::height` where the requested keys' values are provably unchanged since `GetRequest::height`, so a vetoed exact height doesn't permanently strand the request. At minimum, emit a distinguishable event/error so relayers and requesters can detect a permanently-stranded `GetRequest` and trigger its timeout/refund path promptly instead of retrying forever.

### Proof of Concept
1. State machine `S` has state commitments at heights 10 and 11; `LatestStateMachineHeight[S] = 11`.
2. A user dispatches a `GetRequest` targeting `S` at `height = 10` (via `DispatchGet`), expecting a relayer to later prove `keys` at exactly height 10 (`GetRequest::height == proof.height.height` enforced in `modules/ismp/core/src/handlers/response.rs:72` and `modules/pallets/state-coprocessor/src/impls.rs:107`).
3. A collator determines that the commitment at height 10 was fraudulent (10 < latest, so this is a routine, correct veto) and calls `veto_state_commitment(height=10)` (`modules/pallets/fishermen/src/lib.rs:167-193`), which calls `delete_state_commitment` (`modules/pallets/ismp/src/host.rs:194`). Because height 10 isn't the latest (11), `LatestStateMachineHeight[S]` remains 11.
4. Any subsequent, honest `update_client` consensus proof for `S` is compared against `previous_latest_height = 11`; any commitment for height 10 is skipped by `if previous_latest_height > commitment_height.height { continue; }` (`modules/ismp/core/src/handlers/consensus.rs:59-61`) — height 10's commitment can never be restored, as directly demonstrated by `vetoed_height_that_cannot_be_resubmitted_evicts_as_a_noop` (`modules/pallets/testsuite/src/tests/pallet_ismp.rs:781-827`).
5. The relayer (or the requester via `GetRequestClient.deliverToHyperbridge`) can never obtain a valid `response.height == 10` state commitment for `S` again, so the `GetRequest` from step 2 can never be answered — it is permanently stuck until its own timeout, and if the fee/escrow model does not fully refund on timeout, the requester's funds are frozen for the remainder of that period with no possibility of completion.

### Citations

**File:** modules/ismp/core/src/handlers/consensus.rs (L55-66)
```rust
		for commitment_height in commitment_heights.iter() {
			let state_height = StateMachineHeight { id, height: commitment_height.height };

			// Only allow heights greater than latest height
			if previous_latest_height > commitment_height.height {
				continue;
			}

			// Skip duplicate states
			if host.state_machine_commitment(state_height).is_ok() {
				continue;
			}
```

**File:** modules/pallets/ismp/src/host.rs (L206-220)
```rust
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
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp.rs (L778-815)
```rust
// A height below the latest can never be resubmitted — the consensus handler skips
// anything at or below `previous_latest_height` — so its stale queue entry has no
// live twin and evicting it touches nothing.
#[test]
fn vetoed_height_that_cannot_be_resubmitted_evicts_as_a_noop() {
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

		// Veto a height below the latest: the commitment goes away immediately while
		// its queue entry stays behind as a stale index. The latest height is
		// untouched, so 10 stays permanently unsubmittable.
		host.delete_state_commitment(StateMachineHeight { id, height: 10 }).unwrap();
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 10 }).is_err());
		assert_eq!(host.latest_commitment_height(id).unwrap(), 11);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 0, tail: 2 }
		);
		assert_eq!(StateCommitmentQueue::<Test>::get(id, 0), Some(10));
```

**File:** modules/pallets/fishermen/src/lib.rs (L158-177)
```rust
		/// A collator has determined that some [`StateCommitment`] (which is ideally still in
		/// its challenge period) is in fact fraudulent and misrepresentative of the state
		/// changes at the provided height. They aren't required to provide any proofs for
		/// this — any single collator's call deletes the commitment.
		///
		/// Dispatches with `Pays::No`. The on-chain `IsCollator` check is the DOS guard, so
		/// the signer does not need to hold a balance.
		#[pallet::call_index(0)]
		#[pallet::weight((<T as frame_system::Config>::DbWeight::get().reads_writes(1, 2), Pays::No))]
		pub fn veto_state_commitment(
			origin: OriginFor<T>,
			height: StateMachineHeight,
		) -> DispatchResult {
			let account = ensure_signed(origin)?;
			ensure!(T::IsCollator::contains(&account), Error::<T>::UnauthorizedAction);

			let ismp_host = <T as Config>::IsmpHost::default();
			let commitment =
				ismp_host.state_machine_commitment(height).map_err(|_| Error::<T>::VetoFailed)?;
			ismp_host.delete_state_commitment(height).map_err(|_| Error::<T>::VetoFailed)?;
```

**File:** modules/ismp/core/src/handlers/response.rs (L70-74)
```rust
	// Ensure the proof height is equal to each retrieval height specified in the Get
	// requests
	if !msg.requests.iter().all(|get| get.height == proof.height.height) {
		Err(Error::InsufficientProofHeight)?
	}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L105-109)
```rust
		// Ensure the proof height is equal to each retrieval height specified in the Get
		// requests
		if !requests.iter().all(|get| get.height == response.height.height) {
			Err(Error::InsufficientProofHeight)?
		}
```
