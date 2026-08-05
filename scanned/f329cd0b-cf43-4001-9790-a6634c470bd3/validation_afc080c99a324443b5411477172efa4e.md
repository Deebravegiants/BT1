### Title
Head-of-queue message returning `ProcessMessageError::StackLimitReached` permanently stalls a `MessageOriginOf<T>` book with no recovery path - (File: substrate/frame/message-queue/src/lib.rs)

### Summary
`service_queue`'s inner loop over pages only advances `book_state.begin` when a page reports `NoMore`; any `Bailed`/`NoProgress` status (which `StackLimitReached` maps into) causes the loop to `break` without advancing the page pointer, leaving the same message at the head of the book forever. Because `do_execute_overweight_inner` explicitly treats `StackLimitReached` the same as `Unprocessable { permanent: false }` (i.e. "temporarily unprocessable, retry later") rather than as a skip/overweight case, and because manual execution via `execute_overweight` requires the message to already be behind `book_state.begin` (a state that is never reached for the stuck head message), there is no path — automatic or user-triggered — to skip past a message that deterministically triggers `StackLimitReached` on every retry.

### Finding Description
The pallet's `service_queue` (substrate/frame/message-queue/src/lib.rs, `service_queue`) walks pages of a book starting from `book_state.begin`: [1](#0-0) 
`book_state.begin` is only incremented when `service_page` returns `NoMore`; `Bailed`/`NoProgress` causes an immediate `break`, and the book is never unknit from the `ReadyRing` while `total_processed == 0` at that head.

The pallet's design intent (documented at the top of the file) is that "temporarily overweight" messages are perpetually retried, while "permanently overweight" ones are skipped and require manual execution: [2](#0-1) 

`StackLimitReached` is explicitly classified alongside the *temporary*, retry-forever case rather than the skip/overweight case, as shown in `do_execute_overweight_inner`: [3](#0-2) 

This classification is designed for the case where `StackLimitReached` results from the *ambient* Rust call-stack depth at the moment of dispatch (e.g. nested `execute_overweight`/reentrant `service_queues` calls), where a retry from a shallower call stack (a fresh `on_initialize`) is expected to eventually succeed. However, when `StackLimitReached` is returned by `Config::MessageProcessor` because the *message's own payload* encodes deeply nested/recursive XCM (e.g. nested `Transact` causing the XCM executor's own internal recursion counter to trip — visible in `polkadot/xcm/xcm-executor/src/lib.rs` and `polkadot/xcm/xcm-builder/src/process_xcm_message.rs`), the failure is deterministic and content-intrinsic: every retry, from any call-stack depth, will fail identically. The retry-forever design assumption is violated.

