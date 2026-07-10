### Title
CKD Output Validity Check Skipped for `AppPublicKey` Variant in `respond_ckd` — (File: `crates/contract/src/lib.rs`)

---

### Summary

In `respond_ckd`, the cryptographic output validity check (`ckd_output_check`) is placed inside only one branch of a `match` on `request.app_public_key`. When the request uses the `AppPublicKey` variant (the non-publicly-verifiable, legacy path), the branch body is empty and the check is never executed. A single Byzantine attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary, forged `CKDResponse` for any pending `AppPublicKey`-type CKD request, and the contract will accept and deliver it to the user without any cryptographic verification.

---

### Finding Description

`respond_ckd` in `crates/contract/src/lib.rs` contains the following match block:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← empty: no check
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

The `ckd_output_check` function (defined in `crates/contract/src/primitives/ckd.rs`) performs the pairing-based cryptographic check that verifies the BLS12-381 CKD output is correctly formed against the MPC network's public key and the caller's app public key. [2](#0-1) 

For `AppPublicKeyPV` requests, this check is enforced. For `AppPublicKey` requests — the legacy, non-publicly-verifiable variant — the `AppPublicKey(_) => {}` arm is a no-op: the check is entirely absent. [1](#0-0) 

After the match block, `pending_requests::resolve_yields_for` is called unconditionally, which resumes all waiting yield promises with whatever `response` was supplied — verified or not. [3](#0-2) 

The `AppPublicKey` variant is the original, widely-used path. The contract README documents it as the default for `request_app_private_key` callers who do not opt into public verifiability. [4](#0-3) 

---

### Impact Explanation

A single attested participant (one honest-but-malicious node, strictly below the signing threshold) can:

1. Observe any pending `AppPublicKey`-type CKD request in the contract's `pending_ckd_requests` map.
2. Call `respond_ckd` with an arbitrary `CKDResponse { big_y, big_c }` of their choosing.
3. Because `AppPublicKey(_) => {}` performs no cryptographic check, the contract accepts the forged response unconditionally.
4. `resolve_yields_for` resumes all queued yield promises with the forged output, delivering it to the user.

The user receives a confidential key derivation output that was not produced by the threshold MPC protocol — it was unilaterally fabricated by one participant. This constitutes **unauthorized confidential key derivation output without the required participant authorization**, matching the Critical impact class: *"Unauthorized … confidential key derivation output without the required participant authorization."* [5](#0-4) 

---

### Likelihood Explanation

- The attacker only needs to be a single attested participant — no threshold collusion required.
- The `AppPublicKey` variant is the default/legacy path used by most callers (it predates `AppPublicKeyPV`).
- The attack requires no special timing, no network-level access, and no privileged operator role beyond being an attested participant.
- The attacker can observe pending requests on-chain and race to call `respond_ckd` before the honest coordinator does. [6](#0-5) 

---

### Recommendation

Move `ckd_output_check` outside the `AppPublicKeyPV`-only branch, or add an equivalent check for `AppPublicKey`. The check should be mandatory for all CKD response variants before `resolve_yields_for` is called. If `AppPublicKey` does not carry enough information for the same pairing check, the contract should either reject `AppPublicKey` responses without a separate validity proof, or require callers to migrate to `AppPublicKeyPV`. [5](#0-4) 

---

### Proof of Concept

1. User calls `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(some_bls_g1_key)`. A pending CKD request is stored in `pending_ckd_requests`.
2. Attacker (a single attested participant) calls `respond_ckd` with the same `CKDRequest` and a fabricated `CKDResponse { big_y: [0u8;48], big_c: [0u8;48] }`.
3. `respond_ckd` passes `assert_caller_is_attested_participant_and_protocol_active` (attacker is attested). [7](#0-6) 
4. The match hits `AppPublicKey(_) => {}` — no check runs. [8](#0-7) 
5. `resolve_yields_for` resumes the user's yield with the forged response. [3](#0-2) 
6. The user's callback receives a `CKDResponse` that was never computed by the threshold protocol — the attacker has injected an arbitrary confidential key derivation output.

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

**File:** crates/contract/src/primitives/ckd.rs (L1-3)
```rust
use blstrs::G1Projective;
use near_account_id::AccountId;
use near_mpc_contract_interface::types as dtos;
```

**File:** crates/contract/README.md (L276-282)
```markdown
#### CKDRequestArgs (Latest version)

The `request_app_private_key` request takes the following arguments:

- `derivation_path` (String): the derivation path.
- `app_public_key`: the ephemeral public key to encrypt the generated confidential key. Accepts either a plain G1 point string (privately verifiable, legacy) or a tagged enum with `AppPublicKey` (single G1 point) or `AppPublicKeyPV` (a `{pk1, pk2}` pair for public verifiability).
- `domain_id` (integer): the domain ID that identifies the key and signature scheme to use to generate the confidential key
```
