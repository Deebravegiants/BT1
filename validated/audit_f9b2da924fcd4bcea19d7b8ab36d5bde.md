### Title
Missing CKD Response Verification for `AppPublicKey` (Privately Verifiable) Variant Allows Single Byzantine Participant to Inject Fabricated Key Material - (`crates/contract/src/lib.rs`)

### Summary

`respond_ckd` applies cryptographic output verification only for the `AppPublicKeyPV` (publicly verifiable) variant of CKD requests. For the `AppPublicKey` (privately verifiable / legacy) variant, the match arm is empty and no verification is performed. A single Byzantine attested participant — strictly below the signing threshold — can race to call `respond_ckd` with a fabricated `CKDResponse` before honest nodes, causing every caller waiting on that request to receive attacker-controlled key material instead of the correct MPC-derived key.

### Finding Description

`respond_ckd` in `crates/contract/src/lib.rs` handles two variants of CKD requests:

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

For `AppPublicKeyPV`, `ckd_output_check` enforces the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, which can only be satisfied by a response produced by the correct threshold CKD protocol execution. [2](#0-1) 

For `AppPublicKey`, the arm is empty. The contract unconditionally accepts whatever `(big_c, big_y)` the caller supplies and immediately resolves all queued yields for that request key via `resolve_yields_for`. [3](#0-2) 

The `AppPublicKey` variant is the legacy/default format and is the one most callers use (plain G1 point, no `pk2`). [4](#0-3) 

The only guards on `respond_ckd` are: caller is a signer, protocol is running, `accept_requests` is true, and caller is an attested participant. There is no check that the response was produced by threshold-many participants, and no cryptographic binding to the correct output for the `AppPublicKey` variant. [5](#0-4) 

### Impact Explanation

The CKD protocol computes `big_c = r·A + H(pk, app_id)·msk` and `big_y = r·G1`, where `A = a·G1` is the app's ephemeral public key and `msk` is the MPC master secret. The app decrypts `big_c − a·big_y = H(pk, app_id)·msk`, which is the correct derived key.

If an attacker supplies arbitrary `big_c = k·G1` and `big_y = 0·G1` (or any fabricated pair), the app decrypts `k·G1 − a·0 = k·G1`, an attacker-chosen value. The app has no way to detect this because it does not know what the correct output should be — that is the entire point of the confidential derivation.

Every caller whose yield is queued under the same request key receives the fabricated response simultaneously (fan-out drain). This constitutes unauthorized confidential key derivation output delivered without the required threshold-participant authorization.

### Likelihood Explanation

Any single attested participant who turns Byzantine can exploit this. The attacker only needs to:
1. Monitor the chain for `request_app_private_key` calls using the `AppPublicKey` variant.
2. Call `respond_ckd` with a fabricated `CKDResponse` before honest nodes submit the real one.
3. The contract resolves the request immediately; subsequent honest `respond_ckd` calls return `RequestNotFound`.

No threshold collusion is required. The `AppPublicKey` variant is the legacy default, so it is the common case in production.

### Recommendation

For the `AppPublicKey` variant, the contract cannot perform the same pairing-based output check (there is no `pk2`). Two mitigations are possible:

1. **Deprecate `AppPublicKey` in favor of `AppPublicKeyPV`** for all new requests, so the on-chain pairing check is always enforced.
2. **Add a minimum validity check** for the `AppPublicKey` arm: reject responses where `big_c` or `big_y` are the identity point or fail G1 subgroup membership, and document clearly that privately verifiable requests carry weaker on-chain guarantees.

The asymmetry between the two variants should be explicitly documented as a security boundary, not left as a silent empty match arm.

### Proof of Concept

1. Deploy the contract with a BLS12-381 CKD domain.
2. Attacker registers as an attested participant (legitimate node).
3. Victim calls `request_app_private_key` with `AppPublicKey` variant (legacy G1 point).
4. Before honest nodes respond, attacker calls:
   ```json
   respond_ckd(
     request = <victim's CKDRequest>,
     response = { "big_c": "<arbitrary G1 point>", "big_y": "<arbitrary G1 point>" }
   )
   ```
5. Contract executes the `AppPublicKey` arm (empty, no check), calls `resolve_yields_for`, and delivers the fabricated response to the victim.
6. Victim's TEE app decrypts the fabricated `(big_c, big_y)` and derives an attacker-controlled key, believing it to be the correct MPC-derived secret. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L653-666)
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
```

**File:** crates/contract/src/lib.rs (L675-689)
```rust
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

**File:** crates/contract/src/primitives/ckd.rs (L62-74)
```rust
pub(crate) fn app_public_key_check(app_public_key: &dtos::CKDAppPublicKeyPV) -> bool {
    let pk1 = env::bls12381_p1_decompress(&app_public_key.pk1);
    let pk2 = env::bls12381_p2_decompress(&app_public_key.pk2);

    let pairing_input = [
        pk1.as_slice(),
        MINUS_G2_GENERATOR_UNCOMPRESSED.as_slice(),
        G1_GENERATOR_UNCOMPRESSED.as_slice(),
        pk2.as_slice(),
    ]
    .concat();
    env::bls12381_pairing_check(&pairing_input)
}
```

**File:** crates/contract/src/primitives/ckd.rs (L80-102)
```rust
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
