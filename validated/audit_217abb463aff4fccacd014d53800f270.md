### Title
Caller-Supplied `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Signature Replay to Forge Foreign-Chain Verification Attestations — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies an ECDSA signature against a `payload_hash` that is **supplied by the responding participant**, not derived from the pending `VerifyForeignTransactionRequest`. Because the root-key signature is the only check, any single attested participant can replay a valid `{payload_hash, signature}` pair from a previously resolved foreign-tx request to satisfy a completely different pending request, delivering a forged attestation to the waiting caller.

---

### Finding Description

The `respond_verify_foreign_tx` entry point accepts a `VerifyForeignTransactionResponse` struct containing two fields: `payload_hash` (a `Hash256`) and `signature`. The contract's only cryptographic check is:

```rust
// crates/contract/src/lib.rs:726-734
let payload_hash: [u8; 32] = response.payload_hash.0;

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
```

The `payload_hash` is taken entirely from `response` — the caller's input — and is never cross-checked against the `request` parameter that identifies the pending yield. [1](#0-0) 

The correct payload hash for a foreign-tx request is `SHA-256(borsh(ForeignTxSignPayload::V1 { request, values }))`, where `values` are the extracted on-chain observations. This is computed by the node in `build_signature_request` and signed with a zero tweak (root key, no derivation): [2](#0-1) 

The contract never stores the expected hash at request-submission time (it cannot, because `values` are unknown until nodes query the foreign chain). So there is no on-chain anchor to validate `response.payload_hash` against.

**Contrast with `respond` for regular signatures**, which reads the payload hash directly from the immutable `request` object, binding the signature to that specific request:

```rust
// crates/contract/src/lib.rs:600
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
``` [3](#0-2) 

For foreign-tx responses, no equivalent binding exists.

---

### Impact Explanation

A single Byzantine attested participant can execute the following cross-request replay:

1. **Observe** any previously submitted `respond_verify_foreign_tx` transaction on-chain (all NEAR transactions are public). Extract `{payload_hash: H_Y, signature: sig_root(H_Y)}` from the call arguments.
2. **Identify or submit** a pending `verify_foreign_transaction` request X (for a different foreign transaction, or one that would not pass honest node verification).
3. **Call** `respond_verify_foreign_tx(request=X, response={payload_hash: H_Y, signature: sig_root(H_Y)})`.
4. The contract checks: is `sig_root(H_Y)` a valid ECDSA signature over `H_Y` under the root key? **Yes** — it was produced honestly for request Y.
5. The contract resolves the pending yield for request X with the forged response.
6. The caller of X receives `{payload_hash: H_Y, signature: sig_root(H_Y)}` — an attestation that the MPC network signed `H_Y` for their request, which is false.

Any bridge or application that trusts the contract's response without independently recomputing the expected `payload_hash` from the original request and observed values will process an invalid attestation. This enables forged foreign-chain verification and, in bridge contexts, potential double-spend or invalid inbound-flow execution.

The `VerifyForeignTransactionResponse` type confirms the two-field structure that makes this substitution possible: [4](#0-3) 

---

### Likelihood Explanation

The attacker must be an attested participant — a node registered in the MPC network with a valid TEE attestation. This is a meaningful barrier, but the threat model explicitly includes a single Byzantine participant below the signing threshold. Once attested:

- Obtaining a replayable `{payload_hash, signature}` pair requires only reading any prior `respond_verify_foreign_tx` call from NEAR's public transaction history — no privileged access needed.
- Submitting a target request X is open to any NEAR account (the `verify_foreign_transaction` entry point is public and payable).
- Calling `respond_verify_foreign_tx` with the replayed pair requires only being an attested participant, which the attacker already is.

No threshold collusion, no key material, and no network-level attack are required.

---

### Recommendation

The contract must bind the response's `payload_hash` to the pending request. Two approaches:

1. **Store the expected hash at request time** — not directly feasible because `values` (extracted observations) are unknown at submission time.
2. **Require the responder to supply the extracted `values` alongside the response**, then have the contract recompute `SHA-256(borsh(ForeignTxSignPayload::V1 { request, values }))` and assert it equals `response.payload_hash` before accepting the signature. This mirrors how `respond` derives the payload hash from the immutable request object.
3. **Alternatively**, include a request-unique nonce (e.g., the yield `data_id`) in the signed payload so that a signature produced for request Y is cryptographically invalid for request X, even if both use the root key.

---

### Proof of Concept

```
// Step 1: Honest flow for request Y (Bitcoin tx_id = [0xAA; 32])
// MPC nodes verify the transaction, compute:
//   H_Y = SHA-256(borsh(ForeignTxSignPayload::V1 {
//       request: Bitcoin { tx_id: [0xAA;32], ... },
//       values: [BlockHash([0xBB;32])]
//   }))
// Leader calls: respond_verify_foreign_tx(request=Y, response={payload_hash: H_Y, sig: sig_root(H_Y)})
// → Accepted. Caller of Y receives {H_Y, sig_root(H_Y)}.

// Step 2: Byzantine participant Eve observes H_Y and sig_root(H_Y) from NEAR tx history.

// Step 3: Bob submits verify_foreign_transaction(request=X) for Bitcoin tx_id = [0xCC; 32]
//         (a transaction that does NOT exist or has not finalized).

// Step 4: Eve calls:
//   respond_verify_foreign_tx(
//       request = X,   // ← correct key to find Bob's pending yield
//       response = { payload_hash: H_Y, signature: sig_root(H_Y) }  // ← replayed from Y
//   )
// Contract check: verify_ecdsa_signature(sig_root(H_Y), H_Y, root_pk) → OK ✓
// Contract resolves Bob's yield with the forged response.

// Step 5: Bob's contract receives {payload_hash: H_Y, signature: sig_root(H_Y)}.
//         H_Y encodes Bitcoin tx [0xAA;32]'s block hash, not [0xCC;32]'s.
//         Bob's bridge logic, if it trusts the contract, processes a forged attestation.
```

The root cause is at: [5](#0-4) 

with the missing binding between `response.payload_hash` and the `request` parameter that identifies the pending yield.

### Citations

**File:** crates/contract/src/lib.rs (L598-608)
```rust
                    derive_key_secp256k1(&affine, &request.tweak).map_err(RespondError::from)?;

                let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");

                // Check the signature is correct
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    payload_hash,
                    &expected_public_key,
                )
                .is_ok()
```

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L147-150)
```rust
pub struct VerifyForeignTransactionResponse {
    pub payload_hash: Hash256,
    pub signature: SignatureResponse,
}
```
