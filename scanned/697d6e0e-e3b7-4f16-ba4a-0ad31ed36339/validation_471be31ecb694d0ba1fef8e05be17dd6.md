### Title
Check-then-enact race in HRMP outbound message accounting allows `channel.total_size` to exceed `max_total_size` across multiple candidates of the same para in one relay block - ([File: polkadot/runtime/parachains/src/hrmp.rs])

### Summary
`Pallet::check_outbound_hrmp` validates a candidate's outbound HRMP messages against the *currently stored* `HrmpChannel.total_size`, but this check runs at backing time in `process_candidates`, while the actual mutation happens later (and unconditionally) in `queue_outbound_hrmp` during enactment. With elastic scaling, a single para can have multiple candidates backed within the same relay block, each independently checked against the same unmutated channel snapshot, so their combined enactment can push `total_size` past `max_total_size`.

### Finding Description
`check_outbound_hrmp` reads the channel via `HrmpChannels::<T>::get(&channel_id)` and verifies `channel.total_size + msg_size <= channel.max_total_size`: [1](#0-0) 

This check is invoked from `check_validation_outputs`, which is executed for each backed candidate during `process_candidates` (the backing/acceptance phase), independently per candidate: [2](#0-1) 

Crucially, `check_outbound_hrmp` performs no storage mutation — it is a pure read-and-validate function. The actual channel state (`total_size`, `msg_count`, `mqc_head`) is only updated later, in `queue_outbound_hrmp`, which runs during candidate *enactment* (after availability, in `enact_candidate`), and this function contains **no re-validation** of `max_total_size` or `max_capacity` — it unconditionally increments and writes: [3](#0-2) 

With elastic scaling (multiple cores assigned to the same `ParaId` in a single relay block), a collator can submit N distinct candidates in the same relay-chain block context, each carrying an outbound HRMP message to the same channel sized just under the remaining capacity. Because backing/acceptance for each candidate calls `check_outbound_hrmp` against the *same* on-storage `channel.total_size` (unchanged between the N checks, since none of them have been enacted yet), all N checks can pass individually even though their sum exceeds `max_total_size`. When these N candidates are later enacted sequentially (either in the same block if bitfields immediately confirm availability, or across a short subsequent window), `queue_outbound_hrmp` blindly applies each increment without re-checking the bound, resulting in `channel.total_size > channel.max_total_size`.

This is a genuine check-then-enact ordering flaw: the acceptance-criteria function and the enactment function are decoupled in time, and nothing tracks "in-flight, backed-but-not-yet-enacted" message sizes per channel to prevent double-counting against the same base snapshot.

### Impact Explanation
The core queue-accounting invariant "`HrmpChannel.total_size` never exceeds `channel.max_total_size`" can be violated by an unprivileged collator/parachain block producer through ordinary candidate submission (e.g., triggered by user-facing extrinsics that emit outbound HRMP messages, such as XCM reserve transfers). This breaks a relay-chain-enforced resource bound that channel participants (including the recipient para, which budgets buffer/queue capacity based on `max_total_size`) rely on for safety and DoS resistance, potentially causing unbounded queue growth in `HrmpChannelContents` beyond the configured channel bounds and unexpected behavior in receiving parachains that assume the invariant holds.

### Likelihood Explanation
Requires elastic scaling / multiple-cores-per-para to be enabled (a currently rolling-out but real production feature), and requires an actor able to get multiple candidates for the same para backed within the same relay block, each carrying an outbound HRMP message sized close to the remaining channel capacity. This is achievable by a normal collator (not requiring any privileged relay-chain access) producing several candidates per block, each triggered by ordinary parachain-side extrinsics that emit HRMP messages (e.g., repeated reserve-transfer-style XCM sends). It is repeatable every relay block as long as elastic scaling assigns multiple cores to the para.

### Recommendation
Track cumulative "pending" (backed-but-not-yet-enacted) message sizes/counts per channel across candidates processed within the same backing pass (or across pending-availability candidates in general), and validate against that cumulative value in `check_outbound_hrmp`, not just the currently committed `HrmpChannel.total_size`. Alternatively, add a defensive bound check inside `queue_outbound_hrmp` itself, saturating/rejecting/logging if enactment would exceed `max_total_size` or `max_capacity`, rather than relying solely on the earlier, now-stale acceptance check.

### Proof of Concept
Integration test plan (in `polkadot/runtime/parachains/src/hrmp/tests.rs` or an inclusion-pallet integration test with elastic scaling enabled):
1. Set up a channel with `max_total_size = X` and `max_message_size` large enough to allow messages near the cap.
2. Enable elastic scaling / assign 2+ cores to the same `ParaId` in one relay block.
3. Construct N `BackedCandidate`s for that para, each with one outbound HRMP message sized `X/N + 1` bytes (so any single one respects `max_total_size`, but the sum exceeds it).
4. Feed all N backed candidates through `process_candidates` in the same relay block (asserting each individually passes `check_outbound_hrmp`).
5. Drive availability/bitfields so all N candidates enact (`queue_outbound_hrmp` called sequentially) within the same or immediately following block.
6. Assert `HrmpChannels::<T>::get(&channel_id).total_size > max_total_size` — proving the invariant is violated, alongside `HrmpChannelContents` reflecting all N messages that individually passed acceptance but collectively overflow the configured bound.

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
