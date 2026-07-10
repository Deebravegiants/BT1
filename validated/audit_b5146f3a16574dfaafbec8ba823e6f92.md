### Title
Missing On-Chain CKD Output Verification for `AppPublicKey` Variant Allows Single Byzantine Participant to Corrupt and Drain CKD Response Queue — (`crates/contract/src/lib.rs`)

---

### Summary

In `respond_ckd`, the cryptographic output check (`ckd_output_check`) is only invoked for the `AppPublicKeyPV` variant. The `AppPublicKey` (legacy) arm is an explicit no-op. A single attested participant can therefore call `respond_ckd` with arbitrary `big_y` / `big_c` values for any in-flight `AppPublicKey` request, and the contract will accept the call, drain the entire fan-out queue, and deliver the unverified garbage to every queued caller — permanently consuming the pending request slot before the honest MPC leader can respond.

---

### Finding Description

`respond_ckd` in `crates/contract/src/lib.rs` dispatches on the variant of `app_public_key` embedded in the `CKDRequest`:

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

For `AppPublicKeyPV`, `ckd_output_check` verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(H(app_id, pk), pk)`, binding the output to both the requester's ephemeral key and the master BLS key. [2](#0-1) 

For `AppPublicKey`, the arm is empty — any `CKDResponse` bytes pass unconditionally. After the match, `resolve_yields_for` is called unconditionally, which drains **all** queued yield-resume promises for that request key in a single pass: [3](#0-2) 

Once drained, any subsequent honest `respond_ckd` call for the same request returns `RequestNotFound`.

The only gate before the match is `assert_caller_is_attested_participant_and_protocol_active`, which requires the caller to be a registered, TEE-attested participant — a single participant, not a threshold quorum. [4](#0-3) 

The existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` already demonstrates the exact exploit path: it submits `big_y = [1u8; 48]` and `big_c = [2u8; 48]` (invalid curve points / garbage) against an `AppPublicKey` request and asserts the call succeeds and the pending queue is fully drained: [5](#0-4) 

---

### Impact Explanation

A single Byzantine attested participant (strictly below the signing threshold) can:

1. Observe any `request_app_private_key` call that uses the `AppPublicKey` variant (all parameters are public on-chain).
2. Race to call `respond_ckd` with arbitrary `big_y` / `big_c` before the honest MPC leader.
3. The contract accepts the call, fans out the garbage response to every queued caller, and removes the pending-request entry.
4. The honest leader's subsequent `respond_ckd` fails with `RequestNotFound`.
5. Every caller that queued under that request key receives a cryptographically invalid CKD output — one that is not bound to the `app_id` or the master BLS key.

This breaks the production invariant that a CKD output delivered by the contract is the result of a threshold computation over the master key share. The `AppPublicKey` variant is still actively supported (not deprecated) and is the default legacy path shown in the contract README and the e2e test suite. [6](#0-5) 

---

### Likelihood Explanation

- **Attacker prerequisite**: Must be a registered, TEE-attested participant. This is a meaningful barrier but is strictly below the threshold — one compromised or malicious node suffices.
- **Race condition**: The attacker must submit before the honest leader. Because `CKDRequest` is deterministic from public parameters (`app_public_key`, `domain_id`, `app_id`), the attacker can compute the exact request key from on-chain data and submit immediately after observing the user's `request_app_private_key` transaction.
- **No cryptographic work required**: The attacker does not need to know any key share or perform any MPC computation — any 48-byte values for `big_y` and `big_c` are accepted.

---

### Recommendation

Apply `ckd_output_check` for the `AppPublicKey` variant as well. For the legacy single-G1-point case, a weaker but still binding check is possible: verify that `e(big_c, g2) = e(big_y, g2) · e(H(app_id, pk), pk)` (substituting `g2` for the missing `app_pk2`). Alternatively, deprecate and remove the `AppPublicKey` variant entirely, requiring all callers to migrate to `AppPublicKeyPV`, which already has full on-chain verification.

---

### Proof of Concept

The existing test at `crates/contract/src/lib.rs:3404` already constitutes a complete proof of concept. It:

1. Submits `request_app_private_key` with `CKDAppPublicKey::AppPublicKey`.
2. Calls `respond_ckd` with `big_y = [1u8; 48]` and `big_c = [2u8; 48]` (garbage).
3. Asserts `Ok(())` is returned.
4. Asserts the pending queue is fully drained (`get_pending_ckd_request` returns `None`). [7](#0-6) 

No additional test construction is required — the codebase already proves the invariant is broken.

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

**File:** crates/contract/src/pending_requests.rs (L62-88)
```rust
/// Resume every yield queued for `request` with `response_bytes`, draining the
/// fan-out map in one pass. Returns `Err(RequestNotFound)` if the map held no entry.
///
/// Resuming a yield that has already timed out is a no-op at the SDK level.
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

**File:** crates/contract/README.md (L119-120)
```markdown
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
```
