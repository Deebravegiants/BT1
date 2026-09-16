This confirms the analog. The `handle_unsigned` extrinsic in `pallet-state-coprocessor` is dispatched via `ensure_none(origin)` — an unsigned, unauthenticated origin — and the `GetRequestsWithProof.address` field (the account credited with reputation minting) is never checked against any cryptographic signature. Unlike its sibling `pallet-messaging-incentives`, which recovers the relayer's identity by verifying the sr25519 `signer` field on the message with `Signature::verify_and_get_sr25519_pubkey` (`modules/pallets/messaging-incentives/src/lib.rs:140-153`), the state-coprocessor path passes `address` straight through from the submitted payload with no proof of possession.

### Title
Unauthenticated reputation-minting identity in `pallet-state-coprocessor::handle_unsigned` — self-declared `address` field bypasses signature-based relayer attribution - (File: `modules/pallets/state-coprocessor/src/impls.rs`)

### Summary
`GetRequestsWithProof` carries an `address: Vec<u8>` field documented as "Address that should be credited with fees" [1](#0-0)  . The extrinsic that consumes it, `handle_unsigned`, is dispatched with `ensure_none(origin)` [2](#0-1)  — meaning anyone can submit it without a signed transaction or bond. `Self::handle_get_requests` verifies the state/membership proofs for the `GetRequest`/`GetResponse` pair, but never verifies that `address` is cryptographically tied to the submitter of the proof: it is used directly to mint reputation tokens once the byte-rate threshold is met [3](#0-2) .

### Finding Description
This mirrors the reported bug class exactly: a field that is supposed to represent verified authorization/provenance (here, "which relayer delivered this batch and should be rewarded") is instead accepted as self-declared metadata from an unauthenticated caller, rather than being derived from a verified signature.

Contrast with the sibling pallet `pallet-messaging-incentives`, which handles the analogous "who delivered this message" question correctly: it recovers the relayer's account by verifying an sr25519 signature over the message payload via `Signature::verify_and_get_sr25519_pubkey`, and only mints reputation to the recovered (verified) signer [4](#0-3) . Its own test suite explicitly asserts that a garbled/self-declared signature must not mint any reputation [5](#0-4) .

`pallet-state-coprocessor::handle_get_requests`, however, takes `address` verbatim from the submitted `GetRequestsWithProof` struct with no signature check at all, and uses it both to mint reputation and to record `store_response_receipt` / `dispatch_get_response` attribution [6](#0-5) . The `validate_unsigned` implementation only re-runs `handle_get_requests` (for txpool validity) and computes a dedup tag from the request hashes — it performs no signature check on `address` either [7](#0-6) .

Because `handle_unsigned` is permissionless (any peer can submit an unsigned extrinsic with valid state/response proofs it obtained by observation, e.g. by watching the source/dest chains or another relayer's mempool), an attacker can front-run or simply copy someone else's already-fetched proof and resubmit it with their own `address`, claiming the reputation mint for work performed by another relayer's proof-fetching effort. Since `pallet-ismp`'s txpool validation deduplicates by the request-hash-derived tag (not signer), only the first submission of a given proof succeeds — so this is a race for proof reuse/front-running rather than double-claiming, but attribution/identity is still not cryptographically bound to the actual submitter.

### Impact Explanation
Reputation minted here (`ReputationAsset`) is described elsewhere in the codebase as "the primary input to collator selection" [8](#0-7) . An attacker able to attribute reputation to an arbitrary `address` without proving control of any relaying infrastructure can inflate their own collator-selection weight by watching the network for valid `GetRequestsWithProof` payloads (which are public data — proofs and requests are not secret) and resubmitting them with their own `address` before the legitimate relayer does, or by running a sybil operation that fabricates many unsigned submissions with self-chosen addresses whenever it can assemble valid proofs cheaply. This is an unauthorized/unbacked reputation-asset mint tied to collator authority, not merely a griefing/DoS issue.

### Likelihood Explanation
Moderately likely: the proofs and requests needed to construct a valid `GetRequestsWithProof` are public (sourced from chain state), and the transaction is unsigned/free, so the only cost to an attacker is proof construction and network racing against the legitimate relayer — no signature or bond is required to claim the reward's beneficiary field.

### Recommendation
Bind the `address`/reward-beneficiary field to a verified signature the same way `pallet-messaging-incentives::relayer_for` does: require a signature (e.g. over the batch's request hashes or the derived commitment) from the claimed `address`, and recover/verify it in `handle_get_requests`/`validate_unsigned` before using it for reputation minting or receipt attribution, rejecting the call if verification fails.

### Proof of Concept
1. Observe a `GetRequestsWithProof` message (source proof + response state proof) being prepared or already submitted on-chain/mempool by a legitimate relayer for state-coprocessor's `handle_unsigned`.
2. Reconstruct/copy the same `requests`, `source` proof, and `response` proof, but substitute the `address` field with an attacker-controlled 32-byte public key.
3. Submit this as an unsigned extrinsic to `StateCoprocessor::handle_unsigned` before the legitimate relayer's transaction lands.
4. If it lands first (txpool dedup only keys on request-hash tag, not `address`), `handle_get_requests` mints `ReputationMinted` to the attacker's `address` in `modules/pallets/state-coprocessor/src/impls.rs:157-186`, and `store_response_receipt`/`dispatch_get_response` attribute the response to the attacker's address, despite the attacker not having performed any verified signing of the delivery.

### Citations

**File:** modules/pallets/state-coprocessor/src/impls.rs (L42-55)
```rust
/// Message for processing state queries
#[derive(
	Debug, Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, scale_info::TypeInfo,
)]
pub struct GetRequestsWithProof {
	/// The associated Get requests
	pub requests: Vec<GetRequest>,
	/// Proof of these requests on the source chain
	pub source: Proof,
	/// State proof of the requested values in the Get requests.
	pub response: Proof,
	/// Address that should be credited with fees
	pub address: Vec<u8>,
}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L157-186)
```rust
		// Mint reputation tokens to the named relayer. The address is the
		// relayer's raw 32-byte public key as supplied by the coprocessor.
		// A zero rate disables minting and a malformed address simply skips
		// the mint — we don't want a non-32-byte address to fail the whole
		// batch since the response insertion below has no dependency on it.
		// The per-byte rate and reputation asset are inherited from
		// `pallet-messaging-incentives` so both pallets share one source of truth.
		let rate = pallet_messaging_incentives::MintPerByte::<T>::get();
		if !rate.is_zero() && total_bytes > 0 {
			if let Ok(bytes32) = <[u8; 32]>::try_from(address.as_slice()) {
				let relayer: T::AccountId = bytes32.into();
				let bytes_balance: BalanceOf<T> = (total_bytes as u128).saturated_into();
				let amount = rate.saturating_mul(bytes_balance);
				if !amount.is_zero() {
					match <T as pallet_messaging_incentives::Config>::ReputationAsset::mint_into(
						&relayer, amount,
					) {
						Ok(_) => Pallet::<T>::deposit_event(Event::ReputationMinted {
							relayer,
							bytes: total_bytes,
							amount,
						}),
						Err(err) => log::warn!(
							target: "ismp",
							"state-coprocessor: reputation mint failed for {total_bytes}b: {err:?}",
						),
					}
				}
			}
		}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L188-192)
```rust
		for get_response in responses {
			host.store_response_receipt(&get_response, &address)?;
			Self::dispatch_get_response(get_response, address.clone())
				.map_err(|_| Error::Custom("Failed to dispatch get response".to_string()))?;
		}
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L92-104)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			message: GetRequestsWithProof,
		) -> DispatchResult {
			ensure_none(origin)?;

			Self::handle_get_requests(message).map_err(|err| {
				log::error!(target: "ismp", "pallet-coprocessor: {:?}", err);
				Error::<T>::HandlingError
			})?;

			Ok(())
		}
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L107-148)
```rust
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T>
	where
		T::AccountId: AsRef<[u8]>,
		<T as frame_system::Config>::AccountId: From<[u8; 32]>,
		<T as pallet_ismp::Config>::Balance: Into<u128>,
	{
		type Call = Call<T>;

		// empty pre-dispatch so we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			let Call::handle_unsigned { message } = call else {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			};

			if let Err(err) = Self::handle_get_requests(message.clone()) {
				log::error!(target: "ismp", "{:?}", err);
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}

			let mut messages = message
				.requests
				.iter()
				.map(|get| hash_request::<<T as Config>::IsmpHost>(&Request::Get(get.clone())))
				.collect::<Vec<_>>();
			messages.sort();

			// this is so we can reject duplicate batches at the mempool level
			let msg_hash = sp_io::hashing::keccak_256(&messages.encode()).to_vec();

			Ok(ValidTransaction {
				priority: 100,
				requires: vec![],
				provides: vec![msg_hash],
				longevity: 25,
				propagate: true,
			})
		}
```

**File:** modules/pallets/messaging-incentives/src/lib.rs (L137-153)
```rust
	/// Recover the relayer's account from the sr25519 signature on a
	/// `Message`'s `signer` field. Returns `None` if the message has
	/// no signer (e.g. consensus messages) or the signature is bad.
	fn relayer_for(message: &Message) -> Option<T::AccountId> {
		let (signer, signed) = match message {
			Message::Request(msg) =>
				(&msg.signer, sp_io::hashing::keccak_256(&msg.requests.encode())),
			Message::Response(msg) =>
				(&msg.signer, sp_io::hashing::keccak_256(&msg.requests.encode())),
			_ => return None,
		};
		Signature::decode(&mut &signer[..])
			.ok()?
			.verify_and_get_sr25519_pubkey(&signed, None)
			.ok()
			.map(T::AccountId::from)
	}
```

**File:** modules/pallets/testsuite/src/tests/pallet_messaging_incentives.rs (L289-308)
```rust
#[test]
fn unsigned_message_does_not_mint() {
	new_test_ext().execute_with(|| {
		let relayer_pair = sr25519::Pair::from_seed(&[10u8; 32]);
		let relayer_account = AccountId32::new(relayer_pair.public().0);
		setup_relayer_and_asset(&relayer_account);

		MessagingRelayerIncentives::set_mint_per_byte(RuntimeOrigin::root(), 1).unwrap();

		// Replace the signature bytes with garbage — the pallet must
		// refuse to mint when it can't recover a relayer.
		let mut msg = signed_request(&relayer_pair, vec![0u8; 50]);
		if let Message::Request(ref mut r) = msg.message {
			r.signer = vec![0u8; 64];
		}
		MessagingRelayerIncentives::on_executed(vec![msg], vec![]).unwrap();

		assert_eq!(relayer_balance(&relayer_account), 0);
	});
}
```

**File:** docs/content/developers/explore/relayers.mdx (L73-79)
```text
### Rewards

Consensus relayers are paid in `$BRIDGE` on every accepted update,
plus a **non-transferable reputation asset** at a 1:1 ratio.
Reputation is the primary input to [collator selection](/developers/network/collator):
the more proofs you submit, the better your chances of being selected
to author Hyperbridge blocks.
```
