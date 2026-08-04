### Title
Unbounded `hrmp_init_open_channel` + `hrmp_cancel_open_request` cycling lets an attacker para permanently inflate a victim para's `DeliveryFeeFactor` - (File: polkadot/runtime/parachains/src/dmp.rs, polkadot/runtime/parachains/src/hrmp.rs)

### Summary
The HRMP notification path (`init_open_channel` -> `send_to_para` -> `Dmp::queue_downward_message`) unconditionally enqueues a downward message to the *recipient* named in the call and bumps that recipient's `DeliveryFeeFactor` once the DMQ length crosses `threshold`. Because `hrmp_cancel_open_request` removes the pending request (and its "already requested" guard) without a cooldown, an attacker-controlled para can repeatedly cycle `hrmp_init_open_channel(victim, ...)` / `hrmp_cancel_open_request(...)` against the same victim, each cycle costing only a transient reserve/unreserve and normal extrinsic fees — none of which scale with the victim's `DeliveryFeeFactor` — while the victim's fee factor can only fall via `prune_dmq`, which is entirely receiver-driven.

### Finding Description
`Pallet::queue_downward_message` [1](#0-0)  enqueues the message and, if the resulting DMQ length exceeds `threshold = dmq_max_length / THRESHOLD_FACTOR`, calls `increase_fee_factor(para, ...)`. The factor is decreased only in `prune_dmq`, invoked when the *recipient* para actually processes/prunes messages [2](#0-1) . There is no time-based or externally-triggerable decay independent of the recipient consuming its own queue.

`Hrmp::init_open_channel` is reachable from any parachain via the signed `hrmp_init_open_channel` extrinsic (`ensure_parachain` origin) [3](#0-2) . On success it unconditionally sends a `HrmpNewChannelOpenRequest` notification to `recipient` via `send_to_para` -> `dmp::Pallet::<T>::queue_downward_message` [4](#0-3) [5](#0-4) . This queuing bypasses the normal DMP fee-payment path (this is a protocol notification, not a fee-metered XCM send), so the attacker pays no fee proportional to the fee factor it is inflating.

The only guard against repeated requests to the same recipient is the "already requested" check in `init_open_channel` [6](#0-5) . However, `Hrmp::cancel_open_request` lets the sender unilaterally remove its own pending (unconfirmed) request and immediately get its deposit back, with no cooldown or rate limit [7](#0-6) . This clears `HrmpOpenChannelRequests` and decrements `HrmpOpenChannelRequestCount`, re-opening the door for another `hrmp_init_open_channel(victim, ...)` call in the very next block (or even later in the same block, since these are separate extrinsics), each producing another downward message and another opportunity to push the DMQ length back over `threshold`.

Thus: attacker para A repeatedly executes `init_open_channel(A, victim) -> cancel_open_request(A, victim) -> init_open_channel(A, victim) -> ...`. Each iteration queues one message to `victim`'s DMQ via `queue_downward_message`, and once the victim's queue length exceeds `threshold`, `DeliveryFeeFactor[victim]` is multiplicatively increased every iteration. Since the victim's queue can only shrink (and the fee factor only fall) when the victim itself processes and reports `processed_downward_messages` on-chain, a victim that is slow, congested, or simply unable to keep pace with the flood will see its `DeliveryFeeFactor` ratchet upward indefinitely, at negligible/no cost to the attacker beyond ordinary transaction fees.

### Impact Explanation
Legitimate senders paying DMP delivery fees to reach the victim para (e.g. via UMP/XCM routed through `xcm_sender.rs`'s `FeeTracker`-based pricing) are priced out as `DeliveryFeeFactor` for that para climbs, with no mechanism to reset it except the victim outpacing the attacker's flood. This is an economic denial-of-service on a specific para's downward message channel, matching the scoped impact (no direct fund theft, but an effectively trapped/overpriced DMP channel).

### Likelihood Explanation
Feasible with a single attacker-controlled parachain and no cooperation from the victim: `hrmp_init_open_channel`/`hrmp_cancel_open_request` are ordinary signed-by-parachain-origin extrinsics with no rate limiting between cancel and re-init. The attack is fully repeatable every block (bounded only by block weight/extrinsic throughput), and cost per cycle is a temporary deposit (returned) plus base transaction fees — not scaled to the fee factor being inflated. The main mitigating factor is `dmq_max_length` (hard cap dropping further messages), but the fee factor increase from crossing `threshold` (half of max length) persists regardless, and once inflated it decays only through the victim's own processing.

### Recommendation
- Rate-limit or add a cooldown between `hrmp_cancel_open_request` and a subsequent `hrmp_init_open_channel` for the same `(sender, recipient)` pair.
- Consider not counting HRMP-protocol notification messages toward the same `DeliveryFeeFactor`-triggering threshold as regular DMP traffic, or charge the initiating para a fee proportional to the current `DeliveryFeeFactor` of the recipient when sending such notifications.
- Add a time-based decay for `DeliveryFeeFactor` independent of `prune_dmq`, so a stalled/slow recipient's fee factor cannot be inflated indefinitely by a third party.

### Proof of Concept
Rust unit test in `polkadot/runtime/parachains/src/hrmp/tests.rs` (or `dmp/tests.rs`):
1. Register attacker para `A` and victim para `B` (do not have `B` process any DMP messages, i.e. never call `Dmp::prune_dmq(B, _)`).
2. Loop N times:
   - `Hrmp::hrmp_init_open_channel(A_origin, B, cap, size)` — assert `Ok`.
   - Assert `Dmp::dmq_length(B)` increased by 1.
   - `Hrmp::hrmp_cancel_open_request(A_origin, HrmpChannelId{sender:A, recipient:B})` — assert `Ok` and deposit unreserved.
3. After the loop, once `dmq_length(B) > threshold`, assert `DeliveryFeeFactor::<Test>::get(B)` has strictly increased across iterations and never decreases (since `prune_dmq(B, _)` was never called).
4. Assert the attacker's reserved balance returns to baseline after each cycle (cost-free besides tx fees), demonstrating asymmetry between attacker cost and victim fee inflation.

### Citations

**File:** polkadot/runtime/parachains/src/dmp.rs (L300-326)
```rust
	pub fn queue_downward_message(
		config: &HostConfiguration<BlockNumberFor<T>>,
		para: ParaId,
		msg: DownwardMessage,
	) -> Result<(), QueueDownwardMessageError> {
		let serialized_len = msg.len();
		Self::can_queue_downward_message(config, &para, &msg)?;

		let inbound = InboundDownwardQueue::<T>::push_back(para, msg)
			.map_err(|_| QueueDownwardMessageError::ExceedsMaxQueueSize)?;
		let q_len = InboundDownwardQueue::<T>::len(para).unwrap_or(0);

		// obtain the new link in the MQC and update the head.
		DownwardMessageQueueHeads::<T>::mutate(para, |head| {
			let new_head =
				BlakeTwo256::hash_of(&(*head, inbound.sent_at, T::Hashing::hash_of(&inbound.msg)));
			*head = new_head;
		});

		let threshold =
			Self::dmq_max_length(config.max_downward_message_size).saturating_div(THRESHOLD_FACTOR);
		if q_len > threshold as u64 {
			Self::increase_fee_factor(para, serialized_len as u128);
		}

		Ok(())
	}
```

**File:** polkadot/runtime/parachains/src/dmp.rs (L362-373)
```rust
	/// Prunes the specified number of messages from the downward message queue of the given para.
	pub(crate) fn prune_dmq(para: ParaId, processed_downward_messages: u32) {
		InboundDownwardQueue::<T>::drop_front_n(para, processed_downward_messages as u64);
		let q_len = InboundDownwardQueue::<T>::len(para).unwrap_or(0);

		let config = configuration::ActiveConfig::<T>::get();
		let threshold =
			Self::dmq_max_length(config.max_downward_message_size).saturating_div(THRESHOLD_FACTOR);
		if q_len <= threshold as u64 {
			Self::decrease_fee_factor(para);
		}
	}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L515-537)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(<T as Config>::WeightInfo::hrmp_init_open_channel())]
		pub fn hrmp_init_open_channel(
			origin: OriginFor<T>,
			recipient: ParaId,
			proposed_max_capacity: u32,
			proposed_max_message_size: u32,
		) -> DispatchResult {
			let origin = ensure_parachain(<T as Config>::RuntimeOrigin::from(origin))?;
			Self::init_open_channel(
				origin,
				recipient,
				proposed_max_capacity,
				proposed_max_message_size,
			)?;
			Self::deposit_event(Event::OpenChannelRequested {
				sender: origin,
				recipient,
				proposed_max_capacity,
				proposed_max_message_size,
			});
			Ok(())
		}
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1467-1475)
```rust
		let channel_id = HrmpChannelId { sender: origin, recipient };
		ensure!(
			HrmpOpenChannelRequests::<T>::get(&channel_id).is_none(),
			Error::<T>::OpenHrmpChannelAlreadyRequested,
		);
		ensure!(
			HrmpChannels::<T>::get(&channel_id).is_none(),
			Error::<T>::OpenHrmpChannelAlreadyExists,
		);
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1511-1523)
```rust
		Self::send_to_para(
			"init_open_channel",
			&config,
			recipient,
			Self::wrap_notification(|| {
				use xcm::opaque::latest::{prelude::*, Xcm};
				Xcm(vec![HrmpNewChannelOpenRequest {
					sender: origin.into(),
					max_capacity: proposed_max_capacity,
					max_message_size: proposed_max_message_size,
				}])
			}),
		);
```

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1578-1606)
```rust
	fn cancel_open_request(origin: ParaId, channel_id: HrmpChannelId) -> DispatchResult {
		// check if the origin is allowed to close the channel.
		ensure!(channel_id.is_participant(origin), Error::<T>::CancelHrmpOpenChannelUnauthorized);

		let open_channel_req = HrmpOpenChannelRequests::<T>::get(&channel_id)
			.ok_or(Error::<T>::OpenHrmpChannelDoesntExist)?;
		ensure!(!open_channel_req.confirmed, Error::<T>::OpenHrmpChannelAlreadyConfirmed);

		// Remove the request by the channel id and sync the accompanying list with the set.
		HrmpOpenChannelRequests::<T>::remove(&channel_id);
		HrmpOpenChannelRequestsList::<T>::mutate(|open_req_channels| {
			if let Some(pos) = open_req_channels.iter().position(|x| x == &channel_id) {
				open_req_channels.swap_remove(pos);
			}
		});

		Self::decrease_open_channel_request_count(channel_id.sender);
		// Don't decrease `HrmpAcceptedChannelRequestCount` because we don't consider confirmed
		// requests here.

		// Unreserve the sender's deposit. The recipient could not have left their deposit because
		// we ensured that the request is not confirmed.
		T::Currency::unreserve(
			&channel_id.sender.into_account_truncating(),
			open_channel_req.sender_deposit.unique_saturated_into(),
		);

		Ok(())
	}
```

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
