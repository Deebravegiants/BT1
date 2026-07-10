### Title
`respond_ckd` Skips All Cryptographic Output Verification for `AppPublicKey` Requests, Allowing a Single Byzantine Participant to Forge a CKD Response — (`crates/contract/src/lib.rs`)

---

### Summary

In `respond_ckd`, when the pending CKD request carries an `AppPublicKey` (the "privately verifiable" variant), the contract performs **zero on-chain cryptographic verification** of the submitted response before resolving the yield and delivering the key to the caller. A single attested-but-Byzantine MPC participant can call `respond_ckd` with an arbitrary forged `CKDResponse`, and the contract will accept it unconditionally, bypassing the threshold-agreement safety invariant that governs all other MPC outputs.

---

### Finding Description

The structural analog to the LienToken bug is exact:

| LienToken (reference) | NEAR MPC (`respond_ckd`) |
|---|---|
| `s.auctionData` not populated → `stack.length == 0` | `AppPublicKey(_) => {}` — match arm is empty |
| Loop body never executes → no payment to vaults | No pairing/output check executes |
| Settlement (`settleAuction`) completes without obligation fulfillment | `resolve_yields_for` completes without cryptographic obligation fulfillment |

In `respond_ckd` the relevant code is:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← empty: no verification
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}

pending_requests::resolve_yields_for(          // ← always reached for AppPublicKey
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [1](#0-0) 

For comparison, `respond` (ECDSA) always verifies the signature against the derived public key before resolving: [2](#0-1) 

And `respond_ckd` for `AppPublicKeyPV` calls `ckd_output_check`, which performs a BLS12-381 pairing check `e(big_c, G2) = e(big_y, pk2) · e(H(app_id), pk)`: [3](#0-2) 

The `AppPublicKey` variant has no equivalent guard. The `CKDRequest` fields (`app_public_key`, `app_id`, `domain_id`) are all observable on-chain from `pending_ckd_requests`, so an attacker can construct the exact key needed to match a victim's pending request. [4](#0-3) 

---

### Impact Explanation

A single attested MPC participant (Byzantine, below threshold) can:

1. Observe any pending `AppPublicKey` CKD request on-chain.
2. Construct an arbitrary `CKDResponse { big_c: <forged>, big_y: <forged> }`.
3. Call `respond_ckd(request, forged_response)` — the contract accepts it with no cryptographic check.
4. The yield is resolved; the victim's TEE application receives a forged key.

The victim's application derives a wrong deterministic secret. Any data encrypted or authenticated with the expected key becomes inaccessible. The request is consumed (the yield slot is gone), so the victim must pay and retry. A persistent Byzantine node can repeat this for every `AppPublicKey` CKD request, making the CKD service unreliable for all users of the legacy variant.

This breaks the core threshold-agreement safety invariant: CKD outputs are supposed to require honest cooperation from a threshold of participants, but for `AppPublicKey` requests a single participant suffices to forge the output.

**Impact class**: Medium — request-lifecycle and contract execution-flow manipulation that breaks production safety/accounting invariants (threshold requirement for CKD) without requiring network-level DoS or operator misconfiguration. Potentially Critical if the forged key causes irreversible loss of secrets or funds in downstream TEE applications.

---

### Likelihood Explanation

- Requires the attacker to be an **attested MPC participant** — a meaningful barrier, but explicitly within the allowed attacker model ("Byzantine participant strictly below the signing threshold").
- The `CKDRequest` key is fully observable on-chain; no off-chain information is needed.
- The `AppPublicKey` variant is the **legacy/default** variant used by the example CLI when `--publicly-verifiable` is not passed, meaning it is the most common path in practice. [5](#0-4) 

---

### Recommendation

Apply the same on-chain verification discipline to `AppPublicKey` that already exists for `AppPublicKeyPV`. For the `AppPublicKey(pk)` arm, verify the response using the pairing identity:

```
e(big_c - a·big_y, G2) = e(H(app_id), pk_mpc)
```

where `pk_mpc` is the BLS12-381 G2 master public key. This check can be expressed with the existing `env::bls12381_pairing_check` host function, analogous to `ckd_output_check`. Alternatively, deprecate the `AppPublicKey` variant entirely and require all callers to use `AppPublicKeyPV`, which already has a sound on-chain guard.

---

### Proof of Concept

```rust
// Attacker is an attested participant. Victim has a pending AppPublicKey CKD request.
// Attacker reads the pending request from on-chain state:
let victim_request = contract.get_pending_ckd_request(&known_request_key).unwrap();

// Attacker forges an arbitrary response (no key material needed):
let forged_response = CKDResponse {
    big_y: dtos::Bls12381G1PublicKey([0xAA; 48]),
    big_c: dtos::Bls12381G1PublicKey([0xBB; 48]),
};

// Attacker calls respond_ckd — contract accepts with no verification:
contract
    .respond_ckd(victim_request, forged_response)
    .expect("accepted without any cryptographic check");

// Victim's yield is now resolved with the forged key.
// Victim's TEE application receives a wrong deterministic secret.
```

This is directly demonstrated by the existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists`, which passes `big_y: [1u8; 48]` and `big_c: [2u8; 48]` — cryptographically invalid points — and the contract accepts them without complaint: [6](#0-5)

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

**File:** crates/contract/src/lib.rs (L675-688)
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
```

**File:** crates/contract/src/lib.rs (L3403-3441)
```rust
    #[test]
    fn respond_ckd__should_succeed_when_response_is_valid_and_request_exists() {
        let (context, mut contract, _secret_key) = basic_setup(Curve::Bls12381, &mut OsRng);
        let app_public_key: dtos::Bls12381G1PublicKey =
            "bls12381g1:6KtVVcAAGacrjNGePN8bp3KV6fYGrw1rFsyc7cVJCqR16Zc2ZFg3HX3hSZxSfv1oH6"
                .parse()
                .unwrap();
        let request = CKDRequestArgs {
            derivation_path: "".to_string(),
            app_public_key: CKDAppPublicKey::AppPublicKey(app_public_key.clone()),
            domain_id: dtos::DomainId::default(),
        };
        let ckd_request = CKDRequest::new(
            CKDAppPublicKey::AppPublicKey(app_public_key),
            request.domain_id,
            &context.predecessor_account_id,
            &request.derivation_path,
        );
        contract.request_app_private_key(request);
        contract.get_pending_ckd_request(&ckd_request).unwrap();

        let response = CKDResponse {
            big_y: dtos::Bls12381G1PublicKey([1u8; 48]),
            big_c: dtos::Bls12381G1PublicKey([2u8; 48]),
        };

        with_active_participant_and_attested_context(&contract);

        match contract.respond_ckd(ckd_request.clone(), response.clone()) {
            Ok(_) => {
                contract
                    .return_ck_and_clean_state_on_success(ckd_request.clone(), Ok(response))
                    .detach();

                assert!(contract.get_pending_ckd_request(&ckd_request).is_none(),);
            }
            Err(_) => panic!("respond_ckd should not fail"),
        }
    }
```

**File:** crates/contract/src/primitives/ckd.rs (L8-30)
```rust
#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
#[near(serializers=[borsh, json])]
pub struct CKDRequest {
    /// The app ephemeral public key
    pub app_public_key: dtos::CKDAppPublicKey,
    pub app_id: dtos::CkdAppId,
    pub domain_id: DomainId,
}

impl CKDRequest {
    pub fn new(
        app_public_key: dtos::CKDAppPublicKey,
        domain_id: DomainId,
        predecessor_id: &AccountId,
        derivation_path: &str,
    ) -> Self {
        let app_id = derive_app_id(predecessor_id, derivation_path);
        Self {
            app_public_key,
            app_id,
            domain_id,
        }
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

**File:** crates/ckd-example-cli/src/ckd.rs (L25-34)
```rust
    let (ephemeral_private_key, app_public_key) = if args.publicly_verifiable {
        let (scalar, pk1, pk2) = generate_ephemeral_key_pv(&mut OsRng);
        (
            scalar,
            CKDAppPublicKey::AppPublicKeyPV(CKDAppPublicKeyPV { pk1, pk2 }),
        )
    } else {
        let (scalar, pk) = generate_ephemeral_key(&mut OsRng);
        (scalar, CKDAppPublicKey::AppPublicKey(pk))
    };
```
