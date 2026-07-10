### Title
Unverified CKD Response for `AppPublicKey` Variant Allows Single Byzantine Participant to Deliver Forged Secret Key — (File: crates/contract/src/lib.rs)

---

### Summary

The `respond_ckd` function in `MpcContract` accepts CKD (Confidential Key Derivation) responses for the `AppPublicKey` (non-publicly-verifiable) variant **without any on-chain cryptographic verification**. A single attested participant — strictly below the signing threshold — can submit a forged `CKDResponse` for any pending CKD request, causing the requesting user to derive a private key that the attacker also knows. This completely breaks the confidentiality guarantee of the CKD protocol.

---

### Finding Description

`respond_ckd` in `crates/contract/src/lib.rs` handles two variants of `CKDAppPublicKey`:

```rust
// crates/contract/src/lib.rs ~L675-682
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← NO VERIFICATION
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For the `AppPublicKeyPV` variant, the contract runs `ckd_output_check`, which uses a BLS pairing check to confirm the response is consistent with the master public key and the `app_id`. For the `AppPublicKey` (legacy, non-PV) variant, **no such check exists** — the submitted `CKDResponse` (`big_c`, `big_y`) is accepted and delivered to the user unconditionally.

Contrast this with `respond` (ECDSA), which always verifies the submitted signature against the derived public key before accepting it:

```rust
// crates/contract/src/lib.rs ~L602-608
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,
)
.is_ok()
``` [2](#0-1) 

The `respond_ckd` function only requires the caller to be a single attested participant:

```rust
// crates/contract/src/lib.rs ~L653-666
pub fn respond_ckd(&mut self, request: CKDRequest, response: CKDResponse) -> Result<(), Error> {
    let signer = Self::assert_caller_is_signer();
    ...
    self.assert_caller_is_attested_participant_and_protocol_active();
``` [3](#0-2) 

There is no threshold vote, no multi-party agreement, and no cryptographic proof required for the `AppPublicKey` variant. One attested participant is sufficient to resolve any pending CKD yield.

The CKD request construction binds the `app_id` to the predecessor account and derivation path, but the response itself is never checked against the master public key for the non-PV variant:

```rust
// crates/contract/src/primitives/ckd.rs ~L17-30
impl CKDRequest {
    pub fn new(...) -> Self {
        let app_id = derive_app_id(predecessor_id, derivation_path);
        Self { app_public_key, app_id, domain_id }
    }
}
``` [4](#0-3) 

---

### Impact Explanation

The CKD protocol is designed so that the user recovers a secret as:

```
secret = big_c - a * big_y
```

where `a` is the user's ephemeral secret key and `A = a * G1` is their public key submitted in the request.

An attacker who controls `big_c` and `big_y` can choose any known scalar `y` and set:
- `big_y = y * G1`
- `big_c = target_point + y * A`

The user then computes:
```
secret = (target_point + y * A) - a * (y * G1)
       = target_point + y * a * G1 - a * y * G1
       = target_point
```

The attacker forces the user's derived secret to be any value of the attacker's choosing. The attacker knows `target_point`, so they also know the user's "confidential" key. This is a complete break of the CKD confidentiality guarantee.

**Impact class**: Critical — unauthorized access to secret material that materially enables secret recovery. The user believes they hold a private key known only to them; in reality the attacker knows it too.

---

### Likelihood Explanation

The attacker must be a single attested participant in the MPC network — strictly below the signing threshold. This is a realistic Byzantine adversary model explicitly in scope for MPC security. The attack requires:

1. Being one attested participant (not threshold collusion).
2. Monitoring the NEAR blockchain for pending `request_app_private_key` calls using the `AppPublicKey` variant (publicly visible on-chain).
3. Racing the legitimate MPC leader by calling `respond_ckd` with a forged response before the honest nodes do.

The `AppPublicKey` (non-PV) variant is the **default/legacy** format documented in the contract README and the `ckd-example-cli`, making it the most commonly used path:

```
// crates/contract/README.md ~L128-138
_Privately verifiable ckd request (legacy)_
{
  "request": {
    "derivation_path": "mykey",
    "app_public_key": "bls12381g1:6KtVVcAAGacrjNGePN8bp3KV6fYGrw1rFsyc7cVJCqR16Zc2ZFg3HX3hSZxSfv1oH6",
    ...
  }
}
``` [5](#0-4) 

---

### Recommendation

1. **Require `AppPublicKeyPV` for all new CKD requests** and deprecate the `AppPublicKey` variant. The `AppPublicKeyPV` variant already has a correct on-chain pairing check via `ckd_output_check`.

2. If the `AppPublicKey` variant must be retained for backwards compatibility, add an equivalent on-chain verification. The contract already holds the master BLS public key; a proof-of-correct-encryption (e.g., a Schnorr-style DLEQ proof over G1) should be required alongside the response.

3. Align `respond_ckd` with `respond` (ECDSA): the ECDSA path always verifies the submitted signature against the derived public key before resolving the yield. The CKD path should enforce the same principle for both variants.

---

### Proof of Concept

```
1. Attacker is one attested participant in the MPC network (below signing threshold).

2. Victim calls request_app_private_key with:
     app_public_key: AppPublicKey(A)   // legacy non-PV variant
     derivation_path: "mykey"

3. Attacker observes the pending CKDRequest on-chain (publicly visible).

4. Attacker chooses scalar y, computes:
     big_y = y * G1
     big_c = y * A          // forces secret = 0, or any chosen target_point

5. Attacker calls respond_ckd(request, CKDResponse { big_c, big_y })
   before the honest MPC leader does.

6. Contract executes:
     match &request.app_public_key {
         AppPublicKey(_) => {}   // no check — forged response accepted
         ...
     }
     pending_requests::resolve_yields_for(...)  // yield resolved with forged data

7. Victim receives CKDResponse { big_c, big_y } and computes:
     secret = big_c - a * big_y = y*A - a*y*G1 = 0   (or attacker's chosen value)

8. Attacker knows the victim's "confidential" derived key.
   Any application relying on this key for encryption or authentication is compromised.
``` [6](#0-5)

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

**File:** crates/contract/src/primitives/ckd.rs (L17-30)
```rust
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
