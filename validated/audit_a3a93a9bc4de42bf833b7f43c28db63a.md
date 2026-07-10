### Title
Single Attested Participant Can Deliver Unverified CKD Output for Legacy `AppPublicKey` Requests — (`File: crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function in the MPC contract performs **no on-chain verification** of the `CKDResponse` payload when the user's request uses the legacy `AppPublicKey` variant. A single malicious attested participant (strictly below the signing threshold) can call `respond_ckd` with a completely fabricated `CKDResponse`, and the contract will accept it, drain the pending request queue, and deliver the fraudulent key to the user — without any threshold authorization.

---

### Finding Description

The `respond_ckd` function branches on the `app_public_key` field of the request: [1](#0-0) 

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← NO verification
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

For the `AppPublicKeyPV` variant, `ckd_output_check` cryptographically verifies that the encrypted key in the response is correctly derived from the MPC network's BLS12-381 master key and the user's ephemeral public key. For the legacy `AppPublicKey` variant, the match arm is **completely empty** — the response is accepted unconditionally.

After this branch, `resolve_yields_for` is called unconditionally: [2](#0-1) 

This drains the entire pending-request queue and delivers `serde_json::to_vec(&response)` — whatever the attacker supplied — to every waiting caller.

Compare this to `respond` for regular signatures, where the payload being signed is fixed by the on-chain request and the signature is verified against the derived public key: [3](#0-2) 

No equivalent binding exists for `respond_ckd` with `AppPublicKey`.

The `AppPublicKey` (legacy) variant is still documented and accepted by the contract: [4](#0-3) 

---

### Impact Explanation

A single malicious attested participant (one node, below the signing threshold) can:

1. Observe a pending CKD request that uses `AppPublicKey`.
2. Construct an arbitrary `CKDResponse` (e.g., a random BLS ciphertext, or a ciphertext encrypting a known-to-attacker key).
3. Call `respond_ckd` with the fabricated response.
4. The contract accepts it, removes the request from `pending_ckd_requests`, and delivers the fraudulent key to the user.

The user receives a key that was **not** produced by the threshold protocol. The threshold security guarantee — that no single participant can unilaterally produce a CKD output — is broken for all `AppPublicKey` requests. This matches the allowed Critical impact: *"Unauthorized… confidential key derivation output without the required participant authorization."*

---

### Likelihood Explanation

Any single attested participant can execute this attack. The MPC network is designed to tolerate up to `t-1` malicious participants; this vulnerability allows even one malicious participant to corrupt CKD outputs for the legacy variant. The `AppPublicKey` variant remains live and callable on mainnet. The attacker needs no special tooling beyond the ability to submit a NEAR transaction as an attested participant.

---

### Recommendation

Apply the same `ckd_output_check` verification to the `AppPublicKey` variant, or remove the legacy variant from the production contract. If the legacy variant cannot be verified on-chain (because the user's secret key is required), the contract should reject `AppPublicKey` requests entirely and require callers to migrate to `AppPublicKeyPV`, which supports publicly verifiable on-chain verification.

---

### Proof of Concept

1. User submits `request_app_private_key` with `app_public_key = AppPublicKey(some_bls_g1_point)`.
2. The request is queued in `pending_ckd_requests`.
3. Malicious attested participant constructs `CKDResponse { ... }` with arbitrary ciphertext bytes.
4. Malicious participant calls `respond_ckd(request, fabricated_response)`.
5. Contract executes:
   - `assert_caller_is_attested_participant_and_protocol_active()` — passes (caller is attested).
   - `match &request.app_public_key { AppPublicKey(_) => {} ... }` — empty arm, no check.
   - `resolve_yields_for(&mut self.pending_ckd_requests, &request, serde_json::to_vec(&fabricated_response))` — drains queue, delivers fabricated key.
6. User's yield callback fires with the fabricated `CKDResponse`. The user receives a key that was never produced by the threshold protocol.

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

**File:** crates/contract/src/lib.rs (L675-682)
```rust
        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
                if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
                    env::panic_str("CKD output check failed");
                }
            }
        }
```

**File:** crates/contract/src/lib.rs (L684-689)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```

**File:** crates/contract/README.md (L117-120)
```markdown
- `derivation_path` (String): the derivation path (used to derive different keys from the same account).
- `app_public_key`: the ephemeral public key for the CKD request. Two formats are supported:
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
```
