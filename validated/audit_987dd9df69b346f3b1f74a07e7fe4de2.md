### Title
Unvalidated `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Signature Replay — (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies that the submitted ECDSA signature is valid over `response.payload_hash`, but never checks that `response.payload_hash` actually commits to the `request` that is being resolved. A single Byzantine attested participant can replay a valid signature obtained from a prior legitimate foreign-chain signing round to satisfy a completely different pending `verify_foreign_transaction` request, causing the contract to deliver a forged attestation to the waiting caller.

### Finding Description

In `respond_verify_foreign_tx`, the signature check is:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
```

The `payload_hash` is taken entirely from the attacker-supplied `response` argument. The contract only checks that `signature` is a valid ECDSA signature over `response.payload_hash` under the root public key. It does **not** verify that `response.payload_hash` is the canonical `SHA-256(borsh(ForeignTxSignPayload{request: request.request, values: ...}))` for the specific `request` being resolved. [1](#0-0) 

Contrast this with the regular `respond` function, which correctly derives `payload_hash` from the request itself — not from the response:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,
)
``` [2](#0-1) 

The `ForeignTxSignPayload` that nodes actually sign is `SHA-256(borsh({request: ForeignChainRpcRequest, values: Vec<ExtractedValue>}))`. The `request` field inside the payload encodes the specific `tx_id`, chain, and extractors. The contract receives only the 32-byte hash and cannot recompute it — but it also never attempts to bind the hash to the pending request's `tx_id`. [3](#0-2) 

The `pending_verify_foreign_tx_requests` map is keyed by `VerifyForeignTransactionRequest` (which includes `tx_id`, chain, domain, etc.), so the `request` argument must match a pending entry. However, the `response.payload_hash` is entirely free-floating — it is not bound to that key. [4](#0-3) 

### Impact Explanation

A bridge contract calls `verify_foreign_transaction` for Bitcoin `tx_id = X` to confirm that a specific inbound transfer occurred before releasing funds. A rogue attested participant calls `respond_verify_foreign_tx(request={tx_id=X, ...}, response={payload_hash=H_Y, signature=sig_Y})` where `H_Y` and `sig_Y` were obtained from a prior legitimate signing of a different transaction `tx_id = Y`. The contract accepts the call (signature over `H_Y` is valid under the root key), resolves the pending yield for `tx_id = X`, and delivers `{payload_hash: H_Y, signature: sig_Y}` to the bridge contract. The bridge contract receives a response that appears to be a valid MPC attestation for `tx_id = X` but actually attests to `tx_id = Y`. This enables invalid bridge execution or double-spend conditions.

This matches the allowed impact: **High — Forged foreign-chain verification / light-client-style verification bypass that causes invalid bridge execution or double-spend conditions.**

### Likelihood Explanation

A single Byzantine attested participant (below the signing threshold) can execute this attack. All prior `respond_verify_foreign_tx` calls are publicly visible on NEAR (transactions are public), so any participant can harvest `(payload_hash, signature)` pairs from historical on-chain data without needing to have participated in those signing rounds. The attacker only needs to wait for a pending request whose `request` key they can match, then replay any previously observed valid `(payload_hash, signature)` pair for a different transaction on the same chain/domain.

### Recommendation

The contract must bind `response.payload_hash` to the pending `request`. Two options:

1. **Include the full `ForeignTxSignPayload` in the response** so the contract can recompute `SHA-256(borsh(payload))` and verify it equals `response.payload_hash`, and also verify that `payload.request == request.request`.

2. **Have nodes sign a commitment that includes the NEAR receipt ID or the on-chain request key** so the `payload_hash` is cryptographically bound to the specific pending request and cannot be reused across requests.

The analogous fix in the original EVM report was to validate the nonce inside `validateUserOp` so that a signature cannot be replayed for a different operation. Here, the equivalent is to validate that `payload_hash` commits to the specific foreign transaction being attested.

### Proof of Concept

1. User submits `verify_foreign_transaction({chain: Bitcoin, tx_id: [0xAA;32], ...})` → pending request `R_A` is queued.
2. Attacker observes a prior on-chain `respond_verify_foreign_tx` call that resolved request `R_B` (Bitcoin `tx_id = [0xBB;32]`) with `response = {payload_hash: H_B, signature: sig_B}`.
3. Attacker (an attested participant) calls:
   ```
   respond_verify_foreign_tx(
     request = {chain: Bitcoin, tx_id: [0xAA;32], ...},  // matches pending R_A
     response = {payload_hash: H_B, signature: sig_B}    // replayed from R_B
   )
   ```
4. Contract checks: `verify_ecdsa_signature(sig_B, H_B, root_pk)` → **passes** (signature is valid).
5. Contract resolves `R_A`'s yield with `{payload_hash: H_B, signature: sig_B}`.
6. The caller waiting on `R_A` receives an attestation that claims `tx_id = [0xAA;32]` was verified, but `H_B` actually encodes `tx_id = [0xBB;32]` and its extracted values. [5](#0-4) [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L600-608)
```rust
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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L147-150)
```rust
pub struct VerifyForeignTransactionResponse {
    pub payload_hash: Hash256,
    pub signature: SignatureResponse,
}
```
