### Title
Failed `suspended_channels.try_insert` after a successful `Suspend` signal permanently desyncs local suspension tracking, stalling inbound XCMP for the affected sibling - ([File: cumulus/pallets/xcmp-queue/src/lib.rs])

### Summary
In `on_queue_changed`, when `Self::send_signal(para, ChannelSignal::Suspend)` succeeds but the subsequent `suspended_channels.try_insert(para)` fails (because `InboundXcmpSuspended` is at `MaxInboundSuspended` capacity), the pallet has already dispatched a real `Suspend` signal to the sibling but never records the channel as suspended locally. Because `InboundXcmpSuspended` is the sole source of truth used to decide whether to later emit a `Resume` signal, this sibling's channel becomes permanently unresumable by the pallet's automatic backpressure logic, even after its queue fully drains.

### Finding Description
The relevant logic is: [1](#0-0) 

Walking through the failure branch: `Self::send_signal(para, ChannelSignal::Suspend)` is called first [2](#0-1) 
and, if it returns `Ok(())`, it has already mutated `OutboundXcmpStatus`/`SignalMessages` such that the `Suspend` signal will actually be transmitted to the sibling parachain via `XcmpMessageSource`. Only after this side effect has already been committed does the code attempt `suspended_channels.try_insert(para)`. If that insert fails due to `MaxInboundSuspended` being reached, the code merely logs an error and does **not** roll back the already-sent `Suspend` signal, nor does it retry the insert later: [3](#0-2) 

The resume path is gated exclusively on local tracking state: [4](#0-3) 

`suspended` is computed only from `InboundXcmpSuspended::<T>::get().contains(&para)`. Since the para was never inserted (due to the `try_insert` failure), `suspended` will be `false` on every future invocation of `on_queue_changed` for that `para`, regardless of how far `fp.ready_pages` drops. Consequently the `if suspended && fp.ready_pages <= resume_threshold` branch that emits `ChannelSignal::Resume` can never fire for this specific sibling again. Meanwhile the sibling parachain, having received a genuine `Suspend` signal on its `handle_xcmp_messages`/`suspend_channel` path, will keep its outbound channel to this chain suspended indefinitely, since it is waiting for a `Resume` signal that will never be sent by this pallet's automatic logic. There is no root/user dispatchable exposed in this pallet that lets an operator manually re-add a specific `para` to `InboundXcmpSuspended` or force a per-channel `Resume` signal (`suspend_xcm_execution`/`resume_xcm_execution` only toggle the global `QueueSuspended` bool, unrelated to per-channel suspension state) [5](#0-4) 
so recovery requires a runtime upgrade/migration.

The first part of the question (oscillating exactly at `suspend_threshold`/`resume_threshold` to cheaply spam signals) is not itself a distinct bug: each Suspend/Resume toggle requires actually filling and draining the local inbound queue with genuine messages, which is bounded by real message-queue weight/PoV costs and is the intended design of the backpressure mechanism, not a free-to-trigger primitive.

### Impact Explanation
Once the described desync occurs for a given sibling `para`, all future inbound XCMP messages from that sibling are permanently blocked at the source (the sibling's own outbound channel remains suspended forever), even though the receiving chain's queue has drained back below `resume_threshold`. This is a genuine, persistent queue-accounting inconsistency and inbound message loss for the affected sibling chain, matching the scoped impact, and it is not self-healing without manual/governance/runtime-upgrade intervention.

### Likelihood Explanation
This requires `InboundXcmpSuspended` (bounded by `MaxInboundSuspended`) to already be near capacity across many parachains — a systemic congestion precondition rather than something a single unprivileged actor can trivially engineer alone, since `MaxInboundSuspended` is typically configured generously. However, given that precondition (many parachains concurrently congesting their queues, which can be driven by unprivileged XCM/HRMP traffic without any privileged origin), a normal user simply needs their own parachain's queue to cross `suspend_threshold` at the moment the bound is already saturated — no special permissions, signatures, or governance actions are needed to trigger the code path. The bug is a genuine unhandled-error/no-rollback logic error in `on_queue_changed`, not reliance on mocked origins or direct storage mutation.

### Recommendation
Make the two side effects transactional: attempt `suspended_channels.try_insert(para)` *before* calling `Self::send_signal(..., Suspend)`, only sending the signal if the local bookkeeping succeeds; alternatively, if `try_insert` fails after a successful signal send, retry inserting the channel into `InboundXcmpSuspended` on subsequent calls to `on_queue_changed` (e.g., maintain a separate "pending-suspended-but-untracked" retry set), and only allow a real `Resume` to be considered sent once the channel is properly tracked as suspended. At minimum, add a defensive periodic reconciliation (e.g., in `on_idle`) that attempts to insert previously-untracked-but-signaled-suspended channels back into `InboundXcmpSuspended` as capacity frees up.

### Proof of Concept
Rust integration test (extending existing `xcm_enqueueing_backpressure_works` style tests in `cumulus/pallets/xcmp-queue/src/tests.rs`):
1. Configure a mock runtime with `MaxInboundSuspended = 1` (or another small bound).
2. Pre-suspend one sibling `para_a` legitimately (fill its queue to `suspend_threshold`, verify it is in `InboundXcmpSuspended`).
3. Trigger a second sibling `para_b`'s queue to also cross `suspend_threshold` while `InboundXcmpSuspended` is already at capacity (`len() == MaxInboundSuspended`): call `on_queue_changed(para_b, fp_at_or_above_suspend_threshold)`.
4. Assert `Self::send_signal` for `para_b` succeeded (i.e., `SignalMessages`/`OutboundXcmpStatus` for `para_b` shows a pending `Suspend` signal), but `InboundXcmpSuspended` does **not** contain `para_b` (insert failed and was logged).
5. Drain `para_b`'s queue back to/below `resume_threshold` and call `on_queue_changed(para_b, fp_at_or_below_resume_threshold)`.
6. Assert that **no** `Resume` signal is ever queued for `para_b` in `SignalMessages`/`OutboundXcmpStatus`, proving the channel is permanently stuck in a "signaled-suspended-but-untracked" state with no automatic path to resumption.

### Citations

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L176-213)
```rust
	impl<T: Config> Pallet<T> {
		/// Suspends all XCM executions for the XCMP queue, regardless of the sender's origin.
		///
		/// - `origin`: Must pass `ControllerOrigin`.
		#[pallet::call_index(1)]
		#[pallet::weight((T::DbWeight::get().writes(1), DispatchClass::Operational,))]
		pub fn suspend_xcm_execution(origin: OriginFor<T>) -> DispatchResult {
			T::ControllerOrigin::ensure_origin(origin)?;

			QueueSuspended::<T>::try_mutate(|suspended| {
				if *suspended {
					Err(Error::<T>::AlreadySuspended.into())
				} else {
					*suspended = true;
					Ok(())
				}
			})
		}

		/// Resumes all XCM executions for the XCMP queue.
		///
		/// Note that this function doesn't change the status of the in/out bound channels.
		///
		/// - `origin`: Must pass `ControllerOrigin`.
		#[pallet::call_index(2)]
		#[pallet::weight((T::DbWeight::get().writes(1), DispatchClass::Operational,))]
		pub fn resume_xcm_execution(origin: OriginFor<T>) -> DispatchResult {
			T::ControllerOrigin::ensure_origin(origin)?;

			QueueSuspended::<T>::try_mutate(|suspended| {
				if !*suspended {
					Err(Error::<T>::AlreadyResumed.into())
				} else {
					*suspended = false;
					Ok(())
				}
			})
		}
```

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L643-666)
```rust
	fn send_signal(dest: ParaId, signal: ChannelSignal) -> Result<(), Error<T>> {
		let mut s = <OutboundXcmpStatus<T>>::get();
		if let Some(details) = s.iter_mut().find(|item| item.recipient == dest) {
			details.signals_exist = true;
		} else {
			s.try_push(OutboundChannelDetails::new(dest).with_signals()).map_err(|error| {
				tracing::debug!(target: LOG_TARGET, ?error, "Failed to activate XCMP channel");
				Error::<T>::TooManyActiveOutboundChannels
			})?;
		}

		let page = BoundedVec::<u8, T::MaxPageSize>::try_from(
			(XcmpMessageFormat::Signals, signal).encode(),
		)
		.map_err(|error| {
			tracing::debug!(target: LOG_TARGET, ?error, "Failed to encode signal message");
			Error::<T>::TooBig
		})?;
		let page = WeakBoundedVec::force_from(page.into_inner(), None);

		<SignalMessages<T>>::insert(dest, page);
		<OutboundXcmpStatus<T>>::put(s);
		Ok(())
	}
```

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L884-898)
```rust
		let mut suspended_channels = <InboundXcmpSuspended<T>>::get();
		let suspended = suspended_channels.contains(&para);

		if suspended && fp.ready_pages <= resume_threshold {
			if let Err(err) = Self::send_signal(para, ChannelSignal::Resume) {
				tracing::error!(
					target: LOG_TARGET,
					error=?err,
					sibling=?para,
					"defensive: Could not send resumption signal to inbound channel of sibling; channel remains suspended."
				);
			} else {
				suspended_channels.remove(&para);
				<InboundXcmpSuspended<T>>::put(suspended_channels);
			}
```

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L899-918)
```rust
		} else if !suspended && fp.ready_pages >= suspend_threshold {
			tracing::warn!(target: LOG_TARGET, sibling=?para, "XCMP queue for sibling is full; suspending channel.");

			if let Err(err) = Self::send_signal(para, ChannelSignal::Suspend) {
				// It will retry if `drop_threshold` is not reached, but it could be too late.
				tracing::error!(
					target: LOG_TARGET, error=?err,
					"defensive: Could not send suspension signal; future messages may be dropped."
				);
			} else if let Err(err) = suspended_channels.try_insert(para) {
				tracing::error!(
					target: LOG_TARGET,
					error=?err,
					sibling=?para,
					"Too many channels suspended; cannot suspend sibling; further messages may be dropped."
				);
			} else {
				<InboundXcmpSuspended<T>>::put(suspended_channels);
			}
		}
```
