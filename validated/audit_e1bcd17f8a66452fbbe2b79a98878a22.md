### Title
Missing CKD Output Verification for `AppPublicKey` Variant Allows Single Participant to Forge Key Derivation Response - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` applies a cryptographic pairing check (`ckd_output_check`) only for the `AppPublicKeyPV` request variant. For the `AppPublicKey` variant, the branch is an explicit no-op. A single attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary forged `CKDResponse`, which the contract accepts unconditionally and delivers to every waiting caller via `resolve_yields_for`.

---

### Finding Description

The vulnerability class from the external report is: **a safety invariant (check) that is applied to most code paths is silently absent on one specific path**, allowing an attacker to corrupt state or deliver invalid output without the missing guard catching it.

In `respond_ckd`, the contract enforces a BLS12-381 pairing equation on the response only when the request carries an `AppPublicKeyPV` key (which includes both a G1 and G2 component needed for the check). For the `AppPublicKey` variant (a bare G1 point), the match arm is empty:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

After this match, `resolve_yields_for` is called unconditionally, resuming every queued yield with whatever `response` the caller supplied.

The only gate before this point is `assert_caller_is_attested_participant_and_protocol_active`, which requires the caller to be **one** attested participant in the active set — not a threshold of them. [1](#0-0) [2](#0-1) [3](#0-2) 

By contrast, `respond` (ECDSA/EdDSA) always verifies the signature against the derived public key before resolving yields, and `respond_ckd` for `AppPublicKeyPV` always runs `ckd_output_check`. The `AppPublicKey` path is the sole exception. [4](#0-3) [5](#0-4) 

---

### Impact Explanation

**Critical — Confidential key derivation output delivered without threshold authorization.**

A forged `CKDResponse` (`big_c`, `big_y`) is indistinguishable at the contract level from a legitimate one for `AppPublicKey` requests. The requester receives and uses the attacker-chosen elliptic-curve points as their derived application key material. Because `resolve_yields_for` drains the entire fan-out queue in one call, every duplicate submission of the same request also receives the forged output. [6](#0-5) 

The CKD protocol is designed to let users derive application-specific private keys without the MPC network ever learning them. A forged response breaks this guarantee entirely: the attacker controls the output, so the "derived" key is known to the attacker.

---

### Likelihood Explanation

**High.** Any single attested participant in the current epoch can exploit this. The attacker does not need to compromise a threshold of nodes, break TEE isolation, or collude with other participants. They only need to:

1. Observe a pending `AppPublicKey`-type CKD request (visible on-chain via the NEAR indexer).
2. Call `respond_ckd` before any honest node does, supplying arbitrary `big_c`/`big_y` values.

The NEAR indexer that every node already runs makes step 1 trivial. Racing honest nodes is feasible because the attacker can submit the transaction immediately upon seeing the request event, with no cryptographic work required (unlike honest nodes that must run the threshold protocol). [7](#0-6) 

---

### Recommendation

Apply the same output-validity check to the `AppPublicKey` branch. Because `AppPublicKey` carries only a G1 point (no G2 component), `ckd_output_check` cannot be used directly. The fix should either:

1. **Require `AppPublicKeyPV` for all CKD requests** so the pairing check is always available, deprecating the bare `AppPublicKey` variant; or
2. **Derive a G2 component from the G1 key** (e.g., require the caller to supply it, or compute it from a known scalar relationship) so the same pairing equation can be verified; or
3. **Require threshold-many matching `respond_ckd` calls** before resolving yields, analogous to how DKG uses `vote_pk` to collect threshold votes before accepting a public key. [1](#0-0) 

---

### Proof of Concept

1. Alice calls `request_app_private_key` with `CKDRequestArgs { app_public_key: AppPublicKey(some_g1_point), domain_id, derivation_path }`. The contract enqueues a yield and stores the `CKDRequest` in `pending_ckd_requests`.

2. Mallory (one attested participant) observes the pending request via the NEAR indexer.

3. Mallory constructs a `CKDResponse { big_c: attacker_chosen_g1, big_y: attacker_chosen_g1 }` — any valid G1 encodings suffice.

4. Mallory calls `respond_ckd(request, forged_response)`. The contract:
   - Passes `assert_caller_is_signer()` ✓
   - Passes `is_running_or_resharing()` ✓
   - Passes `accept_requests` ✓
   - Passes `assert_caller_is_attested_participant_and_protocol_active()` ✓
   - Hits `AppPublicKey(_) => {}` — **no check** ✓
   - Calls `resolve_yields_for(...)` — delivers forged response to Alice ✓

5. Alice's callback receives `forged_response` and uses `big_c`/`big_y` as her derived key material, which Mallory fully controls. [8](#0-7) [9](#0-8)

### Citations

**File:** crates/contract/src/lib.rs (L602-608)
```rust
                // Check the signature is correct
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    payload_hash,
                    &expected_public_key,
                )
                .is_ok()
```

**File:** crates/contract/src/lib.rs (L653-666)
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

**File:** crates/contract/src/primitives/ckd.rs (L10-31)
```rust
pub struct CKDRequest {
    /// The app ephemeral public key
    pub app_public_key: dtos::CKDAppPublicKey,
    pub app_id: dtos::CkdAppId,
    pub domain_id: DomainId,
}

impl CKDRequest {
    pub fn new(
        app_public_key: dtos::CKDAppPublicKey,
        domain_id: DomainId,
        predecessor_id: &AccountId,
        derivation_path: &str,
    ) -> Self {
        let app_id = derive_app_id(predecessor_id, derivation_path);
        Self {
            app_public_key,
            app_id,
            domain_id,
        }
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
