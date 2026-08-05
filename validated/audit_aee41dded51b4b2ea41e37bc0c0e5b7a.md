Audit Report

## Title
Delivery fee for UMP/DMP/XCMP is computed on the pre-`wrap_version` message, allowing under-payment when version conversion inflates the encoded size - (File: cumulus/primitives/utility/src/lib.rs)

## Summary
`ParentAsUmp::validate` computes `price = P::price_for_delivery((), &xcm)` on the pre-version-conversion `Xcm<()>` at [1](#0-0) , and only afterward calls `W::wrap_version(&d, xcm)` and encodes the resulting `versioned_xcm` into the bytes that are actually decoded-checked and delivered [2](#0-1) . `ExponentialPrice::price_for_delivery` prices strictly by `msg.encoded_size()` of that pre-wrap message [3](#0-2) , so if `into_version` conversion grows the encoded size, the fee undercounts the actual bytes queued/delivered. The identical ordering exists in `ChildParachainRouter::validate` [4](#0-3) .

## Finding Description
The code exactly matches the claim: in both `ParentAsUmp::validate` and `ChildParachainRouter::validate`, `price_for_delivery` is invoked on `&xcm` (the pre-`wrap_version`, internal-latest-version `Xcm<()>`), and only after pricing is `wrap_version` applied, decoded-checked, and encoded into the `data`/`blob` that is passed to `can_send_upward_message`/`can_queue_downward_message` and ultimately queued for delivery. This is confirmed at [5](#0-4)  and [6](#0-5) . `ExponentialPrice`'s doc comment states `M` is "the fee to pay for each and every byte of the message after encoding it" [7](#0-6) , yet the encoding used for that calculation is `msg.encoded_size()` on the un-wrapped message [3](#0-2) , not the size of the version-wrapped bytes that are actually queued. `check_is_decodable()` and `can_send_upward_message`/`can_queue_downward_message` enforce only decode-depth/hard size caps on the final bytes — they do not re-price or reconcile the fee with the final byte length, so the ordering flaw is real and unguarded against for fee-correctness purposes.

This part of the claim is verified as an accurate description of the code's control flow and is a genuine logical inconsistency between the documented pricing intent and the implementation.

## Impact Explanation
The impact is limited strictly to a fee/accounting mismatch: whatever size growth occurs during `into_version` conversion between the pallet's internal latest `Xcm<()>` representation and the destination's `SupportedVersion` is not reflected in the delivery fee charged. This does not enable asset theft, duplication, unbounded message injection, or bypass of the hard message-size caps enforced by `check_is_decodable`/`can_send_upward_message`/`can_queue_downward_message` (those checks operate on the actual post-wrap bytes and would still reject an over-large message regardless of fee). The magnitude of possible under-payment is bounded by how much a version downgrade/conversion can inflate encoding size for a given message — this was not fully quantified in the available context (the concrete `TryFrom`/`into_version` instruction-conversion implementations for each XCM version were not exhaustively reviewed), and the report's own Likelihood Explanation section explicitly acknowledges this: "I could not conclusively quantify how large a growth is achievable... so the *existence* of the ordering flaw is confirmed, but the *magnitude* of exploitable under-payment is not fully verified." Given that byte-fee constants (`M`) in production configurations are typically small relative to base fees, and that any growth from cross-version conversion is generally proportional to the number of `Location`/`Junction`/asset items already present in the message (not attacker-controlled multiplication), this is a bounded, per-message under-charge rather than an economic exploit with unbounded leverage.

## Likelihood Explanation
The code path is reachable by any account that can call `pallet_xcm::send`/`execute` targeting `Parent` or a child parachain — no special privilege required. However, exploitability requires the attacker's message to trigger a genuine size-increasing `into_version` conversion, and the actual achievable fee-under-payment delta per message was not demonstrated with a concrete magnitude or PoC execution in this codebase (the provided PoC is a template with placeholder instructions/values, not an executed or validated reproduction). Without a demonstrated concrete size delta and resulting economically meaningful under-payment, the practical severity is unproven beyond a theoretical accounting inconsistency.

## Recommendation
Compute (or re-validate) `price_for_delivery` using the final `versioned_xcm.encode()` length (post-`wrap_version`) instead of `msg.encoded_size()` on the pre-wrap `Xcm<()>`, in `ParentAsUmp::validate`, `ChildParachainRouter::validate`, and the analogous `XcmpQueue::validate` path, so that byte-based fees are computed on the bytes that are actually queued/delivered.

## Proof of Concept
Not independently executed/validated in this review; the submitted PoC is a template (`assert!(post_wrap_len > pre_wrap_len)` / `assert_ne!(price_charged, expected_correct_price)`) requiring specific instruction/location choices demonstrated to inflate size across `into_version`, which were not supplied or verified against actual `TryFrom` implementations in the codebase. A valid reproduction would need to: construct a concrete `Xcm<()>` in the latest version, show `W::wrap_version` under a real `SupportedVersion` configuration produces a strictly larger encoding, and show the resulting `price_for_delivery` (computed pre-wrap) is less than a fee computed on the actual post-wrap byte length.

### Citations

**File:** cumulus/primitives/utility/src/lib.rs (L71-88)
```rust
	fn validate(dest: &mut Option<Location>, msg: &mut Option<Xcm<()>>) -> SendResult<Vec<u8>> {
		let d = dest.take().ok_or(SendError::MissingArgument)?;

		if d.contains_parents_only(1) {
			// An upward message for the relay chain.
			let xcm = msg.take().ok_or(SendError::MissingArgument)?;
			let price = P::price_for_delivery((), &xcm);
			let versioned_xcm =
				W::wrap_version(&d, xcm).map_err(|()| SendError::DestinationUnsupported)?;
			versioned_xcm
				.check_is_decodable()
				.map_err(|()| SendError::ExceedsMaxMessageSize)?;
			let data = versioned_xcm.encode();

			// Pre-check with our message sender if everything else is okay.
			T::can_send_upward_message(&data).map_err(Self::map_upward_sender_err)?;

			Ok((data, price))
```

**File:** polkadot/runtime/common/src/xcm_sender.rs (L69-82)
```rust
/// Implementation of [`PriceForMessageDelivery`] which returns an exponentially increasing price.
/// The formula for the fee is based on the sum of a base fee plus a message length fee, multiplied
/// by a specified factor. In mathematical form:
///
/// `F * (B + encoded_msg_len * M)`
///
/// Thus, if F = 1 and M = 0, this type is equivalent to [`ConstantPrice<B>`].
///
/// The type parameters are understood as follows:
///
/// - `A`: Used to denote the asset ID that will be used for paying the delivery fee.
/// - `B`: The base fee to pay for message delivery.
/// - `M`: The fee to pay for each and every byte of the message after encoding it.
/// - `F`: A fee factor multiplier. It can be understood as the exponent term in the formula.
```

**File:** polkadot/runtime/common/src/xcm_sender.rs (L89-94)
```rust
	fn price_for_delivery(id: Self::Id, msg: &Xcm<()>) -> Assets {
		let msg_fee = (msg.encoded_size() as u128).saturating_mul(M::get());
		let fee_sum = B::get().saturating_add(msg_fee);
		let amount = F::get_fee_factor(id).saturating_mul_int(fee_sum);
		(A::get(), amount).into()
	}
```

**File:** polkadot/runtime/common/src/xcm_sender.rs (L107-130)
```rust
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
```
