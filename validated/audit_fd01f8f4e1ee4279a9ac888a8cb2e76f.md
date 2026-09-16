### Title
Unauthenticated `signer` field in ISMP request/response messages lets any relayer forge another relayer's fee-payout identity - (File: `modules/pallets/relayer/src/accumulate.rs`)

### Summary
Apache Impala's bug was that a bearer token's signature was never verified before its embedded username was trusted, letting an attacker impersonate any user. Hyperbridge has a structurally identical pattern in the relayer fee-attribution path: the `signer` bytes attached to an ISMP `Message::Request`/`Message::Response` are stored verbatim on the destination chain by `store_request_receipt`/`store_response_receipt` [1](#0-0) , and are later trusted as the identity of the relayer entitled to cross-chain fees by simply *decoding* (not verifying) an embedded `Signature` enum.

### Finding Description
`handle_unsigned` is an unsigned, permissionless extrinsic — anyone can submit an ISMP message with valid state-membership proofs and an arbitrary `signer` field [2](#0-1) . In `handlers/request.rs`, the raw `msg.signer` bytes are passed straight into `host.store_request_receipt(&wrapped_req, &msg.signer)` with no signature check at all — it is treated purely as "the relayer that delivered this message" [3](#0-2) . The `IsmpHost` trait documents this field as "Includes the relayer account" without requiring any cryptographic verification [1](#0-0) .

When relayer fees are later accumulated cross-chain via a storage proof of `RequestReceipts[commitment]`, `decode_receipt_relayer` in the relayer pallet extracts the fee-recipient identity from those same raw stored bytes. For substrate destinations, if the stored bytes are longer than 32 bytes, it does `Signature::decode(&mut &*bytes)...signer()` [4](#0-3) . Critically, `Signature::signer()` only extracts the embedded `public_key`/`address` field from the enum — it performs **no cryptographic verification** that the signature actually signs anything [5](#0-4) , unlike `Signature::verify()` or `verify_and_get_sr25519_pubkey()` which are used elsewhere (e.g. in `fee_handler.rs` and `messaging-incentives`) [6](#0-5) [7](#0-6) .

This mirrors the simtest fixture that constructs a `handle_unsigned` message whose `signer` field is pure random bytes wrapped in `Signature::Sr25519 { public_key: H256::random()..., signature: H256::random()... }`, with no actual signing performed — and the message is still accepted and the receipt stored [8](#0-7) .

So an attacker (any unprivileged party able to submit `handle_unsigned` with valid delivery/membership proofs) can set `signer` to `Signature::Sr25519 { public_key: <victim_or_attacker_chosen_bytes>, signature: <garbage> }`. Because `decode_receipt_relayer` calls `.signer()` and never `.verify()`, the garbage/forged signature is accepted and the embedded `public_key` bytes are trusted as the fee-earning relayer identity for that delivered request, exactly as Impala trusted an unverified bearer-token username.

### Impact Explanation
This breaks relayer-fee accounting integrity in the cross-chain fee accumulation path (`accumulate_fees`, `withdraw_fees`) [9](#0-8) . An attacker who is the actual party submitting `handle_unsigned` for a message (which anyone can do, since it's an unsigned/permissionless extrinsic protected only by valid proofs) can set the `signer` field to any account bytes they like without proving ownership. Downstream, `decode_receipt_relayer` credits relayer-fee accumulation to that forged identity instead of verifying it cryptographically. This is unauthorized value redirection: real relayer fee rewards intended for the actual message deliverer/its designated payee can be attributed to an attacker-chosen account, i.e. theft of relayer fees — a Medium/High severity fund-diversion analogous to Impala's identity-forgery-via-unverified-signature bug.

Note: this analysis could not fully verify the pallet-ismp implementation of `store_request_receipt` in `modules/pallets/ismp/src/host.rs` (only its trait signature was retrievable), which would show the exact stored byte layout; the conclusion rests on the trait contract, the fee/incentive pallets that *do* call `.verify()`, and the `decode_receipt_relayer` function that conspicuously calls only `.signer()`.

### Likelihood Explanation
High-likelihood reachability: `handle_unsigned` is explicitly designed to be callable by anyone with valid proofs [10](#0-9) , and the `signer` field is fully attacker-controlled at message-construction time — no wallet signature over the actual delivery is enforced before the value is used for fee accounting. The gap is real: the same crate provides a correctly-verifying primitive (`Signature::verify`/`verify_and_get_sr25519_pubkey`) that other fee-sensitive code paths use, but `decode_receipt_relayer` — which drives cross-chain relayer fee payout — uses the non-verifying `.signer()` accessor instead.

### Recommendation
In `decode_receipt_relayer` (`modules/pallets/relayer/src/accumulate.rs`), replace the unauthenticated `Signature::decode(...).signer()` call with a genuine verification: recover the signer from `Signature::verify()`/`verify_and_get_sr25519_pubkey()` against the actual message that was delivered (e.g., the request/response commitment or `msg.requests.encode()` hash), matching the pattern already used in `fee_handler.rs` and `messaging-incentives`. Alternatively, if the destination chain's own `store_request_receipt`/`store_response_receipt` already verifies the signer before storing, ensure that verified, not raw, bytes are what gets proven and consumed cross-chain, and add an explicit invariant/test asserting that a garbage `signer` field cannot earn relayer-fee credit.

### Proof of Concept
1. Attacker crafts a valid ISMP `RequestMessage`/`ResponseMessage` (with real membership proof) and submits it via `pallet_ismp::handle_unsigned` (unsigned, permissionless) with `signer = Signature::Sr25519 { public_key: <attacker_or_victim_bytes>, signature: <random_garbage> }.encode()` — mirroring the exact construction already used in the test fixture at `parachain/simtests/src/pallet_ismp.rs:276-289` [8](#0-7) .
2. `handlers/request.rs` stores this unverified `signer` value as the request receipt's relayer field with no cryptographic check [3](#0-2) .
3. On the source chain, `accumulate_fees` proves `RequestReceipts[commitment]` via storage proof and calls `decode_receipt_relayer`, which for substrate destinations decodes the bytes as `Signature` and calls `.signer()` — returning the attacker's chosen `public_key` without ever validating the "signature" [4](#0-3) .
4. The relayer fee for that request is credited to the attacker-controlled account instead of the legitimate relayer/service that actually delivered the message.

### Citations

**File:** modules/ismp/core/src/host.rs (L163-171)
```rust
	/// Stores a receipt for an incoming request after it is successfully routed to a module.
	/// Prevents duplicate incoming requests from being processed. Includes the relayer account
	fn store_request_receipt(&self, req: &Request, signer: &Vec<u8>) -> Result<Vec<u8>, Error>;

	/// Stores a receipt that shows that the given request has received a response. Includes the
	/// relayer account
	/// Implementors should map the request commitment to the response object commitment.
	fn store_response_receipt(&self, req: &GetResponse, signer: &Vec<u8>)
		-> Result<Vec<u8>, Error>;
```

**File:** modules/pallets/ismp/src/lib.rs (L360-367)
```rust
		/// Execute the provided batch of ISMP messages, this will short-circuit and revert if any
		/// of the provided messages are invalid. This is an unsigned extrinsic that permits anyone
		/// execute ISMP messages for free, provided they have valid proofs and the messages have
		/// not been previously processed.
		///
		/// The dispatch origin for this call must be an unsigned one.
		///
		/// - `messages`: the messages to handle or process.
```

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/ismp/core/src/handlers/request.rs (L108-120)
```rust
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
				// Store request receipt to prevent reentrancy attack
				let signer = host.store_request_receipt(&wrapped_req, &msg.signer)?;
				let res = cb.on_accept(request.clone()).map(|weight| {
					total_weights.saturating_accrue(weight);

					let commitment = hash_request::<H>(&wrapped_req);
					Event::PostRequestHandled(RequestResponseHandled {
						commitment,
						relayer: signer,
					})
```

**File:** modules/pallets/relayer/src/accumulate.rs (L303-351)
```rust
}

/// Signed payload authorising a beneficiary redirect on a specific source chain.
/// Including the relayer nonce alongside the state machine keeps the signature usable for
/// exactly one accumulate call on that chain, mirroring how `withdraw_fees` binds its signed
/// payload.
pub fn beneficiary_message(
	nonce: u64,
	state_machine: StateMachine,
	beneficiary: &[u8],
) -> [u8; 32] {
	sp_io::hashing::keccak_256(&(nonce, state_machine, beneficiary).encode())
}

impl<T: Config> Pallet<T> {
	/// Decode a proven `RequestReceipts[commitment]` value into the delivering
	/// relayer's bytes. EVM stores the address RLP encoded, substrate stores the
	/// signer bytes or a signature to recover the signer from. Used by both fee
	/// accumulation and the outbound request delivery claim.
	pub fn decode_receipt_relayer(state_id: StateMachine, raw: &[u8]) -> Result<Vec<u8>, Error<T>> {
		match state_id {
			s if crate::is_pharos(&s) =>
				if raw.len() == 32 {
					Ok(Address::from_slice(&raw[12..]).0.to_vec())
				} else {
					Err(Error::<T>::ProofValidationError)
				},
			s if s.is_evm() => {
				use alloy_rlp::Decodable;
				Ok(Address::decode(&mut &*raw)
					.map_err(|_| Error::<T>::ProofValidationError)?
					.0
					.to_vec())
			},
			s if s.is_substrate() => {
				use codec::Decode;
				let bytes =
					<Vec<u8>>::decode(&mut &*raw).map_err(|_| Error::<T>::ProofValidationError)?;
				Ok(if bytes.len() > 32 {
					Signature::decode(&mut &*bytes)
						.map_err(|_| Error::<T>::SignatureDecodingError)?
						.signer()
				} else {
					bytes
				})
			},
			_ => Err(Error::<T>::MismatchedStateMachine),
		}
	}
```

**File:** modules/utils/crypto/src/verification.rs (L109-115)
```rust
	pub fn signer(&self) -> Vec<u8> {
		match self {
			Signature::Evm { address, .. } => address.clone(),
			Signature::Sr25519 { public_key, .. } => public_key.clone(),
			Signature::Ed25519 { public_key, .. } => public_key.clone(),
		}
	}
```

**File:** modules/pallets/ismp/src/fee_handler.rs (L187-201)
```rust
			let originator = match message.message.clone() {
				Message::Request(msg) => {
					let data = sp_io::hashing::keccak_256(&msg.requests.encode());
					Signature::decode(&mut &msg.signer[..])
						.ok()
						.and_then(|sig| sig.verify_and_get_sr25519_pubkey(&data, None).ok())
				},
				Message::Response(msg) => {
					let data = sp_io::hashing::keccak_256(&msg.requests.encode());
					Signature::decode(&mut &msg.signer[..])
						.ok()
						.and_then(|sig| sig.verify_and_get_sr25519_pubkey(&data, None).ok())
				},
				_ => None,
			};
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

**File:** parachain/simtests/src/pallet_ismp.rs (L276-289)
```rust
	let signature = Signature::Sr25519 {
		public_key: H256::random().as_bytes().to_vec(),
		signature: H256::random().as_bytes().to_vec(),
	};

	// 3. next send the requests
	let tx = subxt::dynamic::tx(
		"Ismp",
		"handle_unsigned",
		vec![messages_to_value(vec![Message::Request(RequestMessage {
			requests: vec![post.clone().into()],
			proof: proof.clone(),
			signer: signature.encode(),
		})])],
```
