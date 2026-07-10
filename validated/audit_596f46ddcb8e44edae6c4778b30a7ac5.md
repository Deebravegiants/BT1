### Title
Single Byzantine Participant Can Forge CKD Output for `AppPublicKey` Variant — (`crates/contract/src/lib.rs`)

---

### Summary

In `respond_ckd`, when the CKD request uses the `CKDAppPublicKey::AppPublicKey` (legacy, privately-verifiable) variant, the contract performs **no cryptographic verification** of the supplied `CKDResponse`. A single attested participant below the signing threshold can race to call `respond_ckd` with arbitrary `big_y` / `big_c` values, and the contract will accept and deliver the forged output to the user. This breaks the threshold-security guarantee: the `AppPublicKeyPV` path is protected by `ckd_output_check`, but the `AppPublicKey` path is silently skipped.

---

### Finding Description

In `respond_ckd` the verification branch is:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← NO CHECK
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}

pending_requests::resolve_yields_for(
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),   // ← unverified response delivered
)
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies the BLS pairing equation that ties `big_y` and `big_c` to the MPC network's public key and the user's app identity, so a single node cannot forge it. [2](#0-1) 

For `AppPublicKey`, the arm is an empty no-op. The response is serialized and passed directly to `resolve_yields_for`, which resumes all queued NEAR yield-resume promises with the attacker-supplied bytes. [3](#0-2) 

The only access controls are:
- `assert_caller_is_signer()` — any NEAR account key
- `assert_caller_is_attested_participant_and_protocol_active()` — must be an attested participant [4](#0-3) 

A single attested participant satisfies both. No threshold cooperation is required.

The `AppPublicKey` variant is the production legacy path, explicitly documented and accepted by `request_app_private_key`. [5](#0-4) 

**Analog to H-03:** In the zkSync report, when `skip_if_legitimate_fat_ptr` is set, `bytes_to_cleanup_out_of_bounds` is zeroed instead of 32, so the memory read is neither enforced nor masked — the attacker's value flows through unchecked. Here, when `AppPublicKey` is used, the CKD output check is zeroed out (empty arm), so the attacker's `CKDResponse` flows through unchecked to the user.

---

### Impact Explanation

**Critical — Unauthorized confidential key derivation output without required participant authorization.**

A single Byzantine attested participant can:
1. Monitor the chain for any pending `CKDRequest` using the `AppPublicKey` variant.
2. Race to call `respond_ckd` before honest nodes, supplying arbitrary `big_y` / `big_c` values (e.g., points for which the attacker knows the discrete log).
3. The contract accepts the response, resolves all queued yields, and delivers the forged key material to the user.

The user receives a confidential key that the attacker controls. Any assets or secrets the user protects with that derived key are immediately compromised. The threshold guarantee (t-of-n) is entirely bypassed for this code path.

---

### Likelihood Explanation

- The `AppPublicKey` variant is the legacy production path, actively used.
- The attacker only needs to be a single attested participant — a realistic adversary model explicitly in scope.
- The attack is a simple race: submit `respond_ckd` before honest nodes. No cryptographic capability is required.
- `resolve_yields_for` drains all queued yields in one call, so a single winning call affects every user who submitted the same request. [3](#0-2) 

---

### Recommendation

Apply the same `ckd_output_check` to the `AppPublicKey` variant, or reject `AppPublicKey` responses at the contract level and require all new requests to use `AppPublicKeyPV`. If private verifiability must be preserved, the contract should at minimum verify that the response is consistent with the MPC network's public key using a weaker on-chain check (e.g., verifying `big_c` is a valid G1 point derived from the network key and app ID), or require threshold-many identical responses before resolving the yield.

---

### Proof of Concept

1. Alice calls `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(alice_pk)` and `derivation_path = "my-wallet"`. A `CKDRequest` is queued.
2. Attacker (a single attested participant) constructs a `CKDResponse { big_y: attacker_g1_point, big_c: attacker_g1_point }` where both points correspond to a key the attacker knows.
3. Attacker calls `respond_ckd(ckd_request, forged_response)` before honest nodes respond.
4. The `AppPublicKey` arm executes `{}` — no check.
5. `resolve_yields_for` resumes Alice's yield with the forged bytes.
6. Alice's callback receives `forged_response` and derives a key the attacker controls.

The existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` confirms the contract accepts an arbitrary `CKDResponse { big_y: [1u8;48], big_c: [2u8;48] }` for the `AppPublicKey` variant with no verification failure: [6](#0-5)

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

**File:** crates/contract/src/lib.rs (L675-688)
```rust
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

**File:** crates/contract/README.md (L276-288)
```markdown
#### CKDRequestArgs (Latest version)

The `request_app_private_key` request takes the following arguments:

- `derivation_path` (String): the derivation path.
- `app_public_key`: the ephemeral public key to encrypt the generated confidential key. Accepts either a plain G1 point string (privately verifiable, legacy) or a tagged enum with `AppPublicKey` (single G1 point) or `AppPublicKeyPV` (a `{pk1, pk2}` pair for public verifiability).
- `domain_id` (integer): the domain ID that identifies the key and signature scheme to use to generate the confidential key

#### SignRequestArgs (Legacy version for backwards compatibility with V1)

- The legacy argument `payload` can be used in place of `payload_v2`; the format for that is an array of 32 integer bytes. This argument can only be used
  to pass in an ECDSA payload.
- The legacy argument `key_version` can be used in place of `domain_id` and means the same thing.
```
