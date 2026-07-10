### Title
Missing On-Chain Output Validation for `AppPublicKey` CKD Variant Allows Single Malicious Participant to Forge Derived Key Response - (File: `crates/contract/src/lib.rs`)

### Summary
`respond_ckd` performs no cryptographic output verification when the request uses the `CKDAppPublicKey::AppPublicKey` variant. A single malicious attested participant (below the signing threshold) can call `respond_ckd` with an arbitrary `CKDResponse`, permanently resolving a user's pending CKD yield with a forged derived key.

### Finding Description
In `respond_ckd`, the contract branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, the contract calls `ckd_output_check`, which verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)` — a full cryptographic proof that the response was computed from the correct master secret key. [2](#0-1) 

For `AppPublicKey` (the legacy/default variant), the arm is an empty block `{}`. Any `CKDResponse` — regardless of its cryptographic relationship to the master key or the request — is unconditionally accepted and forwarded to the user via `resolve_yields_for`. [3](#0-2) 

The `AppPublicKey` variant is the default deserialization path (a plain G1 key string), making it the most commonly used form: [4](#0-3) 

### Impact Explanation
Once a malicious attested participant calls `respond_ckd` with a fabricated `(big_y, big_c)` pair, `resolve_yields_for` drains all queued yields for that request key and delivers the forged response to every waiting caller. The legitimate MPC leader's subsequent `respond_ckd` call finds no pending entry and silently fails. The user receives a `CKDResponse` that decrypts to a key that is **not** derived from the MPC master secret. If the user uses this key to receive or control assets on a foreign chain, those assets are permanently inaccessible (the real derived key is never revealed). This breaks the core safety invariant of the CKD flow: that the returned key is authentically derived from the threshold-held master secret.

### Likelihood Explanation
The `AppPublicKey` variant is the legacy default and is actively used in production (the `ckd-example-cli` README demonstrates it as the primary path). Any single TEE-attested participant — strictly below the signing threshold — can execute this attack. No threshold collusion is required. The attacker only needs to observe a pending `CKDRequest` on-chain (public state) and race the legitimate leader's `respond_ckd` call. Because NEAR transaction ordering is deterministic and the attacker is an on-chain participant, this race is practically winnable.

### Recommendation
Apply the same `ckd_output_check` pairing verification to the `AppPublicKey` variant, or — if on-chain verification is impossible without the G2 key — require callers to always use `AppPublicKeyPV`. At minimum, document that `AppPublicKey` provides no on-chain integrity guarantee and deprecate it in favour of `AppPublicKeyPV`.

### Proof of Concept
1. User submits `request_app_private_key` with `app_public_key = AppPublicKey(some_g1_point)` and `domain_id` pointing to a Bls12381 CKD domain.
2. The request is stored in `pending_ckd_requests` under the derived `CKDRequest` key (public on-chain state).
3. Malicious attested participant constructs an arbitrary `CKDResponse { big_y: random_g1, big_c: random_g1 }`.
4. Malicious participant calls `respond_ckd(request, forged_response)`. All precondition checks pass (signer check, protocol state, TEE attestation, domain type). The `AppPublicKey` match arm executes `{}` — no verification.
5. `resolve_yields_for` resolves all queued yields with the forged response and removes the entry from `pending_ckd_requests`.
6. The legitimate MPC leader's `respond_ckd` call now finds no pending entry and returns an error.
7. The user's NEAR callback receives the forged `CKDResponse`. Decrypting it yields a random scalar unrelated to the MPC master key. Any assets sent to the address derived from this scalar are permanently lost. [5](#0-4) [6](#0-5)

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

**File:** crates/contract/src/primitives/ckd.rs (L76-102)
```rust
/// Check that `e(big_c, g2) = e(big_y, app_pk2) . e(hash_point, public_key)`.
///
/// Point validation is fully delegated to the host, as in
/// [`app_public_key_check`].
pub(crate) fn ckd_output_check(
    app_id: &dtos::CkdAppId,
    output: &CKDResponse,
    app_public_key: &dtos::CKDAppPublicKeyPV,
    public_key: &dtos::Bls12381G2PublicKey,
) -> bool {
    let big_c = env::bls12381_p1_decompress(&output.big_c);
    let big_y = env::bls12381_p1_decompress(&output.big_y);
    let pk2 = env::bls12381_p2_decompress(&app_public_key.pk2);
    let pk = env::bls12381_p2_decompress(public_key);
    let hash_point = hash_app_id_with_pk(public_key.as_slice(), app_id.as_ref());

    let pairing_input = [
        big_c.as_slice(),
        MINUS_G2_GENERATOR_UNCOMPRESSED.as_slice(),
        big_y.as_slice(),
        pk2.as_slice(),
        hash_point.as_slice(),
        pk.as_slice(),
    ]
    .concat();
    env::bls12381_pairing_check(&pairing_input)
}
```

**File:** crates/near-mpc-crypto-types/src/ckd.rs (L15-27)
```rust
pub enum CKDAppPublicKey {
    AppPublicKey(Bls12381G1PublicKey),
    AppPublicKeyPV(CKDAppPublicKeyPV),
}

impl CKDAppPublicKey {
    pub fn g1_public_key(&self) -> &Bls12381G1PublicKey {
        match self {
            CKDAppPublicKey::AppPublicKey(pk) => pk,
            CKDAppPublicKey::AppPublicKeyPV(pv) => &pv.pk1,
        }
    }
}
```
