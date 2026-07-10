### Title
Inconsistent Output Verification in `respond_ckd` Allows Forged CKD Responses for `AppPublicKey` Variant — (`File: crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` contract method applies fundamentally different output validation depending on which `CKDAppPublicKey` variant was used in the original request. For `AppPublicKeyPV` requests, a full BLS12-381 pairing-based cryptographic check is enforced before the response is delivered. For `AppPublicKey` requests, **no output verification is performed at all**. This is a direct structural analog to the reported Wise Lending issue: one code path uses a strict criterion (pairing check) while the parallel path uses a lenient criterion (no check), allowing a Byzantine attested participant below the signing threshold to inject an arbitrary forged CKD response for any pending `AppPublicKey` request.

---

### Finding Description

In `crates/contract/src/lib.rs`, the `respond_ckd` function (lines 653–689) branches on the request variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

For `AppPublicKeyPV`, `ckd_output_check` (defined in `crates/contract/src/primitives/ckd.rs`, lines 80–102) enforces the pairing equation:

```
e(big_c, g2) = e(big_y, app_pk2) · e(H(pk ‖ app_id), mpc_pk)
```

This cryptographically binds the response to the MPC network's master secret key and the user's app identity. For `AppPublicKey`, **no equivalent binding is checked**. The contract fetches the domain's BLS public key (line 668–673) but never uses it to verify the response.

The discrepancy is structural and mirrors the original report exactly:

| Code path | Criterion used |
|---|---|
| `AppPublicKeyPV` response | Full pairing check (strict) |
| `AppPublicKey` response | No check (lenient) |
| Wise Lending liquidation | `weightedCollateral` (strict) |
| Wise Lending withdrawal | `bareCollateral` (lenient) |

Any attested participant — a single Byzantine node below the signing threshold — can call `respond_ckd` with an arbitrary `CKDResponse { big_y, big_c }` for any pending `AppPublicKey` request. The contract will pass the `assert_caller_is_attested_participant_and_protocol_active()` guard (line 666) and immediately resolve the yield with the forged payload (lines 684–688), delivering it to the waiting user.

The `AppPublicKey` variant is the legacy/non-PV path and is actively used in production (see `crates/contract/tests/sandbox/sign.rs` and `crates/e2e-tests/tests/ckd_verification.rs`).

---

### Impact Explanation

A Byzantine attested participant below the signing threshold can corrupt any pending `AppPublicKey` CKD request by submitting arbitrary `(big_y, big_c)` values. The user receives these values via the yield/resume mechanism and computes `sig = big_c − a · big_y` (where `a` is their private scalar). Because the forged values do not satisfy the correct protocol equation, `sig` will not equal `msk · H(pk, app_id)`, and the derived key material is wrong. The user's application silently receives an incorrect private key with no on-chain indication of tampering.

This breaks the production safety invariant that every resolved CKD response is cryptographically bound to the MPC network's master secret. It is a request-lifecycle manipulation that causes incorrect key material to be delivered to users — matching the **Medium** allowed impact: *"request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants."*

---

### Likelihood Explanation

The attack requires only a single Byzantine attested participant (strictly below the signing threshold). The attacker does not need to collude with other participants, does not need to know the MPC master secret, and does not need to break TEE attestation at the hardware level — a software-level compromise of one node (e.g., a supply-chain attack on the node binary, a TEE software vulnerability, or a malicious insider) is sufficient. The `AppPublicKey` variant is the default/legacy path used by most existing integrations, maximizing the attack surface.

---

### Recommendation

Add output verification for the `AppPublicKey` variant. Since `AppPublicKey` does not carry a G2 component (`pk2`), the existing `ckd_output_check` pairing equation cannot be applied directly. Two options:

1. **Require a G2 witness at response time**: extend `CKDResponse` with an optional `pk2` field that the responding node must supply for `AppPublicKey` requests, enabling the same pairing check.
2. **Deprecate `AppPublicKey` in favour of `AppPublicKeyPV`**: enforce that all new requests use the publicly verifiable variant, which already has a full output check.

At minimum, add a comment in the `AppPublicKey` arm documenting that the absence of a check is a known limitation and that the variant is considered insecure against a Byzantine participant.

---

### Proof of Concept

1. User calls `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(A)` for domain `d`. A pending yield is stored in `pending_ckd_requests`.
2. Byzantine attested participant calls `respond_ckd(request, CKDResponse { big_y: [1u8;48], big_c: [2u8;48] })`.
3. The contract passes `assert_caller_is_attested_participant_and_protocol_active()` (line 666), enters the `AppPublicKey` arm (line 676), performs **no check**, and calls `pending_requests::resolve_yields_for` (line 684) with the forged payload.
4. The user's waiting transaction resumes with `big_y = [1u8;48]`, `big_c = [2u8;48]` — values that bear no relation to `msk · H(pk, app_id)`.
5. The user computes `sig = big_c − a · big_y`, obtains a random group element, and their derived key is permanently corrupted.

This is confirmed by the existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` (line 3404), which passes `big_y: [1u8;48], big_c: [2u8;48]` — demonstrably invalid BLS points — and the contract accepts them without error for the `AppPublicKey` variant. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
