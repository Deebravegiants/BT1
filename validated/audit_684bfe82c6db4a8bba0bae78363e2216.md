### Title
Single Attested Participant Can Deliver Fabricated CKD Output for `AppPublicKey` Requests Without Threshold Authorization - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` in the MPC contract performs no cryptographic output verification for the `AppPublicKey` variant of CKD requests. Any single attested participant — well below the signing threshold — can call `respond_ckd` with an entirely fabricated `CKDResponse`, and the contract will accept it and deliver it to the waiting user. This is the direct analog of the Witch `payAll`/`buy` bug: a function that should only succeed when the response is a genuine threshold-protocol output instead succeeds for any caller-supplied value, bypassing the threshold requirement entirely.

---

### Finding Description

`respond_ckd` in `crates/contract/src/lib.rs` dispatches on the `app_public_key` variant of the pending request:

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

For the `AppPublicKeyPV` variant, `ckd_output_check` enforces the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, which cryptographically binds the response to the network's master secret key and the user's app public key. [2](#0-1) 

For the `AppPublicKey` variant, the arm is empty — no pairing check, no binding to the network key, no binding to the user's app public key. The contract proceeds directly to `resolve_yields_for`, serializing and delivering whatever `big_y` and `big_c` the caller supplied. [3](#0-2) 

The existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` confirms this: it passes `[1u8; 48]` and `[2u8; 48]` — clearly invalid BLS12-381 points — as the response, and the test passes without error. [4](#0-3) 

---

### Impact Explanation

**Critical. Unauthorized confidential key derivation output without the required participant authorization.**

The CKD protocol is designed so that the user's derived key is `hash_point * msk`, where `msk` is the network's distributed master secret. No single participant knows `msk`; it requires threshold cooperation to produce a valid `big_c`.

A malicious attested participant can instead supply:
- `big_y = g * y_a` for an attacker-chosen scalar `y_a`
- `big_c = hash_point * msk_a + app_pk * y_a` for an attacker-chosen scalar `msk_a`

The user decrypts: `big_c − big_y * private_key = hash_point * msk_a + app_pk * y_a − g * y_a * private_key = hash_point * msk_a`

The user receives `hash_point * msk_a` as their derived confidential key — a key the attacker fully controls and knows. Any data the user subsequently encrypts to this key is readable by the attacker. The real threshold-derived key is never produced.

---

### Likelihood Explanation

**High.** The `AppPublicKey` variant is the legacy/default path documented in the README and used in the existing sandbox tests and e2e tests. Any single attested participant — one node out of `n`, with no threshold requirement — can race to call `respond_ckd` before the honest nodes do. Because `resolve_yields_for` removes the pending request on first call, the first `respond_ckd` to arrive wins and drains the entire yield queue. [5](#0-4) 

The attacker only needs to be an attested participant (a single compromised or malicious node), which is explicitly within the allowed threat model (Byzantine participant strictly below the signing threshold).

---

### Recommendation

Apply `ckd_output_check` to the `AppPublicKey` variant as well. For the legacy single-G1-point key, the check must be adapted: since `AppPublicKey` provides only `pk1 = g * private_key` (no `pk2`), the contract cannot run the full pairing equation without a G2 component. The correct fix is one of:

1. **Deprecate `AppPublicKey` entirely** and require all new requests to use `AppPublicKeyPV`, which supports the full on-chain pairing check.
2. **Add an off-chain verification path**: require nodes to include a zero-knowledge proof of correct CKD computation alongside the `AppPublicKey` response, and verify it on-chain.
3. **Short-term mitigation**: reject `AppPublicKey` requests in `respond_ckd` until a verifiable scheme is in place, forcing callers to migrate to `AppPublicKeyPV`.

---

### Proof of Concept

1. Alice calls `request_app_private_key` with `AppPublicKey(g * alice_sk)` and `domain_id` pointing to the BLS12-381 CKD domain. The request enters `pending_ckd_requests`.

2. Malicious participant Bob (a single attested node) observes the pending request on-chain.

3. Bob chooses arbitrary scalars `y_b` and `msk_b`. He computes:
   - `big_y = g * y_b`
   - `big_c = hash_app_id_with_pk(network_pk, app_id) * msk_b + (g * alice_sk) * y_b`

4. Bob calls `respond_ckd(ckd_request, CKDResponse { big_y, big_c })`.

5. The contract's `AppPublicKey` arm is empty — no check is performed. `resolve_yields_for` drains Alice's yield with Bob's fabricated response.

6. Alice's yield-resume fires. She receives `(big_y, big_c)` and decrypts: `big_c − big_y * alice_sk = hash_point * msk_b`. Alice believes she has a secure MPC-derived key; in reality Bob knows `msk_b` and can compute the same key.

7. The honest threshold nodes' eventual `respond_ckd` call returns `Err(RequestNotFound)` — the request was already drained by Bob. [6](#0-5) [7](#0-6)

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
