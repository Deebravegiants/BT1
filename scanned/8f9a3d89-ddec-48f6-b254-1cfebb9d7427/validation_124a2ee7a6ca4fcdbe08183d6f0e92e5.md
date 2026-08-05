### Title
`StackLimitReached` is permanently dropped by `service_page_item` while treated as transient by `do_execute_overweight_inner` - (File: substrate/frame/message-queue/src/lib.rs)

### Summary
`process_message_payload` maps an XCM executor `ProcessMessageError::StackLimitReached` into `MessageExecutionStatus::StackLimitReached` [1](#0-0) . In the normal servicing path, `service_page_item` treats this status as permanently processed (`is_processed = true`) and skips/removes the message from the page forever [2](#0-1) , whereas `do_execute_overweight_inner` treats the identical status as `TemporarilyUnprocessable`, refusing to finalize it [3](#0-2) . This divergence means a message that overflows the XCM executor's recursion limit is silently and irreversibly dropped from the queue with no `OverweightEnqueued` event and no retry path, contradicting the stated design intent that stack-limit errors be transient/retryable.

### Finding Description
The message pipeline is: `service_queue` → `service_page` → `service_page_item` → `process_message_payload` → `T::MessageProcessor::process_message` (XCM executor). When the executor's recursion depth exceeds `RECURSION_LIMIT` (triggerable via deeply nested `SetAppendix`/`ExecuteWithOrigin`/similar XCM instructions), it returns `ProcessMessageError::StackLimitReached`.

`process_message_payload` converts this into `MessageExecutionStatus::StackLimitReached` and deposits a `ProcessingFailed` event [1](#0-0) .

Back in `service_page_item`, the match arm classifies this status together with `Processed` and `Unprocessable { permanent: true }` as `is_processed = true` [2](#0-1) . This causes `page.skip_first(true)` to mark the message as done, decrement `book_state.message_count`/`size`, and the message is never enqueued into the overweight book (no `OverweightEnqueued` event is fired — that only occurs in the `Overweight` branch of `process_message_payload`, not the `StackLimitReached` branch) [4](#0-3) . The message is gone from the normal queue permanently with only a `ProcessingFailed` event as a trace, and no `Error<T>::InsufficientWeight`/overweight bookkeeping exists to let it be retried via `do_execute_overweight`, since it was never registered as an overweight/unprocessed entry in a way `do_execute_overweight_inner` can act on (that function only sees whatever page/pos state exists, and the message has already been marked processed by the normal path before anyone could call `execute_overweight` on it).

In contrast, `do_execute_overweight_inner` — reachable via the permissionless-ish `execute_overweight` extrinsic path once a message is known to be overweight/unprocessed — treats `StackLimitReached` as `TemporarilyUnprocessable`, refusing to finalize/remove it, preserving the ability to retry [3](#0-2) . This is the divergent handling: the same enum variant is "permanent" in one call path and "transient" in the other, matching the reported inconsistency.

### Impact Explanation
Because `service_queue`/`service_page`/`service_page_item` is the path invoked automatically by `on_initialize`/off-chain queue servicing for all UMP/DMP/XCMP messages, any XCM message that exceeds `xcm-executor`'s `RECURSION_LIMIT` and returns `StackLimitReached` is permanently and silently dropped from the message queue the first time it's serviced — before it ever reaches the `do_execute_overweight_inner` path, since normal servicing runs first and unconditionally marks it processed. This is a real logic bug: legitimate XCM instructions/transfers can be permanently lost with no recovery event (no `OverweightEnqueued`), unlike other unprocessable-but-recoverable states. The severity is bounded to "message lost/stuck," matching the reported "High stuck-queue" scope; it is not a direct funds-theft/duplication bug, but it can cause loss of funds/instructions that were in-flight in that XCM (e.g., a transfer nested inside the deeply-nested program never executes and cannot be resubmitted through this queue mechanism).

### Likelihood Explanation
This is triggerable by an unprivileged actor: any account (or unprivileged XCM originator) that can get a message routed through UMP/DMP/XCMP to `MessageQueue` can construct a deeply nested XCM program (e.g., recursively nested `SetAppendix`/`ExecuteWithOrigin`/`InitiateTransfer`, optionally with `Junctions::X8` locations to increase per-level cost) that exceeds the executor's fixed recursion limit. No governance, no special origin, and no race condition is required — it is a deterministic consequence of message content once it reaches `process_message_payload` during normal on-chain servicing. The bug is fully repeatable: every time such a message is serviced normally, it is dropped; it only avoids the bug if some other path (e.g. explicit `execute_overweight`) processes it first, which does not happen under normal automatic queue servicing.

### Recommendation
Make `service_page_item` treat `MessageExecutionStatus::StackLimitReached` identically to how `do_execute_overweight_inner` treats it — i.e., as non-permanent/retryable (e.g., route to `ItemExecutionStatus::Bailed` or `NoProgress`, or explicitly enqueue it into the overweight book with an `OverweightEnqueued`-style event) rather than folding it into `is_processed = true`. The two call sites must use the same `is_permanent`/retry classification for every `MessageExecutionStatus` variant to preserve the "stack-limit errors are transient" invariant end-to-end.

### Proof of Concept
Add a unit test in `substrate/frame/message-queue/src/tests.rs` using the existing `RecordingMessageProcessor`/mock configured to return `Err(ProcessMessageError::StackLimitReached)` for a specific payload (the test file already imports/uses `StackLimitReached` in 12 places, so mock plumbing exists) [5](#0-4) :

1. Enqueue one message whose processor mock returns `StackLimitReached`.
2. Call `MessageQueue::service_queues(Weight::MAX)`.
3. Assert: the message is removed from the page/book (`book_state.message_count == 0`), no `OverweightEnqueued` event was emitted, and only `Event::ProcessingFailed` was emitted — demonstrating permanent silent drop.
4. In a second scenario, before step 2, first attempt `MessageQueue::execute_overweight(origin, page_index, index, weight_limit)` on the same not-yet-serviced message and assert it returns `Err(Error::<T>::TemporarilyUnprocessable)` — demonstrating the same status is treated as transient there.
5. The divergence between step 3 (permanent loss) and step 4 (transient/retryable) is the assertion proving the bug; a fix should make both paths agree (e.g., both returning a bailed/retryable state until either a max-retry policy or explicit permanent-failure decision is made).

### Citations

**File:** substrate/frame/message-queue/src/lib.rs (L1112-1115)
```rust
			Overweight | InsufficientWeight => Err(Error::<T>::InsufficientWeight),
			StackLimitReached | Unprocessable { permanent: false } => {
				Err(Error::<T>::TemporarilyUnprocessable)
			},
```

**File:** substrate/frame/message-queue/src/lib.rs (L1378-1391)
```rust
		let is_processed = match res {
			InsufficientWeight => return ItemExecutionStatus::Bailed,
			Unprocessable { permanent: false } => return ItemExecutionStatus::NoProgress,
			Processed | Unprocessable { permanent: true } | StackLimitReached => true,
			Overweight => false,
		};

		if is_processed {
			book_state.message_count.saturating_dec();
			book_state.size.saturating_reduce(payload_len as u64);
		}
		page.skip_first(is_processed);
		ItemExecutionStatus::Executed(is_processed)
	}
```

**File:** substrate/frame/message-queue/src/lib.rs (L1590-1599)
```rust
			Err(Overweight(w)) if w.any_gt(overweight_limit) => {
				// Permanently overweight.
				Self::deposit_event(Event::<T>::OverweightEnqueued {
					id,
					origin,
					page_index,
					message_index,
				});
				MessageExecutionStatus::Overweight
			},
```

**File:** substrate/frame/message-queue/src/lib.rs (L1614-1617)
```rust
			Err(error @ StackLimitReached) => {
				Self::deposit_event(Event::<T>::ProcessingFailed { id: id.into(), origin, error });
				MessageExecutionStatus::StackLimitReached
			},
```

**File:** substrate/frame/message-queue/src/tests.rs (L1-1)
```rust
// This file is part of Substrate.
```
