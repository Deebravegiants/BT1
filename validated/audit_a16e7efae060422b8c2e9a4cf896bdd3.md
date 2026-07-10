### Title
Attacker-Controlled `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Signature Replay — (`File: crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the submitted signature is valid over the caller-supplied `response.payload_hash`, but never checks that `response.payload_hash` is actually derived from the stored `VerifyForeignTransactionRequest`. Any single attested participant who possesses a previously produced valid threshold signature can replay it against any currently pending foreign-tx request, resolving that request with a forged verification result.

---

### Finding Description

In `respond_verify_foreign_tx` the contract performs the following check:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;   // fully attacker-controlled

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,          // verified only against itself, not against stored request
    &secp_pk,               // root public key — no tweak/derivation
)
.is_ok()
``` [1](#0-0) 

The contract then resolves the pending yield keyed on `request` with the full `response` (including the attacker-supplied `payload_hash`):

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

The contract never verifies that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayloadV1 { request: stored_request, values: ... }))`. The `payload_hash` field is entirely attacker-supplied and is only checked for internal self-consistency (the signature covers it), not for correspondence to the stored request.

By contrast, the node-side `build_signature_request` correctly derives the payload hash from the actual foreign-chain inspection result:

```rust
let payload_hash: [u8; ECDSA_PAYLOAD_SIZE_BYTES] =
    foreign_tx_payload.compute_msg_hash()?.into();
``` [3](#0-2) 

The contract never enforces this same derivation on the response it accepts.

The `VerifyForeignTransactionRequest` used as the map key contains only `{request, domain_id, payload_version}` — no caller identity and no binding to any particular `payload_hash`: [4](#0-3) 

---

### Impact Explanation

A single attested participant who participated in any prior legitimate `verify_foreign_transaction` signing round retains the resulting `(payload_hash, signature)` pair. They can replay it against any currently pending request for a different transaction:

1. Victim submits `verify_foreign_transaction` for Bitcoin tx B → pending yield stored under key `request_B`.
2. Attacker (single attested participant) calls `respond_verify_foreign_tx(request = request_B, response = {payload_hash = payload_hash_A, sig = sig_A})` where `(payload_hash_A, sig_A)` was produced by the MPC network for a prior, unrelated transaction A.
3. The contract verifies `sig_A(payload_hash_A)` is valid under the root key — it is — and resolves the yield for `request_B` with `payload_hash_A`.
4. The victim's NEAR callback receives `{payload_hash_A, sig_A}` as the "verified" result for their transaction B.

Any smart contract that uses the returned `VerifyForeignTransactionResponse` to gate fund releases without independently recomputing the expected `payload_hash` from the original request will accept this forged attestation. This enables invalid bridge execution and potential double-spend conditions: the attacker can make a contract believe that an arbitrary foreign-chain transaction (with attacker-chosen extracted values) was verified, when in fact it was not.

Additionally, the victim's pending yield is consumed and cannot be reused; the victim must resubmit and pay again.

This matches the allowed impact: **High — forged foreign-chain verification that causes invalid bridge execution or double-spend conditions**.

---

### Likelihood Explanation

The attack requires only:
- Being a single attested participant (no threshold collusion needed).
- Possessing any previously produced valid `(payload_hash, signature)` pair from any past signing round on the same domain.

Both conditions are easily satisfied by any honest-but-curious or Byzantine node that has ever participated in a `verify_foreign_transaction` signing round. The attack is repeatable and can be targeted at any pending request.

---

### Recommendation

In `respond_verify_foreign_tx`, independently recompute the expected `payload_hash` from the stored request and the extracted values provided in the response, and assert equality before accepting the response. Concretely, the contract should verify:

```
expected_hash = SHA-256(borsh(ForeignTxSignPayloadV1 {
    request: stored_request.request,
    values:  response.extracted_values,
}))
assert!(response.payload_hash == expected_hash)
```

This requires including the `extracted_values` in the `VerifyForeignTransactionResponse` so the contract can perform the check. Alternatively, the `payload_hash` should be computed on-chain from the stored request and the response's extracted values, rather than being accepted as a free parameter from the caller.

---

### Proof of Concept

```
1. Alice submits verify_foreign_transaction(Bitcoin tx_id=0xAAAA, extractors=[BlockHash])
   → pending_verify_foreign_tx_requests[request_A] = [yield_A]
   → MPC network signs: payload_hash_A = SHA256(borsh({request_A, values=[block_hash=0x1111]}))
   → sig_A = ECDSA_sign(root_key, payload_hash_A)
   → respond_verify_foreign_tx(request_A, {payload_hash_A, sig_A}) resolves yield_A ✓

2. Bob submits verify_foreign_transaction(Bitcoin tx_id=0xBBBB, extractors=[BlockHash])
   → pending_verify_foreign_tx_requests[request_B] = [yield_B]

3. Attacker (single attested participant, has sig_A from step 1) calls:
   respond_verify_foreign_tx(
       request  = request_B,          // matches Bob's pending yield
       response = {
           payload_hash = payload_hash_A,   // hash of Alice's transaction
           signature    = sig_A,            // valid sig over payload_hash_A
       }
   )

4. Contract checks:
   - sig_A(payload_hash_A) valid under root key? YES ✓
   - request_B in pending map? YES ✓
   → resolves yield_B with {payload_hash_A, sig_A}

5. Bob's callback receives {payload_hash_A, sig_A}.
   Bob's bridge contract checks only "is the signature valid?" → YES.
   Bob's contract releases funds believing Bitcoin tx 0xBBBB was verified
   with block_hash=0x1111, when in fact it was never verified.
``` [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L715-753)
```rust
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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L41-89)
```rust
impl ForeignChainSignatureVerifier {
    pub fn verify_signature(
        self,
        response: &VerifyForeignTransactionResponse,
        // TODO(#2232): don't use interface API types for public keys
        public_key: &PublicKey,
    ) -> Result<(), VerifyForeignChainError> {
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
        let verification_result = match (public_key, &response.signature) {
            (
                PublicKey::Secp256k1(secp256k1_public_key),
                SignatureResponse::Secp256k1(k256_signature),
            ) => near_mpc_signature_verifier::verify_ecdsa_signature(
                k256_signature,
                &expected_payload_hash,
                secp256k1_public_key,
            ),
            (PublicKey::Ed25519(ed25519_public_key), SignatureResponse::Ed25519 { signature }) => {
                near_mpc_signature_verifier::verify_eddsa_signature(
                    signature,
                    expected_payload_hash.as_slice(),
                    ed25519_public_key,
                )
            }
            // TODO(#2234): improve types so these errors can't happen
            (PublicKey::Bls12381(_bls12381_g2_public_key), _) => {
                return Err(VerifyForeignChainError::UnexpectedSignatureScheme);
            }
            _ => return Err(VerifyForeignChainError::UnexpectedSignatureScheme),
        };

        verification_result.map_err(|_| VerifyForeignChainError::SignatureVerificationFailed)
    }
```
