### Title
Single Malicious Attested Participant Can Deliver Fabricated CKD Response for `AppPublicKey` Requests, Bypassing Threshold Authorization — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` in `MpcContract` performs **no cryptographic verification** of the `CKDResponse` when the pending request uses the `AppPublicKey` (privately-verifiable, legacy) variant. A single malicious attested participant — strictly below the signing threshold — can call `respond_ckd` with an attacker-fabricated response, and the contract will deliver that response to every caller waiting on that request. This bypasses the threshold requirement for confidential key derivation and constitutes unauthorized CKD output without the required participant authorization.

---

### Finding Description

In `respond_ckd` (lines 653–689 of `crates/contract/src/lib.rs`), response verification is conditional on the `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← NO VERIFICATION
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For the `AppPublicKey` arm the match body is empty — the contract accepts any `CKDResponse` value unconditionally. Immediately after, `resolve_yields_for` removes the pending entry and resumes **all** queued yields with the unverified bytes:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

Contrast this with `respond` for signatures, which always verifies the signature cryptographically before calling `resolve_yields_for`: [3](#0-2) 

And with `respond_verify_foreign_tx`, which also always verifies the signature: [4](#0-3) 

The `AppPublicKey` variant is the legacy default, still accepted by the contract and documented as supported: [5](#0-4) 

The only guard on `respond_ckd` is `assert_caller_is_attested_participant_and_protocol_active`, which requires exactly **one** attested participant — not a threshold number: [6](#0-5) 

`resolve_yields_for` drains the entire fan-out queue in one call, so every duplicate submission of the same request receives the fabricated response: [7](#0-6) 

---

### Impact Explanation

A single malicious (or TEE-compromised) attested participant can:

1. Observe any pending `AppPublicKey` CKD request in `pending_ckd_requests`.
2. Call `respond_ckd` with an attacker-chosen `CKDResponse { big_y, big_c }`.
3. The contract accepts the response (no verification for `AppPublicKey`), removes the pending entry, and delivers the fabricated key material to every caller waiting on that request.
4. Users receive a derived key whose plaintext the attacker already knows, enabling decryption of any data the user subsequently encrypts with it.

This is **unauthorized confidential key derivation output without the required participant authorization** — a Critical impact under the allowed scope. The threshold MPC protocol is entirely bypassed at the contract layer for this request variant.

---

### Likelihood Explanation

**Medium.** The attacker must be an attested participant (TEE attestation required), which is a meaningful barrier. However:

- Only **one** of the n participants needs to be malicious or have a compromised TEE — strictly below the signing threshold.
- The `AppPublicKey` variant is the legacy default and is still accepted by the contract, so a large fraction of real CKD requests are affected.
- The attack is silent: the contract emits no error, the pending entry is cleaned up normally, and the victim receives a well-formed (but attacker-controlled) response.

---

### Recommendation

1. **Require `AppPublicKeyPV` for all new CKD requests.** Since `AppPublicKeyPV` carries a G2 component that enables on-chain verification via `ckd_output_check`, it closes the verification gap. Deprecate `AppPublicKey` with a migration path.
2. **If `AppPublicKey` must remain supported**, implement a threshold-based response collection: collect `CKDResponse` submissions from multiple participants and only call `resolve_yields_for` once a threshold of identical responses has been received, analogous to how `vote_pk` / `vote_reshared` accumulate votes before acting.
3. **Document the security limitation** prominently: callers using `AppPublicKey` currently rely entirely on the off-chain MPC protocol for response integrity; the contract provides no on-chain guarantee.

---

### Proof of Concept

```
1. Alice calls request_app_private_key({
       derivation_path: "alice/wallet",
       app_public_key: AppPublicKey(alice_g1_pk),   // legacy variant
       domain_id: 0
   })
   → pending_ckd_requests[CKDRequest{...}] = [YieldIndex{data_id: X}]

2. Malicious attested participant Eve calls respond_ckd(
       request = CKDRequest{ app_public_key: AppPublicKey(alice_g1_pk), ... },
       response = CKDResponse {
           big_y: eve_controlled_g1_point,   // fabricated
           big_c: eve_controlled_g1_point,   // fabricated
       }
   )
   → match AppPublicKey(_) => {}  // no check
   → resolve_yields_for resumes yield X with eve's fabricated bytes

3. Alice's sign() promise resolves with CKDResponse containing
   Eve's chosen key material. Alice uses it to encrypt secrets.
   Eve, knowing the plaintext of big_y/big_c, decrypts Alice's data.
```

The contract's `respond_ckd` path for `AppPublicKey` has no analog to the `verify_ecdsa_signature` / `verify_eddsa_signature` guards that protect `respond`, so the fabricated response passes through without any rejection signal.

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

**File:** crates/contract/src/lib.rs (L718-747)
```rust
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
```

**File:** crates/contract/src/lib.rs (L2389-2403)
```rust
    fn assert_caller_is_attested_participant_and_protocol_active(&self) {
        let participants = self.protocol_state.active_participants();

        Self::assert_caller_is_signer();

        let attestation_check = self
            .tee_state
            .is_caller_an_attested_participant(participants);

        assert_matches::assert_matches!(
            attestation_check,
            Ok(()),
            "Caller must be an attested participant"
        );
    }
```

**File:** crates/contract/README.md (L119-120)
```markdown
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
```

**File:** crates/contract/src/pending_requests.rs (L66-88)
```rust
pub(crate) fn resolve_yields_for<K>(
    requests: &mut LookupMap<K, Vec<YieldIndex>>,
    request: &K,
    response_bytes: Vec<u8>,
) -> Result<(), Error>
where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let resumed = requests
        .remove(request)
        .unwrap_or_default()
        .into_iter()
        .map(|YieldIndex { data_id }| {
            env::promise_yield_resume(&data_id, response_bytes.clone());
        })
        .count();

    if resumed > 0 {
        Ok(())
    } else {
        Err(InvalidParameters::RequestNotFound.into())
    }
}
```
