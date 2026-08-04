### Title
DeliveryFeeFactor tracks only byte-size congestion (`max_total_size`/`THRESHOLD_FACTOR`), not message/page-count congestion, allowing disproportionately cheap consumption of XCMP channel capacity - (File: cumulus/pallets/xcmp-queue/src/lib.rs)

### Summary
The XCMP-queue delivery fee mechanism is documented and implemented to increase `DeliveryFeeFactor` only when the cumulative encoded byte size of a channel's outbound queue exceeds `max_total_size / THRESHOLD_FACTOR`, per the module doc comment. Since an HRMP/XCMP channel is also capacity-bounded by `max_capacity` (a message/page count limit) independent of `max_total_size`, an attacker can craft many small messages that each occupy a full outbound page (via per-page overhead or non-mergeable formats) and push the channel toward its message-count-based congestion limit while remaining under the byte-size threshold that triggers fee increases.

### Finding Description
The doc comment at the top of `cumulus/pallets/xcmp-queue/src/lib.rs` explicitly states the fee model: [1](#0-0) 

and the shared `FeeTracker::increase_fee_factor`/`do_increase_fee_factor` in `polkadot/runtime/parachains/src/lib.rs` computes the multiplier purely from `message_size` in bytes, with no dependency on message/page count: [2](#0-1) 

The existing regression test `verify_fee_factor_increase_and_decrease` confirms the fee factor only reacts to `total_size` crossing `max_total_size / THRESHOLD_FACTOR`, and that "sending the message right now" pricing is driven by that same size-based accounting: [3](#0-2) 

An HRMP channel, however, has two independent congestion dimensions from `AbridgedHrmpChannel`: `max_capacity` (message/page count) and `max_total_size` (bytes), both used in the same test's channel setup: [4](#0-3) 

Because the fee model only reacts to the byte-size dimension, if an attacker can drive `msg_count`/page count toward `max_capacity` while `total_size` stays below `max_total_size / THRESHOLD_FACTOR` (a function of channel configuration and how outbound pages are packed/merged), they consume queue capacity that is genuinely scarce (page slots) without paying the exponentially increasing fee that reflects that scarcity. This requires channel parameters where `max_capacity * (average per-message page overhead)` reaches capacity before `total_size` crosses the byte threshold — a configuration-dependent condition, not something the attacker controls directly (channel config is set by chain operators/governance, not by the unprivileged sender).

### Impact Explanation
If exploitable on a given deployment's channel configuration, this allows an unprivileged sender to occupy a disproportionate share of a channel's finite page/message slots at `MIN_FEE_FACTOR` pricing, while `DeliveryFeeFactor` — and thus the deterrent cost for further congestion — fails to rise to reflect the actual exhaustion risk. This matches the scoped impact of underpriced delivery relative to genuine queue burden, and could contribute to griefing of XCMP channel capacity for other users/parachains sharing that channel.

### Likelihood Explanation
Exploitability is entirely dependent on the relative values of `max_capacity`, `max_message_size`, `max_total_size`, and `THRESHOLD_FACTOR` for a specific channel, plus how `send_fragment`/page-append logic packs multiple small messages into pages (concatenation logic could reduce or eliminate the "one message per page" effect for messages using the same `XcmpMessageFormat`). No code path was found in the reviewed sections that ties fee-factor increase to message count or page count directly — only to `total_size` in bytes — so the described gap in the pricing model is confirmed at the design level. Full confirmation of whether real-world channel configs make the byte-threshold binding always occur before the capacity-count binding (which would neutralize the issue in practice) would require checking the actual `send_fragment`/page-append merging logic and typical channel configs on live/testnet networks, which was not fully retrievable in this session.

### Recommendation
Extend the `FeeTracker`/`send_fragment` congestion check in `cumulus/pallets/xcmp-queue/src/lib.rs` to also factor in message/page count relative to `max_capacity` (e.g., a `THRESHOLD_FACTOR`-style ratio on `msg_count`/`max_capacity`), so `DeliveryFeeFactor` increases when either the byte-size threshold or the message-count threshold is crossed, whichever occurs first.

### Proof of Concept
Extend `verify_fee_factor_increase_and_decrease` in `cumulus/pallets/xcmp-queue/src/tests.rs`:
1. Configure an `AbridgedHrmpChannel` with a low `max_capacity` (e.g., 10) but a large `max_total_size` (e.g., 100_000), so the byte-size threshold (`max_total_size / THRESHOLD_FACTOR`) is far from being reached at 10 messages.
2. Send `max_capacity` (or near it) minimal single-instruction XCM messages designed to each start a new outbound page (varying message shape/format to defeat page-merging where applicable).
3. Assert `DeliveryFeeFactor::<Test>::get(sibling_para_id)` remains at `MIN_FEE_FACTOR` while `msg_count`/page count approaches `max_capacity` (i.e., queue is near capacity-exhaustion but fee has not moved), and separately assert that once `total_size` crosses the byte threshold, fee increases — showing the two congestion signals are decoupled and only one is actually priced.

### Citations

**File:** cumulus/pallets/xcmp-queue/src/lib.rs (L26-34)
```rust
//! To prevent out of memory errors on the `OutboundXcmpMessages` queue, an exponential fee factor
//! (`DeliveryFeeFactor`) is set, much like the one used in DMP.
//! The fee factor increases whenever the total size of messages in a particular channel passes a
//! threshold. This threshold is defined as a percentage of the maximum total size the channel can
//! have. More concretely, the threshold is `max_total_size` / `THRESHOLD_FACTOR`, where:
//! - `max_total_size` is the maximum size, in bytes, of the channel, not number of messages.
//! It is defined in the channel configuration.
//! - `THRESHOLD_FACTOR` just declares which percentage of the max size is the actual threshold.
//! If it's 2, then the threshold is half of the max size, if it's 4, it's a quarter, and so on.
```

**File:** polkadot/runtime/parachains/src/lib.rs (L80-92)
```rust
	fn do_increase_fee_factor(fee_factor: &mut FixedU128, message_size: u128) {
		let message_size_factor = FixedU128::from(message_size.saturating_div(1024))
			.saturating_mul(Self::MESSAGE_SIZE_FEE_BASE);
		*fee_factor = fee_factor
			.saturating_mul(Self::EXPONENTIAL_FEE_BASE.saturating_add(message_size_factor));
	}

	/// Increases the delivery fee factor by a factor based on message size and records the result.
	fn increase_fee_factor(id: Self::Id, message_size: u128) {
		let mut fee_factor = Self::get_fee_factor(id);
		Self::do_increase_fee_factor(&mut fee_factor, message_size);
		Self::set_fee_factor(id, fee_factor);
	}
```

**File:** cumulus/pallets/xcmp-queue/src/tests.rs (L1166-1176)
```rust
		ParachainSystem::open_custom_outbound_hrmp_channel_for_benchmarks_or_tests(
			sibling_para_id,
			AbridgedHrmpChannel {
				max_capacity: 10,
				max_total_size: 1000,
				max_message_size: 104,
				msg_count: 0,
				total_size: 0,
				mqc_head: None,
			},
		);
```

**File:** cumulus/pallets/xcmp-queue/src/tests.rs (L1178-1206)
```rust
		// Fee factor is only increased in `send_fragment`, which is called by `send_xcm`.
		// When queue is not congested, fee factor doesn't change.
		assert_ok!(send_xcm::<XcmpQueue>(destination.clone(), xcm.clone())); // Size 104
		assert_ok!(send_xcm::<XcmpQueue>(destination.clone(), xcm.clone())); // Size 208
		assert_ok!(send_xcm::<XcmpQueue>(destination.clone(), xcm.clone())); // Size 312
		assert_ok!(send_xcm::<XcmpQueue>(destination.clone(), xcm.clone())); // Size 416
		assert_eq!(DeliveryFeeFactor::<Test>::get(sibling_para_id), initial);

		// Sending the message right now is cheap
		let (_, delivery_fees) = validate_send::<XcmpQueue>(destination.clone(), xcm.clone())
			.expect("message can be sent; qed");
		let Fungible(delivery_fee_amount) = delivery_fees.inner()[0].fun else {
			unreachable!("asset is fungible; qed");
		};
		assert_eq!(delivery_fee_amount, 402_000_000);

		let smaller_xcm = Xcm(vec![ClearOrigin; 30]);

		// When we get to half of `max_total_size`, because `THRESHOLD_FACTOR` is 2,
		// then the fee factor starts to increase.
		assert_ok!(send_xcm::<XcmpQueue>(destination.clone(), xcm.clone())); // Size 520
		assert_eq!(DeliveryFeeFactor::<Test>::get(sibling_para_id), FixedU128::from_float(1.05));

		for _ in 0..12 {
			// We finish at size 929
			assert_ok!(send_xcm::<XcmpQueue>(destination.clone(), smaller_xcm.clone()));
		}
		assert!(DeliveryFeeFactor::<Test>::get(sibling_para_id) > FixedU128::from_float(1.88));

```
