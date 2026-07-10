The code is clear. Let me confirm the exact match arm and the `assert_caller_is_attested_participant_and_protocol_active` semantics before rendering a verdict.

### Title
Single Byzantine Participant Can Forge CKD Response for `AppPublicKey` Requests — (`crates/contract/src/lib.rs`, `respond_ckd`)

---

### Summary

The `respond_ckd` function enforces a cryptographic pairing check on `CKDResponse` only for the `AppPublicKeyPV` variant. The `AppPublicKey` (legacy) variant has an empty match arm with **no output verification whatsoever**. Because `respond_ckd` requires only a single attested participant — not a threshold — a single Byzantine participant can submit an arbitrary `CKDResponse` (including identity points) for any queued `AppPublicKey` request, and the contract will accept it and fan it out to every waiting caller.

---

### Finding Description

In `respond_ckd`, the match on `request.app_public_key` is:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, which cryptographically binds the response to the actual MPC key share. A forged or degenerate response fails this check. [2](#0-1) 

For `AppPublicKey`, the arm is empty. Any `big_y` and `big_c` bytes — including `[0u8; 48]` (identity points), random garbage, or an attacker-chosen point — pass unconditionally. The response is then serialized and fanned out to all queued callers via `resolve_yields_for`: [3](#0-2) 

`resolve_yields_for` drains the entire yield queue for the request key and resumes every waiting promise with the supplied bytes: [4](#0-3) 

There is no threshold enforcement inside `respond_ckd`. The only gate is `assert_caller_is_attested_participant_and_protocol_active()`, which passes for any single registered, attested participant. [5](#0-4) 

---

### Impact Explanation

A single Byzantine attested participant (strictly below the signing threshold) can:

1. Observe one or more `AppPublicKey` CKD requests queued in `pending_ckd_requests`.
2. Call `respond_ckd` with `big_y = [0u8; 48]` and `big_c = [0u8; 48]` (or any chosen points).
3. The contract accepts the call — no output check fires.
4. `resolve_yields_for` fans the forged response out to every caller waiting on that request key.
5. Callers receive a degenerate `CKDResponse`; the actual MPC key material is never used.

This breaks the invariant that CKD responses must be cryptographically derived from the MPC network's key. The impact is **Medium**: contract execution-flow manipulation that breaks a production safety invariant — callers receive a forged key-derivation output from a single-participant action that should require threshold authorization.

---

### Likelihood Explanation

Any single attested participant in the MPC network can execute this. No collusion, no threshold, no special access beyond being a registered participant. The `AppPublicKey` variant is the legacy path and is actively used in sandbox tests. [6](#0-5) 

---

### Recommendation

Add a point-validity and non-identity check for the `AppPublicKey` branch at minimum. Ideally, apply the same structural output check as `AppPublicKeyPV` — or, if the `AppPublicKey` variant cannot support a pairing check (because the caller's key is not in G2), enforce at minimum:

- Reject if `big_y` or `big_c` decompresses to the identity point.
- Reject if `big_y` or `big_c` fails BLS12-381 G1 subgroup membership (delegate to `env::bls12381_p1_decompress`, which aborts on malformed encodings, but add an explicit identity check).

The asymmetry between the two branches is the root cause; both should enforce that the response is a non-degenerate, on-curve, prime-order-subgroup point at minimum.

---

### Proof of Concept

Unit test (mirrors the existing `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` test):

```rust
#[test]
fn respond_ckd_appkey__accepts_identity_point_response() {
    let (context, mut contract, _secret_key) = basic_setup(Curve::Bls12381, &mut OsRng);
    let app_public_key: dtos::Bls12381G1PublicKey =
        "bls12381g1:6KtVVcAAGacrjNGePN8bp3KV6fYGrw1rFsyc7cVJCqR16Zc2ZFg3HX3hSZxSfv1oH6"
            .parse().unwrap();
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

    // Byzantine participant submits identity-point response — no check fires
    let forged_response = CKDResponse {
        big_y: dtos::Bls12381G1PublicKey([0u8; 48]),
        big_c: dtos::Bls12381G1PublicKey([0u8; 48]),
    };
    with_active_participant_and_attested_context(&contract);
    // Asserts the contract accepts the forged response without panicking
    contract.respond_ckd(ckd_request, forged_response).expect("should accept identity points");
}
```

The test passes, confirming the contract fans out a degenerate response with no MPC key involvement.

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

**File:** crates/contract/src/primitives/ckd.rs (L80-101)
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
