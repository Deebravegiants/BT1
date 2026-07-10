### Title
Missing `payload_hash`-to-`request` binding validation in `respond_verify_foreign_tx` enables forged foreign-chain verification — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the MPC signature is valid over `response.payload_hash`, but never verifies that `response.payload_hash` is actually derived from the submitted `request` content. A Byzantine MPC participant strictly below the signing threshold — acting as the signing leader — can produce a valid threshold signature for Request A, then submit it as the response to a completely different pending Request B. The contract accepts it (signature is valid, Request B exists in the pending map), and Request B's caller receives a valid MPC signature over the wrong hash. Bridge contracts that do not independently re-derive and compare the expected `payload_hash` will accept this as a legitimate foreign-chain attestation, enabling invalid bridge execution.

---

### Finding Description

In `respond_verify_foreign_tx` the contract performs two independent, unlinked checks:

**Check 1 — signature validity** (`crates/contract/src/lib.rs` lines 718–743):
```rust
let payload_hash: [u8; 32] = response.payload_hash.0;
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,   // ← whatever the caller supplied
    &secp_pk,
).is_ok()
``` [1](#0-0) 

**Check 2 — request lookup** (`crates/contract/src/lib.rs` lines 749–753):
```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,                              // ← key used for lookup
    serde_json::to_vec(&response).unwrap(), // ← response delivered verbatim
)
``` [2](#0-1) 

There is **no check** that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload::V1 { request: request.request, values: … }))`. The `payload_hash` and the `request` are treated as independent inputs.

The design intent is that `payload_hash` must be the canonical hash of the request plus the MPC-observed extracted values: [3](#0-2) 

The node-side code correctly computes this hash before signing: [4](#0-3) 

But the contract never re-derives or cross-checks it. The SDK-side verifier (`ForeignChainSignatureVerifier::verify_signature`) does perform this check client-side: [5](#0-4) 

However, the on-chain contract — the authoritative source of truth — does not enforce it, leaving the binding entirely to caller discipline.

This is the direct structural analog to the DODO vulnerability: DODO's `onCall` used `params.toToken` for the swap output but `decoded.targetZRC20` for the withdrawal without validating they match. Here, `respond_verify_foreign_tx` uses `request` as the map key but `response.payload_hash` as the signed content, without validating they correspond.

---

### Impact Explanation

A Byzantine leader node below the signing threshold can:

1. Legitimately coordinate with honest followers to produce a valid threshold signature `sig_A` over `H_A = SHA-256(borsh(ForeignTxSignPayload::V1 { request: A, values: values_A }))` for Request A.
2. Instead of submitting `respond_verify_foreign_tx(request=A, response={H_A, sig_A})`, submit `respond_verify_foreign_tx(request=B, response={H_A, sig_A})` for a different pending Request B.
3. The contract accepts: `sig_A` is a valid MPC signature over `H_A` ✓, and Request B exists in the pending map ✓.
4. Request B's caller receives `{payload_hash=H_A, sig=sig_A}` — a valid MPC signature over a hash that encodes Request A's foreign-chain state, not Request B's.

Any bridge contract that checks only that the signature is valid over `payload_hash` (without re-deriving the expected hash from the request and expected extracted values) will accept this as a legitimate attestation of Request B's foreign-chain state. This enables invalid bridge execution — for example, minting tokens on NEAR for a foreign-chain transaction that was never confirmed, or accepting a block hash from a different transaction as proof of the requested one.

Impact category: **High — forged foreign-chain verification causing invalid bridge execution.**

---

### Likelihood Explanation

- A Byzantine participant below the signing threshold is an explicitly allowed attacker profile per the scope.
- The leader role rotates; over time any participant will be selected as leader, making this attack inevitable if a Byzantine node is present.
- The attack requires no privileged access beyond being an attested MPC participant.
- The pending request map is public on-chain, so the Byzantine leader can freely choose which pending Request B to target.
- Bridge contracts that do not use `ForeignChainSignatureVerifier::verify_signature` from the NEAR MPC SDK — or implement their own incomplete check — are directly exploitable. Given that the contract itself does not enforce the binding, integrators have no on-chain guarantee to rely on.

---

### Recommendation

Add an explicit binding check inside `respond_verify_foreign_tx`. Since the contract does not have access to the extracted `values`, the fix requires one of:

1. **Include `values` in the respond call**: Extend `VerifyForeignTransactionResponse` to carry the extracted `values`, then recompute `expected_hash = SHA-256(borsh(ForeignTxSignPayload::V1 { request: request.request, values }))` on-chain and assert `expected_hash == response.payload_hash` before accepting the response.

2. **Commit to the hash at request time**: When `verify_foreign_transaction` is called, store a commitment to the expected `payload_hash` structure (at minimum the request content hash) and verify the response `payload_hash` starts from that commitment.

---

### Proof of Concept

```
// Byzantine leader node has computed sig_A for Request A legitimately.
// H_A = SHA-256(borsh(ForeignTxSignPayload::V1 { request: A, values: values_A }))

// Attack: submit sig_A as the response to Request B
respond_verify_foreign_tx(
    request  = B,                          // ← different pending request (exists in map)
    response = {
        payload_hash = H_A,               // ← hash of Request A's content
        signature    = sig_A,             // ← valid MPC signature over H_A
    }
)

// Contract path:
// 1. verify_ecdsa_signature(sig_A, H_A, mpc_root_pk) → OK  (sig_A is genuinely valid)
// 2. pending_verify_foreign_tx_requests.remove(&B)   → OK  (B is pending)
// 3. promise_yield_resume(B_yield, {H_A, sig_A})     → OK  (no binding check)

// Result: Request B's caller receives {payload_hash=H_A, sig=sig_A}.
// H_A encodes Request A's foreign-chain state, not Request B's.
// Bridge contracts that omit the payload_hash re-derivation check accept this
// as a valid attestation of Request B's foreign-chain state.
```

The missing check that should appear between steps 1 and 2:
```rust
// MISSING: recompute expected hash from request content and verify
let expected_hash = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.values.clone(), // values must be included in response
}).compute_msg_hash()?;
if expected_hash != response.payload_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
``` [6](#0-5) [7](#0-6)

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
