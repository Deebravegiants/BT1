### Title
Bounded state-commitment/update-time queue can evict entries needed for legitimate timeout and message-delivery proofs before consumers can use them - (File: `modules/pallets/ismp/src/lib.rs`, `modules/pallets/ismp/src/host.rs`)

### Summary
Analogous to the audited "Insufficient TTL for Checkpoints" bug (a fixed retention window for temporary voting-checkpoint data that can expire before all legitimate consumers finish using it), pallet-ismp retains verified `StateCommitment`s and `StateMachineUpdateTime`s in a capped FIFO structure (`BoundedStateCommitments`, `BoundedStateMachineUpdateTime`, back by `StateCommitmentQueue`/`CommitmentQueueStates`). The retention depth is governed by a fixed count cap (`MAX_STATE_MACHINE_COMMITMENTS = 10_240`, optionally overridden per chain via `StateMachineCommitmentCap`), not by the actual time window that relayers/users need to submit `handle_timeouts`/membership proofs (`challenge_period` + request `timeout_timestamp` + relayer submission delay). If the configured cap is too small relative to a chain's finalization cadence and the protocol's `challenge_period`/timeout windows, legitimate heights get evicted from `BoundedStateCommitments`/`BoundedStateMachineUpdateTime` before relayers can submit `handle_post_request_timeouts`/message-delivery proofs referencing that height. [1](#0-0) [2](#0-1) 

### Finding Description
`store_state_machine_commitment` and `store_state_machine_update_time` insert into per-chain bounded double maps via `insert_bounded_state_commitment`/`insert_bounded_update_time`, which evict the oldest entries via the `StateCommitmentQueue` FIFO once the per-chain cap (`MAX_STATE_MACHINE_COMMITMENTS` or `StateMachineCommitmentCap` override) is exceeded: [3](#0-2) 

Consumers such as `handle_post_request_timeouts` / `handle_get_request_timeouts` in `HandlerV2.sol`, and the Rust `timeout::handle` path, rely on `host.state_machine_commitment(height)` and `host.state_machine_update_time(height)` being available for the height at which a non-membership/membership proof is anchored: [4](#0-3) [5](#0-4) 

Unlike the votes-contract bug where TTL is a wall-clock lifetime, this queue caps retained heights by *count*, so its effective wall-clock retention window is `cap / (state-machine finality frequency)`. This is documented in the pallet's own comments as something that must be tuned per chain ("Chains can be given a different retention depth via `StateMachineCommitmentCap`, sized to their finality cadence... to cover the same wall-clock window") but nothing in the insert path enforces that the cap actually covers `challenge_period + max(timeout_timestamp windows) + relayer submission delay`. If a chain's finality frequency increases (e.g., faster block times, more frequent consensus updates) or the cap is left at a default too small for the configured challenge/timeout periods, honest relayers submitting `PostRequestTimeoutMessage`/`GetTimeoutMessage` for a height that has aged out will hit `StateCommitmentNotFound` on the EVM side or `Error::StateCommitmentNotFound` on the pallet side, exactly mirroring the original report's failure mode where `contract::close` could not find the checkpoint. [6](#0-5) 

### Impact Explanation
If legitimate `StateCommitment`/update-time entries are evicted before a relayer can submit the timeout proof or a pending request's delivery proof, the timeout handler reverts with `StateCommitmentNotFound`, meaning: (1) users cannot recover funds/state via `dispatchTimeOut` for requests whose fee refunds and reversions depend on the timeout path completing, permanently freezing relayer fee refunds and blocking module-level timeout logic that reverses escrowed state; and (2) any pending request/response relying on that height for a membership proof becomes permanently undeliverable once evicted, i.e., "a route unable to deliver messages" for that batch. This is reachable by any unprivileged relayer or user attempting to submit a normal, permissionless timeout/delivery transaction — no privileged action is required to trigger the failure, only for the queue depth/cadence mismatch to exist.

### Likelihood Explanation
Likelihood depends entirely on operational configuration (whether `StateMachineCommitmentCap`/default `MAX_STATE_MACHINE_COMMITMENTS` is sized correctly for a given chain's `challenge_period` + `timeout_timestamp` windows and finality cadence). The pallet's own inline documentation acknowledges this exact risk ("need a deeper queue to retain the same wall-clock window... to cover the same wall-clock window"), indicating the developers are aware misconfiguration is possible, but there is no runtime assertion tying the cap to the configured challenge/timeout periods. For fast-finalizing chains (e.g., short block times) with a default or under-provisioned cap, this could plausibly be reached under normal traffic once the queue fills within less time than the max allowed timeout window (up to 7+ days by ISMP timeout norms), causing legitimate late timeouts to fail deterministically.

### Recommendation
Enforce (rather than merely document) that `StateMachineCommitmentCap` for each state machine is derived from that chain's configured `challenge_period` plus maximum permitted `timeout_timestamp` delta plus a safety buffer for relayer submission delay, similar to the fix in the original report (increasing `MAX_CHECKPOINT_AGE_LEDGERS` to cover `vote_period + grace_period`). Concretely: validate at `store_challenge_period`/cap-setting time that `cap * expected_block_time >= challenge_period + max_timeout_window + buffer`, and reject or auto-correct configurations that violate this invariant, or switch the underlying retention to a genuinely time-based TTL keyed off `state_machine_update_time` rather than a fixed entry-count FIFO.

### Proof of Concept
1. Configure a state machine's `ChallengePeriod` and rely on default `MAX_STATE_MACHINE_COMMITMENTS` (or a `StateMachineCommitmentCap` override) that is undersized relative to its actual finality cadence (e.g., a chain finalizing every few seconds with the default cap sized for a slower chain).
2. Dispatch a `PostRequest` with `timeout_timestamp` set near the protocol's maximum allowed window.
3. Continue producing consensus updates for that state machine (permissionless `handle_unsigned` with valid consensus proofs) until more than `MAX_STATE_MACHINE_COMMITMENTS` (or the per-chain cap) heights have been inserted, causing `insert_bounded_state_commitment`/`insert_bounded_update_time` to evict the height originally used to anchor the pending request.
4. Once `timeout_timestamp` elapses, submit `handlePostRequestTimeouts` (EVM) or `TimeoutMessage::Post` (pallet) referencing the now-evicted height.
5. Observe `StateCommitmentNotFound` (`host.mdx`/`HandlerV2.sol` revert path, or `ismp::Error::StateCommitmentNotFound` in the Rust handler) — the timeout can never be executed for that height again, permanently freezing the relayer fee refund and blocking the source-side module rollback tied to that request. [7](#0-6) [4](#0-3)

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L87-100)
```rust
	/// Default number of state commitments retained per chain in
	/// [`BoundedStateCommitments`]. Chains can be given a different retention
	/// depth via [`StateMachineCommitmentCap`], sized to their finality
	/// cadence: a chain that finalizes every few seconds needs a much larger
	/// cap than one that finalizes every few minutes to cover the same
	/// wall-clock window.
	pub const MAX_STATE_MACHINE_COMMITMENTS: u32 = 10_240;

	/// Upper bound on evictions performed by a single
	/// [`Pallet::insert_bounded_state_commitment`] call. At steady state each
	/// insertion evicts exactly one entry; the headroom lets the queue drain
	/// gradually after a per-chain cap is lowered without unbounded work in
	/// one call.
	pub const MAX_COMMITMENT_EVICTIONS_PER_INSERT: u32 = 4;
```

**File:** modules/pallets/ismp/src/lib.rs (L236-299)
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
	pub type StateMachineCommitmentCap<T: Config> =
		StorageMap<_, Blake2_128Concat, StateMachineId, u32, OptionQuery>;
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

**File:** modules/pallets/ismp/src/host.rs (L73-85)
```rust
	fn state_machine_update_time(
		&self,
		state_machine_height: StateMachineHeight,
	) -> Result<Duration, Error> {
		BoundedStateMachineUpdateTime::<T>::get(
			state_machine_height.id,
			state_machine_height.height,
		)
		.map(|timestamp| Duration::from_secs(timestamp))
		.ok_or_else(|| {
			Error::Custom(format!("Update time not found for {:?}", state_machine_height))
		})
	}
```

**File:** evm/src/core/HandlerV2.sol (L254-270)
```text
    function handlePostRequestTimeouts(IHost host, PostRequestTimeoutMessage calldata message)
        external
        notFrozen(host)
    {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            PostRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();
```
