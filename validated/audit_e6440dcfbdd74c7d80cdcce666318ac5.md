### Title
Single Attested Participant Can Forge CKD Responses for `AppPublicKey` Variant, Bypassing Threshold Requirement — (`crates/contract/src/lib.rs`)

---

### Summary

In `respond_ckd`, when the pending CKD request uses the `CKDAppPublicKey::AppPublicKey` variant, the contract performs **no cryptographic verification** of the submitted `CKDResponse`. A single attested participant (strictly below the signing threshold) can submit an arbitrary, attacker-crafted response for any pending CKD request. The forged response is delivered to the user as if it were a legitimate threshold-computed output, enabling the attacker to supply key material they control.

---

### Finding Description

The `respond_ckd` function in `crates/contract/src/lib.rs` contains a match on `request.app_public_key`:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← empty: no verification
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For the `AppPublicKeyPV` variant, `ckd_output_check` verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(H(app_id), pk)` on-chain, ensuring the response is a valid threshold output. [2](#0-1) 

For the `AppPublicKey` variant, the match arm is empty (`{}`). The contract accepts and delivers any `CKDResponse` — arbitrary `big_y` and `big_c` BLS12-381 G1 points — without any check. [3](#0-2) 

The CKD decryption formula the user applies is:

```
derived_key = big_c − a · big_y
```

where `a` is the user's private key and `A = a·G1` is their submitted public key. If an attacker submits `big_y = G1_identity` (the identity point, which is a valid group element) and `big_c = attacker_scalar · G1`, the user decrypts:

```
attacker_scalar · G1 − a · 0 = attacker_scalar · G1
```

The user receives `attacker_scalar · G1` as their "derived key", and the attacker knows the corresponding scalar `attacker_scalar`. The attacker has thus replaced the legitimate MPC-derived secret with one they control.

The attacker entry path is:
1. Any user calls `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(A)`.
2. A single malicious attested participant calls `respond_ckd` with a crafted `CKDResponse{big_y: identity, big_c: attacker_point}`.
3. `assert_caller_is_attested_participant_and_protocol_active()` passes (the attacker is a legitimate participant).
4. The empty match arm passes with no verification.
5. `pending_requests::resolve_yields_for` delivers the forged response to the user. [4](#0-3) 

This is structurally identical to the M-01 pattern: a verification path that silently returns "valid" (empty arm, analogous to returning `address(0)`) instead of reverting, and the result is used directly in a security-critical operation (delivering key material to the user).

---

### Impact Explanation

**Critical.** A single attested participant — strictly below the signing threshold — can forge a CKD response for any pending `AppPublicKey` request. The user receives attacker-controlled key material indistinguishable from a legitimate threshold output. This constitutes:

- **Unauthorized confidential key derivation output** without the required threshold of participant authorization.
- **Key theft**: the attacker knows the scalar corresponding to the delivered "key", enabling them to impersonate the user in any application that relies on the derived key.

The threshold security model of CKD is completely bypassed for the `AppPublicKey` variant.

---

### Likelihood Explanation

**Medium.** The attacker must be an attested participant (a TEE-attested node in the active participant set). This is a real operational role, not a hypothetical one. Crucially, only **one** such participant needs to be Byzantine — no threshold collusion is required. The `AppPublicKey` variant is the default/legacy variant and is actively used in production (as evidenced by the test at line 3404). [5](#0-4) 

---

### Recommendation

Add cryptographic verification for the `AppPublicKey` variant. Since the user's private key `a` is not available on-chain, the contract cannot verify the full decryption. However, it can enforce that the response is a valid BLS12-381 G1 point pair consistent with the network public key, using a zero-knowledge proof of correct encryption (similar to the `AppPublicKeyPV` pairing check). Alternatively, deprecate the `AppPublicKey` variant and require all CKD requests to use `AppPublicKeyPV`, which has on-chain verifiable output.

At minimum, add a guard that rejects the identity point for `big_y` and `big_c`, and consider requiring the `AppPublicKeyPV` variant for all new requests.

---

### Proof of Concept

1. User submits `request_app_private_key` with `app_public_key = AppPublicKey(A)` where `A = a·G1`.
2. Attacker (single attested participant) observes the pending request on-chain.
3. Attacker picks scalar `s` and calls `respond_ckd` with:
   - `request` matching the pending request
   - `response = CKDResponse { big_y: G1_identity, big_c: s·G1 }`
4. Contract executes `assert_caller_is_attested_participant_and_protocol_active()` — passes.
5. Match arm `AppPublicKey(_) => {}` — no verification, passes.
6. `resolve_yields_for` delivers `{big_y: 0, big_c: s·G1}` to the user.
7. User decrypts: `s·G1 − a·0 = s·G1`. User's derived "secret" is `s·G1`.
8. Attacker knows `s`, so they know the user's derived key. The attacker can now impersonate the user in any application using this key. [6](#0-5) [2](#0-1)

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
