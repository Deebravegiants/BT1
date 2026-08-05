### Title
Single malicious para can cheaply flood a victim para's DMQ via `hrmp_init_open_channel` + `hrmp_cancel_open_request` loop, and `send_to_para` silently drops `ExceedsMaxQueueSize` notifications - (File: `polkadot/runtime/parachains/src/hrmp.rs`)

### Summary
A parachain origin can repeatedly call `hrmp_init_open_channel` followed by `hrmp_cancel_open_request` against a fixed victim recipient, each cycle costing only transaction weight (the deposit is reserved and immediately unreserved), and each cycle enqueues one `HrmpNewChannelOpenRequest` downward message via `send_to_para`/`queue_downward_message`. This can drive the victim's `InboundDownwardQueue` to `Dmp::dmq_max_length`, after which `can_queue_downward_message` returns `ExceedsMaxQueueSize` for any further downward message (HRMP notifications or ordinary XCM DMP traffic) to that para. Separately, `send_to_para`'s error handling only special-cases `ExceedsMaxMessageSize` and silently drops `ExceedsMaxQueueSize`/`Unroutable` errors, so the calling HRMP extrinsic succeeds while the notification is lost without any observable failure.

### Finding Description
`Pallet::<T>::init_open_channel` reserves a deposit, writes `HrmpOpenChannelRequests`, and unconditionally calls `Self::send_to_para(..., queue_downward_message(...))` to notify the recipient [1](#0-0) . The only guard against repeated requests from the same sender is that the specific `(origin, recipient)` channel/request pair must not already exist [2](#0-1) . `cancel_open_request` removes that same request, decrements the sender's open-request counter, and unreserves the deposit [3](#0-2) , which fully clears the state that blocked a repeat call. Nothing enforces a cooldown or a per-recipient rate limit between an `init`→`cancel`→`init` cycle, so a single attacker-controlled parachain can loop this cycle indefinitely against one victim `recipient`, each iteration enqueuing a fresh `HrmpNewChannelOpenRequest` DM.

The queue itself is bounded: `can_queue_downward_message` rejects further enqueues once `dmq_length(para) > dmq_max_length(max_downward_message_size)` with `QueueDownwardMessageError::ExceedsMaxQueueSize` [4](#0-3) , and `queue_downward_message` propagates that same error on `InboundDownwardQueue::push_back` failure [5](#0-4) .

Critically, `hrmp.rs::send_to_para` only pattern-matches `ExceedsMaxMessageSize` when handling the `Result` from `queue_downward_message`; `ExceedsMaxQueueSize` (and `Unroutable`) fall through the `if let` unmatched and are discarded with no log, no event, and no propagated `DispatchError`: [6](#0-5) 
This means once the victim's queue is full, `hrmp_init_open_channel`, `hrmp_accept_open_channel`, and `hrmp_close_channel` calls that target/notify that para continue to succeed at the dispatch level while their DMP notifications vanish silently - a state-desync bug independent of the flooding itself. Any other caller relying on `queue_downward_message` for real HRMP/XCM downward delivery to that para (e.g. `sudo_queue_downward_xcm` or the general XCM router) will correctly observe and propagate `ExceedsMaxQueueSize`, i.e. legitimate downward traffic to the victim is blocked while it's saturated [7](#0-6) .

Recovery is not attacker-controlled: the victim para's own block inclusion drains the queue via `prune_dmq`, invoked when the relay chain processes `processed_downward_messages` from an included candidate [8](#0-7) . So the DoS is not strictly "permanent" - it lasts as long as the attacker's fill rate exceeds the victim's drain rate, which is bounded only by how fast the attacker can dispatch cheap init/cancel cycles versus how much the victim can process per included block.

### Impact Explanation
While the queue is saturated, `Dmp::can_queue_downward_message`/`queue_downward_message` reject all further enqueues for the targeted para with `ExceedsMaxQueueSize`, blocking delivery of legitimate HRMP control notifications (`HrmpNewChannelOpenRequest`/`Accepted`/`Closing`) and any other downward XCM traffic to that para. Independently, the `send_to_para` swallow-bug means HRMP-originated notifications are lost silently even outside of full-saturation edge cases involving `Unroutable`, producing sender/recipient state desync (e.g. a sender believes it requested/closed a channel but the recipient was never informed) with no error surfaced anywhere.

### Likelihood Explanation
Requires the attacker to already control one onboarded parachain (a real, if costly, permissionless capability, not governance-gated). Given that, the `init_open_channel`/`cancel_open_request` loop is cheap (deposit fully returned each cycle, cost is only transaction weight/fees) and has no per-recipient rate limit, so filling `dmq_max_length` entries against a fixed victim is mechanically repeatable, bounded mainly by how many such calls the attacker's para can get included per relay block (UMP/Transact throughput) versus the victim's message-processing throughput.

### Recommendation
- Fix `send_to_para` to handle all `QueueDownwardMessageError` variants explicitly (log/emit an event for `ExceedsMaxQueueSize` and `Unroutable`, not just `ExceedsMaxMessageSize`), so silent notification loss is at minimum observable.
- Consider applying `Dmp`'s existing fee-factor/backpressure mechanism (or an equivalent rate limit/cooldown) to HRMP channel-management notifications themselves, or reject `hrmp_init_open_channel`/`cancel_open_request` cycling above some frequency per `(sender, recipient)` pair, so a single para cannot cheaply and repeatedly re-request/cancel to spam a fixed recipient's DMQ.

### Proof of Concept
Rust unit test in `polkadot/runtime/parachains/src/hrmp/tests.rs` style:
1. Register attacker para `A` and victim para `B`.
2. Compute `max_len = Dmp::dmq_max_length(config.max_downward_message_size)`.
3. Loop `max_len` times: `Hrmp::hrmp_init_open_channel(A_origin, B, cap, size)` (assert `Ok`), then `Hrmp::hrmp_cancel_open_request(A_origin, HrmpChannelId{sender:A, recipient:B})` (assert `Ok`), verifying each iteration appends one entry to `Dmp::dmq_contents_do_not_call_in_consensus(B)`.
4. Assert `Dmp::dmq_length(B) == max_len` (or reaches the cap) after the loop.
5. Call `Hrmp::hrmp_init_open_channel(A_origin, B, cap, size)` one more time and assert it still returns `Ok(())` at the dispatch level (demonstrating the silent swallow) while `Dmp::dmq_length(B)` does **not** increase past the cap (demonstrating the notification was dropped, not queued).
6. Separately call `Dmp::can_queue_downward_message(&config, &B, &some_msg)` directly and assert it returns `Err(QueueDownwardMessageError::ExceedsMaxQueueSize)`, confirming legitimate XCM/DMP delivery to `B` is blocked.

### Citations

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

**File:** polkadot/runtime/parachains/src/dmp.rs (L266-290)
```rust
	/// Determine whether enqueuing a downward message to a specific recipient para would result
	/// in an error. If this returns `Ok(())` the caller can be certain that a call to
	/// `queue_downward_message` with the same parameters will be successful.
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

**File:** polkadot/runtime/parachains/src/dmp.rs (L300-309)
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

**File:** polkadot/runtime/common/src/paras_sudo_wrapper.rs (L160-169)
```rust
			dmp::Pallet::<T>::queue_downward_message(&config, id, xcm.encode()).map_err(|e| match e
			{
				dmp::QueueDownwardMessageError::ExceedsMaxMessageSize => {
					Error::<T>::ExceedsMaxMessageSize.into()
				},
				dmp::QueueDownwardMessageError::ExceedsMaxQueueSize => {
					Error::<T>::ExceedsMaxQueueSize.into()
				},
				dmp::QueueDownwardMessageError::Unroutable => Error::<T>::Unroutable.into(),
			})
```
