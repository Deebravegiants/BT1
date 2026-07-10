### Title
Unvalidated `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Forged Foreign-Chain Verification - (File: crates/contract/src/lib.rs)

---

### Summary

`respond_verify_foreign_tx` accepts a caller-supplied `response.payload_hash` and only checks that the provided signature is valid over that hash using the root public key. It never validates that `response.payload_hash` was actually derived from the `request` fields. A single Byzantine MPC participant (below threshold) who is the leader for one signing round can reuse a legitimately-obtained signature to resolve a *different* pending request with a forged payload hash, causing users to receive a verification response that does not correspond to their submitted foreign-chain transaction.

---

### Finding Description

In `respond_verify_foreign_tx` (lines 691–754 of `crates/contract/src/lib.rs`), the contract performs the following check:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;   // line 726 – attacker-controlled

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

The contract then resolves all pending yields for `request` with the full `response` (including the unvalidated `payload_hash`):

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

The `VerifyForeignTransactionResponse` struct carries `payload_hash` as a free field alongside `signature`: [3](#0-2) 

The `VerifyForeignTransactionRequest` (the map key) contains the original foreign-chain RPC request details: [4](#0-3) 

The contract never computes the expected `payload_hash = SHA-256(borsh(ForeignTxSignPayload{request, extracted_values}))` from the stored `request` and cross-checks it against `response.payload_hash`. This is the missing data-validation step.

By contrast, the regular `respond` function correctly derives the expected public key from the request's tweak before verifying: [5](#0-4) 

---

### Impact Explanation

A single Byzantine MPC participant below the signing threshold who acts as the leader for signing round R1 obtains a valid threshold signature σ₁ over hash H₁ (the correct payload hash for foreign-chain transaction T1). That participant then calls `respond_verify_foreign_tx(R2, {payload_hash: H₁, signature: σ₁})` for a *different* pending request R2 (for transaction T2).

The contract accepts this call because:
1. The caller is an attested participant — `assert_caller_is_attested_participant_and_protocol_active()` passes. [6](#0-5) 
2. σ₁ is a valid ECDSA signature over H₁ using the root key — the only check performed.
3. R2 is present in `pending_verify_foreign_tx_requests` — `resolve_yields_for` succeeds.

All users who submitted R2 receive `{payload_hash: H₁, signature: σ₁}` — a response that encodes T1's extracted values, not T2's. Any downstream bridge contract or application that trusts this response without independently recomputing the expected hash will execute based on false foreign-chain state, enabling invalid bridge execution or double-spend conditions. R1's yields are left unresolved and eventually time out.

**Impact class**: High — forged foreign-chain verification causing invalid bridge execution.

---

### Likelihood Explanation

- Requires one Byzantine MPC participant below threshold who is elected leader for at least one signing round while another request is concurrently pending. Leader election is deterministic (lowest participant ID), so a malicious node can predict when it will be leader.
- No threshold collusion, no key leakage, no TEE break, and no network-level DoS is required.
- The attack is executable in a single on-chain transaction after the malicious leader has participated in one legitimate signing round.
- Likelihood: **Medium** — depends on the attacker being a registered, attested participant and being elected leader, both of which are realistic in a production deployment.

---

### Recommendation

The contract should derive the expected `payload_hash` from the `request` fields and the `extracted_values` included in the response, then assert equality before accepting the response. Concretely:

1. Include `extracted_values` in `VerifyForeignTransactionResponse` (they are already part of `ForeignTxSignPayload` on the node side).
2. In `respond_verify_foreign_tx`, recompute `expected_hash = SHA-256(borsh(ForeignTxSignPayload{request: request.request, values: response.extracted_values}))` and assert `expected_hash == response.payload_hash` before the signature check.

This mirrors how `respond` binds the signature to the request via the derived key tweak, ensuring the response is cryptographically tied to the specific request.

---

### Proof of Concept

**Setup**: Two pending requests R1 (Bitcoin tx T1) and R2 (Bitcoin tx T2) are queued in `pending_verify_foreign_tx_requests`. Malicious node M is the leader for R1's signing round.

1. M coordinates the MPC signing protocol for R1. All threshold nodes independently verify T1 on Bitcoin and agree on `H1 = SHA-256(borsh(ForeignTxSignPayload{request: R1.request, values: [block_hash_of_T1]}))`. The network produces σ₁ over H₁.

2. Instead of calling `respond_verify_foreign_tx(R1, {payload_hash: H1, signature: σ1})`, M calls:
   ```
   respond_verify_foreign_tx(R2, {payload_hash: H1, signature: σ1})
   ```

3. Contract execution path:
   - `assert_caller_is_attested_participant_and_protocol_active()` → passes (M is attested).
   - `verify_ecdsa_signature(σ1, H1, root_pk)` → passes (σ₁ is a valid signature over H₁).
   - `resolve_yields_for(&mut pending_verify_foreign_tx_requests, &R2, serialize({payload_hash: H1, signature: σ1}))` → resolves all R2 yields.

4. Users who submitted R2 (for T2) receive `{payload_hash: H1, signature: σ1}`. H₁ encodes T1's block hash, not T2's. Any bridge contract consuming this response without locally recomputing the expected hash will act on falsified foreign-chain data.

5. R1's yields time out. R2 has been fraudulently resolved. The malicious node has caused forged foreign-chain verification with a single below-threshold participant. [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L596-608)
```rust
                    .as_affine();
                let expected_public_key =
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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L147-150)
```rust
pub struct VerifyForeignTransactionResponse {
    pub payload_hash: Hash256,
    pub signature: SignatureResponse,
}
```
