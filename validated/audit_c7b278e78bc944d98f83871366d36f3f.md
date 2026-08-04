### Title
Permanent inbound channel suspension due to unhandled `send_signal` failure in `on_queue_changed` - (File: cumulus/pallets/xcmp-queue/src/lib.rs)

### Summary
`OnQueueChanged::on_queue_changed` only clears a sibling's suspension flag when `Self::send_signal(para, ChannelSignal::Resume)` returns `Ok`; on any `Err` (e.g. `TooManyActiveOutboundChannels` or `TooBig`) it merely logs and leaves the channel in `InboundXcmpSuspended` with no retry mechanism [1](#0-0) . Because `on_queue_changed` only fires when the message-queue footprint actually changes, a suspended channel whose one resume attempt fails has no further trigger to retry, resulting in indefinite starvation of that sibling's inbound XCM traffic.

### Finding Description
The suspend/resume state machine works as follows:
- `on_queue_changed` reads `resume_threshold`/`suspend_threshold` from `QueueConfig` and, when a previously-suspended sibling's `ready_pages` drops to/below `resume_threshold`, calls `Self::send_signal(para, ChannelSignal::Resume)` [2](#0-1) .
- `send_signal` first tries to find an existing `OutboundChannelDetails` entry for `dest` in `OutboundXcmpStatus`; if none exists it must `try_push` a new one, which fails with `Error::TooManyActiveOutboundChannels` once the bounded vector (capacity `MaxActiveOutboundChannels`) is full [3](#0-2) . It also bounds the encoded signal page to `T::MaxPageSize`, returning `Error::TooBig` on overflow, though a bare `ChannelSignal` encoding is tiny and this path is not realistically reachable by crafted signal content alone [4](#0-3) .
- Critically, on any `Err` from `send_signal`, the code path in `on_queue_changed` does **not** retry, does **not** requeue the resume attempt, and does **not** remove the para from `suspended_channels`; it only emits a `tracing::error!` [5](#0-4) . The `suspended_channels.remove(&para)` and storage write only happen in the `else` (success) branch [6](#0-5) .
- `on_queue_changed` is only invoked by the message queue when a footprint change occurs for that origin. If the queue for the suspended para stays static after the failed resume (no more inbound messages arrive, or arriving messages don't change `ready_pages` across the threshold again), there is no subsequent call that would re-attempt `send_signal`. This makes the suspension effectively permanent for that sibling until an unrelated footprint change happens to occur again below `resume_threshold` — which, if `OutboundXcmpStatus` remains saturated with other active channels, will fail again with the same error.

Exploit precondition: `OutboundXcmpStatus` (bounded by `MaxActiveOutboundChannels`) must be at capacity with entries for other destinations at the moment resume is attempted for the victim channel, and the victim para must have no pre-existing entry in `OutboundXcmpStatus` (i.e. the local chain has not yet sent anything outbound to that sibling). An attacker (or a busy/flooding set of participants) driving heavy outbound XCM traffic to many distinct sibling chains (up to `MaxActiveOutboundChannels`) while simultaneously flooding one target sibling's inbound queue to cross `suspend_threshold` can arrange for this precondition to hold at the exact block where the queue drains back under `resume_threshold`.

No signature/origin/fee check exists here that would stop this: `send_fragment`/`send_signal` are internal pallet mechanics invoked by the runtime's message routing on behalf of normal XCM sends triggered by ordinary extrinsics (e.g. reserve transfers, `pallet_xcm::send`), and the failure handling gap is a pure logic error, not a bypassed permission check.

### Impact Explanation
If triggered, `InboundXcmpSuspended` keeps the sibling parachain listed as suspended indefinitely. Since the runtime's XCMP inbound handler on the local side will keep the paired channel effectively degraded/suspended (per the pallet's inbound-suspend contract), all subsequent inbound XCM messages from that sibling — including reserve-asset transfer messages, arbitrary XCM interactions, and any HRMP-based governance/asset flows — can be delayed or dropped without a further external trigger, i.e., halting message delivery for a targeted sibling channel as scoped.

### Likelihood Explanation
This requires: (1) the local chain to be actively routing outbound XCM to a number of distinct sibling parachains at or near `MaxActiveOutboundChannels` (a chain-wide state, but reachable at scale on busy chains such as an asset hub with wide HRMP connectivity, or intentionally by an attacker with resources to trigger sends toward many distinct paraIds if permitted by filters); and (2) precise timing so the victim para has no existing `OutboundXcmpStatus` entry when the resume attempt occurs, while `OutboundXcmpStatus` is saturated. This is a non-trivial, timing- and scale-dependent precondition, not a single-transaction trivial exploit, but it is a genuine gap in the recovery logic — there is no explicit code defense against this outcome (only a `defensive!`-style log), and no retry or requeue exists elsewhere in the pallet to self-heal after a failed resume attempt.

### Recommendation
In `on_queue_changed`, on `send_signal` failure the pallet should not silently give up: either (a) keep an explicit pending-resume marker and retry the resume signal on `on_idle`/the next block regardless of further footprint changes, or (b) reserve capacity in `OutboundXcmpStatus` for signal-only entries so `TooManyActiveOutboundChannels` cannot occur for the resume path specifically (e.g., a dedicated small headroom bound below `MaxActiveOutboundChannels`, or evicting the least-recently-used signals-only entry to make room for a resume signal). At minimum, add a scheduled retry (e.g., via `on_idle`) that re-attempts `Self::send_signal(para, ChannelSignal::Resume)` for all paras still in `InboundXcmpSuspended` whose footprint is already below `resume_threshold`, so a one-time `send_signal` failure cannot permanently freeze a channel.

### Proof of Concept
Integration test plan (in `cumulus/pallets/xcmp-queue/src/tests.rs` style, using the pallet's mock runtime):
1. Configure `MaxActiveOutboundChannels` to a small bound `N` in the mock config.
2. Populate `OutboundXcmpStatus` with `N` distinct `OutboundChannelDetails` entries for paras `P1..PN` (via normal `send_fragment`/`send_xcm` calls to those destinations), none of which is the victim para `V`.
3. Drive inbound XCMP traffic from `V` (via `XcmpMessageHandler::handle_xcmp_messages`/enqueue path) until `fp.ready_pages >= suspend_threshold`, causing `on_queue_changed` to suspend `V` and add it to `InboundXcmpSuspended`.
4. Drain `V`'s queue (process/pop messages) until `fp.ready_pages <= resume_threshold`, triggering another `on_queue_changed` call for `V`.
5. Assert that because `OutboundXcmpStatus` is already at `N` (`MaxActiveOutboundChannels`) with no existing entry for `V`, `send_signal(V, ChannelSignal::Resume)` returns `Err(Error::TooManyActiveOutboundChannels)`.
6. Assert `InboundXcmpSuspended::<T>::get()` **still contains** `V` after this call, and after advancing multiple additional blocks/idle hooks with no further footprint change for `V`, the para remains permanently in `InboundXcmpSuspended` (i.e., no self-healing occurs) — proving the invariant "critical queues must not be permanently halted by valid user input" is violated.

### Citations

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L643-652)
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
```

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L654-661)
```rust
		let page = BoundedVec::<u8, T::MaxPageSize>::try_from(
			(XcmpMessageFormat::Signals, signal).encode(),
		)
		.map_err(|error| {
			tracing::debug!(target: LOG_TARGET, ?error, "Failed to encode signal message");
			Error::<T>::TooBig
		})?;
		let page = WeakBoundedVec::force_from(page.into_inner(), None);
```

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L879-898)
```rust
impl<T: Config> OnQueueChanged<ParaId> for Pallet<T> {
	// Suspends/Resumes the queue when certain thresholds are reached.
	fn on_queue_changed(para: ParaId, fp: QueueFootprint) {
		let QueueConfigData { resume_threshold, suspend_threshold, .. } = <QueueConfig<T>>::get();

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
