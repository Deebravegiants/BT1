### Title
`respond_verify_foreign_tx` Does Not Bind `payload_hash` to the Submitted `request` — Cross-Request Replay of Foreign-Chain Verification Responses - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the supplied ECDSA signature is valid over the supplied `payload_hash`, but it never checks that `payload_hash` is actually the hash of a `ForeignTxSignPayload` derived from the `request` argument being resolved. A Byzantine attested participant can therefore replay a legitimately-produced `(payload_hash, signature)` pair from a past foreign-chain verification response to satisfy a completely different pending request, delivering a forged attestation to the waiting caller without the MPC nodes ever querying the foreign chain for that request.

---

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` performs two independent checks and then resolves the pending yield:

1. It verifies `response.signature` over `response.payload_hash` against the domain's root public key.
2. It looks up `request` in `pending_verify_foreign_tx_requests` and drains the queue. [1](#0-0) 

The critical gap is that the contract **never asserts** that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload { request: <the same request>, values: ... }))`. The two checks are entirely decoupled: the signature check uses `payload_hash` from the response, while the queue lookup uses `request` from the call arguments. Nothing ties them together.

The `ForeignTxSignPayload` that nodes are supposed to sign is constructed as:

```
msg_hash = SHA-256(borsh(ForeignTxSignPayload::V1 { request: ForeignChainRpcRequest, values: Vec<ExtractedValue> }))
``` [2](#0-1) 

This hash binds the signature to a specific `(request, observed_values)` pair. However, the contract never reconstructs or validates this binding on-chain. It accepts any `payload_hash` for which a valid root-key signature exists, regardless of whether that hash was produced for the `request` being resolved.

The `VerifyForeignTransactionRequest` used as the map key contains only `(request, domain_id, payload_version)` — no per-submission nonce, receipt ID, or timestamp — so any previously completed response for a structurally identical or different request can be replayed against any pending entry in the queue. [3](#0-2) 

---

### Impact Explanation

A Byzantine attested participant (one node acting maliciously, well below the signing threshold) can:

1. Observe a legitimately completed `respond_verify_foreign_tx` call for request R1 (e.g., Bitcoin tx A), recording `(payload_hash_A, sig_A)`.
2. Wait for any user to submit `verify_foreign_transaction` for request R2 (e.g., Bitcoin tx B, or even the same tx with different extractors).
3. Immediately call `respond_verify_foreign_tx(request = R2, response = { payload_hash: payload_hash_A, sig: sig_A })`.
4. The contract accepts: `sig_A` is a valid root-key signature over `payload_hash_A`. R2 is pending. Both checks pass.
5. The user's yield is resolved with `payload_hash_A` — an attestation that encodes Bitcoin tx A's data, not Bitcoin tx B's.

The user's NEAR contract receives a valid MPC-signed `VerifyForeignTransactionResponse` for a foreign transaction it never actually verified. If the downstream contract uses this response to authorize a bridge action (e.g., releasing tokens on NEAR because a deposit was detected on the foreign chain), the attacker can trigger that action without the underlying foreign-chain event having occurred, or can reuse the same foreign-chain event's attestation to satisfy multiple independent requests — a direct double-spend condition.

This matches the allowed impact: **"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass, or participant/attestation authorization bypass that causes invalid bridge execution or double-spend conditions."**

---

### Likelihood Explanation

- A single Byzantine attested participant is sufficient; no threshold collusion is required.
- The attacker only needs to observe on-chain data (all `respond_verify_foreign_tx` calls and their arguments are public NEAR transactions) and submit one transaction.
- The window of opportunity is any time a `verify_foreign_transaction` request is pending in the queue, which is the normal operating state of the bridge.
- The attack is fully deterministic and requires no cryptographic capability beyond reading chain history.

---

### Recommendation

Inside `respond_verify_foreign_tx`, after verifying the signature, reconstruct the expected `payload_hash` from the `request` argument and the extracted values encoded in `response`, and assert equality before resolving the yield:

```rust
// Pseudo-code
let expected_hash = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.extracted_values.clone(), // requires adding this field
}).compute_msg_hash()?;

if expected_hash != response.payload_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
```

Alternatively, include the `ForeignTxSignPayload` (not just its hash) in the `VerifyForeignTransactionResponse` so the contract can verify the binding on-chain. At minimum, the contract must verify that `response.payload_hash` encodes a payload whose `request` field matches the `request` argument passed to `respond_verify_foreign_tx`. [4](#0-3) 

---

### Proof of Concept

**Setup:** Two pending `verify_foreign_transaction` requests exist:
- R1: `BitcoinRpcRequest { tx_id: [0xAA; 32], confirmations: 1, extractors: [BlockHash] }`
- R2: `BitcoinRpcRequest { tx_id: [0xBB; 32], confirmations: 1, extractors: [BlockHash] }`

**Step 1:** Honest MPC nodes process R1 and the leader calls:
```
respond_verify_foreign_tx(
  request = R1,
  response = { payload_hash: H(ForeignTxSignPayload{R1, [BlockHash=0xCC..]}), sig: sig_R1 }
)
```
This is accepted. R1's yield is resolved. `(payload_hash_R1, sig_R1)` is now public on-chain.

**Step 2:** Before honest nodes process R2, the Byzantine participant calls:
```
respond_verify_foreign_tx(
  request = R2,
  response = { payload_hash: payload_hash_R1, sig: sig_R1 }
)
```

**Step 3:** The contract at lines 729–734 verifies `sig_R1` over `payload_hash_R1` against the root key — **valid**. At line 749, it looks up R2 in `pending_verify_foreign_tx_requests` — **found**. The yield is resolved.

**Result:** R2's caller receives `{ payload_hash: payload_hash_R1, sig: sig_R1 }` — an attestation that Bitcoin tx `0xAA` was verified, delivered in response to a request for Bitcoin tx `0xBB`. The MPC network never queried the foreign chain for `0xBB`. [5](#0-4) [2](#0-1)

### Citations

**File:** crates/contract/src/lib.rs (L691-754)
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

        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain.0.into())?;

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

        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
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
