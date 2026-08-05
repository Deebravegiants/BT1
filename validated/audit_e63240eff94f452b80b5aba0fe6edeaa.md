Audit Report

## Title
Unbounded, cost-free HRMP open/cancel-request loop allows a parachain to spam a victim para's downward message queue - ([File: polkadot/runtime/parachains/src/hrmp.rs], [File: polkadot/runtime/parachains/src/dmp.rs])

## Summary
`Pallet::init_open_channel`, `accept_open_channel`, and `close_channel` in `hrmp.rs` unconditionally push an `HrmpNewChannelOpenRequest`/`HrmpChannelAccepted`/`HrmpChannelClosing` notification into the *recipient's* downward message queue via `Self::send_to_para` -> `dmp::Pallet::<T>::queue_downward_message`, without requiring recipient consent. Because `cancel_open_request` fully refunds the sender's deposit and deletes the in-flight request (resetting `HrmpOpenChannelRequestCount`), an onboarded malicious para can repeat `hrmp_init_open_channel(victim, …)` followed immediately by `hrmp_cancel_open_request` to inject an unbounded stream of notifications into an arbitrary victim's DMQ at only the cost of extrinsic weight/UMP dispatch fees.

## Finding Description
`init_open_channel` (`polkadot/runtime/parachains/src/hrmp.rs:1443-1526`) validates only the caller's own per-para request-count limits (`egress_cnt + open_req_cnt < channel_num_limit`) and the recipient's validity, then unconditionally calls `Self::send_to_para`, which calls `dmp::Pallet::<T>::queue_downward_message(&config, recipient, ...)` [1](#0-0) . `cancel_open_request` (`hrmp.rs:1578-1606`) removes the `HrmpOpenChannelRequests`/`HrmpOpenChannelRequestsList` entries, decrements `HrmpOpenChannelRequestCount`, and fully unreserves the sender's deposit [2](#0-1) , which resets the attacker's quota so the init->cancel cycle can be repeated indefinitely.

`can_queue_downward_message`/`queue_downward_message` (`dmp.rs:269-326`) reject a message only when `dmq_length(para) > dmq_max_length(...)`, a finite but large hard cap (`MAX_POSSIBLE_ALLOCATION / max_downward_message_size`) [3](#0-2) [4](#0-3) . There is no per-sender rate limiting for HRMP notification injection independent of that global hard cap.

One correction to the original claim: `queue_downward_message` does apply the `DeliveryFeeFactor` congestion-pricing mechanism universally to *every* enqueued message once `q_len` exceeds `dmq_max_length / THRESHOLD_FACTOR`, via `Self::increase_fee_factor(para, serialized_len)` — this is not bypassed for HRMP notifications [5](#0-4) . However, this fee-factor increase raises the *cost of sending future XCM messages to the victim through the Sender/Router interface* for third parties — it does not charge the attacker anything extra for its own `hrmp_init_open_channel`/`cancel_open_request` calls, so it does not deter the attack itself, though it does mean the claim's statement that the fee mechanism is "entirely bypassed" is not fully accurate — it interacts with, but does not stop, the described DMQ-filling behavior.

## Impact Explanation
If sustained at a sufficient rate, this allows an onboarded parachain to fill a victim para's `DownwardMessageQueuePages` with junk system notifications, causing `can_queue_downward_message` to reject legitimate downward messages (`ExceedsMaxMessageSize`) targeting the victim once `dmq_length(victim)` exceeds the hard cap. This is a temporary, recoverable congestion/DoS condition against a single victim para's DMP channel rather than a loss-of-funds or consensus-safety issue, and it self-heals once the attacker stops or the victim's collators drain the backlog via `prune_dmq`.

## Likelihood Explanation
The precondition is significant: the attacker must control an onboarded parachain capable of dispatching parachain-origin extrinsics (via UMP), which is itself a privileged and resource-intensive position (requiring a parachain slot/coretime) rather than something any unprivileged end user can trivially obtain. Additionally, the actual achievable injection rate is bounded by the relay chain's per-block UMP dispatch weight/message-count limits, and the hard cap `dmq_max_length = MAX_POSSIBLE_ALLOCATION / max_downward_message_size` is large, meaning saturating a victim's queue would require a large, sustained volume of iterations across many blocks — the report itself acknowledges this ("the absolute size of `dmq_max_length` means saturating the queue requires many iterations across many blocks"). The deposit-refund loop does make each individual iteration net-zero-cost in reserved balance, which is a genuine minor economic design gap, but the overall attack's practical severity is limited by these throughput and precondition constraints.

## Recommendation
Rate-limit or fee-meter HRMP channel-management notification injection independently of the refundable deposit — e.g., charge a small non-refundable fee per open/cancel cycle, or track open+cancel churn per `(origin, recipient)` pair and cap it so the counters cannot be reset by cancellation. Consider tying the existing `DeliveryFeeFactor` mechanism's cost more directly to the message-injecting caller rather than only to future senders, so repeated injection into a congested queue becomes progressively expensive for the originating para itself.

## Proof of Concept
As described in the submission: register an attacker para `A` and victim para `V`; loop `hrmp_init_open_channel(A, V, …)` followed by `hrmp_cancel_open_request` to increment `Dmp::dmq_length(V)` on each iteration while confirming the attacker's reserved balance returns to baseline after each cancel; continue until `dmq_length(V) > dmq_max_length(...)` and confirm a subsequent legitimate `queue_downward_message` call to `V` fails with `ExceedsMaxMessageSize`; then call `Dmp::prune_dmq(V, N)` to show recovery. This test would need to be run with realistic relay-chain block/weight constraints on UMP dispatch to determine actual feasibility, which was not independently verified here.

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1477-1523)
```rust
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
