### Title
Unverified CKD Response for `AppPublicKey` Variant Allows Single Participant to Forge Confidential Key Derivation Output — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function fetches the current master public key from contract state but only uses it to validate responses for the `AppPublicKeyPV` variant. For the `AppPublicKey` (privately verifiable, legacy) variant, the caller-supplied `CKDResponse` (`big_y`, `big_c`) is accepted with **zero cryptographic validation**. A single Byzantine attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary forged response for any pending `AppPublicKey` CKD request, bypassing the threshold requirement entirely and delivering a forged key derivation output to the user.

---

### Finding Description

In `respond_ckd`, the contract correctly fetches the current master public key from authoritative state:

```rust
let PublicKeyExtended::Bls12381 {
    public_key: dtos::PublicKey::Bls12381(public_key),
} = self.public_key_extended(request.domain_id)?
```

But then immediately discards it for the `AppPublicKey` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no validation at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

The caller-supplied `CKDResponse` is then unconditionally forwarded to the user via `resolve_yields_for`. [2](#0-1) 

This is the direct structural analog to the external report's bug: the authoritative current state (master public key) is fetched but **not used** to validate the caller-supplied output values, exactly as `borrowIndex` was fetched but `amount` was never adjusted against it in `DebtToken.burn`.

By contrast, `respond` for signatures correctly verifies the signature against the current public key before accepting it: [3](#0-2) 

The `AppPublicKey` variant is the legacy default and is actively supported per the contract README. [4](#0-3) 

---

### Impact Explanation

A single Byzantine attested participant (below threshold) can:

1. Observe any pending `AppPublicKey` CKD request in `pending_ckd_requests`.
2. Call `respond_ckd` with arbitrary `big_y` and `big_c` values.
3. The contract accepts the forged response without any verification.
4. The user receives a forged key derivation output.

Because the attacker knows the user's public key (`app_public_key` is in the request), they can compute a valid-looking ElGamal-style encryption of a key they control under the user's public key. The user receives what appears to be a valid CKD output but is actually a key the attacker knows — enabling full key compromise of the derived secret.

This is a **threshold bypass**: instead of requiring t-of-n participants to cooperate in the MPC computation, a single participant unilaterally forges the output. This falls squarely under:

> *Critical. Unauthorized … confidential key derivation output without the required participant authorization.*
> *Critical. Bypass of threshold-signature requirements … that materially enables forgery or secret recovery.*

---

### Likelihood Explanation

- The `AppPublicKey` variant is the legacy default and is actively used.
- Any single attested participant can exploit this — no collusion, no threshold cooperation, no privileged operator access required.
- The attacker only needs to be an attested participant (TEE attestation), which is a reachable role for a Byzantine node strictly below the signing threshold.
- The attack requires no network-level capabilities and no knowledge of other participants' key shares.

---

### Recommendation

Apply `ckd_output_check` (or an equivalent BLS-based verification) to `AppPublicKey` requests as well, using the master public key already fetched from state. If on-chain verification is cryptographically impossible for the privately verifiable variant, the contract should require threshold-many participants to submit identical responses before resolving the yield, mirroring the threshold guarantee that the MPC computation is supposed to provide. Alternatively, deprecate `AppPublicKey` in favor of the publicly verifiable `AppPublicKeyPV` variant for all new requests.

---

### Proof of Concept

1. User submits `request_app_private_key` with `AppPublicKey` variant (legacy/privately verifiable).
2. Attested participant P1 (single node, below threshold t) calls `respond_ckd` with a forged `CKDResponse { big_y: [attacker_chosen_point], big_c: [attacker_computed_encryption] }`.
3. Contract reaches the `AppPublicKey(_) => {}` branch — no check is performed. [5](#0-4) 
4. `resolve_yields_for` delivers the forged response to the user's pending yield. [2](#0-1) 
5. User receives a key derivation output that the attacker controls, bypassing the t-of-n threshold requirement with a single participant.

### Citations

**File:** crates/contract/src/lib.rs (L583-644)
```rust
        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain)?;

        let signature_is_valid = match (&response, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                // generate the expected public key
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");
                let affine = *k256::PublicKey::try_from(&secp_pk)
                    .expect("stored key is always valid")
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
            }
            (
                dtos::SignatureResponse::Ed25519 { signature },
                PublicKeyExtended::Ed25519 {
                    edwards_point: public_key_edwards_point,
                    ..
                },
            ) => {
                let derived_public_key_edwards_point = derive_public_key_edwards_point_ed25519(
                    &public_key_edwards_point,
                    &request.tweak,
                );
                let derived_public_key_32_bytes =
                    dtos::Ed25519PublicKey::from(derived_public_key_edwards_point.compress());

                let message = request.payload.as_eddsa().expect("Payload is not EdDSA");

                near_mpc_signature_verifier::verify_eddsa_signature(
                    signature,
                    message,
                    &derived_public_key_32_bytes,
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
```

**File:** crates/contract/src/lib.rs (L668-682)
```rust
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
```

**File:** crates/contract/src/lib.rs (L684-688)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/contract/README.md (L119-121)
```markdown
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
- `domain_id` (integer): identifies the master key to use for deriving the ckd, and must correspond to bls12381.
```
