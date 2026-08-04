### Title
Silent loss of HRMP channel notifications on DMQ-full to attacker-flood-driven queue exhaustion - (File: polkadot/runtime/parachains/src/hrmp.rs)

### Summary
`hrmp::Pallet::<T>::send_to_para` (polkadot/runtime/parachains/src/hrmp.rs:1891-1913) calls `dmp::Pallet::<T>::queue_downward_message` to notify a parachain about HRMP channel lifecycle events, but only handles the `QueueDownwardMessageError::ExceedsMaxMessageSize` case with a `debug_assert!(false)` and log line. It does not handle `QueueDownwardMessageError::ExceedsMaxQueueSize`, which is exactly the error returned by `dmp::can_queue_downward_message` when a parachain's DMQ is already full. This means an attacker who fills their own para's DMQ can cause HRMP channel notifications to be silently dropped — with no log, no panic, and no error surfaced to the caller — while the relay-chain-side HRMP channel state is still mutated unconditionally.

### Finding Description
`send_to_para` is invoked from the HRMP channel management logic (`hrmp_init_open_channel`, `hrmp_accept_open_channel`, `hrmp_close_channel`, and the channel-processing logic executed in `Pallet::<T>::on_new_session`/session-boundary channel commit) after the relay-chain-side channel state (`HrmpOpenChannelRequests`, `HrmpChannels`, `HrmpIngressChannelsIndex`, etc.) has already been updated in storage. The DMP notification is meant to inform a parachain that a channel-related state transition occurred. Its return type is `()`: [1](#0-0) 

Because `send_to_para` returns unit and does not propagate `Result` to its callers, the storage state changes for the HRMP channel are committed regardless of whether the notification is actually enqueued into the destination para's DMQ. The only error branch handled is `ExceedsMaxMessageSize`: [2](#0-1) 

`dmp::Pallet::<T>::queue_downward_message` can also return `QueueDownwardMessageError::ExceedsMaxQueueSize` (documented in the module doc comment) when the target para's DMQ has reached its hard `max_messages` bound: [3](#0-2) [4](#0-3) 

Because the `if let` in `send_to_para` only matches `ExceedsMaxMessageSize`, the `ExceedsMaxQueueSize` case falls through with **no log, no debug_assert, and no error at all** — the notification is silently discarded and the caller has no indication anything went wrong.

An unprivileged actor controlling (or acting as) a parachain-side collator/account able to submit XCM `Transact`/DMP-consuming traffic into its own para's DMQ (or, more relevantly, HRMP traffic that grows a *counterparty* para's DMQ) can flood the DMQ close to `max_messages` before a legitimate channel action (open/accept/close) is enacted in the same block/session-boundary. When `send_to_para` then attempts to enqueue the notification, `can_queue_downward_message` rejects it due to `ExceedsMaxQueueSize`, and the notification is lost while the HRMP channel storage has already transitioned (e.g., channel marked open/closed on the relay chain, indices updated) without the destination para ever being informed via DMP.

### Impact Explanation
This causes a genuine invariant violation: HRMP channel state on the relay chain can diverge from what parachains believe based on DMP-delivered notifications, since the state mutation is committed atomically in relay-chain storage but the corresponding downward notification can be dropped non-atomically. This does not steal funds directly, but it desynchronizes cross-chain channel state, potentially leaving a parachain unaware that a channel was opened/closed, degrading XCM delivery between chains until manual intervention (e.g., a subsequent explicit `hrmp_close_channel`/force-clean governance action) is required. The queue/validation-path invariant ("Critical queues... must not be permanently halted/desynced by valid user input") is violated because ordinary DMQ growth, achievable by ordinary users, can suppress notification delivery with zero observability in production builds (the `debug_assert!` is a no-op in release/production runtimes and doesn't even fire for this specific error branch anyway).

### Likelihood Explanation
Feasibility depends on being able to fill a specific para's DMQ to `max_messages` within the same block/session boundary that a channel-management extrinsic is processed. `max_messages` is derived from `MAX_POSSIBLE_ALLOCATION / max_downward_message_size`, which can be a large number depending on runtime configuration, making a single-block flood potentially costly but not impossible for well-resourced actors, especially against parachains with small `max_downward_message_size`/permissive DMP acceptance. Channel-management notifications are typically enacted at session boundaries (not directly in the extrinsic call), giving an attacker a window of many blocks to grow the DMQ before the notification is actually sent, significantly increasing feasibility versus a strict same-block requirement.

### Recommendation
Change `send_to_para` to return a `Result` and propagate `ExceedsMaxQueueSize` (and any other error) as a hard failure to its callers, aborting/rolling back the channel state transition (or deferring the notification with a retry queue) rather than silently proceeding. At minimum, add explicit handling and logging for `ExceedsMaxQueueSize` so operators can observe the failure, and consider making channel-state commits conditional on successful notification enqueueing to preserve the "notify or fail atomically" invariant.

### Proof of Concept
Integration test in `polkadot/runtime/parachains/src/hrmp/tests.rs`:
1. Configure a mock `HostConfiguration` with a small `max_downward_message_size`/DMQ hard limit for para B.
2. Flood para B's DMQ via repeated `dmp::Pallet::<Test>::queue_downward_message` calls (using normal DMP-sending paths reachable from XCM, e.g., simulated `Transact` messages) until `dmq_length(B) == dmq_max_length - 1`.
3. Have para A call `Pallet::<Test>::init_open_channel(A, B, ...)` then have B call `accept_open_channel(B, A)` in the same block/session so that `send_to_para` fires the accept notification toward A/B.
4. Assert: `HrmpChannels::<Test>::get(&channel_id)` shows the channel as open (state committed) **while** `DownwardMessageQueuePages`/DMQ for the target para does NOT contain the expected notification, proving desync — i.e., assert both "channel committed" and "notification missing" hold simultaneously, which should never occur (test expects them to fail atomically together, but implementation lets them diverge).

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1891-1913)
```rust
	/// Sends/enqueues notification to the destination parachain.
	fn send_to_para(
		log_label: &str,
		config: &HostConfiguration<BlockNumberFor<T>>,
		dest: ParaId,
		notification_bytes_for: impl FnOnce(ParaId) -> polkadot_primitives::DownwardMessage,
	) {
		// prepare notification
		let notification_bytes = notification_bytes_for(dest);

		// try to enqueue
		if let Err(dmp::QueueDownwardMessageError::ExceedsMaxMessageSize) =
			dmp::Pallet::<T>::queue_downward_message(&config, dest, notification_bytes)
		{
			// this should never happen unless the max downward message size is configured to a
			// jokingly small number.
			log::error!(
				target: "runtime::hrmp",
				"sending '{log_label}::notification_bytes' failed."
			);
			debug_assert!(false);
		}
	}
```

**File:** polkadot/runtime/parachains/src/dmp.rs (L40-43)
```rust
//! As an extra defensive measure, a `max_messages` hard
//! limit is set to the number of messages in the DownwardMessageQueue. Messages
//! that would increase the number of messages in the queue above this hard
//! limit are dropped.
```

**File:** polkadot/runtime/parachains/src/dmp.rs (L80-87)
```rust
pub enum QueueDownwardMessageError {
	/// The message being sent exceeds the configured max message size.
	ExceedsMaxMessageSize,
	/// Message rejected due to queue being full.
	ExceedsMaxQueueSize,
	/// The destination is unknown.
	Unroutable,
}
```
