### Title
`respond_verify_foreign_tx` Accepts Any Valid Signature Without Binding It to the Pending Request — Cross-Request Replay of Foreign-Chain Verification Responses - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies only that the submitted signature is cryptographically valid over `response.payload_hash`, but never verifies that `response.payload_hash` is the correct hash for the `request` being resolved. A single malicious attested participant acting as signing coordinator can take a legitimately-produced MPC signature for request A and submit it as the response to a different pending request B. The contract accepts it, and the caller of request B receives a `VerifyForeignTransactionResponse` whose `payload_hash` encodes the extracted values of a completely different foreign-chain transaction.

---

### Finding Description

In `respond_verify_foreign_tx` (lines 691–753 of `crates/contract/src/lib.rs`), the contract performs two independent checks and then resolves the pending yield:

1. **Signature validity check** — verifies `sig` is a valid ECDSA signature over `response.payload_hash` under the domain's root public key.
2. **Pending-request lookup** — calls `resolve_yields_for(&mut self.pending_verify_foreign_tx_requests, &request, ...)` using the caller-supplied `request` struct as the map key.

What is **never checked** is whether `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload::V1 { request: request.request, values: <actual extracted values> }))`. The contract has no way to recompute this hash because the extracted `values` are not stored on-chain — they are determined off-chain by the MPC nodes during foreign-chain inspection. The contract therefore cannot bind the signature to the specific request it is resolving. [1](#0-0) 

The `payload_hash` used for signature verification is taken verbatim from the response: [2](#0-1) 

After the signature check passes, the response (containing the attacker-controlled `payload_hash`) is serialised and delivered to every yield queued under `request`: [3](#0-2) 

The `ForeignTxSignPayload` that nodes actually sign commits to both the request and the extracted values: [4](#0-3) 

---

### Impact Explanation

A bridge contract that calls `verify_foreign_transaction` to confirm a foreign-chain deposit before releasing funds receives a `VerifyForeignTransactionResponse`. It can verify the ECDSA signature over `payload_hash` using the MPC root public key — and that check passes. But `payload_hash` encodes the extracted values (e.g., `BlockHash`) of a **different** transaction, not the one the bridge submitted. The bridge contract therefore acts on fabricated attestation data: it may release funds for a transaction that was never confirmed, or release them twice (double-spend), depending on how it interprets the extracted values.

The SDK-level verifier (`ForeignChainSignatureVerifier::verify_signature`) can catch this only if the caller already knows the expected extracted values: [5](#0-4) 

For the primary bridge use-case the caller does **not** know the extracted values in advance — that is precisely what they are asking the MPC network to determine. The SDK verifier therefore provides no protection in the common case.

---

### Likelihood Explanation

The attack requires exactly **one** malicious attested participant acting as signing coordinator. The coordinator:

1. Leads a legitimate signing session for request A, assembles the threshold signature over `hash_A`, and retains it without submitting the response on-chain (request A times out).
2. Monitors the NEAR chain for a target pending request B (trivially observable).
3. Calls `respond_verify_foreign_tx(request = request_B, response = {payload_hash: hash_A, signature: sig_A})`.

The contract accepts the call because `sig_A` is a valid MPC signature over `hash_A`, and `request_B` exists in the pending map. No threshold collusion is required; the coordinator already holds the assembled signature from step 1. [6](#0-5) 

---

### Recommendation

The contract must bind the response to the request before accepting it. Since the extracted `values` are not stored on-chain, the simplest fix is to include the `payload_hash` as part of the pending-request map key at submission time — i.e., have the node that first responds also commit the `payload_hash`, and store it alongside the yield indices. Subsequent `respond_verify_foreign_tx` calls for the same request must supply the identical `payload_hash`, which the contract can then verify against the stored commitment before checking the signature.

Alternatively, the contract can require the responding node to supply the extracted `values` explicitly, recompute `SHA-256(borsh(ForeignTxSignPayload::V1 { request, values }))` on-chain, and verify the signature against that recomputed hash rather than the caller-supplied one.

---

### Proof of Concept

```
1. Attacker (attested participant P) leads signing for request_A:
   - request_A = VerifyForeignTransactionRequest { request: Bitcoin(tx_id=[0x11;32], ...), domain_id: 0, ... }
   - MPC nodes inspect Bitcoin, extract BlockHash=[0xAA;32]
   - hash_A = SHA256(borsh(ForeignTxSignPayload::V1 { request: request_A.request, values: [BlockHash=[0xAA;32]] }))
   - P assembles sig_A = MPC_sign(hash_A)  ← valid threshold signature
   - P does NOT call respond_verify_foreign_tx for request_A (lets it time out)

2. Victim bridge contract submits:
   - request_B = VerifyForeignTransactionRequest { request: Bitcoin(tx_id=[0x22;32], ...), domain_id: 0, ... }
   - Bridge is waiting for the extracted BlockHash to decide whether to release funds.

3. Attacker calls:
   respond_verify_foreign_tx(
     request = request_B,          // exists in pending map ✓
     response = {
       payload_hash: hash_A,       // hash of a DIFFERENT payload
       signature: sig_A,           // valid MPC sig over hash_A ✓
     }
   )

4. Contract checks:
   - verify_ecdsa_signature(sig_A, hash_A, root_pk) → OK  ✓
   - pending_verify_foreign_tx_requests.get(request_B) → found ✓
   - resolve_yields_for(request_B, serialize({payload_hash: hash_A, sig: sig_A}))

5. Bridge contract receives VerifyForeignTransactionResponse {
     payload_hash: hash_A,   // encodes BlockHash=[0xAA;32] for tx_id=[0x11;32]
     signature: sig_A,
   }
   - verify_ecdsa_signature(sig_A, hash_A, root_pk) → OK  ✓  (bridge trusts this)
   - Bridge releases funds believing tx_id=[0x22;32] was confirmed in block 0xAA...
   - Actual block for tx_id=[0x22;32] was never verified.
```

### Citations

**File:** crates/contract/src/lib.rs (L691-713)
```rust
    #[handle_result]
    pub fn respond_verify_foreign_tx(
        &mut self,
        request: VerifyForeignTransactionRequest,
        response: VerifyForeignTransactionResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!(
            "respond_verify_foreign_tx: signer={}, request={:?}",
            &signer,
            &request
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L718-743)
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
```

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
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

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L48-64)
```rust
        let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
            request: self.request,
            values: self.expected_extracted_values,
        });

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
