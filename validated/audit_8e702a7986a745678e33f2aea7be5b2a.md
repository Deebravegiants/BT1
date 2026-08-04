### Title
Cheap, deposit-refunding HRMP open/cancel-request loop lets a single para spam a victim para's `DownwardMessageQueuePages` with unbounded system notifications, saturating its DMQ and blocking new downward messages - ([File: polkadot/runtime/parachains/src/dmp.rs], [File: polkadot/runtime/parachains/src/hrmp.rs])

### Summary
`Pallet::init_open_channel`/`accept_open_channel`/`close_channel` in `hrmp.rs` unconditionally call `Self::send_to_para` -> `dmp::Pallet::<T>::queue_downward_message`, injecting an `HrmpNewChannelOpenRequest`/`HrmpChannelAccepted`/`HrmpChannelClosing` XCM notification into the *recipient's* DMQ without the recipient's consent. Because `hrmp_cancel_open_request` fully refunds the sender's deposit and removes the in-flight request, a malicious para can loop `hrmp_init_open_channel(victim, …)` immediately followed by `hrmp_cancel_open_request`, generating one free DM per iteration toward an arbitrary victim indefinitely, since `HrmpOpenChannelRequestCount`/`HrmpEgressChannelsIndex` limits are only checked against currently *outstanding* (non-cancelled) requests.

### Finding Description
`Pallet::init_open_channel` (`hrmp.rs:1443-1526`) checks per-attacker limits (`egress_cnt + open_req_cnt < channel_num_limit`, deposit availability, recipient validity) but none of these checks account for repeated open→cancel cycles, because `hrmp_cancel_open_request` deletes the `HrmpOpenChannelRequests`/`HrmpOpenChannelRequestsList` entry and decrements the counters, fully resetting the attacker's quota [1](#0-0) . Each `init_open_channel` call unconditionally calls `Self::send_to_para` which calls `dmp::Pallet::<T>::queue_downward_message` targeting the *recipient* (victim), not the caller [2](#0-1) [3](#0-2) .

`can_queue_downward_message`/`queue_downward_message` in `dmp.rs` only reject a message once `dmq_length(victim) > dmq_max_length(...)`, a large but finite hard cap derived from `MAX_POSSIBLE_ALLOCATION / max_downward_message_size` [4](#0-3) [5](#0-4) . There is no per-sender rate limit, no fee charged for HRMP notification injection (only a refundable deposit), and the `DeliveryFeeFactor` congestion pricing mechanism only affects XCM senders that explicitly pay delivery fees through the `Sender` interface—HRMP notifications bypass that economic deterrent entirely since they are injected as free relay-chain-originated "system notifications". A colluding/malicious para (attacker only needs *itself* to be onboarded; no cooperation from the victim is required) can therefore repeatedly call `hrmp_init_open_channel(victim, …)` then `hrmp_cancel_open_request`, at the rate its own UMP message throughput and relay-chain block weight allow, continuously injecting entries into `DownwardMessageQueuePages[victim]`.

Once `dmq_length(victim)` approaches `dmq_max_length`, `can_queue_downward_message` starts rejecting *all* further downward messages to the victim—including legitimate governance/XCM messages sent by third parties—until the victim's collators process/prune enough of the backlog (`Pallet::prune_dmq`) to fall back under the threshold. As long as the attacking para sustains the flood at or above the victim's drain rate, the victim's queue remains saturated with attacker-injected junk notifications, and legitimate senders cannot get new downward messages queued.

### Impact Explanation
The victim para's downward message queue (`DownwardMessageQueuePages`) can be filled by an unrelated, unprivileged para at negligible net cost (deposit is refunded, only extrinsic weight fees are consumed), causing legitimate downward messages (from users' XCM sends, HRMP notifications from third parties, or governance actions targeting that para) to be rejected with `ExceedsMaxMessageSize`/queue-full errors while the attack is sustained. This is a temporary but potentially sustained/indefinite denial-of-service against a specific victim para's DMP channel, not a fund-loss or consensus-safety bug; the queue self-heals once the victim processes backlog or the attacker stops, so it is not literally "permanent," but an actively-sustained attacker can keep the channel effectively unusable for as long as they choose.

### Likelihood Explanation
Preconditions: the attacker must control an onboarded parachain (able to dispatch `hrmp_init_open_channel`/`hrmp_cancel_open_request` via its own parachain-origin UMP/Transact path)—no cooperation from the victim or a second colluding para is strictly required, since the recipient of the notification never needs to accept. The loop is cheap (deposit refunded on cancel) and repeatable every block subject to UMP message throughput/weight limits, making the attack feasible and fully repeatable over time, though the absolute size of `dmq_max_length` means saturating the queue requires many iterations across many blocks.

### Recommendation
Rate-limit or fee-meter HRMP channel-management notification injection independent of the refundable deposit—e.g., charge a small non-refundable fee per `hrmp_init_open_channel`/`cancel_open_request` cycle, or track open+cancel churn per `(origin, recipient)` pair per session and cap it, so an attacker cannot reset its "outbound channel" quota by cancelling. Additionally consider applying the existing `DeliveryFeeFactor` congestion-pricing mechanism to HRMP system notifications so repeated injection into a congested victim queue becomes progressively more expensive for the originating para.

### Proof of Concept
Integration test in `polkadot/runtime/parachains/src/hrmp/tests.rs` style:
1. Register attacker para `A` and victim para `V` (`register_parachain`).
2. Loop N times: `assert_ok!(Hrmp::hrmp_init_open_channel(A_origin, V, cap, size))`; then `assert_ok!(Hrmp::hrmp_cancel_open_request(A_origin, HrmpChannelId{sender:A, recipient:V}))`.
3. After each iteration assert `Dmp::dmq_length(V)` increases by 1 and the attacker's reserved balance returns to baseline after cancel (deposit is refunded, confirming zero net cost).
4. Continue looping until `Dmp::dmq_length(V) > Dmp::dmq_max_length(max_downward_message_size)` and assert that a subsequent legitimate `dmp::Pallet::<Test>::queue_downward_message(&config, V, legit_msg)` call returns `Err(QueueDownwardMessageError::ExceedsMaxMessageSize)`, proving V's own legitimate traffic is blocked by third-party-injected spam.
5. Assert that after `Dmp::prune_dmq(V, N)` (simulating V processing its backlog), the legitimate message can then be enqueued—demonstrating the congestion is real but recoverable, and quantifying how many spam iterations are needed to force it.

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

**File:** polkadot/runtime/parachains/src/dmp.rs (L392-394)
```rust
	fn dmq_max_length(max_downward_message_size: u32) -> u32 {
		MAX_POSSIBLE_ALLOCATION.checked_div(max_downward_message_size).unwrap_or(0)
	}
```
