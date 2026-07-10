### Title
Single Byzantine Participant Can Corrupt Legacy CKD `AppPublicKey` Response Without On-Chain Verification — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` in the MPC contract performs **no cryptographic verification** of the response when the request uses the legacy `AppPublicKey` variant of `CKDAppPublicKey`. A single malicious attested participant (Byzantine, strictly below the signing threshold) can observe a pending `request_app_private_key` call, reconstruct the `CKDRequest` key from public on-chain state, and immediately call `respond_ckd` with arbitrary garbage `(big_y, big_c)` values. The contract accepts the call unconditionally, resolves the user's yield with garbage data, and the user receives an unusable encrypted key — breaking the threshold security guarantee that no single participant should be able to corrupt the CKD output.

---

### Finding Description

In `respond_ckd`, the contract branches on the `CKDAppPublicKey` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← empty: no verification
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` performs a BLS12-381 pairing check that cryptographically proves the response is a correctly computed ElGamal encryption of the derived key under the MPC master secret. For the legacy `AppPublicKey` arm, the body is **empty** — no verification of any kind is performed. [2](#0-1) 

After the match, `resolve_yields_for` is called unconditionally, delivering whatever `response` the attested participant provided to every pending yield queued under that request key. [3](#0-2) 

**Attack path:**

1. User calls `request_app_private_key` with `AppPublicKey` variant. The full `CKDRequest` key — `(app_public_key, app_id, domain_id)` — is visible in on-chain state via `get_pending_ckd_request`.
2. A single malicious attested participant (below threshold) reads the pending request from the contract.
3. The attacker calls `respond_ckd` with the correct `CKDRequest` but an arbitrary garbage `CKDResponse { big_y: [0u8;48], big_c: [0u8;48] }`.
4. The contract passes all guards (`assert_caller_is_attested_participant_and_protocol_active`, protocol running, domain valid) and reaches the `AppPublicKey` arm — which does nothing.
5. `resolve_yields_for` delivers the garbage response to the user's yield, consuming the pending request.
6. The user receives `(big_y, big_c)` that cannot be decrypted to a valid confidential key.

This is directly confirmed by the existing test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists`, which passes `CKDResponse { big_y: [1u8;48], big_c: [2u8;48] }` — not valid BLS12-381 G1 points — and the contract accepts them without complaint: [4](#0-3) 

The threshold security guarantee is violated: normally at least `t` participants must cooperate to produce a valid CKD response. With `AppPublicKey`, a single Byzantine participant can corrupt the output unilaterally, racing the legitimate leader node.

The `AppPublicKey` variant is still actively used — the `ckd-example-cli` uses it by default, and the contract README documents it as the primary legacy format: [5](#0-4) 

---

### Impact Explanation

- The user's pending CKD request is consumed (yield resolved) with garbage data; the user cannot derive their confidential key.
- The user must retry with a fresh ephemeral `app_public_key`, paying gas again.
- The threshold security invariant for CKD is broken: a single Byzantine participant (below threshold) can corrupt any `AppPublicKey` CKD request, which is a production safety/accounting invariant violation.
- Maps to **Medium** — "Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration."

---

### Likelihood Explanation

- Requires a single malicious attested participant, which is explicitly within the MPC threat model (up to `t-1` Byzantine participants).
- No threshold cooperation is needed; one participant suffices.
- The `CKDRequest` key is fully visible on-chain, so the attacker can reconstruct it without any off-chain knowledge.
- The attacker only needs to submit `respond_ckd` before the legitimate leader node does — a straightforward race on NEAR's mempool.
- The `AppPublicKey` variant remains the default in the CLI and is documented as the primary legacy path.

---

### Recommendation

1. **Require `AppPublicKeyPV` for all new requests.** The `AppPublicKeyPV` variant has on-chain verification via `ckd_output_check` and should be the only accepted variant going forward. Deprecate `AppPublicKey` with a clear migration path.
2. **If `AppPublicKey` must remain**, add a minimum validity check: verify that `big_y` and `big_c` are valid, non-identity BLS12-381 G1 points before resolving the yield. This does not provide full security but prevents trivially garbage responses.
3. **Analogous to the permit-front-running fix in the reference report**: check whether the response is already correct before accepting a new one — i.e., if a valid response has already been delivered, do not allow it to be overwritten.

---

### Proof of Concept

```rust
// Step 1: User submits request_app_private_key with AppPublicKey (legacy)
// CKDRequest key is visible on-chain: (app_public_key, app_id, domain_id)

// Step 2: Malicious attested participant reconstructs the CKDRequest
let ckd_request = CKDRequest {
    app_public_key: CKDAppPublicKey::AppPublicKey(user_app_public_key),
    app_id: derive_app_id(&user_account_id, &user_derivation_path),
    domain_id: user_domain_id,
};

// Step 3: Attacker submits garbage response before the legitimate leader node
let garbage_response = CKDResponse {
    big_y: Bls12381G1PublicKey([0u8; 48]),  // not a valid G1 point
    big_c: Bls12381G1PublicKey([0u8; 48]),  // not a valid G1 point
};

// Step 4: Contract accepts unconditionally — AppPublicKey arm is empty
contract.respond_ckd(ckd_request, garbage_response);
// → Ok(()) — pending request consumed, user receives garbage (big_y, big_c)
// User cannot decrypt; must retry with a new app_public_key
```

The existing unit test at `crates/contract/src/lib.rs:3403–3441` already demonstrates this: it passes `[1u8;48]` / `[2u8;48]` (not valid BLS12-381 points) as the response and the contract returns `Ok(())` with no verification error. [6](#0-5)

### Citations

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

**File:** crates/contract/src/primitives/ckd.rs (L76-101)
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
```

**File:** crates/contract/README.md (L128-138)
```markdown
_Privately verifiable ckd request (legacy)_

```Json
{
  "request": {
    "derivation_path": "mykey",
    "app_public_key": "bls12381g1:6KtVVcAAGacrjNGePN8bp3KV6fYGrw1rFsyc7cVJCqR16Zc2ZFg3HX3hSZxSfv1oH6",
    "domain_id": 2
  }
}
```
```
