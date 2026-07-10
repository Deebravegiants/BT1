### Title
`respond_verify_foreign_tx` Does Not Bind `payload_hash` to the Routing `request`, Enabling Cross-Request Response Replay - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies only that the ECDSA signature in the response is valid over the caller-supplied `payload_hash`. It never checks that `payload_hash` was actually derived from the `request` parameter used as the routing key. A single malicious attested participant (below the signing threshold) can replay a legitimately-produced response for request A to resolve a completely different pending request B, delivering a forged verification attestation to the caller of request B.

### Finding Description

`respond_verify_foreign_tx` accepts two independent arguments:

- `request: VerifyForeignTransactionRequest` — used only as a map key to locate and drain the pending yield queue.
- `response: VerifyForeignTransactionResponse` — contains `payload_hash` (a `Hash256`) and a `signature` over that hash.

The contract's only cryptographic check is:

```rust
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,   // ← taken directly from response, never tied to `request`
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

There is no assertion that `payload_hash == SHA-256(borsh(ForeignTxSignPayload { request: request.request, values: <anything> }))`. The `request` field is consumed only by `resolve_yields_for` to pick the right yield slot:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

The signed payload is defined as:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
// msg_hash = SHA-256(borsh(ForeignTxSignPayload))
``` [3](#0-2) 

Because the contract never reconstructs or checks the `request` component of the hash, any valid `(payload_hash, signature)` pair — regardless of which `ForeignChainRpcRequest` it was computed for — will pass validation and be delivered to the yield waiting on the supplied routing key.

The design document acknowledges this gap by placing the verification burden on callers: *"The response contains the hash of the sign payload, so callers can verify the signature by checking it against the expected hash they reconstruct locally."* [4](#0-3) 

The SDK helper `ForeignChainSignatureVerifier::verify_signature` does perform this check client-side:

```rust
let payload_is_correct = expected_payload_hash == response.payload_hash;
if !payload_is_correct {
    return Err(VerifyForeignChainError::IncorrectPayloadSigned { ... });
}
``` [5](#0-4) 

But this is an off-chain SDK helper — it is not enforced by the on-chain contract. Any bridge contract that does not use this helper, or that trusts the `VerifyForeignTransactionResponse` returned by the NEAR promise directly, is exposed.

### Impact Explanation

A malicious attested participant (a single Byzantine node, strictly below the signing threshold) can:

1. Observe a legitimately produced `VerifyForeignTransactionResponse` for request A (e.g., attesting that Bitcoin tx `0xAA` finalized with block-hash `0xBB`).
2. Wait for a different pending request B (e.g., for Bitcoin tx `0xCC`) to appear in the contract's yield queue.
3. Call `respond_verify_foreign_tx(request = B, response = response_A)`.
4. The contract accepts the call (signature is valid over `payload_hash_A`), drains the yield for request B, and delivers `response_A` to B's caller.
5. B's caller receives a `VerifyForeignTransactionResponse` whose `payload_hash` encodes request A's data, not request B's. If the caller does not independently verify the hash, it treats the attestation as proof that tx `0xCC` finalized — which it did not.

This enables **forged foreign-chain verification**: a bridge contract can be made to believe an arbitrary foreign transaction was verified and finalized, enabling invalid inbound bridge execution or double-spend conditions.

### Likelihood Explanation

- The attacker needs only to be an attested MPC participant — a single Byzantine node below the threshold suffices.
- The response for request A is observable on-chain the moment the honest leader submits it; no off-protocol access is required.
- Bridge contracts that call `verify_foreign_transaction` and act on the returned `VerifyForeignTransactionResponse` without re-deriving and comparing the `payload_hash` are directly vulnerable. The design doc explicitly delegates this check to callers, making omission likely in practice.

### Recommendation

The contract should enforce that `response.payload_hash` is consistent with the `request` routing key. Since `payload_hash = SHA-256(borsh(ForeignTxSignPayload { request, values }))` and the contract cannot know `values`, the hash structure should be changed to allow partial verification. Two concrete options:

1. **Structured hash**: Change the payload hash to `SHA-256(SHA-256(borsh(request)) || SHA-256(borsh(values)))`. The contract can then recompute `SHA-256(borsh(request.request))` from the routing key and verify it matches the first half of the pre-image commitment included in the response.

2. **Include the request in the response**: Require `respond_verify_foreign_tx` to also supply the `ForeignChainRpcRequest` that was signed, and assert it equals `request.request` before accepting the response. The `payload_hash` can still be the compact form returned to callers.

Either approach closes the gap without relying on caller-side SDK usage.

### Proof of Concept

```
Setup:
  - Two pending requests: A (Bitcoin tx 0xAA) and B (Bitcoin tx 0xCC)
  - MPC network produces response_A = { payload_hash: H(A, [BlockHash=0xBB]), sig: σ_A }
  - Honest leader submits respond_verify_foreign_tx(request=A, response=response_A) → resolves A

Attack:
  - Mallory (attested participant, below threshold) submits:
      respond_verify_foreign_tx(request=B, response=response_A)

Contract check:
  - verify_ecdsa_signature(σ_A, H(A, [BlockHash=0xBB]), root_pk) → OK  ✓
  - resolve_yields_for(pending[B], response_A)                   → OK  ✓

Result:
  - B's caller receives response_A
  - payload_hash encodes tx 0xAA + block-hash 0xBB, NOT tx 0xCC
  - If caller skips payload_hash verification → accepts forged attestation for tx 0xCC
```

The root cause is in `crates/contract/src/lib.rs` at `respond_verify_foreign_tx` (lines 691–754): the `request` parameter is used only for yield routing, never to constrain the `payload_hash` in the response. [6](#0-5)

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

**File:** docs/foreign-chain-transactions.md (L155-156)
```markdown
The response contains the hash of the sign payload, so callers can verify the signature
by checking it against the expected hash they reconstruct locally.
```

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L57-63)
```rust
        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
```
