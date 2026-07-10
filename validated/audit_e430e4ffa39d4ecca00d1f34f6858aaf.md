### Title
Single Attested Participant Can Submit Fabricated CKD Response for `AppPublicKey` Requests, Bypassing Threshold Requirement - (`File: crates/contract/src/lib.rs`)

### Summary

`respond_ckd` performs no cryptographic verification of the response payload when the request uses the `AppPublicKey` (non-PV, legacy) variant. Any single attested participant — well below the signing threshold — can call `respond_ckd` with an arbitrary `CKDResponse`, and the contract will accept it and deliver the fabricated key material to the requesting user.

### Finding Description

`respond_ckd` dispatches on the `app_public_key` variant of the pending `CKDRequest`:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no verification
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For the `AppPublicKeyPV` variant, `ckd_output_check` verifies that the response is the correct MPC-derived output. For the `AppPublicKey` (legacy) variant, the arm is an empty block — the response is accepted unconditionally and immediately forwarded to the user via `resolve_yields_for`. [2](#0-1) 

The caller is gated only by `assert_caller_is_attested_participant_and_protocol_active`, which requires a single valid TEE attestation — not a threshold of participants. [3](#0-2) 

The `AppPublicKey` variant is explicitly documented as the "privately verifiable, legacy" path still accepted for backwards compatibility. [4](#0-3) 

### Impact Explanation

**Critical — Unauthorized confidential key derivation output without the required participant authorization; bypass of threshold-signature requirements.**

A `CKDResponse` is the MPC-derived secret key encrypted to the user's ephemeral `app_public_key`. Because `app_public_key` is a public value submitted on-chain with the request, any party can encrypt arbitrary key material to it. A malicious single participant can:

1. Observe a pending `request_app_private_key` request that uses the `AppPublicKey` variant (visible on-chain).
2. Generate an attacker-controlled key pair `(sk_attacker, pk_attacker)`.
3. Encrypt `sk_attacker` to the user's public `app_public_key`, forming a valid-looking `CKDResponse`.
4. Call `respond_ckd` with this fabricated response. The contract accepts it without verification.
5. The user decrypts the response and receives `sk_attacker` — a key the attacker already knows.
6. Any funds or secrets the user subsequently derives from or protects with this key are under the attacker's control.

This completely bypasses the reconstruction threshold (e.g., 2-of-3) that is supposed to govern key derivation outputs.

### Likelihood Explanation

**Medium.** The attacker must be an attested participant (requires a valid TEE attestation and membership in the active participant set). However, this is a reachable role — any current participant satisfies the precondition. Pending CKD requests are publicly observable on-chain. The attack requires no collusion, no leaked secrets, and no network-level access beyond normal NEAR transaction submission. The `AppPublicKey` variant remains in production for backwards compatibility, so the vulnerable code path is live.

### Recommendation

Apply the same `ckd_output_check` verification to the `AppPublicKey` variant that is already applied to `AppPublicKeyPV`. If public verifiability is not possible for the legacy variant, the contract should at minimum require that `respond_ckd` is called only after a threshold of participants have independently agreed on the same response (e.g., by collecting votes before resolving the yield), mirroring the threshold guarantee that governs `respond` for signatures.

Alternatively, deprecate and remove the `AppPublicKey` variant entirely, requiring all new requests to use `AppPublicKeyPV`.

### Proof of Concept

1. Alice calls `request_app_private_key` with `app_public_key: AppPublicKey(pk_alice)`. The request is stored in `pending_ckd_requests`.
2. Attacker (a single attested participant) observes the pending request on-chain, reads `pk_alice`.
3. Attacker generates `(sk_evil, pk_evil)` and computes `ct = Encrypt(pk_alice, sk_evil)`, forming `CKDResponse { ciphertext: ct }`.
4. Attacker calls `respond_ckd(request, fabricated_response)`.
5. `respond_ckd` passes the `assert_caller_is_attested_participant_and_protocol_active` check (attacker is a valid participant).
6. The `AppPublicKey(_) => {}` arm executes — no verification.
7. `resolve_yields_for` delivers `fabricated_response` to Alice's waiting yield.
8. Alice decrypts and receives `sk_evil`. The attacker knows `sk_evil` and can use it to steal any assets Alice derives from or protects with this key. [5](#0-4) [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L653-689)
```rust
    #[handle_result]
    pub fn respond_ckd(&mut self, request: CKDRequest, response: CKDResponse) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();
        log!("respond_ckd: signer={}, request={:?}", &signer, &request);

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        self.assert_caller_is_attested_participant_and_protocol_active();

        let PublicKeyExtended::Bls12381 {
            public_key: dtos::PublicKey::Bls12381(public_key),
        } = self.public_key_extended(request.domain_id)?
        else {
            env::panic_str("Domain is not compatible with CKD (expected Bls12381 curve)");
        };

        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
                if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
                    env::panic_str("CKD output check failed");
                }
            }
        }

        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```

**File:** crates/contract/README.md (L280-282)
```markdown
- `derivation_path` (String): the derivation path.
- `app_public_key`: the ephemeral public key to encrypt the generated confidential key. Accepts either a plain G1 point string (privately verifiable, legacy) or a tagged enum with `AppPublicKey` (single G1 point) or `AppPublicKeyPV` (a `{pk1, pk2}` pair for public verifiability).
- `domain_id` (integer): the domain ID that identifies the key and signature scheme to use to generate the confidential key
```
