Audit Report

## Title
Inbound `ConcatenatedOpaqueVersionedXcm` handling creates spurious `OutboundChannelDetails` entries, consuming `MaxActiveOutboundChannels` capacity - (File: cumulus/pallets/xcmp-queue/src/lib.rs)

## Summary
`Pallet::handle_xcmp_messages` mutates the bounded `OutboundXcmpStatus` storage as a side effect of merely receiving an inbound page in `XcmpMessageFormat::ConcatenatedOpaqueVersionedXcm` format, via `try_get_or_insert_outbound_channel(&mut all_channels, sender)`, even though the sender is never a destination of any outbound message. This conflates "record that a peer supports the opaque encoding" with "allocate outbound channel capacity," letting each distinct inbound sender consume a slot of the bounded `T::MaxActiveOutboundChannels` vector without ever being sent anything.

## Finding Description
In the `ConcatenatedOpaqueVersionedXcm` branch of `handle_xcmp_messages`, the code retrieves `<OutboundXcmpStatus<T>>::get()`, calls `Self::try_get_or_insert_outbound_channel(&mut all_channels, sender)` to set a support flag, and writes the (potentially grown) vector back with `<OutboundXcmpStatus<T>>::put(all_channels)`: [1](#0-0) 

`try_get_or_insert_outbound_channel` will `try_push` a brand-new `OutboundChannelDetails::new(sender)` if no entry for that recipient already exists in the bounded vec: [2](#0-1) 

This is the same bounded storage, capacity `T::MaxActiveOutboundChannels`, that `send_fragment` and `send_signal` rely on when actually dispatching outbound messages/signals: [3](#0-2) [4](#0-3) [5](#0-4) 

This behavior originates from the `ConcatenatedOpaqueVersionedXcm` negotiation feature (see `prdoc/stable2603/pr_11263.prdoc`), which intentionally stores per-recipient support flags in `OutboundXcmpStatus`, but the implementation records this for the *sender of an inbound page* rather than only for actual outbound recipients, so it can create entries with no corresponding outbound traffic.

The mitigating factor is that `XcmpMessageSource::take_outbound_messages`, invoked every block, prunes any entry whose `ChannelInfo::get_channel_status` returns `Closed` — i.e., no real outbound HRMP channel toward that ParaId: [6](#0-5) 

So a spurious entry created purely from inbound processing is removed the next time this runs (once per block), confining the effect to the current block unless re-triggered every block.

## Impact Explanation
Within a single block, an attacker controlling (or having caused acceptance of) up to `T::MaxActiveOutboundChannels` distinct inbound HRMP channels toward the victim can flood minimal opaque-format pages from each sender before any legitimate `send_fragment`/`send_signal` executes in that block, causing the legitimate call to fail with `MessageSendError::TooManyChannels` / `Error::TooManyActiveOutboundChannels`. This is a genuine, code-confirmed accounting bug: an inbound-only interaction consumes capacity meant for outbound channel bookkeeping. However, it is a transient, per-block griefing effect rather than a persistent denial of service, since `take_outbound_messages` prunes closed-channel entries every block, requiring the attacker to re-flood every single block to sustain any effect.

## Likelihood Explanation
Exploitation requires the attacker to actually possess `T::MaxActiveOutboundChannels` (e.g. 128 in the mock/most production configs) distinct, relay-chain-validated one-way inbound HRMP channels toward the victim — these cannot be forged by an unprivileged signed account and normally require bilateral HRMP channel establishment (deposit plus acceptance by the victim or an auto-accept relay-chain policy). Assembling that many real channels toward a single victim is costly and, absent an unusually permissive channel-acceptance policy on the victim's part, requires the victim's own participation in accepting the channels. Combined with the fact that the griefing effect resets every block and must be continuously re-triggered, the practical likelihood of a sustained, impactful exploitation is low, though the underlying code defect (conflating inbound-encoding negotiation with outbound-channel-slot allocation) is real and confirmed in the current code.

## Recommendation
Do not insert a new `OutboundChannelDetails` entry into the bounded `OutboundXcmpStatus` merely to record that a sender supports opaque encoding. Use `try_get_outbound_channel` (read-only lookup) instead of `try_get_or_insert_outbound_channel` when processing inbound pages, and only set the support flag if an outbound-channel entry already exists for that recipient; alternatively, track "recipient supports `ConcatenatedOpaqueVersionedXcm`" in a separate, unbounded-by-`MaxActiveOutboundChannels` storage item (e.g., a `StorageMap<ParaId, OutboundChannelFlags>`) so this negotiation bookkeeping is decoupled from the outbound-sending capacity accounting.

## Proof of Concept
1. In a mock runtime with a small `MaxActiveOutboundChannels` (e.g., `ConstU32<2>`), call `Pallet::<Test>::handle_xcmp_messages` with an iterator yielding, for `MaxActiveOutboundChannels` distinct `ParaId`s, minimal pages encoded as `(XcmpMessageFormat::ConcatenatedOpaqueVersionedXcm, <empty/trivial opaque xcm>).encode()`.
2. Assert `OutboundXcmpStatus::<Test>::get().len() == MaxActiveOutboundChannels` even though no outbound message was queued to any of these ParaIds.
3. In the same block (before `take_outbound_messages` runs), attempt `Pallet::<Test>::send_fragment` (or the `SendXcm` `deliver` path) to a new, unrelated `ParaId` with an actual open outbound HRMP channel, and observe it fails with `MessageSendError::TooManyChannels` / `Error::TooManyActiveOutboundChannels`.
4. Call `Pallet::<Test>::take_outbound_messages(...)` and confirm the spurious entries are pruned because `ChannelInfo::get_channel_status` returns `Closed` for those ParaIds, demonstrating the transient, per-block nature of the exhaustion.

### Citations

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L334-338)
```rust
	pub(super) type OutboundXcmpStatus<T: Config> = StorageValue<
		_,
		BoundedVec<OutboundChannelDetails, T::MaxActiveOutboundChannels>,
		ValueQuery,
	>;
```

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L521-538)
```rust
	fn try_get_or_insert_outbound_channel(
		all_channels: &mut BoundedVec<OutboundChannelDetails, T::MaxActiveOutboundChannels>,
		recipient: ParaId,
	) -> Option<&mut OutboundChannelDetails> {
		for channel_idx in 0..all_channels.len() {
			if all_channels[channel_idx].recipient == recipient {
				return Some(&mut all_channels[channel_idx]);
			}
		}

		all_channels
			.try_push(OutboundChannelDetails::new(recipient))
			.inspect_err(|e| {
				tracing::error!(target: LOG_TARGET, error=?e, "Failed to insert outbound HRMP channel");
			})
			.ok()?;
		all_channels.last_mut()
	}
```

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L587-590)
```rust
		let mut all_channels = <OutboundXcmpStatus<T>>::get();
		let channel_details =
			Self::try_get_or_insert_outbound_channel(&mut all_channels, recipient)
				.ok_or(MessageSendError::TooManyChannels)?;
```

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

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L1010-1019)
```rust
						XcmpMessageFormat::ConcatenatedOpaqueVersionedXcm => {
							let mut all_channels = <OutboundXcmpStatus<T>>::get();
							if let Some(channel_details) =
								Self::try_get_or_insert_outbound_channel(&mut all_channels, sender)
							{
								channel_details
									.flags
									.notice_concatenated_opaque_versioned_xcm_support();
							}
							<OutboundXcmpStatus<T>>::put(all_channels);
```

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L1108-1119)
```rust
			let (max_size_now, max_size_ever) = match T::ChannelInfo::get_channel_status(*para_id) {
				ChannelStatus::Closed => {
					// This means that there is no such channel anymore. Nothing to be done but
					// swallow the messages and discard the status.
					for i in *first_index..*last_index {
						<OutboundXcmpMessages<T>>::remove(*para_id, i);
					}
					if *signals_exist {
						<SignalMessages<T>>::remove(*para_id);
					}
					return false;
				},
```
