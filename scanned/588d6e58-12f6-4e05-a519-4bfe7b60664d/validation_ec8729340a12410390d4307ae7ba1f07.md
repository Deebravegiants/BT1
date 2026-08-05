### Title
Free HRMP open/cancel notification loop lets an attacker parachain grief a victim's downward message queue and bypass the `DeliveryFeeFactor` anti-spam mechanism - (File: polkadot/runtime/parachains/src/hrmp.rs, polkadot/runtime/parachains/src/dmp.rs)

### Summary
`hrmp_init_open_channel` unconditionally enqueues an `HrmpNewChannelOpenRequest` DMP notification to the target recipient via `queue_downward_message`/`can_queue_downward_message`, while the paired `hrmp_cancel_open_request` refunds the deposit and removes the request without any cooldown. An attacker-controlled parachain can therefore loop init→cancel against a fixed victim para at near-zero net cost, growing the victim's `DownwardMessageQueuePages` without triggering any economic deterrent, since the `DeliveryFeeFactor` mechanism is not applied as a gating check on this code path.

### Finding Description
`Pallet::init_open_channel` (`polkadot/runtime/parachains/src/hrmp.rs:1443-1526`) checks only concurrent-request limits (`egress_cnt + open_req_cnt < channel_num_limit`) and unconditionally calls `Self::send_to_para(..., Self::wrap_notification(...))` at lines 1511-1523, which calls `dmp::Pallet::<T>::queue_downward_message` (`hrmp.rs:1892-1913`). `hrmp_cancel_open_request`/`cancel_open_request` (`hrmp.rs:1578-1606`) removes the request, decrements `HrmpOpenChannelRequestCount`, and unreserves the sender deposit — but per the implementers'-guide spec and the code, it sends **no** DMP notification. Because the concurrent-request counter is decremented on cancel, the per-account channel-count limit (`config.hrmp_max_parachain_outbound_channels`) never blocks repeated cycles over time; it only bounds requests outstanding *at a single instant*.

In `dmp.rs`, `can_queue_downward_message` (`dmp.rs:269-290`) enforces `serialized_len <= max_downward_message_size` and a hard cap `dmq_length(para) <= dmq_max_length(...)` (derived from `MAX_POSSIBLE_ALLOCATION / max_downward_message_size`), returning `ExceedsMaxMessageSize` once the queue is full — this is documented as an OOM-prevention "hard limit," not a per-sender or per-para fairness control. `queue_downward_message` (`dmp.rs:300-326`) independently raises `DeliveryFeeFactor` once `dmq_length` exceeds `dmq_max_length/THRESHOLD_FACTOR`, but that fee factor is only consumed by callers that price outgoing DMP messages (e.g. real XCM senders); the HRMP notification path calls `queue_downward_message` directly with no fee check or payment, so the fee-factor deterrent does not restrain the attacker at all — it only inflates fees for unrelated, legitimate future senders to that para.

Exploit flow: attacker's parachain repeatedly dispatches `hrmp_init_open_channel(victim, ...)` then `hrmp_cancel_open_request(...)` (each cycle refunds the sender deposit, so the only recurring cost is weight/PoV for the UMP-dispatched extrinsics), each `init` call enqueuing one message into `DownwardMessageQueuePages[victim]`. Repeated across enough blocks (bounded only by UMP/candidate weight and message-count limits, not by any per-target cooldown), `dmq_length(victim)` approaches `dmq_max_length`. Once at cap, subsequent `can_queue_downward_message` calls for `victim` — including from unrelated/legitimate senders and system messages — return `ExceedsMaxMessageSize` and are dropped (see `send_to_para`'s `debug_assert!(false)` fallback), denying downward delivery to that specific para.

### Impact Explanation
This is a targeted, low-cost denial-of-service of downward message delivery to a specific victim parachain: once `dmq_length(victim)` is driven near `dmq_max_length`, all further DMP messages to that para (XCM transfers, HRMP channel-closing notices, teleport instructions, etc.) are silently dropped rather than delivered, matching the scoped impact of "temporary or indefinite denial of downward message delivery to a targeted parachain."

### Likelihood Explanation
Preconditions require only that the attacker control a registered parachain capable of dispatching `hrmp_init_open_channel`/`hrmp_cancel_open_request` (both `ensure_parachain`-gated, reachable by any parachain, no special privilege). The attack is repeatable indefinitely across blocks; the sender deposit is refunded every cycle so there is no escalating economic cost, and the `DeliveryFeeFactor` anti-spam mechanism — the system's intended defense against exactly this kind of queue-filling — is bypassed because it is never checked on the HRMP notification path. The only throttle is UMP/candidate weight and per-block upward message count limits, which slow but do not prevent eventual queue exhaustion.

### Recommendation
Apply a cost or rate limit to HRMP open/cancel notification spam directed at the same recipient — e.g., charge (and do not refund) a fee tied to `DeliveryFeeFactor` for notifications sent via `send_to_para`, enforce a minimum cooldown between `hrmp_init_open_channel` calls from the same `(sender, recipient)` pair, or track and cap the number of open/cancel cycles per sender/recipient pair per session, so that repeated free cycling cannot approach `dmq_max_length` for an arbitrary victim.

