Audit Report

## Title
Unthrottled DMP queue flooding via free HRMP notifications (`hrmp_init_open_channel`/`hrmp_cancel_open_request` cycling) - ([File: polkadot/runtime/parachains/src/dmp.rs])

## Summary
`Pallet::queue_downward_message`/`can_queue_downward_message` in `dmp.rs` enforce only a hard queue-size cap with no per-sender or per-message-count throttle, and the `DeliveryFeeFactor` anti-spam mechanism is never priced against HRMP channel-management notifications. Because `hrmp.rs::send_to_para` calls `dmp::Pallet::<T>::queue_downward_message` directly rather than routing through `ChildParachainRouter`/`ExponentialPrice::price_for_delivery`, a parachain can repeatedly cycle `hrmp_init_open_channel`/`hrmp_cancel_open_request` against a victim para to push free notifications into its downward queue up to the hard cap, with all deposits refunded on cancellation.

## Finding Description
`can_queue_downward_message` only checks message size and the hard cap `dmq_length(para) > dmq_max_length(...)` with no per-sender accounting [1](#0-0) . `queue_downward_message` increases `DeliveryFeeFactor` once a threshold is crossed [2](#0-1) , but that fee factor is only consumed as a priced input inside `ExponentialPrice::price_for_delivery`, invoked by `ChildParachainRouter::validate` for XCM-`send`-initiated downward messages [3](#0-2) . HRMP protocol notifications instead call `dmp::Pallet::<T>::queue_downward_message` directly from `hrmp.rs::send_to_para`, with no price computed or charged against the sender [4](#0-3) . Consequently the rising fee factor never makes this specific injection path more costly for the attacker — it only raises delivery cost for unrelated third parties later trying to `send` XCM to the same victim.

The exploit cycle is real and repeatable: `init_open_channel` reserves a deposit, records the request, and unconditionally enqueues an `HrmpNewChannelOpenRequest` notification to the recipient [5](#0-4) , and `cancel_open_request` fully removes the request/count entries and unreserves the deposit [6](#0-5) , allowing the cycle to repeat against the same victim indefinitely since no persistent per-target state accumulates. The `hrmp_max_parachain_outbound_channels` limit only bounds concurrently *open* requests plus existing channels, and since `HrmpOpenChannelRequestCount` is decremented on cancellation, it does not bound the cumulative number of cycles over time.

The DMP module's own documentation confirms the fee factor is intended as the queue's anti-spam mechanism, with the hard cap as a defensive last resort against OOM [7](#0-6) , but that fee mechanism structurally cannot apply to this HRMP-driven injection path.

## Impact Explanation
Filling a victim para's downward queue to the hard cap causes subsequent downward messages — including legitimate governance dispatches and XCM sends — to be rejected via `ExceedsMaxMessageSize`/`ExceedsMaxQueueSize`, since both legitimate and attacker-originated messages pass through the same `queue_downward_message` gate. This is a genuine, if narrow, denial-of-service against a specific victim para's downward message channel, distinguishable from ordinary fee-throttled spam because this path is exempt from the economic deterrent that governs all other downward traffic.

## Likelihood Explanation
The realistic constraint significantly reduces practical severity relative to the report's framing: `hrmp_init_open_channel`/`hrmp_cancel_open_request` require `ensure_parachain` origin, meaning the attacker must already control an onboarded parachain and dispatch these calls through that parachain's UMP/inclusion process — not a freely-callable signed extrinsic from any account. Each parachain can typically inject only a limited number of such dispatches per relay-chain block (bounded by per-candidate UMP limits and block weight), making the "fill queue to hard cap" attack slow (likely requiring many blocks/hours depending on `max_downward_message_size` and hard-cap sizing) rather than an instant DoS, though it remains sustainable and repeatable at near-zero net monetary cost (deposits refunded) beyond the underlying cost of operating a parachain and the relay-chain weight it consumes.

## Recommendation
Apply delivery-fee/queue-pressure throttling to HRMP-triggered downward notifications in `hrmp.rs::send_to_para` (e.g., charge the sending para's fee factor or a fixed cost per notification), or impose a cooldown/quota on `hrmp_init_open_channel`/`hrmp_cancel_open_request` cycles per `(sender, recipient)` pair so that cost-free notification traffic cannot be regenerated without bound.

## Proof of Concept
1. Register attacker para `A` and victim para `V` in a `polkadot/runtime/parachains/src/hrmp/tests.rs`-style test.
2. Loop: call `Hrmp::init_open_channel(A, V, cap, size)` then `Hrmp::cancel_open_request(A, HrmpChannelId{A,V})`.
3. Observe `Dmp::dmq_length(V)` growing by one message per iteration while `A`'s reserved deposit returns to its pre-call balance after each cancel, and confirm `Dmp::get_fee_factor(V)` rising does not gate or fail subsequent `init_open_channel` calls from `A`.
4. Continue until `dmq_length(V) == dmq_max_length(max_downward_message_size)`; verify a subsequent `ChildParachainRouter`/`pallet_xcm::send` targeting `V` fails with `SendError::ExceedsMaxMessageSize`, confirming legitimate traffic is blocked.

### Citations

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

**File:** polkadot/runtime/common/src/xcm_sender.rs (L98-131)
```rust
pub struct ChildParachainRouter<T, W, P>(PhantomData<(T, W, P)>);

impl<T: configuration::Config + dmp::Config, W: xcm::WrapVersion, P> SendXcm
	for ChildParachainRouter<T, W, P>
where
	P: PriceForMessageDelivery<Id = ParaId>,
{
	type Ticket = (HostConfiguration<BlockNumberFor<T>>, ParaId, Vec<u8>);

	fn validate(
		dest: &mut Option<Location>,
		msg: &mut Option<Xcm<()>>,
	) -> SendResult<(HostConfiguration<BlockNumberFor<T>>, ParaId, Vec<u8>)> {
		let d = dest.take().ok_or(MissingArgument)?;
		let id = if let (0, [Parachain(id)]) = d.unpack() {
			*id
		} else {
			*dest = Some(d);
			return Err(NotApplicable);
		};

		// Downward message passing.
		let xcm = msg.take().ok_or(MissingArgument)?;
		let config = configuration::ActiveConfig::<T>::get();
		let para = id.into();
		let price = P::price_for_delivery(para, &xcm);
		let versioned_xcm = W::wrap_version(&d, xcm).map_err(|()| DestinationUnsupported)?;
		versioned_xcm.check_is_decodable().map_err(|()| ExceedsMaxMessageSize)?;
		let blob = versioned_xcm.encode();
		dmp::Pallet::<T>::can_queue_downward_message(&config, &para, &blob)
			.map_err(Into::<SendError>::into)?;

		Ok(((config, para, blob), price))
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
