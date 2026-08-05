Audit Report

## Title
Unprivileged parachain can spam a victim's downward message queue via repeated `hrmp_init_open_channel`/`hrmp_cancel_open_request` cycles without ever paying the recipient deposit - (File: polkadot/runtime/parachains/src/hrmp.rs)

## Summary
`Pallet::init_open_channel` unconditionally queues a `HrmpNewChannelOpenRequest` downward message (DMP) to the recipient before any recipient-side deposit or confirmation is required, reserving only the sender's own (fully refundable) deposit. `cancel_open_request` fully unreserves that sender deposit and clears the pending-request slot, allowing the same `(origin, recipient)` pair to be reopened immediately, so a malicious parachain origin can loop the two calls to inject unbounded `HrmpNewChannelOpenRequest` messages into the victim's DMQ at only the cost of ordinary transaction fees.

## Finding Description
`Self::init_open_channel` only validates the sender's own outbound channel/request limits (`HrmpEgressChannelsIndex` + `HrmpOpenChannelRequestCount` vs. `hrmp_max_parachain_outbound_channels`) and reserves `hrmp_sender_deposit` from `origin`, then calls `Self::send_to_para` to queue an `HrmpNewChannelOpenRequest` XCM to `recipient` via `dmp::Pallet::queue_downward_message`. [1](#0-0) 
No recipient deposit or confirmation is required at this stage — `hrmp_recipient_deposit` is only reserved in `accept_open_channel`, which the attacker never needs to call. [2](#0-1) 

`cancel_open_request` removes the pending request, decrements `HrmpOpenChannelRequestCount` for the sender, and fully unreserves the sender's deposit, with no cooldown or per-recipient throttle. [3](#0-2) 
Because `HrmpOpenChannelRequestCount` returns to zero after cancellation, the outbound-channel-limit check in `init_open_channel` never blocks a repeated cycle, since the attacker never holds more than one outstanding request at a time.

Each iteration queues exactly one DMP message via `dmp::Pallet::queue_downward_message`, whose only checks are message-size vs. `max_downward_message_size` and a global, sender-agnostic hard cap `dmq_max_length = MAX_POSSIBLE_ALLOCATION / max_downward_message_size`. [4](#0-3) [5](#0-4) 
There is no per-sender quota and no fee deducted from the attacker at insertion time; the `DeliveryFeeFactor`/`increase_fee_factor` mechanism only raises the price of *future* sends to that recipient once occupancy passes a threshold, and does not throttle or charge the party generating the spam at insertion time.

The relevant extrinsic wrappers confirm this is reachable via an ordinary `ensure_parachain` origin (i.e., any registered parachain's XCM/UMP-dispatched call, not privileged governance), and `hrmp_cancel_open_request` is callable by either participant with only a witness-length check, not a cooldown. [6](#0-5) 

The implementer's guide description of the entry points and session-change cleanup confirms there is no per-cycle rate limit and that pending unconfirmed requests are otherwise only cleaned up at session boundaries (for offboarding paras) or when confirmed/enacted — not as a defense against this specific cancel-and-retry loop. [7](#0-6) 

## Impact Explanation
An attacker controlling two ParaIds (reachable via the parachain-origin call path) can repeatedly queue `HrmpNewChannelOpenRequest` DMP messages to a victim parachain, pushing the victim's DMQ length toward the global hard cap `dmq_max_length`, without ever paying the non-refundable `hrmp_recipient_deposit`. Since the cap is shared across all senders to that recipient, filling a large fraction of it degrades or blocks delivery of legitimate downward messages (including from other honest parachains or system messages) to the victim until the queue is drained by the victim's own collators, representing a real backpressure/DoS risk against the affected parachain's inbound DMP/XCM traffic. This is a genuine, in-scope Polkadot SDK runtime logic issue (not node-only, not governance-only, and triggerable by a normal parachain-origin call).

## Likelihood Explanation
The precondition of controlling two ParaIds imposes real cost/friction (acquiring parachain or parathread status), which is a meaningful economic barrier beyond a simple signed account, but is not equivalent to a privileged/governance-only action — many independent teams operate parachains and parathreads that are not otherwise trusted by every other chain, matching the threat model HRMP deposits are meant to address. Given that precondition, the attack loop itself is cheap and repeatable: each cycle costs only the two extrinsics' weight/fees, since the `hrmp_sender_deposit` is refunded every iteration and no other economic friction is enforced by `init_open_channel`/`cancel_open_request`. The main limiting factor is block space for submitting enough extrinsic pairs within available blocks, which is a resource constraint rather than a protocol-level defense, consistent with the report's claim.

## Recommendation
Add a per-(sender, recipient) or per-sender cooldown/rate limit that prevents immediately reopening a request right after cancellation (e.g., a minimum number of blocks/sessions between a cancellation and a new request to the same recipient). Alternatively, charge a small non-refundable fee per `HrmpNewChannelOpenRequest` notification (distinct from the refundable `hrmp_sender_deposit`) so that the cost of generating DMP spam scales with the number of notifications sent rather than being fully recoverable via `cancel_open_request`. Consider also applying delivery-fee-factor-style charges to the sender at insertion time rather than only pricing future unrelated messages to the recipient.

## Proof of Concept
1. Register two ParaIds, `para_attacker` and `para_victim`, both valid parachains (per `paras::Pallet::<T>::is_valid_para`), and fund `para_attacker`'s account with balance sufficient to cover `hrmp_sender_deposit` (fully recycled each cycle) plus transaction fees.
2. Loop N times:
   - Call `Hrmp::hrmp_init_open_channel(para_attacker_origin, para_victim, capacity, msg_size)` — queues one `HrmpNewChannelOpenRequest` DMP to `para_victim` and reserves `hrmp_sender_deposit`.
   - Call `Hrmp::hrmp_cancel_open_request(para_attacker_origin, HrmpChannelId{sender: para_attacker, recipient: para_victim}, witness)` — unreserves the deposit and clears the pending request.
3. Assert after the loop: `Balances::reserved_balance(para_attacker) == 0` (no cumulative deposit cost) and `Dmp::dmq_length(para_victim) == N` (unpaid DMQ entries accumulated).
4. Push N toward `Dmp::dmq_max_length(max_downward_message_size)` and show a subsequent legitimate downward message to `para_victim` fails with `QueueDownwardMessageError::ExceedsMaxQueueSize`, demonstrating the shared-queue DoS described in `dmp::Pallet::can_queue_downward_message`/`queue_downward_message`.

### Citations

**File:** polkadot/runtime/parachains/src/hrmp.rs (L654-670)
```rust
		#[pallet::call_index(6)]
		#[pallet::weight(<T as Config>::WeightInfo::hrmp_cancel_open_request(*open_requests))]
		pub fn hrmp_cancel_open_request(
			origin: OriginFor<T>,
			channel_id: HrmpChannelId,
			open_requests: u32,
		) -> DispatchResult {
			let origin = ensure_parachain(<T as Config>::RuntimeOrigin::from(origin))?;
			ensure!(
				HrmpOpenChannelRequestsList::<T>::decode_len().unwrap_or_default() as u32 <=
					open_requests,
				Error::<T>::WrongWitness
			);
			Self::cancel_open_request(origin, channel_id.clone())?;
			Self::deposit_event(Event::OpenChannelCanceled { by_parachain: origin, channel_id });
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

**File:** polkadot/roadmap/implementers-guide/src/runtime/hrmp.md (L178-226)
```markdown
* `hrmp_init_open_channel(recipient, proposed_max_capacity, proposed_max_message_size)`:
    1. Check that the `origin` is not `recipient`.
    1. Check that `proposed_max_capacity` is less or equal to `config.hrmp_channel_max_capacity` and greater than zero.
    1. Check that `proposed_max_message_size` is less or equal to `config.hrmp_channel_max_message_size` and greater
       than zero.
    1. Check that `recipient` is a valid para.
    1. Check that there is no existing channel for `(origin, recipient)` in `HrmpChannels`.
    1. Check that there is no existing open channel request (`origin`, `recipient`) in `HrmpOpenChannelRequests`.
    1. Check that the sum of the number of already opened HRMP channels by the `origin` (the size of the set found
    `HrmpEgressChannelsIndex` for `origin`) and the number of open requests by the `origin` (the value from
    `HrmpOpenChannelRequestCount` for `origin`) doesn't exceed the limit of channels
    (`config.hrmp_max_parachain_outbound_channels` or `config.hrmp_max_parathread_outbound_channels`) minus 1.
    1. Check that `origin`'s balance is more or equal to `config.hrmp_sender_deposit`
    1. Reserve the deposit for the `origin` according to `config.hrmp_sender_deposit`
    1. Increase `HrmpOpenChannelRequestCount` by 1 for `origin`.
    1. Append `(origin, recipient)` to `HrmpOpenChannelRequestsList`.
    1. Add a new entry to `HrmpOpenChannelRequests` for `(origin, recipient)`
        1. Set `sender_deposit` to `config.hrmp_sender_deposit`
        1. Set `max_capacity` to `proposed_max_capacity`
        1. Set `max_message_size` to `proposed_max_message_size`
        1. Set `max_total_size` to `config.hrmp_channel_max_total_size`
    1. Send a downward message to `recipient` notifying about an inbound HRMP channel request.
        * The DM is sent using `queue_downward_message`.
        * The DM is represented by the `HrmpNewChannelOpenRequest`  XCM message.
            * `sender` is set to `origin`,
            * `max_message_size` is set to `proposed_max_message_size`,
            * `max_capacity` is set to `proposed_max_capacity`.
* `hrmp_accept_open_channel(sender)`:
    1. Check that there is an existing request between (`sender`, `origin`) in `HrmpOpenChannelRequests`
        1. Check that it is not confirmed.
    1. Check that the sum of the number of inbound HRMP channels opened to `origin` (the size of the set found in
    `HrmpIngressChannelsIndex` for `origin`) and the number of accepted open requests by the `origin` (the value from
    `HrmpAcceptedChannelRequestCount` for `origin`) doesn't exceed the limit of channels
    (`config.hrmp_max_parachain_inbound_channels` or `config.hrmp_max_parathread_inbound_channels`) minus 1.
    1. Check that `origin`'s balance is more or equal to `config.hrmp_recipient_deposit`.
    1. Reserve the deposit for the `origin` according to `config.hrmp_recipient_deposit`
    1. For the request in `HrmpOpenChannelRequests` identified by `(sender, P)`, set `confirmed` flag to `true`.
    1. Increase `HrmpAcceptedChannelRequestCount` by 1 for `origin`.
    1. Send a downward message to `sender` notifying that the channel request was accepted.
        * The DM is sent using `queue_downward_message`.
        * The DM is represented by the `HrmpChannelAccepted` XCM message.
            * `recipient` is set to `origin`.
* `hrmp_cancel_open_request(ch)`:
    1. Check that `origin` is either `ch.sender` or `ch.recipient`
    1. Check that the open channel request `ch` exists.
    1. Check that the open channel request for `ch` is not confirmed.
    1. Remove `ch` from `HrmpOpenChannelRequests` and `HrmpOpenChannelRequestsList`
    1. Decrement `HrmpAcceptedChannelRequestCount` for `ch.recipient` by 1.
    1. Unreserve the deposit of `ch.sender`.
```
