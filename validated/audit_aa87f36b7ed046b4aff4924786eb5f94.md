### Title
`respond_verify_foreign_tx` Accepts Any Valid Payload Hash Regardless of Request Identity, Enabling Cross-Request Response Substitution — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_verify_foreign_tx` function verifies that the MPC signature is valid over `response.payload_hash`, but never verifies that `response.payload_hash` was actually computed from the specific `request` argument supplied in the same call. A single Byzantine attested participant (below signing threshold) can take a legitimately-produced `(payload_hash, signature)` pair from one resolved foreign-tx request and use it to resolve a completely different pending request, delivering forged extracted values to every caller waiting on that second request.

---

### Finding Description

In `respond_verify_foreign_tx` the contract performs two independent steps:

**Step 1 — signature check** (lines 718–743): verifies that `response.signature` is a valid ECDSA signature over `response.payload_hash` under the domain's root public key.

**Step 2 — yield resolution** (lines 749–753): calls `pending_requests::resolve_yields_for` to drain all queued yields for `request`, delivering `response` (which contains `payload_hash` and `signature`) to every waiting caller. [1](#0-0) 

The `payload_hash` is computed off-chain by MPC nodes as `ForeignTxSignPayloadV1 { request, values }.compute_msg_hash()`, where `values` are the chain-specific extracted values (block hash, log data, etc.). [2](#0-1) 

The contract **never recomputes** `payload_hash` from the `request` parameter it received, and it **never checks** that the hash it is verifying actually encodes that specific request. The two steps are completely decoupled: any `(payload_hash, signature)` pair that passes the root-key signature check is accepted as a valid response to any pending request.

This is the direct analog of the Uniswap TRST-H-7 bug: just as that contract read from the shared NonfungiblePositionManager pool position (aggregating all users) instead of the position-specific token-ID slot, this contract reads a shared/reusable `payload_hash` (valid for any request) instead of one that is cryptographically bound to the specific request being resolved.

The `respond_verify_foreign_tx` entry point requires only that the caller is an attested participant — no leader check, no threshold quorum. [3](#0-2) 

Because `resolve_yields_for` drains the **entire** queue for a request key on the first successful call, the Byzantine node only needs to win the race against honest nodes for the target request. [4](#0-3) 

---

### Impact Explanation

A bridge contract consuming the `VerifyForeignTransactionResponse` returned to callers of request B would receive `payload_hash_A` — a hash encoding the extracted values (amounts, block hashes, log data) of a completely different foreign transaction A. If the bridge uses those extracted values to credit a deposit or authorize a withdrawal, the attacker can substitute the response for a large-value transaction to satisfy a small-value (or fabricated) request, enabling theft or double-spend. Every caller whose yield was queued under request B is affected simultaneously.

This matches the allowed HIGH impact: *"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass, or participant/attestation authorization bypass that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

- Requires only **one** Byzantine attested participant — strictly below the signing threshold.
- The attacker needs no special capability beyond observing on-chain data: once an honest node submits `respond_verify_foreign_tx(request_A, {payload_hash_A, sig_A})`, the `(payload_hash_A, sig_A)` pair is permanently visible on-chain and reusable.
- The attack is a simple, deterministic front-run: submit `respond_verify_foreign_tx(request_B, {payload_hash_A, sig_A})` before honest nodes respond to request B.
- No threshold collusion, no TEE attacks, no social engineering, no network-level DoS required.

---

### Recommendation

Bind `payload_hash` to the specific request on-chain. The simplest fix is to include the extracted `values` in `VerifyForeignTransactionResponse` and have the contract independently recompute `payload_hash = ForeignTxSignPayloadV1 { request, values }.compute_msg_hash()`, then assert it equals `response.payload_hash` before accepting the response. This mirrors the fix in the Uniswap report: read the position-specific value (recomputed from the known request) rather than trusting the caller-supplied hash.

---

### Proof of Concept

1. User A submits `verify_foreign_transaction` for `request_A` (e.g., a Bitcoin tx depositing 10 BTC).
2. User B submits `verify_foreign_transaction` for `request_B` (e.g., a Bitcoin tx depositing 0.001 BTC).
3. Honest MPC nodes process `request_A` and post `respond_verify_foreign_tx(request_A, {payload_hash_A, sig_A})` on-chain. `payload_hash_A` encodes `(request_A, [BlockHash([0xAA;32])])`.
4. Byzantine attested participant reads `{payload_hash_A, sig_A}` from the NEAR chain.
5. Byzantine participant calls `respond_verify_foreign_tx(request_B, {payload_hash_A, sig_A})`.
6. Contract checks: is `sig_A` a valid signature over `payload_hash_A` under the root key? **Yes** — passes.
7. Contract calls `resolve_yields_for(&mut self.pending_verify_foreign_tx_requests, &request_B, serialize({payload_hash_A, sig_A}))` — drains all yields for `request_B`.
8. User B's NEAR contract receives `{payload_hash_A, sig_A}` — a response encoding the 10 BTC deposit's block hash and values, not their 0.001 BTC deposit.
9. Bridge contract credits User B with 10 BTC based on the forged extracted values, enabling theft. [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L3687-3693)
```rust
        let payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
            request: request.request.clone(),
            values: vec![ExtractedValue::BitcoinExtractedValue(
                BitcoinExtractedValue::BlockHash([42u8; 32].into()),
            )],
        });
        let payload_hash = payload.compute_msg_hash().unwrap().0;
```

**File:** crates/contract/src/pending_requests.rs (L1-14)
```rust
//! Storage and bookkeeping for pending request fan-out.
//!
//! Each pending-request map stores a `Vec<YieldIndex>` so that duplicate
//! submissions of the same request key queue up and all receive the same MPC
//! response. This module owns:
//!
//! * the cap on how many yields may be queued for a single key,
//! * the queue mutations (`push`, FIFO pop, drain),
//! * the read/write policy on the fan-out map: `push_pending_yield` appends,
//!   `resolve_yields_for` drains the full queue on a response, and
//!   `pop_oldest_pending_yield` removes the head entry on a timeout.
//!
//! Callers in `lib.rs` go through these helpers rather than touching the maps
//! directly, so the queue policy lives in one place.
```
