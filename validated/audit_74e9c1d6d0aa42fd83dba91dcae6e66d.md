### Title
Missing On-Chain CKD Response Verification for `AppPublicKey` Variant Allows Single Byzantine Participant to Corrupt or Control Derived Secret Material — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` enforces a cryptographic pairing check (`ckd_output_check`) on the response only when the `AppPublicKeyPV` variant is used. When the `AppPublicKey` (legacy) variant is used, the response is accepted with **zero cryptographic verification**. A single Byzantine attested participant — strictly below the signing threshold — can race to submit an arbitrary `CKDResponse` for any pending `AppPublicKey` request, causing the user to derive a wrong or fully attacker-controlled confidential key.

---

### Finding Description

The `respond_ckd` function in `crates/contract/src/lib.rs` contains the following branch:

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

For `AppPublicKeyPV`, `ckd_output_check` enforces the pairing equation `e(big_c, G2) = e(big_y, app_pk2) · e(H(pk, app_id), pk)`, which cryptographically binds the response to the MPC network's master secret key and the user's ephemeral public key. [2](#0-1) 

For `AppPublicKey`, **no analogous check exists**. The contract unconditionally calls `resolve_yields_for` with whatever `(big_y, big_c)` the caller supplied. [3](#0-2) 

This is structurally identical to the Argo bug: the wrapper (`argo_liquidate`) enforces the security check, but the underlying function (`argo_engine::liquidate_repay`) does not. Here, `AppPublicKeyPV` enforces the check, but `AppPublicKey` does not — and both share the same `respond_ckd` entry point callable by any attested participant.

The user's decryption step is:

```
sig = big_c − a · big_y
key = HKDF(sig)
```

If a Byzantine participant submits `big_y = G1_identity` (the identity point, a valid group element) and `big_c = P` for any chosen point `P`, then `a · big_y = 0` and `sig = P`. The attacker chose `P`, so they know `sig` and can compute `key = HKDF(P)` — fully recovering the user's confidential key.

The off-chain `decrypt_secret_and_verify` in the example CLI does verify the result: [4](#0-3) 

However, this verification is **not enforced by the contract** and is absent from the on-chain yield-resume path. Any application that consumes the CKD output without independently verifying it is vulnerable.

---

### Impact Explanation

A single Byzantine attested participant (below the signing threshold) can:

1. Observe a pending `AppPublicKey` CKD request in the contract's `pending_ckd_requests` map.
2. Race to call `respond_ckd` before the honest leader, supplying `big_y = G1_identity` and `big_c = P` for any chosen `P`.
3. The contract accepts the response without verification and resolves the yield.
4. The user receives `(G1_identity, P)` and computes `sig = P − a · G1_identity = P`.
5. The attacker, who chose `P`, computes `key = HKDF(P)` and recovers the user's confidential key.

This constitutes **unauthorized recovery of secret material derived by the MPC network**, bypassing the threshold requirement: normally t-of-n honest participants are required to produce a valid CKD output, but a single Byzantine participant can substitute an arbitrary, attacker-controlled output for `AppPublicKey` requests.

Matched allowed impact: *Critical — bypass of threshold-signature requirements or unauthorized access to secret material that materially enables secret recovery.*

---

### Likelihood Explanation

- Any single attested participant who turns Byzantine can exploit this immediately.
- The attacker only needs to submit `respond_ckd` before the honest leader. Since the contract resolves on the first call that matches a pending request key, a racing Byzantine node wins if it is faster.
- `AppPublicKey` is the default/legacy variant and is used by the reference CLI without the `--publicly-verifiable` flag, making it the common case. [5](#0-4) 

---

### Recommendation

1. **Deprecate `AppPublicKey`** in favor of `AppPublicKeyPV`, which has an enforceable on-chain pairing check. The contract README already labels `AppPublicKey` as "legacy."
2. If `AppPublicKey` must be retained, add a contract-level guard that rejects responses where `big_y` is the identity point, and prominently document that callers **must** run `decrypt_secret_and_verify` before trusting the derived key.
3. Alternatively, require all CKD requests to use `AppPublicKeyPV` so that `ckd_output_check` is always enforced on-chain, mirroring how `respond` always verifies the ECDSA/EdDSA signature before resolving the yield. [6](#0-5) 

---

### Proof of Concept

1. User calls `request_app_private_key` with `AppPublicKey` variant (any G1 point as the ephemeral key). A pending CKD request is stored in `pending_ckd_requests`.
2. Byzantine attested participant calls `respond_ckd` with:
   - `request` = the matching `CKDRequest` (observable on-chain)
   - `response.big_y` = compressed encoding of the G1 identity point
   - `response.big_c` = compressed encoding of any chosen G1 point `P`
3. `respond_ckd` passes the `AppPublicKey` branch with no check, calls `resolve_yields_for`, and the yield is resumed with the forged response.
4. The user's callback receives `(big_y=identity, big_c=P)` and computes `sig = P − a · identity = P`.
5. The attacker computes `key = HKDF(P)` and has recovered the user's confidential key. [7](#0-6) [8](#0-7)

### Citations

**File:** crates/contract/src/lib.rs (L586-644)
```rust
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

**File:** crates/ckd-example-cli/src/ckd.rs (L31-34)
```rust
    } else {
        let (scalar, pk) = generate_ephemeral_key(&mut OsRng);
        (scalar, CKDAppPublicKey::AppPublicKey(pk))
    };
```

**File:** crates/ckd-example-cli/src/ckd.rs (L117-138)
```rust
fn decrypt_secret_and_verify(
    big_y: &Bls12381G1PublicKey,
    big_c: &Bls12381G1PublicKey,
    private_key: Scalar,
    app_id: CkdAppId,
    mpc_public_key: &Bls12381G2PublicKey,
) -> Result<[u8; BLS12381G1_PUBLIC_KEY_SIZE]> {
    let big_y: G1Projective = big_y.try_into().context("invalid G1 point")?;
    let big_c: G1Projective = big_c.try_into().context("invalid G1 point")?;
    let mpc_public_key: G2Projective = mpc_public_key.try_into().context("invalid G2 point")?;

    // decrypt the secret
    let secret = big_c - big_y * private_key;

    // verify the secret
    if !verify(&mpc_public_key, app_id.as_ref(), &secret) {
        anyhow::bail!("Verification failed!");
    }

    // return the secret as bytes
    Ok(secret.to_compressed())
}
```
