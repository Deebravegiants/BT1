### Title
Single Malicious Participant Can Resolve Pending `verify_foreign_transaction` Requests with Mismatched Payload Hash — (File: crates/contract/src/lib.rs)

---

### Summary

The `respond_verify_foreign_tx` function in the MPC contract verifies that a submitted signature is cryptographically valid for the provided `payload_hash`, but does **not** verify that `payload_hash` is actually the hash of `(request, extracted_values)` for the specific pending `request`. A single malicious attested participant (below threshold) can replay a valid `(payload_hash, signature)` pair observed from a previous on-chain call and use it to resolve a completely different pending `verify_foreign_transaction` request, delivering forged foreign-chain verification data to downstream bridge contracts.

---

### Finding Description

In `respond_verify_foreign_tx` at `crates/contract/src/lib.rs`, the contract performs three checks:

1. The caller is an attested participant.
2. `response.signature` is a valid ECDSA signature over `response.payload_hash` under the domain's root public key.
3. `request` exists in `pending_verify_foreign_tx_requests`. [1](#0-0) 

What is **absent** is any check that `response.payload_hash` is the hash of `ForeignTxSignPayloadV1 { request: <the submitted request>, values: <...> }`. The signed payload is defined as: [2](#0-1) 

The hash commits to both the `ForeignChainRpcRequest` and the `ExtractedValue` list. However, the contract's `respond_verify_foreign_tx` never reconstructs or checks this binding — it only checks that the signature is valid for *whatever* `payload_hash` the caller supplies.

Because threshold ECDSA signatures produced by the MPC network are standard ECDSA signatures over a 32-byte hash, they are publicly verifiable and replayable by anyone who observes them on-chain. The `build_signature_request` function in the node confirms that the signed message is purely `payload_hash` with no request-specific nonce embedded in the signed bytes: [3](#0-2) 

---

### Impact Explanation

A single malicious attested participant (strictly below the signing threshold) can:

1. Observe a valid `respond_verify_foreign_tx(request_A, {payload_hash_A, sig_A})` call on-chain.
2. Submit `respond_verify_foreign_tx(request_B, {payload_hash_A, sig_A})` for a different pending `request_B`.

The contract accepts this because `sig_A` is a valid root-key signature for `payload_hash_A`, and `request_B` is pending. All callers waiting for `request_B` receive `{payload_hash_A, sig_A}` as their response.

- **If the downstream bridge contract uses `ForeignChainSignatureVerifier::verify_signature` from the SDK**, it will detect `expected_payload_hash ≠ response.payload_hash` and reject — the impact is request-lifecycle corruption (the pending slot is consumed, the user must resubmit). [4](#0-3) 

- **If the downstream bridge contract does not perform this check** (e.g., only verifies the ECDSA signature is valid under the root key), it will accept a signature that attests to the foreign-chain state of `request_A` while believing it attests to `request_B`. This enables forged foreign-chain verification — for example, a bridge could be made to release funds on NEAR based on a Bitcoin transaction confirmation that was actually for a different, unrelated transaction.

---

### Likelihood Explanation

**Medium.** The attack requires only a single compromised or malicious attested participant — well below the signing threshold. The attacker needs no cryptographic capability beyond observing the NEAR blockchain: valid `(payload_hash, signature)` pairs from prior `respond_verify_foreign_tx` calls are permanently visible in transaction history. Any pending `verify_foreign_transaction` request is a valid target. The attack is cheap, requires no special timing, and can be executed repeatedly.

---

### Recommendation

In `respond_verify_foreign_tx`, bind the accepted `payload_hash` to the submitted `request`. Two options:

1. **Require the response to include the extracted values**: change `VerifyForeignTransactionResponse` to include `values: Vec<ExtractedValue>`, then have the contract recompute `expected_hash = SHA-256(borsh(ForeignTxSignPayloadV1 { request, values }))` and assert `expected_hash == response.payload_hash` before accepting.

2. **Embed the request hash in the signed payload**: change `ForeignTxSignPayloadV1` to include a commitment to the on-chain request key (e.g., `request_id` or `borsh_hash(request)`), so a signature produced for `request_A` is cryptographically invalid for `request_B` even if the extracted values happen to be the same.

Option 1 is simpler and consistent with the existing design; option 2 provides stronger domain separation.

---

### Proof of Concept

```
1. Alice submits verify_foreign_transaction(request_A)
   request_A = { tx_id: [0xAA; 32], confirmations: 6, extractors: [BlockHash] }

2. Bob submits verify_foreign_transaction(request_B)
   request_B = { tx_id: [0xBB; 32], confirmations: 6, extractors: [BlockHash] }

3. Honest MPC nodes process request_A:
   values_A = [BlockHash([0x11; 32])]
   payload_hash_A = SHA-256(borsh(ForeignTxSignPayloadV1 { request_A, values_A }))
   sig_A = threshold_sign(payload_hash_A)

4. Honest participant submits:
   respond_verify_foreign_tx(request_A, { payload_hash_A, sig_A })
   → accepted; Alice receives { payload_hash_A, sig_A }

5. Malicious participant (single, below threshold) observes step 4 on-chain and submits:
   respond_verify_foreign_tx(request_B, { payload_hash_A, sig_A })

   Contract checks:
   ✓ caller is attested participant
   ✓ verify_ecdsa_signature(sig_A, payload_hash_A, root_pk) == Ok
   ✓ request_B exists in pending_verify_foreign_tx_requests
   ✗ payload_hash_A == hash(request_B, some_values)  ← NOT CHECKED
   → accepted; Bob receives { payload_hash_A, sig_A }

6. Bob's bridge contract receives { payload_hash_A, sig_A }.
   If it only checks signature validity (not payload binding):
   verify_ecdsa_signature(sig_A, payload_hash_A, root_pk) == Ok
   → bridge processes action as if tx_B was verified, using attestation data for tx_A.
```

### Citations

**File:** crates/contract/src/lib.rs (L718-747)
```rust
        let signature_is_valid = match (&response.signature, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");

                let payload_hash: [u8; 32] = response.payload_hash.0;

                // Check the signature is correct against the root public key
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    &payload_hash,
                    &secp_pk,
                )
                .is_ok()
            }
            (signature_response, public_key_requested) => {
                return Err(RespondError::SignatureSchemeMismatch {
                    mpc_scheme: Box::new(signature_response.clone()),
                    user_scheme: Box::new(public_key_requested),
                }
                .into());
            }
        };

        if !signature_is_valid {
            return Err(RespondError::InvalidSignature.into());
        }
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1509)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}

impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-48)
```rust
fn build_signature_request(
    request: &VerifyForeignTxRequest,
    foreign_tx_payload: &dtos::ForeignTxSignPayload,
) -> anyhow::Result<SignatureRequest> {
    let payload_hash: [u8; ECDSA_PAYLOAD_SIZE_BYTES] =
        foreign_tx_payload.compute_msg_hash()?.into();
    let payload_bytes: BoundedVec<u8, ECDSA_PAYLOAD_SIZE_BYTES, ECDSA_PAYLOAD_SIZE_BYTES> =
        payload_hash.into();

    Ok(SignatureRequest {
        id: request.id,
        receipt_id: request.receipt_id,
        payload: Payload::Ecdsa(payload_bytes),
        tweak: Tweak::new([0u8; 32]),
        entropy: request.entropy,
        timestamp_nanosec: request.timestamp_nanosec,
        domain: request.domain_id,
    })
}
```

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L53-64)
```rust
        let expected_payload_hash = expected_payload
            .compute_msg_hash()
            .map_err(|_| VerifyForeignChainError::FailedToComputeMsgHash)?;

        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
        }
```
