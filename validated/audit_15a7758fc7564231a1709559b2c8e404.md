The code is clear enough to make a determination. Here is the analysis:

**Key code path in `respond_ckd`** (`crates/contract/src/lib.rs`, lines 675–688):

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no verification
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

**`resolve_yields_for`** (`crates/contract/src/pending_requests.rs`, lines 66–88): a **single call** drains the entire queue and resolves all yields — there is no threshold-counting of responders.

**`ckd_output_check`** (`crates/contract/src/primitives/ckd.rs`, lines 80–102): verifies `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)` using the G2 component `pk2` — which only exists in `AppPublicKeyPV`, not in `AppPublicKey`.

---

### Title
Single Attested Participant Can Forge CKD Response for `AppPublicKey` Variant — (`crates/contract/src/lib.rs`)

### Summary
`respond_ckd` performs no cryptographic verification for `CKDAppPublicKey::AppPublicKey` requests. Any single attested participant can call it with an arbitrary `(big_y, big_c)` pair, and the contract will unconditionally resolve the pending yield with the forged response.

### Finding Description
In `respond_ckd`, the match on `request.app_public_key` has an empty arm for the `AppPublicKey` variant: [1](#0-0) 

`ckd_output_check` — which verifies the pairing equation binding `big_c` to the network master secret key and the app's public key — is only called for `AppPublicKeyPV`: [2](#0-1) 

The `AppPublicKey` variant carries only a G1 key (no G2 component), so the pairing check cannot be applied. However, the contract does not fall back to any alternative verification — it simply skips all checks.

`resolve_yields_for` resolves the yield on the **first** call that reaches it: [3](#0-2) 

There is no threshold-counting of responders. The threshold enforcement for `AppPublicKeyPV` and for `respond` (signatures) is entirely in the cryptographic check — once that check passes, one call resolves everything. For `AppPublicKey`, there is no such check, so one call from any attested participant resolves the yield with whatever bytes were supplied.

`assert_caller_is_attested_participant_and_protocol_active` (called at line 666) only confirms the caller is a current attested participant — it does not require the caller to be a designated leader or to represent a threshold quorum: [4](#0-3) 

### Impact Explanation
A single Byzantine attested participant (well below the signing threshold) can:

1. Observe any pending `AppPublicKey` CKD request in the contract.
2. Call `respond_ckd` with an arbitrary `CKDResponse { big_y: ..., big_c: ... }`.
3. The contract accepts it without any verification and resolves the yield.
4. The app receives a forged derived key that does not satisfy `big_c = msk·H(pk, app_id) + app_pk1·y`.
5. The app cannot recover the correct BLS-encrypted secret; its derived key is permanently corrupted.

This is unauthorized confidential key derivation output delivered without the required threshold participant authorization — matching the Critical impact scope.

### Likelihood Explanation
The attacker needs only to be a single valid attested participant. No threshold collusion, no TEE compromise, no key leakage is required. The exploit is a direct on-chain call.

### Recommendation
The `AppPublicKey` variant must either:
- Be deprecated in favor of `AppPublicKeyPV`, which carries the G2 component enabling the pairing-based contract-side verification; or
- Have an alternative binding check added (e.g., require the response to be accompanied by a threshold BLS signature over `(app_id, big_y, big_c)` that the contract can verify against the network public key).

Leaving the `AppPublicKey` arm empty while `resolve_yields_for` resolves on a single call is the root cause.

### Proof of Concept
1. Submit a `request_app_private_key` call with `CKDAppPublicKey::AppPublicKey(some_g1_pk)`.
2. From any single attested participant account, call:
   ```
   respond_ckd(request, CKDResponse { big_y: [0x80, 0, ..., 0], big_c: [0x80, 0, ..., 0] })
   ```
   (any valid-encoding G1 compressed points, or even the generator repeated).
3. Observe the contract resolves the yield successfully with no error.
4. The app callback receives `(big_y, big_c)` that do not satisfy the CKD equation; it cannot recover `msk·H(pk, app_id)`.

### Citations

**File:** crates/contract/src/lib.rs (L654-689)
```rust
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
