### Title
Unverified `signer` field lets any relayer forge request/response delivery attribution in `RequestReceipts` - ([File: modules/pallets/ismp/src/host.rs])

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic is permissionless and unsigned, so the only on-chain record of "who delivered this message" is the `signer` byte-blob carried inside the `Message` itself. That blob is expected to be a cryptographic `Signature` (as used elsewhere in the codebase for fee-charging and reward attribution), but the function that turns it into a stored relayer identity, `extract_signer`, never calls `Signature::verify()` — it only calls `Signature::signer()`, which unconditionally returns the embedded `public_key`/`address` field regardless of whether the accompanying `signature` bytes are valid. This is the same class of bug as the n8n advisory: a value that looks like an authenticated credential (a signature) is stored/consumed as if it had been verified, when it was not.

### Finding Description
`modules/pallets/ismp/src/host.rs`:
```rust
fn extract_signer(signer: &[u8]) -> Result<Vec<u8>, Error> {
	if signer.len() > 32 {
		Signature::decode(&mut signer.as_ref())
			.map(|sig| sig.signer())        // <-- no .verify()
			.map_err(|_| Error::SignatureDecodingFailed)
	} else {
		Ok(signer.to_vec())
	}
}
``` [1](#0-0) 

`Signature::signer()` simply returns the enum's stored public key/address field; it performs no ECDSA/Ed25519/Sr25519 recovery or check against any message, unlike `Signature::verify()`/`verify_and_get_sr25519_pubkey()`: [2](#0-1) 

`extract_signer` is invoked by `store_request_receipt`/`store_response_receipt`, the `IsmpHost` methods documented as recording "the account of the responsible relayer": [3](#0-2) 

These are called from the core ISMP request/response handlers with the raw, attacker-controlled `msg.signer` field of an incoming `Message`, dispatched via the permissionless unsigned `handle_unsigned` call: [4](#0-3) [5](#0-4) 

The documentation explicitly states this receipt is later trusted as the proof of who delivered a message and is used to accumulate relayer fees:


and `pallet-ismp-relayer`'s `decode_receipt_relayer`, used by both `accumulate_fees` and the outbound-request-delivery-reward claim, reads that same receipt value back and — for the substrate branch — again only calls `.signer()` on the decoded `Signature`, never `.verify()`: [6](#0-5) 

So on the write path (`extract_signer`) and the read path (`decode_receipt_relayer`) the "signer" is treated as an authenticated identity, but neither step ever checks that the `signature` bytes are a valid signature produced by the claimed `public_key`/`address` over anything. This differs sharply from the EVM side, where the relayer identity is `msg.sender` (`_msgSender()`), a value the EVM itself cryptographically guarantees: [7](#0-6) 

By contrast, on the substrate side the entire binding of "delivery credit" to an identity rests on an unauthenticated byte blob.

Some downstream consumers do add their own independent signature check before moving funds (e.g. `WeightFeeHandler::on_executed` verifies via `verify_and_get_sr25519_pubkey`, and `process_outbound_request_delivery_claim` separately verifies a `signature.verify(...)` over the claim payload before paying a reward): [8](#0-7) [9](#0-8) 

But `RequestReceipts`/`ResponseReceipts` themselves — the canonical, protocol-documented "who delivered this" record used across the messaging-incentives and relayer-fee subsystems — are populated and later re-decoded with no cryptographic verification whatsoever.

### Impact Explanation
Any party submitting `handle_unsigned` messages (the permissionless, unsigned entry point every relayer uses) can set the `signer` field of a `RequestMessage`/`ResponseMessage` to `Signature::{Sr25519,Ed25519,Evm}{ public_key: <arbitrary account>, signature: <garbage> }`. Because `extract_signer`/`decode_receipt_relayer` never verify the signature, the on-chain `RequestReceipts`/`ResponseReceipts` will record an arbitrary chosen account as "the relayer that delivered this message" even though that account never produced any valid signature and may not even control the corresponding key. This breaks the integrity guarantee the protocol's own documentation asserts for this storage item ("alongside the account of the responsible relayer"), which downstream reward/incentive logic (`accumulate_fees`, messaging-incentives, and any future consumer that trusts the receipt without its own independent check) relies on for correct attribution. This is a forged-identity/authentication-bypass condition of the exact class described in the report (CWE-290): a value is accepted and persisted as an authenticated credential without verification.

### Likelihood Explanation
High likelihood of triggering: `handle_unsigned` is the standard, permissionless, unsigned path every relayer already uses to deliver ordinary requests/responses; forging the `signer` field costs nothing extra (no valid signature, no private key needed) and requires no special privilege — only a syntactically well-formed `Signature` enum value.

### Recommendation
`extract_signer` must call `Signature::verify()` against a well-defined message (e.g. the same digest used elsewhere, `keccak_256(&requests.encode())`) and only fall back to trusting the embedded identity once verification succeeds; if verification fails, either reject the message or store no relayer attribution rather than an unverified one. `decode_receipt_relayer`'s substrate branch should likewise require a proven signature rather than trusting `.signer()` alone. Any consumer of `RequestReceipts`/`ResponseReceipts` that treats the stored value as a proven identity should be reviewed to ensure the receipt itself is trustworthy, not just re-verified ad hoc at each call site.

### Proof of Concept
1. Attacker (or any relayer) builds a `PostRequest`/`RequestMessage` with a valid state-membership proof (a normal, legitimately delivered message).
2. Sets `signer = Signature::Sr25519 { public_key: <victim_or_arbitrary_pubkey>, signature: vec![0u8; 64] }.encode()` — an intentionally invalid signature.
3. Submits via `Ismp::handle_unsigned([Message::Request(msg)])` (unsigned, permissionless).
4. `execute` → `handlers::request` calls `host.store_request_receipt(&wrapped_req, &msg.signer)` → `extract_signer` decodes the `Signature` and returns `<victim_or_arbitrary_pubkey>` without ever checking the (invalid) signature bytes — as shown in `modules/pallets/ismp/src/host.rs:351-359`.
5. `RequestReceipts[commitment]` now records `<victim_or_arbitrary_pubkey>` as "the relayer that delivered this request," even though no valid signature by that key was ever produced — an unverifiable, forged delivery attribution that downstream relayer-fee/incentive logic (`decode_receipt_relayer` in `modules/pallets/relayer/src/accumulate.rs:317-351`) will subsequently re-decode the same way, with no additional cryptographic check.

### Citations

**File:** modules/pallets/ismp/src/host.rs (L261-283)
```rust
	fn store_request_receipt(&self, req: &Request, signer: &Vec<u8>) -> Result<Vec<u8>, Error> {
		let signer = extract_signer(signer)?;

		let hash = hash_request::<Self>(req);
		child_trie::RequestReceipts::<T>::insert(hash, &signer);
		Ok(signer)
	}

	fn store_response_receipt(
		&self,
		res: &GetResponse,
		signer: &Vec<u8>,
	) -> Result<Vec<u8>, Error> {
		let signer = extract_signer(signer)?;

		let hash = hash_request::<Self>(&res.request());
		let response = hash_response::<Self>(&res);
		child_trie::ResponseReceipts::<T>::insert(
			hash,
			ResponseReceipt { response, relayer: signer.clone() },
		);
		Ok(signer)
	}
```

**File:** modules/pallets/ismp/src/host.rs (L351-359)
```rust
fn extract_signer(signer: &[u8]) -> Result<Vec<u8>, Error> {
	if signer.len() > 32 {
		Signature::decode(&mut signer.as_ref())
			.map(|sig| sig.signer())
			.map_err(|_| Error::SignatureDecodingFailed)
	} else {
		Ok(signer.to_vec())
	}
}
```

**File:** modules/utils/crypto/src/verification.rs (L97-115)
```rust
	pub fn verify_and_get_sr25519_pubkey(
		&self,
		msg: &[u8; 32],
		public_key_op: Option<Vec<u8>>,
	) -> Result<[u8; 32], anyhow::Error> {
		match self {
			Signature::Sr25519 { public_key, signature } =>
				Self::verify_sr25519(signature, public_key, msg, &public_key_op),
			_ => Err(anyhow!("Signature is not of type Sr25519")),
		}
	}

	pub fn signer(&self) -> Vec<u8> {
		match self {
			Signature::Evm { address, .. } => address.clone(),
			Signature::Sr25519 { public_key, .. } => public_key.clone(),
			Signature::Ed25519 { public_key, .. } => public_key.clone(),
		}
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

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L317-351)
```rust
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

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```

**File:** modules/pallets/ismp/src/fee_handler.rs (L186-199)
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
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L169-173)
```rust
		let delivered_by = Self::decode_receipt_relayer(destination, &raw)?;

		let msg = outbound_request_delivery_message(commitment, destination, payee);
		let recovered = signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
		ensure!(recovered == delivered_by, Error::<T>::OutboundRequestSignerMismatch);
```
