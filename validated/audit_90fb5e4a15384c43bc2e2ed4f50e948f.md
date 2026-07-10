### Title
Unbound `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Signature Replay by a Byzantine Attested Participant — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that `response.signature` is a valid MPC threshold signature over `response.payload_hash`, but it never verifies that `response.payload_hash` is actually the hash of `ForeignTxSignPayload { request, values }` for the submitted `request`. Because the extracted `values` are not stored on-chain, the contract has no way to enforce this binding. A single Byzantine attested participant can replay a valid `(payload_hash, signature)` pair from any past foreign-tx verification to resolve a completely different pending request, causing the contract to return a forged attestation to the caller.

---

### Finding Description

**Root cause — missing payload-to-request binding check**

In `respond_verify_foreign_tx`, the contract performs two checks:

1. The caller is an attested participant (trusted source for the public key — Issue 1 from the external report does not apply here).
2. The MPC signature is valid over `response.payload_hash`.

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

What is **never checked**: that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload { request, values }))` for the `request` parameter passed in. The `values` (the foreign-chain extracted data) are not stored on-chain, so the contract cannot reconstruct the expected hash. [2](#0-1) 

The `ForeignTxSignPayload` binds both the `request` (tx_id, extractors) and the `values` (observed foreign-chain data) into the signed hash: [3](#0-2) 

Without the on-chain binding check, the contract accepts any `(payload_hash, signature)` pair where the signature is a valid MPC signature — regardless of whether `payload_hash` corresponds to the `request` being resolved.

**Exploit path (single Byzantine attested participant, below threshold)**

1. Attacker is an attested MPC participant (satisfies `assert_caller_is_attested_participant_and_protocol_active`).
2. Attacker observes a past successful `respond_verify_foreign_tx` call on-chain for transaction T1, obtaining `(payload_hash_T1, signature_T1)` — both are public.
3. Attacker submits a new `verify_foreign_transaction` request for a different transaction T2 (e.g., an unconfirmed or invalid foreign-chain transaction), paying the deposit. This creates a pending yield under `T2_request`.
4. Attacker calls `respond_verify_foreign_tx(T2_request, { payload_hash: payload_hash_T1, signature: signature_T1 })`.
5. The contract checks: is `signature_T1` valid over `payload_hash_T1` under the MPC public key? **Yes** — it was a real threshold signature. Does `T2_request` exist in `pending_verify_foreign_tx_requests`? **Yes**. Both checks pass.
6. `resolve_yields_for` resolves the yield for `T2_request` with the forged response. [4](#0-3) 

The caller of `verify_foreign_transaction(T2)` receives `{ payload_hash: payload_hash_T1, signature: signature_T1 }` — a response that attests to T1's foreign-chain state, not T2's.

**SDK verifier catches it — but the contract does not enforce it**

The `near-mpc-sdk` `ForeignChainSignatureVerifier::verify_signature` does perform the binding check client-side:

```rust
let payload_is_correct = expected_payload_hash == response.payload_hash;
if !payload_is_correct {
    return Err(VerifyForeignChainError::IncorrectPayloadSigned { ... });
}
``` [5](#0-4) 

However, this is a **client-side library check**, not a contract-enforced invariant. Bridge contracts that verify only the ECDSA signature validity (without re-computing the expected payload hash from their own state) will accept the forged response.

---

### Impact Explanation

**Category: High — Forged foreign-chain verification causing invalid bridge execution.**

A Byzantine attested participant (single node, no threshold collusion required) can cause the MPC contract to return a cryptographically valid but semantically forged attestation for any pending foreign-tx request. A bridge contract that trusts the contract's response without independently re-computing `H(request, expected_values)` and comparing it to `response.payload_hash` will accept the forged attestation and process a foreign-chain event (e.g., a deposit) that was never actually verified. This directly enables invalid bridge execution and potential double-spend conditions.

---

### Likelihood Explanation

**Medium.** The attacker must be an attested MPC participant — a role that requires on-chain registration and TEE attestation, but is reachable without threshold-level collusion. The impact requires the victim bridge contract to skip the payload-hash binding check, which is a realistic omission for contracts that rely on the MPC contract to enforce correctness. The attack requires no cryptographic breaks, no leaked keys, and no network-level access — only the ability to call a public contract method with replayed on-chain data.

---

### Recommendation

The contract should enforce the binding between `response.payload_hash` and `request` on-chain. The simplest fix is to require the responder to also submit the `values` (extracted foreign-chain data), recompute `expected_hash = SHA-256(borsh(ForeignTxSignPayload { request, values }))` inside the contract, and assert `response.payload_hash == expected_hash` before accepting the response:

```rust
// Recompute expected hash from request + submitted values
let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.values.clone(), // values added to response DTO
});
let expected_hash = expected_payload.compute_msg_hash()?;
if expected_hash != response.payload_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
```

This mirrors the fix in the external report's `isValidMessage` check and the existing client-side check in `ForeignChainSignatureVerifier::verify_signature`. [6](#0-5) 

---

### Proof of Concept

```
// Step 1: Observe past valid response on-chain for tx T1
payload_hash_T1 = <from past respond_verify_foreign_tx event>
signature_T1    = <from past respond_verify_foreign_tx event>

// Step 2: Submit new request for unverified tx T2
near call mpc_contract verify_foreign_transaction \
  '{"request": {"request": {"Bitcoin": {"tx_id": T2_id, ...}}, "domain_id": X, ...}}' \
  --deposit 1

// Step 3: Replay old response against new pending request
near call mpc_contract respond_verify_foreign_tx \
  '{"request": {"request": {"Bitcoin": {"tx_id": T2_id, ...}}, "domain_id": X, ...},
    "response": {"payload_hash": payload_hash_T1, "signature": signature_T1}}' \
  --accountId attested_participant_account

// Result: contract resolves T2's yield with T1's payload_hash+signature.
// Bridge contract receives a "verified" response for T2 backed by T1's attestation.
```

The contract's only guards — `verify_ecdsa_signature(signature_T1, payload_hash_T1, mpc_pk)` and the existence of `T2_request` in pending — both pass. No threshold collusion, no cryptographic break, no privileged access beyond attested participant status. [7](#0-6)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1502)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
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

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L47-64)
```rust
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
```
