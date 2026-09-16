Now I found the concrete analog. Both `outbound_request_delivery_message` and `outbound_consensus_delivery_message` produce a raw 32-byte hash that is signed directly via `dest.sign(&msg)` (no domain-separation prefix such as a fixed protocol tag) and verified via `Signature::verify(&self, msg: &[u8; 32], ...)` in `modules/utils/crypto/src/verification.rs`, which for the EVM variant does a raw `secp256k1_ecdsa_recover` over the bare 32-byte digest — exactly the "sign(hash)" pattern the report flags as dangerous, with no EIP-191/text prefix and no leading domain-separator constant distinguishing one claim type's digest space from another's.

### Title
Raw, un-domain-separated hash signing in outbound reward claims enables cross-claim-type signature confusion - ([File: modules/pallets/relayer/src/outbound_request.rs], [File: modules/pallets/relayer/src/accumulate.rs], [File: modules/utils/crypto/src/verification.rs])

### Summary
`pallet-ismp-relayer` verifies two independent reward-claim types — outbound request delivery and outbound consensus delivery — by recovering a signer from a bare 32-byte keccak digest with no protocol/claim-type domain tag, mirroring the audited weakness where `signText`/`signOperation` sign raw hashes without a prefix that would prevent one signed artifact from being valid in a different context.