### Proof of Concept
Rust integration test in `polkadot/runtime/parachains/src/hrmp/tests.rs` style:
1. Register attacker para `A` and victim para `V` (`register_parachain`), advance to a live session.
2. In a loop (e.g., N = enough to approach `dmq_max_length(config.max_downward_message_size)`):
   - `assert_ok!(Hrmp::hrmp_init_open_channel(A_origin, V, cap, size))`
   - assert `Dmp::dmq_length(V)` increased by 1 and `HrmpOpenChannelRequests` contains the request.
   - `assert_ok!(Hrmp::hrmp_cancel_open_request(A_origin, HrmpChannelId{A,V}, 1))`
   - assert deposit for `A` is fully unreserved (net cost ~0) and `HrmpOpenChannelRequestCount(A) == 0`.
3. After the loop, assert `Dmp::dmq_length(V)` is at or near `Dmp::dmq_max_length` (expose via a test-only getter or infer via repeated failures).
4. Attempt a legitimate `queue_downward_message`/another `hrmp_init_open_channel` targeting `V` from a different, honest para `B` and assert it now returns `Err(QueueDownwardMessageError::ExceedsMaxMessageSize)` (or is silently dropped), proving denial of downward delivery to `V`.
5. Assert `DeliveryFeeFactor::get(V)` increased (showing the fee mechanism fired) while asserting the attacker `A`'s net token cost across the loop was zero beyond weight, proving the fee mechanism did not economically deter the attack. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** polkadot/runtime/parachains/src/dmp.rs (L269-290)
```rust
	pub fn can_queue_downward_message(
		config: &HostConfiguration<BlockNumberFor<T>>,
		para: &ParaId,
		msg: &DownwardMessage,
	) -> Result<(), QueueDownwardMessageError> {
		let serialized_len = msg.len() as u32;
		if serialized_len > config.max_downward_message_size {
			return Err(QueueDownwardMessageError::ExceedsMaxMessageSize);
		}

		// Hard limit on Queue size
		if Self::dmq_length(*para) > Self::dmq_max_length(config.max_downward_message_size) {
			return Err(QueueDownwardMessageError::ExceedsMaxMessageSize);
		}

		// If the head exists, we assume the parachain is legit and exists.
		if !paras::Heads::<T>::contains_key(para) {
			return Err(QueueDownwardMessageError::Unroutable);
		}

		Ok(())
	}
```

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

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1443-1526)
```rust
	pub fn init_open_channel(
		origin: ParaId,
		recipient: ParaId,
		proposed_max_capacity: u32,
		proposed_max_message_size: u32,
	) -> DispatchResult {
		ensure!(origin != recipient, Error::<T>::OpenHrmpChannelToSelf);
		ensure!(
			paras::Pallet::<T>::is_valid_para(recipient),
			Error::<T>::OpenHrmpChannelInvalidRecipient,
		);

		let config = configuration::ActiveConfig::<T>::get();
		ensure!(proposed_max_capacity > 0, Error::<T>::OpenHrmpChannelZeroCapacity);
		ensure!(
			proposed_max_capacity <= config.hrmp_channel_max_capacity,
			Error::<T>::OpenHrmpChannelCapacityExceedsLimit,
		);
		ensure!(proposed_max_message_size > 0, Error::<T>::OpenHrmpChannelZeroMessageSize);
		ensure!(
			proposed_max_message_size <= config.hrmp_channel_max_message_size,
			Error::<T>::OpenHrmpChannelMessageSizeExceedsLimit,
		);

		let channel_id = HrmpChannelId { sender: origin, recipient };
		ensure!(
			HrmpOpenChannelRequests::<T>::get(&channel_id).is_none(),
			Error::<T>::OpenHrmpChannelAlreadyRequested,
		);
		ensure!(
			HrmpChannels::<T>::get(&channel_id).is_none(),
			Error::<T>::OpenHrmpChannelAlreadyExists,
		);

		let egress_cnt = HrmpEgressChannelsIndex::<T>::decode_len(&origin).unwrap_or(0) as u32;
		let open_req_cnt = HrmpOpenChannelRequestCount::<T>::get(&origin);
		let channel_num_limit = config.hrmp_max_parachain_outbound_channels;
		ensure!(
			egress_cnt + open_req_cnt < channel_num_limit,
			Error::<T>::OpenHrmpChannelLimitExceeded,
		);

		// Do not require deposits for channels with or amongst the system.
		let is_system = origin.is_system() || recipient.is_system();
		let deposit = if is_system { 0 } else { config.hrmp_sender_deposit };
		if !deposit.is_zero() {
			T::Currency::reserve(
				&origin.into_account_truncating(),
				deposit.unique_saturated_into(),
			)?;
		}

		// mutating storage directly now -- shall not bail henceforth.

		HrmpOpenChannelRequestCount::<T>::insert(&origin, open_req_cnt + 1);
		HrmpOpenChannelRequests::<T>::insert(
			&channel_id,
			HrmpOpenChannelRequest {
				confirmed: false,
				_age: 0,
				sender_deposit: deposit,
				max_capacity: proposed_max_capacity,
				max_message_size: proposed_max_message_size,
				max_total_size: config.hrmp_channel_max_total_size,
			},
		);
		HrmpOpenChannelRequestsList::<T>::append(channel_id);

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

		Ok(())
	}
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
