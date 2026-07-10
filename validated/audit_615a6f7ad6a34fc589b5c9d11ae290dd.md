### Title
`respond_verify_foreign_tx` Does Not Bind `response.payload_hash` to the Pending Request — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_verify_foreign_tx` function verifies that the submitted signature is cryptographically valid over `response.payload_hash`, but never checks that `response.payload_hash` is the canonical hash of the `request` being resolved. A single Byzantine MPC participant (below threshold) can replay any previously-obtained threshold signature — over a different foreign transaction's payload hash — to resolve any pending `verify_foreign_transaction` request with fraudulent data.

---

### Finding Description

In `respond_verify_foreign_tx`, the contract performs two checks:

1. The signature is valid over `response.payload_hash` using the root public key.
2. The `request` key exists in `pending_verify_foreign_tx_requests`. [1](#0-0) 

Critically, the contract does **not** verify that `response.payload_hash` is the hash of `ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 { request: request.request, values: ... })` for the specific `request` being resolved. The `payload_hash` field in the response is entirely caller-supplied and unconstrained relative to the `request` key used to look up the pending yield.

The `ForeignTxSignPayload` hash construction is: [2](#0-1) 

The MPC nodes compute this hash correctly on their side: [3](#0-2) 

But the contract never re-derives or cross-checks this hash against the `request` when accepting a response.

The `VerifyForeignTransactionRequest` stored as the pending map key contains only `{ request: ForeignChainRpcRequest, domain_id, payload_version }` — it does not contain the extracted `values`: [4](#0-3) 

Because the contract cannot independently reconstruct the full `ForeignTxSignPayload` (it lacks the `values` extracted by MPC nodes), it cannot verify the binding. This is the structural gap.

**Attack path:**

1. The MPC network previously signed `payload_hash_Y` for foreign transaction Y (this call is on-chain and publicly observable).
2. A pending `verify_foreign_transaction` request X exists in the contract (for a different foreign transaction).
3. A single Byzantine MPC participant calls `respond_verify_foreign_tx(request_X, { payload_hash_Y, sig_Y })`.
4. The contract verifies `sig_Y` is valid over `payload_hash_Y` ✓ and that `request_X` is pending ✓ — both checks pass.
5. The contract resolves `request_X` and returns `{ payload_hash_Y, sig_Y }` to the original caller.
6. The caller receives a fraudulent verification response: the MPC network's attestation for transaction Y is presented as the attestation for transaction X.

This is the direct analog of the external report: the signed payload does not include all parameters needed to bind it to the specific operation being authorized (the `request` being resolved is not committed to in the signed `payload_hash`).

The SDK's `ForeignChainSignatureVerifier::verify_signature` does perform this check client-side: [5](#0-4) 

However, this is an off-chain SDK helper, not an on-chain enforcement. Bridge contracts or other callers that do not use the SDK, or that only check for the presence of a response without verifying `payload_hash`, are fully exposed.

---

### Impact Explanation

A single Byzantine MPC participant (below threshold) can cause the NEAR MPC contract to return a fraudulent `VerifyForeignTransactionResponse` — one whose `payload_hash` and signature correspond to a completely different foreign transaction than the one requested. Any bridge or cross-chain application that trusts the contract's response without independently verifying `payload_hash` against the expected transaction will accept this forged attestation, enabling invalid bridge execution or double-spend conditions.

This maps to the **High** allowed impact: *"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass, or participant/attestation authorization bypass that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

The attack requires only a single attested MPC participant to act maliciously. All `respond_verify_foreign_tx` calls are on-chain and publicly observable, so any participant can trivially obtain a valid `(payload_hash, signature)` pair from a prior completed request. No key material beyond normal participant access is needed. The attacker only needs to wait for a new pending request to target.

---

### Recommendation

The contract should enforce that `response.payload_hash` is consistent with the `request` being resolved. Since the contract cannot independently reconstruct the full `ForeignTxSignPayload` (it lacks the extracted `values`), the recommended fix is to include the `ForeignChainRpcRequest` (or its hash) as a mandatory component of the signed payload and verify it on-chain. Concretely:

- Extend `ForeignTxSignPayload` or the signing commitment to include a binding to the `VerifyForeignTransactionRequest` key (e.g., hash of `request.request`).
- In `respond_verify_foreign_tx`, recompute `expected_request_hash = hash(request.request)` and verify that `response.payload_hash` encodes this value (e.g., by requiring the payload to be structured as `hash(request_hash || values_hash)`).
- Alternatively, require MPC nodes to submit the extracted `values` alongside the response so the contract can independently verify `response.payload_hash == ForeignTxSignPayload::V1(...).compute_msg_hash()`.

---

### Proof of Concept

```
// Setup: MPC network previously signed payload_hash_Y for Bitcoin tx_id Y.
// The response (payload_hash_Y, sig_Y) is observable on-chain.

// A new pending request X exists for Bitcoin tx_id X.
// Attacker (single Byzantine participant) calls:

contract.respond_verify_foreign_tx(
    VerifyForeignTransactionRequest {
        request: ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest {
            tx_id: X_TX_ID,   // <-- the pending request for tx X
            ...
        }),
        domain_id: ...,
        payload_version: V1,
    },
    VerifyForeignTransactionResponse {
        payload_hash: payload_hash_Y,  // <-- hash of tx Y's payload (replayed)
        signature: sig_Y,              // <-- threshold signature over payload_hash_Y (replayed)
    },
);

// The contract:
// 1. Verifies sig_Y over payload_hash_Y against root public key → PASSES
// 2. Finds request_X in pending_verify_foreign_tx_requests → PASSES
// 3. Resolves request_X with { payload_hash_Y, sig_Y }

// The caller of request_X receives payload_hash_Y (tx Y's attestation)
// instead of the correct attestation for tx X.
// A bridge contract not using the SDK's verify_signature would accept this.
```

The contract's signature check at line 729 passes because `sig_Y` is a valid threshold signature over `payload_hash_Y`. The binding between `payload_hash` and `request` is never enforced on-chain. [6](#0-5)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1504-1509)
```rust
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-47)
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
