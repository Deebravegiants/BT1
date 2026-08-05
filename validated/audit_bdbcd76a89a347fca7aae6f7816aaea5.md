Audit Report

## Title
Failed `suspended_channels.try_insert` after a successful `Suspend` signal permanently desyncs local suspension tracking, stalling inbound XCMP for the affected sibling - ([File: cumulus/pallets/xcmp-queue/src/lib.rs])

## Summary
In `on_queue_changed`, `Self::send_signal(para, ChannelSignal::Suspend)` is called and, if successful, the `Suspend` signal is already committed to `OutboundXcmpStatus`/`SignalMessages` for transmission to the sibling. Only afterwards does the code attempt `suspended_channels.try_insert(para)`; if this fails because `InboundXcmpSuspended` is at `MaxInboundSuspended` capacity, the error is merely logged and never rolled back or retried, leaving the sibling's channel "signaled-suspended" on the wire but untracked locally. [1](#0-0) 

## Finding Description
`on_queue_changed` computes `suspended` solely from `InboundXcmpSuspended::<T>::get().contains(&para)` [2](#0-1) . In the suspend branch, `send_signal` is invoked first, and only on its success does the code attempt `suspended_channels.try_insert(para)`; if that insert fails, the code logs a "defensive" error and takes no corrective action, leaving `InboundXcmpSuspended` never updated for that `para` [1](#0-0) . `send_signal` itself directly mutates `OutboundXcmpStatus` and `SignalMessages`, meaning the `Suspend` signal will genuinely be sent to the sibling regardless of whether the subsequent bookkeeping step succeeds [3](#0-2) . Since the resume branch is gated exclusively on `suspended` (derived from `InboundXcmpSuspended`), and that para was never inserted, the resume branch condition `suspended && fp.ready_pages <= resume_threshold` can never become true for this para again, so no automatic `Resume` signal will ever be sent by this logic [4](#0-3) . The pallet's `suspend_xcm_execution`/`resume_xcm_execution` calls only toggle the unrelated global `QueueSuspended` bool and provide no way to manually reinsert a specific `para` into `InboundXcmpSuspended` or force a per-channel resume, confirming there is no recovery path short of a runtime upgrade/migration.

This matches the code exactly as cited, and the root cause (a non-atomic signal-send followed by a fallible local-bookkeeping step with no rollback or retry) is real and verifiable directly in the source.

## Impact Explanation
Once the desync occurs for a given sibling `para`, that sibling's outbound channel (suspended per its own receipt of the genuine `Suspend` signal) will never receive a corresponding `Resume` signal from this pallet's automatic backpressure logic, even after the local queue for that `para` fully drains. This causes a persistent, non-self-healing inbound XCMP stall for the affected sibling — a genuine state-inconsistency and message-delivery-loss bug in core parachain messaging infrastructure.

## Likelihood Explanation
The bug is only reachable when `InboundXcmpSuspended` (bounded by `MaxInboundSuspended`) is already at full capacity across many parachains at the moment a new sibling's queue crosses `suspend_threshold`. This is a systemic congestion precondition (multiple siblings concurrently suspended) rather than something a single unprivileged actor can unilaterally and cheaply engineer, since `MaxInboundSuspended` is configured as a reasonably generous bound in production runtimes (values referenced across asset-hub, bridge-hub, collectives, coretime, people, penpal, and other runtime configs). No privileged origin, governance action, or malicious node behavior is required to reach the code path in principle — only queue-footprint growth via genuine XCM/HRMP traffic — but a real-world trigger requires many parachains near-simultaneously saturating the bound, which is a plausible but non-trivial precondition to arrange.

## Recommendation
Make the two side effects transactional: attempt `suspended_channels.try_insert(para)` before calling `Self::send_signal(..., Suspend)`, and only send the signal if the local insert succeeds. Alternatively, if the insert fails after a successful signal send, retry inserting the para into `InboundXcmpSuspended` on subsequent calls to `on_queue_changed` (e.g. via a separate pending-but-untracked retry set), and add periodic reconciliation (e.g. in `on_idle`) to insert previously signaled-but-untracked suspended channels back into `InboundXcmpSuspended` as capacity frees up.

## Proof of Concept
1. Configure a mock runtime with a small `MaxInboundSuspended` bound (e.g. 1).
2. Drive `para_a`'s queue footprint to `suspend_threshold` via `on_queue_changed`, confirming it is inserted into `InboundXcmpSuspended` (filling the bound to capacity).
3. Drive `para_b`'s queue footprint to `suspend_threshold` via `on_queue_changed` while `InboundXcmpSuspended` is already full; confirm `Self::send_signal(para_b, ChannelSignal::Suspend)` succeeds (a `Suspend` signal is queued in `OutboundXcmpStatus`/`SignalMessages` for `para_b`) but `suspended_channels.try_insert(para_b)` fails and `InboundXcmpSuspended` does not contain `para_b`.
4. Drain `para_b`'s queue footprint back to/below `resume_threshold` and call `on_queue_changed(para_b, ...)` again.
5. Assert no `Resume` signal is ever queued for `para_b`, demonstrating the permanent desync described above.

### Citations

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

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L884-885)
```rust
		let mut suspended_channels = <InboundXcmpSuspended<T>>::get();
		let suspended = suspended_channels.contains(&para);
```

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L887-898)
```rust
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
