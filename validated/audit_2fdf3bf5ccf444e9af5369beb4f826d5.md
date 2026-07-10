I have all the information needed. Let me analyze the exact code paths.

### Title
Missing CKD Output Verification for `AppPublicKey` Variant Allows Single Byzantine Participant to Forge Key Material for All Queued Callers — (`crates/contract/src/lib.rs`, `crates/contract/src/primitives/ckd.rs`)

---

### Summary

`respond_ckd` performs no cryptographic output verification when the request uses the `CKDAppPublicKey::AppPublicKey` variant. A single Byzantine attested participant can call `respond_ckd` with an arbitrary forged `CKDResponse`, and `resolve_yields_for` will drain the entire fan-out queue (up to 128 yields) with the attacker-controlled bytes in one call.

---

### Finding Description

In `respond_ckd` (`crates/contract/src/lib.rs:675-682`), the match on `request.app_public_key` has an empty arm for `AppPublicKey`:

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

For `AppPublicKeyPV`, `ckd_output_check` enforces the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, binding the response to the network public key and the caller's ephemeral key. [2](#0-1) 

For `AppPublicKey`, there is no analogous check. Any `CKDResponse` with syntactically valid BLS12-381 G1 points is accepted unconditionally.

After the (absent) check, `resolve_yields_for` removes the entire queue for the request key and calls `env::promise_yield_resume` for every entry: [3](#0-2) 

The queue cap is 128 entries: [4](#0-3) 

So a single `respond_ckd` call with a forged response resolves all 128 queued yields simultaneously.

The `AppPublicKey` variant is a live, documented production path (described as "privately verifiable (legacy)" in the contract README and supported by the CLI without any flag): [5](#0-4) 

---

### Impact Explanation

A Byzantine attested participant who calls `respond_ckd` with a chosen `(big_y, big_c)` pair:

1. Delivers attacker-controlled encrypted key material to every caller in the fan-out queue (up to 128 callers per call).
2. Because the attacker chose `big_y` and `big_c`, they know the corresponding plaintext secret — the callers' derived keys are fully compromised.
3. The yields are consumed; callers cannot retry the same request. They must submit new requests, which the attacker can forge again.

This is unauthorized confidential key derivation output delivered without threshold participant authorization — the threshold MPC computation is bypassed entirely by a single participant.

---

### Likelihood Explanation

The attacker must be a registered, TEE-attested MPC participant (`assert_caller_is_attested_participant_and_protocol_active` at lib.rs:666). [6](#0-5) 

This is explicitly within the allowed threat model: "Byzantine behavior strictly below the signing threshold." A single Byzantine node is below any practical threshold. The attacker does not need to be the designated leader for the request — any attested participant can call `respond_ckd` for any pending request.

---

### Recommendation

Add an output binding check for the `AppPublicKey` variant. Since `AppPublicKey` provides only a G1 point `A = a·G1` (no G2 component), the pairing equation used by `ckd_output_check` cannot be applied directly on-chain. Options:

1. **Deprecate `AppPublicKey` entirely** and require all callers to use `AppPublicKeyPV`, which provides the G2 component needed for on-chain verification. The README already labels `AppPublicKey` as "legacy."
2. **Require threshold agreement** before `respond_ckd` resolves yields — e.g., collect responses from a threshold of participants and only resolve when they agree, analogous to how signing requires threshold votes.
3. **Add a Schnorr/BLS proof of knowledge** for the `AppPublicKey` variant that binds `(big_y, big_c)` to the network public key and `app_id` without requiring the G2 component.

---

### Proof of Concept

```rust
// Queue 128 AppPublicKey CKD requests for the same key
let app_pk = CKDAppPublicKey::AppPublicKey(Bls12381G1PublicKey([1u8; 48]));
let ckd_request = CKDRequest::new(app_pk, domain_id, &predecessor, "path");
for _ in 0..128 {
    contract.request_app_private_key(CKDRequestArgs { ... });
}
assert_eq!(contract.pending_ckd_requests.get(&ckd_request).map(|q| q.len()), Some(128));

// Byzantine participant submits a completely forged response
with_active_participant_and_attested_context(&contract);
let forged = CKDResponse {
    big_y: Bls12381G1PublicKey([0xde; 48]),  // attacker-chosen
    big_c: Bls12381G1PublicKey([0xad; 48]),  // attacker-chosen
};
contract.respond_ckd(ckd_request.clone(), forged).unwrap();

// All 128 yields are drained with the forged bytes in one call
assert!(contract.pending_ckd_requests.get(&ckd_request).is_none());
// Every caller's yield-resume callback receives the attacker's (big_y, big_c)
```

The contract's existing test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` already demonstrates that arbitrary byte values `[1u8; 48]` / `[2u8; 48]` are accepted for `AppPublicKey` with no rejection: [7](#0-6)

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

**File:** crates/contract/src/lib.rs (L3404-3441)
```rust
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

**File:** crates/contract/src/pending_requests.rs (L24-37)
```rust
/// Maximum number of concurrent yield-resume promises that can be queued for a single
/// request key (i.e. the number of duplicate submissions whose responses fan out from
/// one MPC reply).
///
/// The ceiling is needed because `respond*` drains the entire queue in one call: every
/// queued yield triggers a host-side `promise_yield_resume`, paid for out of the
/// responder's 300 TGas budget. Without a cap, an attacker could enqueue enough
/// duplicates to make `respond*` run out of gas and strand every queued caller.
///
/// 128 is validated empirically by the sandbox test
/// `test_contract_request_duplicate_requests_fan_out`, which fills the queue to this
/// cap across all four signature schemes and confirms `respond*` drains it inside its
/// 300 TGas budget.
pub const MAX_PENDING_REQUEST_FAN_OUT: u8 = 128;
```

**File:** crates/contract/src/pending_requests.rs (L74-81)
```rust
    let resumed = requests
        .remove(request)
        .unwrap_or_default()
        .into_iter()
        .map(|YieldIndex { data_id }| {
            env::promise_yield_resume(&data_id, response_bytes.clone());
        })
        .count();
```

**File:** crates/contract/README.md (L118-120)
```markdown
- `app_public_key`: the ephemeral public key for the CKD request. Two formats are supported:
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
```
