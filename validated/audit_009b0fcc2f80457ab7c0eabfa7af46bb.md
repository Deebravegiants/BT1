Audit Report

## Title
Check-then-enact race in HRMP outbound message accounting allows `channel.total_size` to exceed `max_total_size` across multiple candidates of the same para in one relay block - ([File: polkadot/runtime/parachains/src/hrmp.rs])

## Summary
`check_outbound_hrmp` validates a candidate's outbound HRMP messages against the currently stored `HrmpChannel.total_size`, but this check occurs during backing/acceptance (`check_validation_outputs`, invoked per-candidate from `process_candidates`), while the actual size mutation happens later and unconditionally in `queue_outbound_hrmp` during enactment. Since neither `check_outbound_hrmp` nor `queue_outbound_hrmp` tracks in-flight, backed-but-not-yet-enacted totals, multiple candidates of the same para backed in one relay block (enabled by elastic scaling) can each pass acceptance against the same stale snapshot and later collectively exceed `max_total_size` upon sequential enactment.

## Finding Description
`check_outbound_hrmp` reads `HrmpChannels::<T>::get(&channel_id)` and validates `channel.total_size + msg_size <= channel.max_total_size` without any mutation: [1](#0-0) 

This is invoked from `check_validation_outputs` in `inclusion/mod.rs`, which runs per backed candidate during the acceptance-criteria check: [2](#0-1) 

The actual state mutation occurs separately in `queue_outbound_hrmp`, which unconditionally increments `channel.total_size` and `channel.msg_count` and writes back to storage, with no re-validation against `max_total_size` or `max_capacity`: [3](#0-2) 

This decoupling between the read-only acceptance check and the later unconditional enactment write is real and confirmed by direct inspection of the code. With elastic scaling assigning multiple cores to the same `ParaId`, several candidates for that para can be backed in the same relay block, each independently calling `check_outbound_hrmp` against the same unmutated `HrmpChannels` storage entry, since none of the candidates have been enacted yet at backing time.

## Impact Explanation
If exploitable, this would violate the relay-chain-enforced invariant that `HrmpChannel.total_size` never exceeds `channel.max_total_size`, potentially causing unbounded queue growth in `HrmpChannelContents` beyond configured bounds and unexpected behavior in receiving parachains that assume this bound holds. This would be a genuine accounting/resource-bound violation in the HRMP pallet, not a node-only or admin-only issue, and would be triggerable by an ordinary collator via normal parachain block production (e.g., XCM messages triggering HRMP sends), not requiring privileged relay-chain access.

## Likelihood Explanation
This requires elastic scaling (multiple cores assigned to the same `ParaId` within one relay block) to be enabled and active, and requires the para's collator(s) to construct multiple candidates each carrying outbound HRMP messages sized close to the remaining channel capacity, all backed within the same relay block before any of them are enacted. This is a real, currently-active feature path (elastic scaling), and the mechanics described (independent per-candidate checks against unmutated storage, followed by unconditional sequential enactment writes) are confirmed present in the code without any additional per-block or per-para cumulative tracking to prevent double-counting against the same base snapshot.

## Recommendation
Track cumulative "pending" (backed-but-not-yet-enacted) message sizes/counts per channel across all candidates processed within the same backing pass (or across all currently pending-availability candidates), and validate `check_outbound_hrmp` against that cumulative value rather than only the currently committed `HrmpChannel.total_size`. As a defense-in-depth measure, add a saturating/rejecting check inside `queue_outbound_hrmp` itself against `max_total_size` and `max_capacity` at enactment time, rather than relying solely on the earlier, potentially stale acceptance check.

## Proof of Concept
1. Configure a channel with `max_total_size = X` and `max_message_size` sufficient to allow messages sized near the cap.
2. Enable elastic scaling and assign 2+ cores to the same `ParaId` within one relay block.
3. Construct N `BackedCandidate`s for that para, each carrying one outbound HRMP message sized `X/N + 1` bytes, so any single message respects `max_total_size` individually but the sum exceeds it.
4. Process all N backed candidates through `process_candidates` in the same relay block; each individually passes `check_outbound_hrmp` since `HrmpChannels` storage is unchanged between checks.
5. Drive availability/bitfields so all N candidates enact via `queue_outbound_hrmp` sequentially within the same or an immediately following block.
6. Assert `HrmpChannels::<T>::get(&channel_id).total_size > max_total_size`, demonstrating that the bound was violated despite each candidate individually passing acceptance.

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1264-1287)
```rust
			let channel_id = HrmpChannelId { sender, recipient: out_msg.recipient };

			let channel = match HrmpChannels::<T>::get(&channel_id) {
				Some(channel) => channel,
				None => return Err(OutboundHrmpAcceptanceErr::NoSuchChannel { channel_id, idx }),
			};

			let msg_size = out_msg.data.len() as u32;
			if msg_size > channel.max_message_size {
				return Err(OutboundHrmpAcceptanceErr::MaxMessageSizeExceeded {
					idx,
					msg_size,
					max_size: channel.max_message_size,
				});
			}

			let new_total_size = channel.total_size + out_msg.data.len() as u32;
			if new_total_size > channel.max_total_size {
				return Err(OutboundHrmpAcceptanceErr::TotalSizeExceeded {
					idx,
					total_size: new_total_size,
					limit: channel.max_total_size,
				});
			}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1377-1408)
```rust
	pub(crate) fn queue_outbound_hrmp(sender: ParaId, out_hrmp_msgs: HorizontalMessages) {
		let now = frame_system::Pallet::<T>::block_number();

		for out_msg in out_hrmp_msgs {
			let channel_id = HrmpChannelId { sender, recipient: out_msg.recipient };

			let mut channel = match HrmpChannels::<T>::get(&channel_id) {
				Some(channel) => channel,
				None => {
					// apparently, that since acceptance of this candidate the recipient was
					// offboarded and the channel no longer exists.
					continue;
				},
			};

			let inbound = InboundHrmpMessage { sent_at: now, data: out_msg.data };

			// book keeping
			channel.msg_count += 1;
			channel.total_size += inbound.data.len() as u32;

			// compute the new MQC head of the channel
			let prev_head = channel.mqc_head.unwrap_or(Default::default());
			let new_head = BlakeTwo256::hash_of(&(
				prev_head,
				inbound.sent_at,
				T::Hashing::hash_of(&inbound.data),
			));
			channel.mqc_head = Some(new_head);

			HrmpChannels::<T>::insert(&channel_id, channel);
			HrmpChannelContents::<T>::append(&channel_id, inbound);
```

**File:** polkadot/runtime/parachains/src/inclusion/mod.rs (L1406-1415)
```rust
		hrmp::Pallet::<T>::check_outbound_hrmp(&self.config, para_id, horizontal_messages)
			.map_err(|e| {
				log::debug!(
					target: LOG_TARGET,
					"Check outbound hrmp for parachain `{}` failed, error: {:?}",
					u32::from(para_id),
					e
				);
				e
			})?;
```
