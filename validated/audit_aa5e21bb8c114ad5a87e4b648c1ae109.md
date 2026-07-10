### Title
Unvalidated CKD Response for `AppPublicKey` Variant Allows Single Byzantine Participant to Deliver Attacker-Controlled Key - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function in the MPC contract performs cryptographic output validation **only** for the `AppPublicKeyPV` (publicly verifiable) variant. For the `AppPublicKey` (privately verifiable) variant, the contract accepts any arbitrary `big_y` and `big_c` values from any single attested participant without verification. This is a direct analog to the Dojo namespace/hash inconsistency: the contract stores a `CKDRequest` (used as the lookup key / access-control anchor) but does not enforce that the `CKDResponse` is consistent with it — i.e., that the response was actually produced by the threshold protocol over the correct `app_id` and MPC key.

---

### Finding Description

In `respond_ckd`, the contract branches on the variant of `app_public_key`:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no validation
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` enforces the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, cryptographically binding the response to the MPC network key and the correct `app_id`. [2](#0-1) 

For `AppPublicKey`, there is **no equivalent check**. The contract immediately proceeds to resolve the pending yield with whatever `big_y`/`big_c` the caller supplied. The existing unit test confirms this: it passes `[1u8; 48]` and `[2u8; 48]` — not valid BLS12-381 G1 points — and the contract accepts them without error. [3](#0-2) 

The gate protecting `respond_ckd` is `assert_caller_is_attested_participant_and_protocol_active`, which only requires the caller to be a current attested participant — not that a threshold of participants agreed on the response. [4](#0-3) 

The `CKDRequest` struct (used as the BTreeMap key for pending requests) contains `app_public_key`, `app_id`, and `domain_id`. All three fields are publicly readable from on-chain contract state, so any participant can reconstruct the exact key needed to resolve a pending request. [5](#0-4) 

---

### Impact Explanation

A single Byzantine participant (strictly below the signing threshold) can:

1. Read a pending `AppPublicKey` CKD request from public contract state.
2. Call `respond_ckd` with the correct `CKDRequest` key but with attacker-chosen `big_y = G1_identity` and `big_c = target_point`.
3. The contract resolves the yield and delivers `(big_y, big_c)` to the requesting app.
4. The app computes `secret = big_c − big_y · a = target_point − 0 = target_point`, a value the attacker fully controls and knows.
5. The app uses this attacker-controlled value as its confidential key — to encrypt data, derive signing keys, or authenticate to other systems.

This constitutes **unauthorized confidential key derivation output without the required participant authorization**: the threshold protocol is bypassed entirely for the `AppPublicKey` variant. The attacker can also race the honest leader (front-run the `respond_ckd` call) since NEAR transaction ordering is not guaranteed within a block.

---

### Likelihood Explanation

- The `AppPublicKey` variant is the default/legacy variant used by the majority of CKD callers (the `AppPublicKeyPV` variant is newer and opt-in).
- Any single attested participant can call `respond_ckd` — no threshold agreement is required by the contract.
- All inputs needed to construct the correct `CKDRequest` lookup key are publicly visible on-chain.
- The attack requires no cryptographic forgery, no TEE compromise, and no network-level capability — only a valid NEAR account that is a current participant.

---

### Recommendation

Apply the same cryptographic binding to the `AppPublicKey` variant that already exists for `AppPublicKeyPV`. Concretely, verify that `e(big_c, g2) = e(big_y, g2·a) · e(hash_point, public_key)` using the G1 app public key. Since the `AppPublicKey` variant does not supply a G2 companion key, the contract should either:

- Require callers to upgrade to `AppPublicKeyPV` (which provides the G2 key needed for on-chain verification), or
- Derive the G2 companion from the stored G1 key if the protocol guarantees it (not generally possible without the discrete log), or
- Require threshold-signed attestation of the response value before accepting it (e.g., a vote-based mechanism similar to `vote_pk`).

---

### Proof of Concept

```
// Attacker is participant[0] (below threshold t)
// Victim called request_app_private_key with AppPublicKey variant

// Step 1: read pending request from chain state
let ckd_request = contract.get_pending_ckd_request(...); // public view call

// Step 2: craft attacker-controlled response
// big_y = G1 identity (compressed encoding: 0xc0 || 0x00...00)
// big_c = attacker's chosen G1 point (attacker knows its discrete log)
let malicious_response = CKDResponse {
    big_y: Bls12381G1PublicKey(G1_IDENTITY_COMPRESSED),
    big_c: Bls12381G1PublicKey(ATTACKER_CHOSEN_POINT),
};

// Step 3: call respond_ckd as attested participant (no threshold needed)
contract.respond_ckd(ckd_request, malicious_response);

// Result: victim app computes secret = ATTACKER_CHOSEN_POINT - identity * a
//       = ATTACKER_CHOSEN_POINT
// Attacker knows this value and can impersonate the victim's derived key.
``` [6](#0-5)

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

**File:** crates/contract/src/lib.rs (L2389-2402)
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
```

**File:** crates/contract/src/lib.rs (L3424-3440)
```rust
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
```

**File:** crates/contract/src/primitives/ckd.rs (L8-31)
```rust
#[derive(Debug, Clone, Eq, Ord, PartialEq, PartialOrd)]
#[near(serializers=[borsh, json])]
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
