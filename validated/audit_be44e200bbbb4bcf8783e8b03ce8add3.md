### Title
Single Byzantine Participant Can Deliver Forged CKD Output for Legacy `AppPublicKey` Requests — (`File: crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` performs no cryptographic verification of the response payload when the pending request uses the legacy `CKDAppPublicKey::AppPublicKey` variant. Any single attested participant can call `respond_ckd` with an arbitrary `CKDResponse`, the contract accepts it, resolves all queued yields with the forged data, and permanently removes the pending request — delivering a wrong derived key to the user and blocking the legitimate MPC response.

---

### Finding Description

In `respond_ckd`, the response is verified only for the `AppPublicKeyPV` variant:

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

For `AppPublicKey` (the legacy, privately-verifiable variant), the branch is a no-op. After this match, `resolve_yields_for` is called unconditionally:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

`resolve_yields_for` removes the entire pending-request entry and resumes every queued yield with whatever bytes were serialized from `response`:

```rust
let resumed = requests
    .remove(request)
    .unwrap_or_default()
    .into_iter()
    .map(|YieldIndex { data_id }| {
        env::promise_yield_resume(&data_id, response_bytes.clone());
    })
    .count();
``` [3](#0-2) 

The only gate in front of `respond_ckd` is `assert_caller_is_attested_participant_and_protocol_active`, which requires the caller to be **one** attested participant — not a threshold of them. [4](#0-3) 

Contrast this with `respond` for threshold signatures, which verifies the signature cryptographically against the derived public key before resolving any yield, making it impossible for a single participant to forge a valid response: [5](#0-4) 

---

### Impact Explanation

A single Byzantine attested participant can:

1. Observe any pending `AppPublicKey` CKD request in contract state.
2. Call `respond_ckd` with fabricated `big_y` / `big_c` values before the honest MPC response arrives.
3. The contract accepts the forged response with no verification, resolves all queued yields, and removes the pending entry.
4. The user's NEAR call returns the forged `CKDResponse`. Because `AppPublicKey` is "privately verifiable," the user cannot detect the forgery on-chain.
5. The legitimate MPC `respond_ckd` call subsequently fails with `RequestNotFound` — the request is gone.

The user decrypts `big_c` with their ephemeral secret `a` and derives a wrong key. Any funds or assets controlled by that derived key on a foreign chain become inaccessible or are under the attacker's control if the attacker chose `big_c = a_attacker * G1` for a known `a_attacker`.

**Impact class:** Critical — confidential key derivation output delivered without the required threshold-participant authorization; a single Byzantine participant below the signing threshold suffices.

---

### Likelihood Explanation

- The attacker must be an attested MPC participant (not an arbitrary external caller), which limits the pool. However, the threshold is designed to tolerate up to `t-1` Byzantine participants, and this attack requires only one.
- The attack window is the latency between the user's `request_app_private_key` transaction being indexed and the honest nodes' `respond_ckd` landing on-chain — typically seconds to tens of seconds, easily observable from the NEAR mempool or block explorer.
- The `AppPublicKey` (legacy) variant is explicitly supported and documented as the default for existing integrations.

---

### Recommendation

Apply the same on-chain cryptographic verification to `AppPublicKey` responses that `AppPublicKeyPV` already enjoys via `ckd_output_check`. If a publicly-verifiable check is not possible for the legacy variant by design, require that `respond_ckd` collect a threshold of matching responses before resolving yields — analogous to how threshold signatures require a cryptographically valid signature that implicitly encodes threshold participation. At minimum, document that `AppPublicKey` requests are vulnerable to single-participant response forgery and migrate callers to `AppPublicKeyPV`.

---

### Proof of Concept

1. User calls `request_app_private_key` with `AppPublicKey(pk)` on domain `d`. The contract stores the pending CKD request.
2. Attacker (any single attested participant) observes the pending request and immediately calls:
   ```
   respond_ckd(
     request = CKDRequest { app_public_key: AppPublicKey(pk), app_id: ..., domain_id: d },
     response = CKDResponse { big_y: [1u8; 48], big_c: [2u8; 48] }  // arbitrary garbage
   )
   ```
3. `respond_ckd` passes the `AppPublicKey(_) => {}` branch with no check, calls `resolve_yields_for`, removes the pending entry, and resumes the user's yield with the forged bytes.
4. The user's `request_app_private_key` call resolves with `{ big_y: [1;48], big_c: [2;48] }`.
5. The honest MPC nodes' subsequent `respond_ckd` call returns `Err(RequestNotFound)`.
6. The user decrypts the forged `big_c` with their secret `a` and obtains a wrong derived key — confirmed by the existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists`, which shows that `CKDResponse { big_y: [1u8;48], big_c: [2u8;48] }` is accepted without error for an `AppPublicKey` request. [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L642-644)
```rust
        if !signature_is_valid {
            return Err(RespondError::InvalidSignature.into());
        }
```

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
