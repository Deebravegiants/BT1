Based on my analysis of the actual production code, here is my finding:

---

### Title
Single Attested Participant Can Deliver Fabricated CKD Output for `AppPublicKey` Requests — (`crates/contract/src/lib.rs`)

### Summary

The `respond_ckd()` function unconditionally skips the `ckd_output_check` pairing-equation verification when the pending `CKDRequest` uses the `AppPublicKey` variant. Because `respond_ckd()` requires only a single attested participant (no threshold enforcement on-chain), a single Byzantine participant can call it with an arbitrary fabricated `CKDResponse`, and the contract will resolve the yield with that fabricated output — no cryptographic proof required.

### Finding Description

In `lib.rs:675-682`:

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

For `AppPublicKeyPV`, the contract calls `ckd_output_check` which verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, binding the response to the network's master public key and the app's key pair. [2](#0-1) 

For `AppPublicKey`, the arm is an empty no-op. The function then immediately calls `resolve_yields_for`, which resumes every queued yield with whatever `response` bytes were passed in — no verification of any kind. [3](#0-2) 

The `AppPublicKey` variant carries only a G1 key and has no `pk2` (G2 key), so the pairing check structurally cannot be applied to it. However, the contract provides no substitute guard — no threshold counter, no multi-party commit/reveal, no aggregated proof — for this variant. [4](#0-3) 

`respond_ckd()` enforces only that the caller is a single attested participant: [5](#0-4) 

There is no on-chain threshold counter, no quorum check, and no aggregated proof requirement before `resolve_yields_for` is called. [6](#0-5) 

### Impact Explanation

A single Byzantine attested participant can:
1. Wait for any user to submit a CKD request using `AppPublicKey`.
2. Race-call `respond_ckd()` with arbitrary `big_c` / `big_y` values of their choosing.
3. The contract resolves the yield with the fabricated output — the requester receives a derived key that the attacker fully controls.

Because the attacker chooses `big_c`, they know the discrete-log relationship and can impersonate the derived key or decrypt material encrypted to it. This is **unauthorized confidential key derivation output without the required participant authorization** — a Critical-scope impact under the program rules.

### Likelihood Explanation

The attacker must be an attested MPC participant, which is a meaningful barrier. However, the threshold for this attack is **one** — any single attested node that goes Byzantine can execute it against every `AppPublicKey` CKD request in flight. No collusion, no key leakage, and no network-level capability is required.

### Recommendation

For `AppPublicKey` requests, either:
- **Require `AppPublicKeyPV`** for all CKD requests that need on-chain output integrity (deprecate the unverifiable variant), or
- **Add a threshold-enforced multi-response aggregation path** for `AppPublicKey` so that `resolve_yields_for` is only called after a quorum of attested participants have submitted matching responses, or
- **Document and enforce** that `AppPublicKey` is only usable in contexts where the requester explicitly accepts that output integrity is not contract-enforced (e.g., gated by a separate flag or a different entry point with a clear security disclaimer).

### Proof of Concept

```rust
// Sandbox integration test sketch:
// 1. User calls the CKD entry point with CKDAppPublicKey::AppPublicKey(random_g1_pk).
// 2. Single attested participant calls respond_ckd() with:
//    CKDResponse { big_c: random_bytes_48, big_y: random_bytes_48 }
// 3. Assert: the yield resolves successfully (Ok(())) and the requester
//    receives the fabricated big_c/big_y — no panic, no rejection.
// The AppPublicKeyPV variant with the same fabricated response would
// panic at "CKD output check failed", proving the asymmetry.
``` [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L655-666)
```rust
        let signer = Self::assert_caller_is_signer();
        log!("respond_ckd: signer={}, request={:?}", &signer, &request);

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

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

**File:** crates/contract/src/primitives/ckd.rs (L546-561)
```rust
    #[test]
    #[expect(non_snake_case)]
    fn ckd_output_check__should_reject_tampered_big_c() {
        // Given
        let mut rng = StdRng::seed_from_u64(42);
        let (app_id, mut response, app_pk, network_pk) = make_valid_ckd_output(&mut rng);
        response.big_c = dtos::Bls12381G1PublicKey(
            (G1Projective::generator() * Scalar::random(&mut rng)).to_compressed(),
        );

        // When
        let accepted = ckd_output_check(&app_id, &response, &app_pk, &network_pk);

        // Then
        assert!(!accepted);
    }
```

**File:** crates/near-mpc-crypto-types/src/ckd.rs (L15-18)
```rust
pub enum CKDAppPublicKey {
    AppPublicKey(Bls12381G1PublicKey),
    AppPublicKeyPV(CKDAppPublicKeyPV),
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
