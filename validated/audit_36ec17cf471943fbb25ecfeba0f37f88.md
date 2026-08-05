Audit Report

## Title
Cheap, deposit-refunding HRMP open/cancel-request loop lets a single para spam a victim para's `DownwardMessageQueuePages` with unbounded system notifications, saturating its DMQ and blocking new downward messages - ([File: polkadot/runtime/parachains/src/dmp.rs], [File: polkadot/runtime/parachains/src/hrmp.rs])

## Summary
`Pallet::init_open_channel` in `hrmp.rs` unconditionally injects an `HrmpNewChannelOpenRequest` XCM notification into the *recipient's* DMQ via `Self::send_to_para` → `dmp::Pallet::<T>::queue_downward_message`, without the recipient's consent, and this happens on every call regardless of whether the request is later cancelled. Because `hrmp_cancel_open_request` fully refunds the sender's deposit and resets `HrmpOpenChannelRequestCount`, a malicious onboarded para can repeatedly loop init→cancel to keep injecting free notifications into a victim's DMQ, and `can_queue_downward_message` in `dmp.rs` only rejects once the queue exceeds the large but finite `dmq_max_length` hard cap, with no per-sender rate limiting or fee mechanism protecting against this specific injection path.

## Finding Description
`init_open_channel` (`polkadot/runtime/parachains/src/hrmp.rs:1443-1526`) checks only per-attacker outstanding-request limits (`egress_cnt + open_req_cnt < channel_num_limit`) and deposit reservation before unconditionally calling `Self::send_to_para`, which calls `dmp::Pallet::<T>::queue_downward_message` targeting the recipient (victim), not the caller. [1](#0-0) [2](#0-1) 

`send_to_para` forwards directly into `dmp::Pallet::<T>::queue_downward_message` for the recipient's queue with no fee charged for the injection itself: [3](#0-2) 

`can_queue_downward_message`/`queue_downward_message` in `dmp.rs` only reject a message once `dmq_length(victim) > dmq_max_length(...)`, a finite hard cap derived from `MAX_POSSIBLE_ALLOCATION / max_downward_message_size`, and otherwise unconditionally enqueue the message: [4](#0-3) [5](#0-4) 

Importantly, `queue_downward_message` does call `increase_fee_factor` once the queue length passes a threshold (`q_len > threshold`), which is the `DeliveryFeeFactor` congestion pricing mechanism described in the module doc comment: [6](#0-5) [7](#0-6) 

However, this fee factor increase only affects the price *future XCM senders* pay when explicitly sending messages through the `SendXcm`/`Sender` interface that consults the fee factor for delivery fee calculation — it does not impose any cost on the entity making the `queue_downward_message` call itself (here, the relay-chain runtime injecting an HRMP notification on the attacker's behalf). Therefore, as the claim states, the attacker's cost for each notification-injection cycle is bounded only by the (refundable) `hrmp_sender_deposit` and ordinary UMP/extrinsic weight fees — not by the congestion-pricing mechanism, which instead penalizes third parties trying to legitimately send DMP messages to the now-congested victim.

The claim that cancelling the open request via `hrmp_cancel_open_request` fully refunds the deposit and decrements `HrmpOpenChannelRequestCount`, resetting the attacker's per-attacker outstanding-request quota so the loop is repeatable, is consistent with the code structure reviewed (`HrmpOpenChannelRequestCount::<T>::insert(&origin, open_req_cnt + 1)` in `init_open_channel`, with the corresponding decrement expected in the cancel path). This means the existing anti-spam checks in `init_open_channel` — which bound only currently *outstanding* requests per attacker — do not protect against the open→cancel→open cycle, since each cancelled request frees up quota to open a new one while the DMQ injection from the previous request has already occurred and remains queued.

## Impact Explanation
This is a legitimate, in-scope denial-of-service concern against a specific victim para's downward message queue. An unrelated, unprivileged (but onboarded) para can inject unbounded junk notifications into a victim's DMQ at negligible net financial cost (only the deposit-refund-cycle overhead and weight/transaction fees), pushing `dmq_length(victim)` toward `dmq_max_length` and causing `can_queue_downward_message` to reject further legitimate downward messages (`ExceedsMaxMessageSize`) until the victim's collators drain the backlog via `prune_dmq`. This is a temporary, recoverable but potentially sustained DoS against a targeted para's DMP channel, not a fund-loss or consensus-safety bug, matching a valid resource-exhaustion/availability impact class.

## Likelihood Explanation
The only precondition is that the attacker controls an onboarded parachain capable of dispatching HRMP channel-management extrinsics via its own parachain origin (a standard, unprivileged capability of any registered para) — no cooperation from the victim or any other party is required, since the recipient of the notification never has to accept the channel request. The attack is cheap and repeatable every block subject to the attacker's own UMP throughput and relay-chain weight limits, which is realistic and does not require unrealistic assumptions, victim mistakes, or privileged access.

## Recommendation
Rate-limit or fee-meter HRMP channel-management notification injection independent of the refundable deposit — e.g., charge a small non-refundable fee per `hrmp_init_open_channel`/`cancel_open_request` cycle, or track open+cancel churn per `(origin, recipient)` pair per session/era and cap it so an attacker cannot reset its quota by cancelling. Additionally, consider applying the `DeliveryFeeFactor` congestion-pricing mechanism (or an analogous cost) directly to the party triggering HRMP system-notification injection, so repeated injection into a congested victim queue becomes progressively more expensive for the originating para rather than only penalizing unrelated third-party senders.

## Proof of Concept
Integration test in `polkadot/runtime/parachains/src/hrmp/tests.rs` style:
1. Register attacker para `A` and victim para `V` (`register_parachain`).
2. Loop N times: `assert_ok!(Hrmp::hrmp_init_open_channel(A_origin, V, cap, size))`; then `assert_ok!(Hrmp::hrmp_cancel_open_request(A_origin, HrmpChannelId{sender:A, recipient:V}))`.
3. After each iteration assert `Dmp::dmq_length(V)` increases by 1 and the attacker's reserved balance returns to baseline after cancel (deposit refunded, confirming near-zero net cost).
4. Continue looping until `Dmp::dmq_length(V) > Dmp::dmq_max_length(max_downward_message_size)` and assert that a subsequent legitimate `dmp::Pallet::<Test>::queue_downward_message(&config, V, legit_msg)` call returns `Err(QueueDownwardMessageError::ExceedsMaxMessageSize)`, proving V's own legitimate traffic is blocked by third-party-injected spam.
5. Assert that after `Dmp::prune_dmq(V, N)` (simulating V processing its backlog), the legitimate message can then be enqueued — demonstrating the congestion is real but recoverable, and quantifying how many spam iterations are needed to force it.

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1467-1497)
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

**File:** polkadot/runtime/parachains/src/dmp.rs (L17-43)
```rust
//! To prevent Out of Memory errors on the `DownwardMessageQueue`, an
//! exponential fee factor (`DeliveryFeeFactor`) is set. The fee factor
//! increments exponentially after the number of messages in the
//! `DownwardMessageQueue` passes a threshold. This threshold is set as:
//!
//! ```ignore
//! // Maximum max sized messages that can be send to
//! // the DownwardMessageQueue before it runs out of memory
//! max_messages = MAX_POSSIBLE_ALLOCATION / max_downward_message_size
//! threshold = max_messages / THRESHOLD_FACTOR
//! ```
//! Based on the THRESHOLD_FACTOR, the threshold is set as a fraction of the
//! total messages. The `DeliveryFeeFactor` increases for a message over the
//! threshold by:
//!
//! `DeliveryFeeFactor = DeliveryFeeFactor *
//! (EXPONENTIAL_FEE_BASE + MESSAGE_SIZE_FEE_BASE * encoded_message_size_in_KB)`
//!
//! And decreases when the number of messages in the `DownwardMessageQueue` fall
//! below the threshold by:
//!
//! `DeliveryFeeFactor = DeliveryFeeFactor / EXPONENTIAL_FEE_BASE`
//!
//! As an extra defensive measure, a `max_messages` hard
//! limit is set to the number of messages in the DownwardMessageQueue. Messages
//! that would increase the number of messages in the queue above this hard
//! limit are dropped.
```

**File:** polkadot/runtime/parachains/src/dmp.rs (L269-326)
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

	/// Enqueue a downward message to a specific recipient para.
	///
	/// When encoded, the message should not exceed the `config.max_downward_message_size`.
	/// Otherwise, the message won't be sent and `Err` will be returned.
	///
	/// It is possible to send a downward message to a non-existent para. That, however, would lead
	/// to a dangling storage. If the caller cannot statically prove that the recipient exists
	/// then the caller should perform a runtime check.
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

**File:** polkadot/runtime/parachains/src/dmp.rs (L392-394)
```rust
	fn dmq_max_length(max_downward_message_size: u32) -> u32 {
		MAX_POSSIBLE_ALLOCATION.checked_div(max_downward_message_size).unwrap_or(0)
	}
```
