### Title
Unverified CKD Response for `AppPublicKey` Variant Allows Single Malicious Node to Forge Confidential Key Derivation Output - (File: crates/contract/src/lib.rs)

---

### Summary

In `respond_ckd`, the `CKDAppPublicKey::AppPublicKey` match arm is empty — no cryptographic verification of the CKD response is performed. Execution falls through unconditionally to `resolve_yields_for`, which accepts and delivers the response to the user. A single malicious attested participant can submit an arbitrary forged response for any pending `AppPublicKey` CKD request, bypassing the threshold requirement entirely. The contract consumes the request and delivers the forged output to the caller.

---

### Finding Description

In `respond_ckd` at `crates/contract/src/lib.rs` lines 675–682, the contract branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← empty: no check
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
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)` using the BLS12-381 host functions, and panics on failure. [2](#0-1) 

For `AppPublicKey`, the arm is `{}` — execution falls through to `resolve_yields_for` regardless of whether the response is cryptographically valid. `resolve_yields_for` removes the request from the pending map and resumes all queued yields with the supplied bytes, permanently consuming the request. [3](#0-2) 

The only caller-side guards in `respond_ckd` are: protocol is running/resharing, `accept_requests` is true, and the caller is an attested participant. There is no check that the caller was the elected leader for this CKD computation, nor any check that a threshold of nodes agreed on the response. [4](#0-3) 

This is the direct analog of the Babylon bug: after a condition that should have halted processing (invalid finality sig over a fork / invalid CKD response), there is no `return`, so execution continues and incorrectly finalises the request as successfully resolved.

---

### Impact Explanation

A single Byzantine attested participant — strictly below the signing threshold — can:

1. Observe any pending `AppPublicKey` CKD request in contract storage (the `CKDRequest` key is public).
2. Call `respond_ckd` with an arbitrary `CKDResponse` (e.g. all-zero `big_y`/`big_c`).
3. The contract accepts the response without any cryptographic check, removes the request from `pending_ckd_requests`, and resumes the user's yield with the forged bytes.
4. The user's callback receives the forged `(big_y, big_c)` pair. Decryption with the app's private key yields garbage — the confidential key is unrecoverable from this response.
5. The request is permanently consumed; the user must re-submit, but the same attacker can immediately corrupt the replacement request.

This constitutes a confidential key derivation output delivered without the required threshold-participant authorization, matching the Critical allowed impact: *"Unauthorized … confidential key derivation output without the required participant authorization."*

---

### Likelihood Explanation

- Any single attested participant (TEE-verified node) can call `respond_ckd` at any time for any pending request — no leader election or threshold proof is required by the contract.
- The `CKDRequest` key (derived from `app_public_key`, `domain_id`, `app_id`) is stored in plain contract state and is observable by all nodes via the chain indexer.
- The attack requires no collusion, no key leakage, and no privileged operator access — only membership in the attested participant set.
- The `AppPublicKey` variant is the original, widely-used CKD variant (the `AppPublicKeyPV` variant is the newer addition), so the attack surface covers all legacy CKD users.

---

### Recommendation

The contract must not accept a `respond_ckd` call for `AppPublicKey` requests without enforcing the threshold requirement. Two options:

1. **Require `AppPublicKeyPV` for all new requests** and deprecate `AppPublicKey`. The publicly-verifiable variant already has an on-chain pairing check that a single node cannot forge.
2. **Add a threshold-vote accumulation step** for `AppPublicKey` responses: collect `respond_ckd` calls from at least `threshold` distinct attested participants who all supply the same `(big_y, big_c)` before resolving the yield. Only when a quorum of identical responses is reached should `resolve_yields_for` be called.

---

### Proof of Concept

```
// Attacker is an attested participant (account: "evil.near")
// Victim submitted: request_app_private_key({ app_public_key: AppPublicKey(pk), ... })
// Contract now has a pending CKDRequest in pending_ckd_requests

// Attacker reads the CKDRequest key from contract state (public view call)
let ckd_request = contract.get_pending_ckd_request(&known_request).unwrap();

// Attacker calls respond_ckd with all-zero garbage
evil_account.call(contract.id(), "respond_ckd")
    .args_json(json!({
        "request": ckd_request,
        "response": {
            "big_y": "bls12381g1:AAAA...AAAA",   // 48 zero bytes
            "big_c": "bls12381g1:AAAA...AAAA",
        }
    }))
    .transact()
    .await
    .unwrap();
// → contract accepts, resolves yield, victim receives forged (big_y, big_c)
// → victim's app cannot decrypt a valid confidential key
// → request is permanently consumed
```

The `AppPublicKey` match arm performs no check, so `env::panic_str("CKD output check failed")` is never reached for this variant, and `resolve_yields_for` always executes. [1](#0-0) [5](#0-4)

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