Because the head message is never skipped (`page.skip_first`/`skip_ready` is only invoked for `Processed`/`Unprocessable{permanent:true}`/`Overweight`-flagged paths, not for the `Bailed`/`NoProgress` path taken by `StackLimitReached`), and because `do_execute_overweight_inner`'s guard requires the message to be strictly behind `book_state.begin`: [4](#0-3) 
the stuck message is never eligible for `execute_overweight` (it is still exactly at `book_state.begin`/`page.first`, so `page_index < book_state.begin` is false and `pos < page.first` is false). No permissionless recovery call exists for this state; the book remains "ready" (still in `ReadyRing`) but perpetually makes zero progress, and every subsequent valid message enqueued to the same `MessageOriginOf<T>` (same parachain-origin book, e.g. same sibling parachain's HRMP/XCMP queue, or the same DMP origin) is queued strictly behind the poisoned message and is never serviced.

### Impact Explanation
An unprivileged party who controls a parachain's outbound HRMP/XCMP channel (or a DMP-reachable sender) can craft one deeply-nested/recursive XCM message that deterministically returns `ProcessMessageError::StackLimitReached` from `Config::MessageProcessor`. Once enqueued as the head of that origin's book, the book is permanently stalled: it stays in the `ReadyRing` making no progress, and any legitimate messages sent afterward to the same origin (queue) are starved indefinitely, with no operator/governance-independent recovery mechanism (the message is not skippable, not overweight-flagged, and not eligible for `execute_overweight`). This is a availability/DoS impact scoped to that origin's queue, matching the "Critical queues... must not be permanently halted by valid user input" invariant.

### Likelihood Explanation
Feasible for any account able to send XCM through a parachain channel or DMP path that reaches this pallet's `MessageProcessor` (e.g. `pallet_message_queue` fed by `pallet_xcmp_queue`/`ParachainSystem` DMP handling). Constructing deeply nested XCM (nested `Transact`/`SetAppendix`/recursive instruction sequences) to trip the XCM executor's fixed recursion limit is a standard, repeatable technique requiring no special privilege, only a valid channel and normal message fee/weight payment. The attack is fully repeatable and doesn't depend on race conditions or timing.

### Recommendation
Treat `ProcessMessageError::StackLimitReached` returned during *page servicing* (not manual re-execution) more conservatively: after a bounded number of consecutive `StackLimitReached` bail-outs for the same head message/page position, mark the message overweight (skip it via `page.skip_first`) so it becomes eligible for manual `execute_overweight`, rather than looping forever with `NoProgress`. Alternatively, track a retry counter per stuck message and permanently drop/flag it (`Unprocessable{permanent:true}`-style handling) once the retry budget is exhausted, ensuring `book_state.begin` can advance and the book unstalls.

### Proof of Concept
Rust unit test plan in `substrate/frame/message-queue/src/tests.rs`:
1. Configure the mock `MessageProcessor` so that a specific crafted payload (e.g. tagged `b"stack_limit"`) always returns `Err(ProcessMessageError::StackLimitReached)` unconditionally (independent of remaining weight/call depth), simulating content-intrinsic recursion.
2. `MessageQueue::enqueue_message(bounded_vec, origin)` with the poison payload, then enqueue N valid follow-up messages with normal payloads to the same `origin`.
3. Call `MessageQueue::service_queues(Weight::MAX)` across several simulated blocks.
4. Assert: (a) `BookStateFor::<Test>::get(origin).message_count == N + 1` remains unchanged (no processing progress) after several service cycles; (b) none of the valid follow-up messages' processed markers are set; (c) `Pallet::do_execute_overweight` on the poisoned message's `page_index`/`index` returns `Error::Queued` (proving it cannot be manually skipped); confirming permanent starvation of the queue with no available recovery path.

### Citations

**File:** substrate/frame/message-queue/src/lib.rs (L54-57)
```rust
//!
//! A failed message can be temporarily or permanently overweight. The pallet will perpetually try
//! to execute a temporarily overweight message. A permanently overweight message is skipped and
//! must be executed manually.
```

**File:** substrate/frame/message-queue/src/lib.rs (L1094-1099)
```rust
		ensure!(
			page_index < book_state.begin ||
				(page_index == book_state.begin && pos < page.first.into() as usize),
			Error::<T>::Queued
		);
		ensure!(!is_processed, Error::<T>::AlreadyProcessed);
```

**File:** substrate/frame/message-queue/src/lib.rs (L1100-1116)
```rust
		use MessageExecutionStatus::*;
		let mut weight_counter = WeightMeter::with_limit(weight_limit);
		match Self::process_message_payload(
			origin.clone(),
			page_index,
			index,
			payload,
			&mut weight_counter,
			Weight::MAX,
			// ^^^ We never recognise it as permanently overweight, since that would result in an
			// additional overweight event being deposited.
		) {
			Overweight | InsufficientWeight => Err(Error::<T>::InsufficientWeight),
			StackLimitReached | Unprocessable { permanent: false } => {
				Err(Error::<T>::TemporarilyUnprocessable)
			},
			Unprocessable { permanent: true } | Processed => {
```

**File:** substrate/frame/message-queue/src/lib.rs (L1241-1252)
```rust
		while book_state.end > book_state.begin {
			let (processed, status) =
				Self::service_page(&origin, &mut book_state, weight, overweight_limit);
			total_processed.saturating_accrue(processed);
			match status {
				// Store the page progress and do not go to the next one.
				Bailed | NoProgress => break,
				// Go to the next page if this one is at the end.
				NoMore => (),
			};
			book_state.begin.saturating_inc();
		}
```
