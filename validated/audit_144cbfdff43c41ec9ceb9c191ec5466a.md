### Title
Unverified `Signature::signer()` accessor lets a relayer forge the substrate delivery-receipt identity, permanently misdirecting or freezing relayer fee accumulation - (File: `modules/utils/crypto/src/verification.rs`)

### Summary
`Signature::signer()` returns the caller-declared `address` field for the `Evm` variant without ever running a cryptographic check, while `Signature::verify()` on the very same type actually recovers the signer from the ECDSA signature. `modules/pallets/relayer/src/accumulate.rs::decode_receipt_relayer` uses the unauthenticated `signer()` accessor to interpret a substrate destination's `RequestReceipts` value as the delivering relayer's identity. Because the raw receipt bytes are supplied by whoever submits the (permissionless, unsigned) `handle_unsigned` delivery extrinsic, an attacker can embed an arbitrary, unverified `Evm{address, signature}` blob as the "signer" and have it accepted as the delivering party's identity — an authentication-method confusion identical in class to the CodeChecker advisory: one identity-assertion path is cryptographically checked, a second path on the same credential type is not, and downstream code trusts the unchecked one.

### Finding Description
`modules/utils/crypto/src/verification.rs`:
```rust
pub fn signer(&self) -> Vec<u8> {
    match self {
        Signature::Evm { address, .. } => address.clone(),
        Signature::Sr25519 { public_key, .. } => public_key.clone(),
        Signature::Ed25519 { public_key, .. } => public_key.clone(),
    }
}
``` [1](#0-0) 

For `Sr25519`/`Ed25519`, "signer" is the public key itself, which is at least tied to the signature check performed elsewhere in `verify()`. But for `Evm`, `signer()` returns the caller-supplied `address` field directly — `verify()` (the only place that actually calls `secp256k1_ecdsa_recover`) computes the real signer independently and never cross-checks it against `address`: [2](#0-1) 

`decode_receipt_relayer` in the relayer pallet decodes a proven substrate `RequestReceipts[commitment]` value and, when the stored bytes are longer than 32 bytes, treats them as a `Signature` and calls the unauthenticated `.signer()`:
```rust
s if s.is_substrate() => {
    let bytes = <Vec<u8>>::decode(&mut &*raw)...?;
    Ok(if bytes.len() > 32 {
        Signature::decode(&mut &*bytes)...?.signer()
    } else {
        bytes
    })
},
``` [3](#0-2) 

This means whichever bytes were written into `RequestReceipts[commitment]` at message-handling time are trusted as-is if they decode as `Signature::Evm`, with the `address` field taken at face value — no ECDSA recovery, no binding to any signature. Delivery itself is permissionless: `pallet_ismp::handle_unsigned` is `ensure_none` and accepts any batch of ISMP messages with valid state/consensus proofs, and a live test in the repo shows the message's `signer` field is arbitrary submitter-chosen bytes (random, unrelated to any real key) at handling time: [4](#0-3) [5](#0-4) 

`decode_receipt_relayer`'s output is then used as the trusted "delivering relayer" identity in two fund-moving paths:

1. Fee accumulation credits the fee directly to this decoded address when no beneficiary redirect is supplied: [6](#0-5) 
and the per-request result map is keyed by it in `validate_results`: [7](#0-6) 

2. The outbound-request delivery reward claim compares a cryptographically-recovered `recovered` value against this same unverified `delivered_by`: [8](#0-7) 

In both cases, the relayer that submits the substrate-destination delivery message fully controls the "signer" bytes written into the receipt, and can freely choose an `Evm{address: X, signature: <any 65 bytes>}` encoding — `signer()` returns `X` unconditionally.

### Impact Explanation
Any account that permissionlessly relays a message to a substrate destination (`handle_unsigned` requires no signed origin) can write an attacker-chosen "delivering relayer" identity into `RequestReceipts[commitment]`. This value later determines who `accumulate()` credits with the relayer fee for that commitment. By choosing an address nobody controls (or one the attacker cannot itself have signed for), fees that should have gone to the actual delivering relayer are credited to an unreachable/arbitrary account inside `Fees::<T>`, which is a permanent freezing of those relayer funds (no path back to the true relayer). Conversely, since the value is entirely self-declared and not tied to any real signature, the mechanism also breaks the intended guarantee that a claimed "signer"/relayer identity corresponds to a real key — the same authentication-method-confusion class as the external advisory (one path verifies, a second untrusted path is accepted as equivalent proof of identity). This is reachable by an unprivileged relayer submitting a single unsigned extrinsic, matching the required "relayer fee and reward accounting" attack surface.

### Likelihood Explanation
High reachability: `pallet_ismp::handle_unsigned` is open to anyone with a valid delivery proof, and the `signer` field of a `RequestMessage` is not independently authenticated against the actual delivering account at write time (demonstrated by the repository's own test using random, unrelated signature bytes). The only additional step needed is choosing bytes that decode as `Signature::Evm` with the desired `address`, which `Signature`'s SCALE encoding trivially allows. No consensus, state-proof, or cryptographic secret is required to control the resulting "signer" value.

### Recommendation
Remove the `Evm` arm's blind trust in `signer()`, or forbid the accessor from being used as an identity assertion at all. `decode_receipt_relayer` must cryptographically recover the address (via `Signature::verify` against whatever message the relayer's submission was supposed to attest to) rather than reading a self-declared `address` field. If no signed message exists to verify at receipt-write time, the write path should reject `Signature::Evm` receipts with untied signatures, or store the recovered address (computed once, from a real signature) instead of the raw attacker-supplied structure.

### Proof of Concept
1. Attacker (any account, no special privileges) prepares a valid ISMP `Message::Request` batch destined for a substrate chain, with a legitimate state/consensus proof for delivery, but sets the request's `signer` field to `Signature::Evm { address: <attacker-or-arbitrary-address>, signature: vec![0u8; 65] }` (an arbitrary 65-byte blob; `verify()` is never called on this value at write time, as shown by the existing test using random garbage successfully accepted via `handle_unsigned`) — [9](#0-8) .
2. Submits `Ismp::handle_unsigned` with this message; it is processed with `ensure_none` origin and the receipt is written to `RequestReceipts[commitment]` on the destination — [5](#0-4) .
3. Later, when `Pallet::accumulate` proves this receipt and calls `decode_receipt_relayer`, the substrate branch decodes the stored bytes as `Signature::Evm` and calls `.signer()`, returning the attacker-chosen `address` unchanged — [3](#0-2) .
4. `accumulate()` credits the relayer fee to this attacker-chosen `delivery_address` (no beneficiary redirect required) — [6](#0-5) , permanently misdirecting the fee to an address of the attacker's choosing that need not correspond to any key the true relayer (or anyone) controls.

### Citations

**File:** modules/utils/crypto/src/verification.rs (L40-52)
```rust
		match self {
			Signature::Evm { signature, .. } => {
				if signature.len() != 65 {
					Err(anyhow!("Invalid Signature"))?
				}

				let mut sig = [0u8; 65];
				sig.copy_from_slice(&signature);
				let pub_key = sp_io::crypto::secp256k1_ecdsa_recover(&sig, msg)
					.map_err(|_| anyhow!("Signature Verification failed"))?;
				let signer = sp_io::hashing::keccak_256(&pub_key[..])[12..].to_vec();
				Ok(signer)
			},
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

**File:** modules/pallets/relayer/src/accumulate.rs (L139-147)
```rust
			beneficiary_address
		} else {
			let _ = Fees::<T>::try_mutate(state_machine, delivery_address.clone(), |inner| {
				*inner += total_fee;
				Ok::<(), ()>(())
			});

			delivery_address
		};
```

**File:** modules/pallets/relayer/src/accumulate.rs (L292-298)
```rust
			let address = Self::decode_receipt_relayer(
				proof.dest_proof.height.id.state_id,
				&encoded_receipt,
			)?;
			let entry = result.entry(address).or_insert(U256::zero());
			*entry += fee;
			commitments.push(commitment);
```

**File:** modules/pallets/relayer/src/accumulate.rs (L337-348)
```rust
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
```

**File:** parachain/simtests/src/pallet_ismp.rs (L270-293)
```rust
	let update_time: u64 = Decode::decode(&mut &*item)?;
	assert_eq!(now.as_secs(), update_time);

	let proof = StateMachineProof { hasher: HashAlgorithm::Keccak, storage_proof: proof }.encode();
	let proof = Proof { height, proof };

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
	);

	// send once
	let progress = client.tx().create_unsigned(&tx)?.submit_and_watch().await?;
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

**File:** modules/pallets/relayer/src/outbound_request.rs (L169-173)
```rust
		let delivered_by = Self::decode_receipt_relayer(destination, &raw)?;

		let msg = outbound_request_delivery_message(commitment, destination, payee);
		let recovered = signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
		ensure!(recovered == delivered_by, Error::<T>::OutboundRequestSignerMismatch);
```