### Finding Description
`outbound_request_delivery_message(commitment, dest_chain, payee)` computes `keccak_256(&(commitment, dest_chain, payee).encode())` [1](#0-0) , and the relayer signs this exact digest directly with the destination chain key via `dest.sign(&msg)` [2](#0-1) . On-chain, `signature.verify(&msg, None)` recovers the signer straight from this bare digest and compares it to the relayer address proven in the destination receipt [3](#0-2) .

The sibling `outbound_consensus_delivery_message(set_id, destination, payee)` claim uses the identical pattern: build a message tuple, hash it, and sign the raw digest with `dest.sign(&msg)` [4](#0-3) .

The shared `Signature::verify` primitive recovers a signer purely from whatever 32-byte value it is handed, with no context byte, tag, or fixed prefix baked into the digest computation itself — for the EVM variant it calls `sp_io::crypto::secp256k1_ecdsa_recover(&sig, msg)` directly on the raw digest, exactly like the `signTextHash`/`signOperation` pattern the external report calls out as a "sign(blake_hash(data,32))" risk with no protection against confusable payloads [5](#0-4) .

Because `dest.sign()` is a generic signing primitive on the `IsmpProvider`/chain-key abstraction (used across many call sites: `tesseract/messaging/substrate/src/provider.rs`, `tesseract/messaging/tron/src/provider.rs`, `tesseract/messaging/evm/src/provider.rs`, etc.), the same relayer signing key that authorizes `OutboundRequestDeliveryClaim` messages is the same key used elsewhere to sign other raw digests for delivery/claim flows. None of these digests carry a distinguishing domain tag (e.g., `b"HB-OUTBOUND-REQUEST-CLAIM"` or similar) comparable to the "prefix the data with a constant string longer than the hash length" mitigation the report recommends. If any two claim/message schemas that this key signs ever happen to SCALE-encode to colliding byte sequences (e.g., through type ambiguity between `(H256, StateMachine, [u8;32])` used for request claims and `(u64, StateMachine, [u8;32])` used for consensus claims, or future claim types added to the same pallet), a signature produced for one context would verify for the other, since the verification function is context-blind and only checks digest equality plus signer identity.

### Impact Explanation
If a domain-confusable digest collision or a new claim type reusing the same tuple shape is ever introduced, an attacker (or a relayer acting maliciously, or a message dispatcher able to influence encoded fields) could take a signature legitimately produced for one claim (e.g., a consensus delivery reward) and resubmit it to satisfy a different claim's signer check, since the raw-hash verification pipeline provides no cryptographic separation between claim types beyond the specific tuple contents that happen not to collide today. This directly targets the relayer-fee/reward accounting path reachable by any relayer submitting a `claim_outbound_request_delivery_reward`/`claim_outbound_consensus_delivery_reward` extrinsic, and a successful confusion would let a party siphon treasury-funded rewards (`OutboundRequestRewardTransferFailed`/`OutboundRequestDeliveryRewarded` path) without having performed the corresponding delivery, i.e., theft of funds from the treasury account.

### Likelihood Explanation
Today the fields differ in type (`H256` vs `u64` in the first tuple slot) and SCALE encoding of distinct types generally does not produce identical byte sequences for typical value ranges, so an immediate practical collision is not demonstrated here — this significantly limits real-world exploitability absent a future schema change or an as-yet-unfound low-entropy collision. However, the design itself is fragile exactly the way the report warns: nothing in the digest computation or `Signature::verify` enforces domain separation, so any future extension of pallet-relayer's claim types that reuses `keccak_256(&(...).encode())` on similarly-shaped tuples reintroduces the exact "blind hash signing" risk, and there is no defense-in-depth to catch it.

### Recommendation
Prefix every claim message digest with a fixed, claim-type-specific domain separator before hashing (e.g., `keccak_256(&(b"HB-OUTBOUND-REQUEST-CLAIM", commitment, dest_chain, payee).encode())` and a distinct constant for the consensus-claim variant), and make `Signature::verify` / the message-builder functions require an explicit domain tag parameter so future claim types cannot omit it. This mirrors the report's recommendation to prefix signed data with a constant string that rules out cross-context reuse, applied to `outbound_request_delivery_message` in `modules/pallets/relayer/src/outbound_request.rs` and `outbound_consensus_delivery_message` in `modules/pallets/relayer/src/accumulate.rs`.

### Proof of Concept
Not independently reproducible from the indexed source alone: exploitation requires either (a) a future/added claim type in pallet-ismp-relayer whose tuple SCALE-encodes to the same bytes as an existing claim type for some payee/commitment/set_id combination, or (b) discovery of an encoding collision between the two existing tuple shapes. The concrete, verifiable root cause — raw-digest signing with no domain separator, shared across `outbound_request_delivery_message`, `outbound_consensus_delivery_message`, and the generic `Signature::verify` — is demonstrated at the cited lines; a full end-to-end forged-claim PoC would require constructing/confirming such a collision, which was not found within the indexed content and should be validated by a background engineer with codebase-wide search/build access (e.g., enumerating all `keccak_256(&(...).encode())` claim-message constructors in `modules/pallets/relayer/` to check for shared tuple shapes across claim types).

### Citations

**File:** modules/pallets/relayer/src/outbound_request.rs (L146-153)
```rust
			.try_into()
			.map_err(|_| Error::<T>::OutboundRequestModuleIdTooLong)?;
		let reward = OutboundRequestDeliveryReward::<T>::get(&module_id);
		ensure!(reward > BalanceOf::<T>::default(), Error::<T>::OutboundRequestNoRewardConfigured);

		ensure!(destination == request.dest, Error::<T>::MismatchedStateMachine);

		let state_machine = ismp::handlers::validate_state_machine(&host, state_proof.height)
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L169-173)
```rust
		let delivered_by = Self::decode_receipt_relayer(destination, &raw)?;

		let msg = outbound_request_delivery_message(commitment, destination, payee);
		let recovered = signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
		ensure!(recovered == delivered_by, Error::<T>::OutboundRequestSignerMismatch);
```

**File:** tesseract/messaging/messaging/src/outbound_request_claim.rs (L271-283)
```rust

	let msg = outbound_request_delivery_message(commitment, destination, payee);
	let signature = dest.sign(&msg);

	let claim = OutboundRequestDeliveryClaim {
		request: pending.request.clone(),
		state_proof: Proof {
			height: StateMachineHeight { id: dest.state_machine_id(), height: dest_height },
			proof: proof_bytes,
		},
		payee,
		signature,
	};
```

**File:** tesseract/messaging/messaging/src/outbound_claim.rs (L347-356)
```rust
	let msg = outbound_consensus_delivery_message(pending.set_id, pending.destination, payee);
	let claim = OutboundConsensusDeliveryClaim {
		state_proof: Proof {
			height: StateMachineHeight { id: dest.state_machine_id(), height: dest_height },
			proof: proof_bytes,
		},
		set_id: pending.set_id,
		payee,
		signature: dest.sign(&msg),
	};
```

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
