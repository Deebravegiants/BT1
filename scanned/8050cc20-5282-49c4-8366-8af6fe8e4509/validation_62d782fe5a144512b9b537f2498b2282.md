### Title
Unprivileged parachain can spam a victim's downward message queue via repeated `hrmp_init_open_channel`/`hrmp_cancel_open_request` cycles without ever paying the recipient deposit - (File: polkadot/runtime/parachains/src/hrmp.rs)

### Summary
`Pallet::init_open_channel` unconditionally sends a `HrmpNewChannelOpenRequest` DMP message to the target recipient before any recipient-side deposit or confirmation is required, and `cancel_open_request` fully refunds the sender's deposit and clears the pending-request slot so the same `(origin, recipient)` pair can be reopened immediately. This lets a parachain-origin attacker loop `hrmp_init_open_channel` → `hrmp_cancel_open_request` many times pre-session, injecting one `HrmpNewChannelOpenRequest` message per iteration into the victim's downward message queue (DMQ) at essentially the cost of ordinary transaction fees, since the sender deposit is returned each cycle and the recipient deposit is never taken.

### Finding Description
`Self::init_open_channel` [1](#0-0)  only checks the sender's own outbound channel/request limits (`HrmpEgressChannelsIndex` + `HrmpOpenChannelRequestCount` against `hrmp_max_parachain_outbound_channels`) and reserves only `hrmp_sender_deposit` from `origin`, then unconditionally calls `Self::send_to_para(... HrmpNewChannelOpenRequest ...)`, which queues a downward message to `recipient` via `dmp::Pallet::queue_downward_message`. No deposit or confirmation from the recipient is required at this stage — `hrmp_recipient_deposit` is only reserved later in `accept_open_channel` [2](#0-1) , which the attacker never calls.

`cancel_open_request` [3](#0-2)  removes the pending request, decrements `HrmpOpenChannelRequestCount` for the sender, and fully `unreserve`s the sender's deposit — with no cooldown, no per-recipient rate limit, and no penalty. Because `HrmpOpenChannelRequestCount` is decremented back to zero, the "outbound channel limit" check in `init_open_channel` never blocks a repeat because the attacker never has more than one outstanding request at a time.

Each iteration therefore queues exactly one DMP message into the victim's queue via `Dmp::queue_downward_message` [4](#0-3) . The only checks performed by `can_queue_downward_message` [5](#0-4)  are (a) message size vs. `max_downward_message_size`, and (b) a **global, sender-agnostic** hard cap `dmq_max_length = MAX_POSSIBLE_ALLOCATION / max_downward_message_size` [6](#0-5) . There is no per-sender or per-request-type quota, and no fee is deducted from the attacker at insertion time. The `DeliveryFeeFactor`/`increase_fee_factor` mechanism [7](#0-6)  only raises the *price of future sends* to that recipient (read via the `FeeTracker` trait, consumed elsewhere e.g. by XCM delivery-fee routers) — it does not charge or throttle the attacker who is generating the spam, and it does not block insertion once the hard cap is not yet reached.

Because the hard cap is shared across all senders to a given recipient, an attacker who fills a large fraction of it degrades DMP delivery for every legitimate sender to that parachain, not just itself — matching the "queue processing/backpressure halt" impact described. The `hrmp_sender_deposit`, which is the only economic friction in the loop, is returned every cycle, so it imposes no cumulative cost; the attacker only pays ordinary weighted transaction fees for `hrmp_init_open_channel` and `hrmp_cancel_open_request`, whose weight does not scale with the recipient's queue occupancy.

### Impact Explanation
An unprivileged parachain origin (any two ParaIds it controls) can drive the victim's DMQ length toward the global hard cap `MAX_POSSIBLE_ALLOCATION / max_downward_message_size` purely with `HrmpNewChannelOpenRequest` notification spam, without ever reserving `hrmp_recipient_deposit`. Once near/at the cap, `queue_downward_message` starts rejecting *all* further downward messages to the victim (from any sender, including governance/system messages), delaying legitimate DMP delivery and effectively causing backpressure/halt for that parachain's inbound XCM traffic until the queue is drained by the victim's own collators or the attacker's requests expire at the next session boundary.

### Likelihood Explanation
Preconditions are modest: the attacker needs two registered ParaIds it controls (parachains or parathreads reachable via `ensure_parachain` origin) and enough balance to cover the transient `hrmp_sender_deposit` (fully refunded each cycle) plus ordinary transaction fees for the two calls per iteration. The loop is fully repeatable within a single session (many blocks), and each iteration is a straightforward pair of extrinsics with no cooldown, replay protection, or per-recipient throttling to prevent it. The main limiting factor is block space/weight for submitting enough extrinsics before the session boundary, which is a resource constraint rather than a protocol-level defense.

### Recommendation
Introduce a per-(sender, recipient) or per-sender rate limit / cooldown on repeated `init_open_channel` → `cancel_open_request` cycles (e.g., don't allow a new request to the same recipient immediately after a cancellation within the same session), and/or require a non-refundable minimum fee (distinct from the refundable deposit) for sending `HrmpNewChannelOpenRequest` notifications, so that the cost of generating DMP messages scales with the number of notifications sent rather than being fully recoverable via cancellation. Alternatively, apply the existing `DeliveryFeeFactor` mechanism (or a dedicated one) to charge the *sender* of the HRMP notification at insertion time rather than only pricing future unrelated messages to that recipient.

### Proof of Concept
Rust integration test (in `polkadot/runtime/parachains/src/hrmp/tests.rs` style) idea:
1. Register `para_attacker_a`, `para_attacker_b` (unused, just to be a valid recipient placeholder) and `para_victim` with sufficient balance for `hrmp_sender_deposit`.
2. Loop N times (e.g. N = 500):
   - `Hrmp::init_open_channel(para_attacker_a, para_victim, capacity, msg_size)`
   - `Hrmp::cancel_open_request(para_attacker_a, HrmpChannelId{sender: para_attacker_a, recipient: para_victim})`
3. After the loop, assert:
   - `Balances::reserved_balance(para_attacker_a) == 0` (deposit was never permanently locked/spent),
   - `Dmp::dmq_length(para_victim) == N` (one `HrmpNewChannelOpenRequest` queued per iteration, unpaid by recipient deposit),
   - Optionally push N toward `Dmp::dmq_max_length(max_downward_message_size)` and assert that a legitimate downward message to `para_victim` (e.g. via `sudo_queue_downward_xcm` or another para's HRMP notification) starts failing with `QueueDownwardMessageError::ExceedsMaxQueueSize` — demonstrating the shared-queue DoS.

### Citations

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

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1532-1557)
```rust
	pub fn accept_open_channel(origin: ParaId, sender: ParaId) -> DispatchResult {
		let channel_id = HrmpChannelId { sender, recipient: origin };
		let mut channel_req = HrmpOpenChannelRequests::<T>::get(&channel_id)
			.ok_or(Error::<T>::AcceptHrmpChannelDoesntExist)?;
		ensure!(!channel_req.confirmed, Error::<T>::AcceptHrmpChannelAlreadyConfirmed);

		// check if by accepting this open channel request, this parachain would exceed the
		// number of inbound channels.
		let config = configuration::ActiveConfig::<T>::get();
		let channel_num_limit = config.hrmp_max_parachain_inbound_channels;
		let ingress_cnt = HrmpIngressChannelsIndex::<T>::decode_len(&origin).unwrap_or(0) as u32;
		let accepted_cnt = HrmpAcceptedChannelRequestCount::<T>::get(&origin);
		ensure!(
			ingress_cnt + accepted_cnt < channel_num_limit,
			Error::<T>::AcceptHrmpChannelLimitExceeded,
		);

		// Do not require deposits for channels with or amongst the system.
		let is_system = origin.is_system() || sender.is_system();
		let deposit = if is_system { 0 } else { config.hrmp_recipient_deposit };
		if !deposit.is_zero() {
			T::Currency::reserve(
				&origin.into_account_truncating(),
				deposit.unique_saturated_into(),
			)?;
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

**File:** polkadot/runtime/parachains/src/dmp.rs (L392-394)
```rust
	fn dmq_max_length(max_downward_message_size: u32) -> u32 {
		MAX_POSSIBLE_ALLOCATION.checked_div(max_downward_message_size).unwrap_or(0)
	}
```
