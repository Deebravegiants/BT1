### Title
Unbounded, fee-exempt HRMP-notification flooding of `DownwardMessageQueue` bypasses `DeliveryFeeFactor` backpressure - ([File: polkadot/runtime/parachains/src/dmp.rs])

### Summary
`Pallet::<T>::queue_downward_message` enforces a hard queue-length cap (`dmq_max_length`) and raises `DeliveryFeeFactor` once a threshold is crossed, but this fee is only ever charged to callers of the *priced* XCM send path (`ExponentialPrice::price_for_delivery` in `xcm_sender.rs`). The HRMP pallet's channel-management notifications (`hrmp_init_open_channel`, `hrmp_accept_open_channel`, `hrmp_close_channel`) call `dmp::Pallet::<T>::queue_downward_message` directly through `Hrmp::send_to_para`, without paying any fee tied to `DeliveryFeeFactor`. An attacker controlling a single parachain can therefore repeatedly enqueue downward messages to a victim para at a fixed, non-escalating extrinsic-weight cost, saturating the victim's queue up to `dmq_max_length` while the escalating fee never touches the attacker.

### Finding Description
`Pallet::<T>::queue_downward_message` (dmp.rs lines 300-326) enqueues the message and separately calls `Self::increase_fee_factor` only once `q_len > threshold`. This fee factor is consumed exclusively by `FeeTracker::get_fee_factor`/`ExponentialPrice::price_for_delivery` [1](#0-0)  which is the pricing mechanism for the *paid* `ChildParachainRouter` XCM-send path — it is never checked or debited inside `queue_downward_message` itself [2](#0-1) .

The HRMP pallet's `send_to_para` helper calls `dmp::Pallet::<T>::queue_downward_message` unconditionally for `HrmpNewChannelOpenRequest`, `HrmpChannelAccepted`, and `HrmpChannelClosing` notifications, with no fee payment or throttling tied to `DeliveryFeeFactor` [3](#0-2) . `hrmp_init_open_channel` (`init_open_channel`) sends one such DM to the `recipient` every time it succeeds [4](#0-3) , and success only requires that no existing `HrmpOpenChannelRequests` entry exists for the `(origin, recipient)` pair and that the origin has not exceeded `hrmp_max_parachain_outbound_channels` concurrent requests [5](#0-4) . Crucially, `hrmp_cancel_open_request` removes the pending request entirely (refunding the deposit and freeing the origin/recipient slot), so a single attacker-controlled para can cycle `hrmp_init_open_channel` → `hrmp_cancel_open_request` → `hrmp_init_open_channel` against the *same* victim recipient indefinitely, producing one queued DM per cycle at a fixed weight-based fee (deposit fully refunded, no dependency on `DeliveryFeeFactor`).

Once the victim's queue approaches `dmq_max_length`, `can_queue_downward_message` starts rejecting further enqueue attempts (dmp.rs lines 279-282), but the caller (`hrmp::send_to_para`) swallows that failure with only a `debug_assert!(false)` (a no-op in release builds) [6](#0-5) , so the attacker's own state-machine transitions (`HrmpOpenChannelRequests`/`HrmpOpenChannelRequestsList` mutations) continue to succeed even while the queue is pinned at capacity. The victim's queue drains only as fast as its own collator processes messages (`prune_dmq`), and the attacker can refill it at the same low fixed cost, keeping the queue saturated and `DeliveryFeeFactor` for that para pinned at an extreme value as demonstrated by `verify_fee_factor_reaches_high_value`, which shows the aggregate fee factor exceeding `100_000_000` well before `dmq_max_length` is reached [7](#0-6) .

### Impact Explanation
Legitimate senders using the priced `ChildParachainRouter`/`ExponentialPrice` path to reach the victim para are priced out (fee scales with the now-huge `DeliveryFeeFactor`), while once the queue is at `dmq_max_length`, `can_queue_downward_message` rejects *all* new downward messages regardless of source — starving the victim para of downward message delivery. The attacker's own notification-triggering cost stays flat (bounded extrinsic weight fee, fully refundable deposit) and does not scale with the fee factor, breaking the intended proportional-backpressure invariant for this specific message-origination path.

### Likelihood Explanation
Precondition is only that the attacker control one parachain capable of dispatching `Origin::Parachain` calls to `hrmp_init_open_channel`/`hrmp_cancel_open_request` — no privileged access is needed. The cycle is repeatable indefinitely and limited only by the attacker's block-weight/UMP throughput, not by the victim's fee-factor growth, since HRMP notifications never consult `DeliveryFeeFactor`.

### Recommendation
Either (a) apply the same `DeliveryFeeFactor`-based cost/throttling to HRMP-notification-triggered `queue_downward_message` calls (e.g., require the initiating para to pay a fee scaled by the target's current fee factor, or reject/limit notification sends once a para's queue is above threshold), or (b) rate-limit `hrmp_cancel_open_request` re-use (e.g., cooldown or per-session cap on open/cancel cycles per `(origin, recipient)`), so a single attacker cannot cheaply regenerate unlimited notifications toward the same victim.

### Proof of Concept
Extend `polkadot/runtime/parachains/src/dmp/tests.rs`'s `verify_fee_factor_reaches_high_value` pattern into an integration test in the `hrmp` pallet:
1. Register attacker para `A` and victim para `V`.
2. Loop N times: call `Hrmp::hrmp_init_open_channel(Origin::Parachain(A), V, cap, size)` (assert `Ok`), assert a new DM appended to `Dmp::dmq_contents_do_not_call_in_consensus(V)`, then call `Hrmp::hrmp_cancel_open_request(Origin::Parachain(A), HrmpChannelId{sender:A, recipient:V})` (assert `Ok`, deposit fully refunded).
3. Assert `Dmp::dmq_length(V)` grows by 1 each cycle and eventually reaches `Dmp::dmq_max_length(...)`.
4. Assert `Dmp::DeliveryFeeFactor::<Test>::get(V)` grows to an extreme value while the attacker's reserved balance after each full cycle returns to its pre-cycle amount (i.e., attacker's cost per cycle is only the fixed extrinsic weight fee, not proportional to the fee factor).
5. Assert that once `dmq_length(V) == dmq_max_length`, a simulated legitimate `queue_downward_message(V, ...)` call (representing a governance/system or priced XCM send) returns `Err(QueueDownwardMessageError::ExceedsMaxMessageSize)`, demonstrating denial of service.

