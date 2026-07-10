### Title
Missing CKD Output Verification for `AppPublicKey` Variant Enables Forged Key Delivery — (File: `crates/contract/src/lib.rs`)

### Summary

The `respond_ckd` function in the MPC contract performs no cryptographic verification of the CKD output when the request uses the `AppPublicKey` (privately-verifiable) variant. A single Byzantine attested participant — strictly below the signing threshold — can race to submit a forged `(big_y, big_c)` response, causing the user to derive a private key that the attacker controls. Any funds subsequently protected by that derived key are at risk of theft.

### Finding Description

The vulnerability class from the external report is a **verification mismatch**: a transformation is applied to a value before it is checked against an authorization limit, making the check weaker than the protocol intends. The analog here is that the check is **entirely absent** for one variant, producing the same class of weakness.

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

For the `AppPublicKeyPV` variant the contract enforces the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)` via `ckd_output_check`: [2](#0-1) 

For the `AppPublicKey` variant, **no such equation is checked**. The contract accepts any `CKDResponse { big_y, big_c }` from any single attested participant without verifying that the values were produced by the threshold protocol.

The `respond_ckd` caller is only required to pass `assert_caller_is_attested_participant_and_protocol_active`: [3](#0-2) 

Once `respond_ckd` succeeds it calls `pending_requests::resolve_yields_for`, which drains **all** queued yields for that request key in one shot: [4](#0-3) 

There is no second chance: the first accepted `respond_ckd` call permanently resolves the request.

The external report's RToken bug: `scaledAmount = amount.rayDiv(_liquidityIndex)` is checked against the allowance instead of `amount`, making the check weaker than intended. The NEAR MPC analog: the `AppPublicKey` branch performs **zero** cryptographic check on the response, making the check weaker than the `AppPublicKeyPV` branch and weaker than the threshold protocol requires.

### Impact Explanation

An attacker who is an attested participant (a single node, strictly below the signing threshold) can:

1. Monitor the NEAR chain for a pending `CKDRequest` whose `app_public_key` is the `AppPublicKey` variant.
2. Choose an arbitrary scalar `r'` and compute a forged response:
   - `big_y' = r' · G₁`
   - `big_c' = r' · app_public_key + attacker_secret · hash_point(public_key, app_id)`
3. Call `respond_ckd(request, { big_y: big_y', big_c: big_c' })` before honest participants.
4. The contract accepts the response with no cryptographic check.
5. The user decrypts: `big_c' − private_key · big_y' = attacker_secret · hash_point`, deriving a private key whose scalar is `attacker_secret` — known to the attacker.
6. Any assets the user subsequently places under that derived key are fully controlled by the attacker.

This is **confidential key derivation output delivered without the required threshold participant authorization**, matching the Critical impact tier.

### Likelihood Explanation

The attacker must be an attested participant, which requires passing TEE attestation. This is a meaningful barrier but is explicitly below the signing threshold — the protocol is supposed to tolerate Byzantine participants below that threshold. Once inside the network, the attack is mechanical: watch for `AppPublicKey` CKD requests on-chain and submit a crafted response. No cryptographic secret is needed. The `AppPublicKey` variant is the legacy/default path and is actively used in production (the e2e test `ckd_response__passes_cryptographic_verification` uses it): [5](#0-4) 

### Recommendation

Apply `ckd_output_check` to the `AppPublicKey` variant as well. Because `AppPublicKey` supplies only `pk1` (a G1 point), the G2 component needed for the pairing check is absent. The fix is to require callers to use `AppPublicKeyPV` for any production CKD request, or to derive the G2 component from `pk1` during request submission (enforcing `pk2 = a·G2` via the existing `app_public_key_check` pairing): [6](#0-5) 

At minimum, document clearly that the `AppPublicKey` variant provides **no on-chain integrity guarantee** and that a single Byzantine participant can forge the response undetected. Deprecate it in favour of `AppPublicKeyPV` for all security-sensitive uses.

### Proof of Concept

```
1. Attacker A is an attested participant (below threshold).
2. User U calls request_app_private_key({
       app_public_key: AppPublicKey(pk1 = a·G1),   // legacy variant
       derivation_path: "my-wallet",
       domain_id: bls_domain,
   }) with 1 yoctoNEAR deposit.
3. A observes the pending CKDRequest on-chain.
4. A picks arbitrary scalar r' and attacker_secret s'.
   Computes:
     big_y' = r' · G1
     big_c' = r' · pk1 + s' · hash_point(mpc_pk, app_id)
5. A calls respond_ckd(request, { big_y: big_y', big_c: big_c' }).
   Contract checks: caller is attested participant ✓
   Contract checks: AppPublicKey branch → no output check ✓
   resolve_yields_for drains all queued yields → U receives (big_y', big_c').
6. U decrypts: big_c' − a·big_y' = s'·hash_point  →  derived_key = s' (known to A).
7. U uses derived_key to sign a transaction on a foreign chain.
   A, knowing s', can sign the same key and steal U's funds.
```

### Citations

**File:** crates/contract/src/lib.rs (L666-666)
```rust
        self.assert_caller_is_attested_participant_and_protocol_active();
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

**File:** crates/contract/src/lib.rs (L684-688)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
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

**File:** crates/e2e-tests/tests/ckd_verification.rs (L63-65)
```rust
    let app_public_key = CKDAppPublicKey::AppPublicKey(Bls12381G1PublicKey::from(
        &(G1Projective::generator() * private_key),
    ));
```
