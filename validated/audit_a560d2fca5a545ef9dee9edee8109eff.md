### Title
Single Attested Participant Can Forge CKD Response for `AppPublicKey` Requests, Bypassing Threshold Requirement - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function performs **no cryptographic output verification** for `CKDAppPublicKey::AppPublicKey` requests. Unlike `respond` (which verifies every signature) and `respond_ckd` with `AppPublicKeyPV` (which runs `ckd_output_check`), the `AppPublicKey` match arm is a silent no-op. Any single attested participant can call `respond_ckd` with an arbitrary `CKDResponse`, bypassing the threshold requirement and delivering a forged confidential key derivation output to the requesting user.

---

### Finding Description

In `respond_ckd`, after the attestation check passes, the contract branches on the request's app public key variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no verification
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, the contract runs `ckd_output_check`, which verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)` on-chain, making it impossible to forge a valid response without the MPC secret key. [2](#0-1) 

For `AppPublicKey`, the arm is `{}` — the contract accepts any `(big_y, big_c)` pair unconditionally. The only gate is `assert_caller_is_attested_participant_and_protocol_active`, which checks that the caller is a single attested participant in the current epoch. [3](#0-2) 

By contrast, `respond` (for threshold signatures) always verifies the cryptographic output before resolving the yield: [4](#0-3) 

The asymmetry is structural: for `AppPublicKey` CKD, the contract has no mechanism to confirm that threshold-many participants agreed on the response. A single Byzantine participant can race the honest leader's transaction and resolve the pending yield with arbitrary `big_y` / `big_c` values.

The pending-request queue resolves on a first-come-first-served basis via `resolve_yields_for`. Once the attacker's forged response resolves the yield, the honest response arrives too late and the user has already received the corrupted output. [5](#0-4) 

---

### Impact Explanation

**Critical — Unauthorized confidential key derivation output without the required participant authorization.**

The CKD protocol is designed to deliver a derived private key (encoded as a BLS12-381 G1 point) encrypted under the user's ephemeral public key. If a malicious participant forges `(big_y, big_c)`:

- The user decrypts the response and obtains a wrong G1 point as their derived key.
- Any funds or application secrets the user has already committed to addresses or identifiers derived from the *expected* key become permanently inaccessible — the user holds a key that does not match the commitment.
- The attacker cannot directly recover the user's private scalar `r` from the forged response, so they cannot themselves spend the locked funds; the result is **permanent freezing** of those funds.
- Repeated front-running prevents the user from ever obtaining the correct key, even across retried requests.

This directly matches the allowed impact: *"Unauthorized confidential key derivation output without the required participant authorization"* and *"permanent freezing of funds controlled by the MPC network."*

---

### Likelihood Explanation

- **Attacker role:** Any single attested participant — a role that is legitimately admitted to the network and whose account key is stored on-chain. No threshold collusion is required; one Byzantine node suffices.
- **Attack surface:** Every pending `AppPublicKey` CKD request is observable on-chain. The attacker monitors the NEAR indexer for `request_app_private_key` calls with the `AppPublicKey` variant and races the honest leader's `respond_ckd` call.
- **Feasibility:** NEAR does not guarantee transaction ordering within a block. A participant running a modified node can submit `respond_ckd` immediately upon seeing the request, before the honest leader's response is included.
- **No special knowledge required:** The forged `(big_y, big_c)` can be any valid BLS12-381 G1 points; the contract performs no pairing check for this variant.

---

### Recommendation

1. **Deprecate `AppPublicKey` for new requests** and require callers to use `AppPublicKeyPV`, which provides on-chain public verifiability via `ckd_output_check`. The README already labels `AppPublicKey` as "legacy."
2. **If `AppPublicKey` must be retained**, implement a commit-reveal or multi-response aggregation scheme: require threshold-many participants to submit matching `(big_y, big_c)` values before the yield is resolved, analogous to how `vote_pk` collects threshold votes before accepting a public key.
3. **Short-term mitigation:** Add a contract-level flag to stop accepting new `AppPublicKey` CKD requests (`accept_requests`-style gate) until a threshold-enforcing mechanism is in place.

---

### Proof of Concept

1. User calls `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(app_pk)` and attaches 1 yoctoNEAR deposit. The request is enqueued in `pending_ckd_requests`.
2. Malicious attested participant observes the pending request on-chain via the NEAR indexer.
3. Malicious participant calls `respond_ckd(ckd_request, CKDResponse { big_y: [1u8;48].into(), big_c: [2u8;48].into() })` — arbitrary garbage values.
4. The contract passes `assert_caller_is_attested_participant_and_protocol_active` (the attacker is a legitimate participant).
5. The `AppPublicKey` match arm executes `{}` — no verification occurs.
6. `resolve_yields_for` resolves the yield with the forged response; the user's promise callback fires with the corrupted `(big_y, big_c)`.
7. The user decrypts the response and obtains a wrong derived key. Any funds committed to addresses derived from the expected key are permanently inaccessible.
8. The honest leader's subsequent `respond_ckd` call finds no pending yield to resolve and silently returns `Ok(())`.

This is confirmed by the existing test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists`, which shows that arbitrary `big_y = [1u8;48]` and `big_c = [2u8;48]` are accepted without complaint for the `AppPublicKey` variant: [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L642-651)
```rust
        if !signature_is_valid {
            return Err(RespondError::InvalidSignature.into());
        }

        pending_requests::resolve_yields_for(
            &mut self.pending_signature_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
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

**File:** crates/contract/src/lib.rs (L2389-2403)
```rust
    fn assert_caller_is_attested_participant_and_protocol_active(&self) {
        let participants = self.protocol_state.active_participants();

        Self::assert_caller_is_signer();

        let attestation_check = self
            .tee_state
            .is_caller_an_attested_participant(participants);

        assert_matches::assert_matches!(
            attestation_check,
            Ok(()),
            "Caller must be an attested participant"
        );
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
