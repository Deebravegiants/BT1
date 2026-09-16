Based on the investigation, I found a valid analog in Hyperbridge's `pallet-ismp` state commitment retention mechanism, which parallels the "unclaimed rewards can be lost when merkle root is changed" bug class: state commitments (the equivalent of the "root") that relayer reward claims depend on can be evicted from the bounded storage before the proof-of-delivery claim is submitted.

### Title
Bounded state-commitment eviction can permanently strand unclaimed relayer rewards - (File: `modules/pallets/ismp/src/lib.rs`, `modules/pallets/relayer/src/accumulate.rs`, `modules/pallets/relayer/src/outbound_consensus.rs`, `modules/pallets/relayer/src/outbound_request.rs`)

### Summary
Every ISMP `StateMachineHeight → StateCommitment` entry (the "root" a relayer must prove against to unlock its reward) is retained in a bounded, per-chain FIFO queue, `BoundedStateCommitments`/`StateCommitmentQueue`, capped at `StateMachineCommitmentCap` (default `MAX_STATE_MACHINE_COMMITMENTS`). New consensus updates keep pushing heights into this queue and evict the oldest entries once the cap is reached [1](#0-0) . Fee/reward accumulation for relayers (`accumulate_fees`, `claim_outbound_consensus_delivery_reward`, `claim_outbound_request_delivery_reward`) all require submitting a state proof anchored at a specific historical height whose commitment must still exist in this bounded map [2](#0-1) . If a relayer delays claiming (e.g. is racing other relayers, network delay, waiting for `wait_for_state_machine_update`) and enough new consensus updates for that same destination land in the interim, the height they need is evicted before they submit their claim — exactly analogous to a merkle root being replaced before a leaf is claimed.

### Finding Description
The relayer pallet's reward mechanisms are fundamentally proof-of-delivery mechanisms: a relayer must present a `Proof` anchored at `state_proof.height`, and the pallet resolves and verifies that height's stored state commitment via `validate_state_machine` before paying out [3](#0-2) . The underlying storage backing those commitments, `BoundedStateCommitments`, is explicitly capped per chain, and the comments in the pallet describe an eviction FIFO that removes the oldest heights once a chain's cap is exceeded [4](#0-3) . Fast-finality chains (e.g. EVM chains that finalize/produce state updates frequently) will cycle through their cap quickly, so any claim not submitted promptly risks referencing a height that no longer exists in storage.

This directly parallels the FootiumPrizeDistributor bug: there, `setERC20MerkleRoot`/`setETHMerkleRoot` overwrite the single root a claimant needs, silently orphaning any earned-but-unclaimed leaf. Here, `store_state_machine_commitment` (triggered by every accepted consensus update, permissionlessly submittable by anyone relaying a valid consensus proof) keeps overwriting/evicting old entries in the bounded map, silently orphaning any relayer's earned-but-unclaimed proof height. The `unit test` explicitly documents this rollback/veto and cap-driven eviction behavior as expected pallet mechanics, confirming the eviction is a real, reachable code path, not a theoretical one [5](#0-4) .

### Impact Explanation
A relayer that has legitimately delivered a message/consensus rotation/request and is entitled to a fee or `OutboundConsensusDeliveryReward`/`OutboundRequestDeliveryReward` can permanently lose that reward if the claim isn't submitted before the required height falls out of the bounded retention window. This is a direct, permanent loss of relayer-earned funds (fees accrued by users/protocol are effectively unclaimable), matching the "permanent freezing/loss of funds" impact bar. Because any account can submit consensus updates that advance the retained window (`update_client` is permissionless and simply requires a valid consensus proof [6](#0-5) ), an adversary or even normal high-throughput relaying activity from unrelated relayers can accelerate eviction of a competitor's claim window, griefing a specific relayer out of its earned reward.

### Likelihood Explanation
Likelihood is real but conditional: it requires (a) a relayer's claim submission being delayed relative to the retention window (network/consensus proof latency, contention for the `wait_for_state_machine_update` gate, or simply the relayer race described in the incentivization doc where the losing relayer must still eventually claim), and (b) enough intervening consensus/state updates for that specific destination to exceed the configured cap before the claim lands. For chains with short retention caps or fast block/finality cadence this is plausible during normal operation, without any malicious actor needed, though governance can raise `StateMachineCommitmentCap` per chain to mitigate it [7](#0-6) .

### Recommendation
- Add a "claim window" grace mechanism: retain state commitments long enough to cover a relayer's expected claim latency, or expose an explicit "claimable height" registry separate from the bounded proof cache that is not subject to FIFO eviction until the associated reward has been claimed or expired.
- Alternatively, allow claims to reference a state commitment that has been evicted but was previously observed (e.g., by archiving a Merkle/accumulator commitment of evicted state roots) so a late relayer can still produce a valid historical proof.
- Increase default `MAX_STATE_MACHINE_COMMITMENTS` / per-chain caps for high-throughput destinations, and emit a warning/monitor metric before eviction of a height that has an outstanding, unclaimed reward tied to it.

### Proof of Concept
1. Relayer R delivers a message/consensus rotation to destination chain D at height `H`, becoming eligible for a reward tied to `RequestReceipts[commitment]`/`EvmHost._epochs[set_id]` at `H`.
2. Before R submits `claim_outbound_consensus_delivery_reward` / `claim_outbound_request_delivery_reward` / `accumulate_fees` referencing `state_proof.height = H`, other relayers or normal network activity submit `ConsensusMessage`s that advance D's state machine height past the pallet's per-chain `StateMachineCommitmentCap`, causing the eviction path documented and tested in `vetoed_height_that_cannot_be_resubmitted_evicts_as_a_noop`/queue-eviction logic to drop `H`'s entry from `BoundedStateCommitments` [5](#0-4) .
3. R submits its claim; `validate_state_machine`/`host.state_machine_commitment(height)` now fails to find `H`, causing the claim to be rejected (e.g., `OutboundDestinationStateNotKnown`), and R's reward is permanently unclaimable since `H`'s commitment cannot be regenerated without a fresh, real consensus proof from that exact historical height (impossible after the fact for most consensus clients).

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L236-297)
```rust
	/// Holds a map of state machine heights to their verified state commitments. These state
	/// commitments end up here after they are successfully verified by a `ConsensusClient`.
	/// Keyed by `(StateMachineId, height)` so we can cap entries per chain at
	/// [`StateMachineCommitmentCap`] (default [`MAX_STATE_MACHINE_COMMITMENTS`]).
	#[pallet::storage]
	#[pallet::getter(fn state_commitments)]
	pub type BoundedStateCommitments<T: Config> = StorageDoubleMap<
		_,
		Blake2_128Concat,
		StateMachineId,
		Blake2_128Concat,
		u64,
		StateCommitment,
		OptionQuery,
	>;

	/// Holds the timestamp at which a state machine height was updated. Used in ensuring
	/// that the configured challenge period elapses. Same per-chain cap as
	/// [`BoundedStateCommitments`].
	#[pallet::storage]
	#[pallet::getter(fn state_machine_update_time)]
	pub type BoundedStateMachineUpdateTime<T: Config> = StorageDoubleMap<
		_,
		Blake2_128Concat,
		StateMachineId,
		Blake2_128Concat,
		u64,
		u64,
		OptionQuery,
	>;

	/// Per-chain FIFO queue of heights retained in [`BoundedStateCommitments`]
	/// and [`BoundedStateMachineUpdateTime`], keyed by a monotonically
	/// increasing insertion index. Insertion order matches height order because
	/// consensus updates only ever advance a state machine, so evicting at the
	/// head removes the oldest height. Entries whose height was vetoed via
	/// `delete_state_commitment` are left in place and become harmless no-ops
	/// when their index is evicted.
	///
	/// Each insertion touches O(1) small storage items, so the per-chain cap
	/// can grow without adding I/O or PoV weight to the insert path.
	#[pallet::storage]
	pub type StateCommitmentQueue<T: Config> = StorageDoubleMap<
		_,
		Blake2_128Concat,
		StateMachineId,
		Twox64Concat,
		u64,
		u64,
		OptionQuery,
	>;

	/// Head/tail indices for [`StateCommitmentQueue`], per chain.
	#[pallet::storage]
	pub type CommitmentQueueStates<T: Config> =
		StorageMap<_, Blake2_128Concat, StateMachineId, CommitmentQueueState, ValueQuery>;

	/// Per-chain override for the number of state commitments retained. Chains
	/// with faster finality emit state machine updates more frequently and
	/// need a deeper queue to retain the same wall-clock window of provable
	/// heights. Falls back to [`MAX_STATE_MACHINE_COMMITMENTS`] when unset.
	#[pallet::storage]
```

**File:** modules/pallets/ismp/src/lib.rs (L482-507)
```rust
		/// Set the number of state commitments retained per chain, overriding
		/// [`MAX_STATE_MACHINE_COMMITMENTS`]. Size each cap to the chain's
		/// finality cadence: `desired retention window / finality interval`.
		/// Raising a cap simply pauses eviction until the queue grows into it;
		/// lowering one drains the excess gradually, bounded by
		/// [`MAX_COMMITMENT_EVICTIONS_PER_INSERT`] per subsequent insertion.
		///
		/// The dispatch origin for this call must be `T::AdminOrigin`.
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

**File:** modules/pallets/relayer/src/accumulate.rs (L16-24)
```rust
//! Fee accumulation.
//!
//! Relayers prove deliveries on the source/destination chains using a
//! [`WithdrawalProof`] and accumulate the earned fees into the
//! [`crate::pallet::Fees`] map. This module owns the proof verification
//! pipeline, the storage-key derivations for the two chain families (EVM and
//! Substrate), and the per-leaf result validation that ties source-side fee
//! metadata to destination-side delivery receipts.

```

**File:** docs/outbound-request-incentivization.md (L128-136)
```markdown
7. **State-machine match.** `state_proof.height.id.state_id == request.dest`. Defends against a relayer building a proof against a different chain than the request was sent to.

8. **Destination type and receipt key.** Use the `Pallet::request_receipt_key` helper (defined alongside the claim in `outbound_request.rs`):
   - EVM destinations: 32-byte slot hash `derive_unhashed_map_key(commitment, REQUEST_RECEIPTS_SLOT)`, the same key the EVM state machine's `receipts_state_trie_key` produces.
   - Substrate destinations: `pallet_ismp::child_trie::RequestReceipts::<T>::storage_key(commitment)`, identical to the substrate state machine's receipt key.

   A destination that is neither EVM nor substrate is rejected with `OutboundRequestUnsupportedDestination`.

9. **State proof verification.** Resolve the destination client with `ismp::handlers::validate_state_machine(&host, height)`, then `verify_withdrawal_proof(state_machine, &state_proof, vec![key])` against hyperbridge's stored state commitment for the destination. A verification failure maps to `OutboundDestinationStateNotKnown` (no commitment at that height), and a missing or null slot value maps to `OutboundDeliveryNotProven`.
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp.rs (L778-827)
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

		// The stale index is evicted as a no-op on the next insertion.
		store(12);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 1, tail: 3 }
		);
		assert!(StateCommitmentQueue::<Test>::get(id, 0).is_none());
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 11 }).is_ok());
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 12 }).is_ok());
	})
}
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L28-47)
```rust
/// This function handles verification of consensus messages for consensus clients
pub fn update_client<H>(host: &H, msg: ConsensusMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	let consensus_client_id = host.consensus_client_id(msg.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized { consensus_state_id: msg.consensus_state_id },
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	let trusted_state = host.consensus_state(msg.consensus_state_id)?;
	host.is_consensus_client_frozen(msg.consensus_state_id)?;
	host.is_expired(msg.consensus_state_id)?;

	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
	host.store_consensus_state(msg.consensus_state_id, new_state)?;
```