### Citations

**File:** polkadot/runtime/common/src/xcm_sender.rs (L84-94)
```rust
impl<A: Get<AssetId>, B: Get<u128>, M: Get<u128>, F: FeeTracker> PriceForMessageDelivery
	for ExponentialPrice<A, B, M, F>
{
	type Id = F::Id;

	fn price_for_delivery(id: Self::Id, msg: &Xcm<()>) -> Assets {
		let msg_fee = (msg.encoded_size() as u128).saturating_mul(M::get());
		let fee_sum = B::get().saturating_add(msg_fee);
		let amount = F::get_fee_factor(id).saturating_mul_int(fee_sum);
		(A::get(), amount).into()
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

**File:** polkadot/runtime/parachains/src/hrmp.rs (L1467-1483)
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

**File:** polkadot/runtime/parachains/src/dmp/tests.rs (L295-312)
```rust
#[test]
fn verify_fee_factor_reaches_high_value() {
	let a = ParaId::from(123);
	let mut genesis = default_genesis_config();
	genesis.configuration.config.max_downward_message_size = 51200;
	new_test_ext_integrity(genesis, || {
		register_paras(&[a]);

		let max_messages =
			Dmp::dmq_max_length(ActiveConfig::<Test>::get().max_downward_message_size);
		let mut total_fee_factor = FixedU128::from_float(1.0);
		for _ in 1..max_messages {
			assert_ok!(queue_downward_message(a, vec![]));
			total_fee_factor = total_fee_factor + (DeliveryFeeFactor::<Test>::get(a));
		}
		assert!(total_fee_factor > FixedU128::from_u32(100_000_000));
	});
}
```
