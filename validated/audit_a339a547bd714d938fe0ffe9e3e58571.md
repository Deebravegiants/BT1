### Title
Single Byzantine Participant Can Deliver Arbitrary CKD Output for `AppPublicKey` Requests, Bypassing Threshold Requirement — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` performs no cryptographic verification of the submitted `CKDResponse` when the request uses the `AppPublicKey` variant. A single Byzantine attested participant can call `respond_ckd` with arbitrary `big_y`/`big_c` values, resolve all pending yields for the victim's CKD request, and deliver a malicious derived-key ciphertext — without any threshold of honest participants agreeing on the output.

---

### Finding Description

The `respond_ckd` method in `crates/contract/src/lib.rs` handles two variants of `CKDAppPublicKey`:

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

For `AppPublicKeyPV`, the contract calls `ckd_output_check`, which verifies the pairing relationship between the submitted ciphertext and the MPC network's BLS12-381 public key. For `AppPublicKey`, the arm is a no-op — the contract unconditionally proceeds to `resolve_yields_for`, delivering whatever `big_y` and `big_c` the caller supplied. [2](#0-1) 

The access-control gate (`assert_caller_is_attested_participant_and_protocol_active`) only confirms the caller holds a valid TEE attestation and is in the active participant set. It does not enforce that the submitted response is the output of the threshold protocol. [3](#0-2) 

Because `resolve_yields_for` resolves **all** pending yields for the request in a single call, the first `respond_ckd` call wins. Subsequent honest-participant submissions find no remaining yields and are silently ignored.

---

### Impact Explanation

A single Byzantine attested participant can:

1. Monitor the chain for pending `CKDRequest` entries whose `app_public_key` is `AppPublicKey`.
2. Call `respond_ckd` with fabricated `big_y` and `big_c` values before any honest participant.
3. The contract accepts the response without verification and resolves all waiting yields with the malicious ciphertext.
4. The requesting application (e.g., a TEE app managing foreign-chain assets) receives a wrong encrypted key. If it uses that key to control funds, those funds are permanently inaccessible or transferred to an attacker-controlled address.

This is a **Critical** impact: confidential key derivation output is produced without the required threshold-participant authorization. The threshold requirement — that t-of-n participants must agree on the derived key — is entirely bypassed for the `AppPublicKey` variant.

---

### Likelihood Explanation

The `AppPublicKey` variant is the default "privately verifiable" mode documented and supported in the contract ABI. [4](#0-3) 

Any single attested participant (one of the n nodes in the active set, strictly below the signing threshold) can execute this attack. The attacker only needs to observe a pending CKD request and submit a response before honest nodes do — a straightforward race on the NEAR mempool. No collusion, no key leakage, and no physical TEE compromise is required; the attacker is a legitimately attested participant who submits a malformed response.

---

### Recommendation

Apply the same `ckd_output_check` to the `AppPublicKey` variant. If a publicly-verifiable check is not possible for the single-point `AppPublicKey` form, either:

- Deprecate `AppPublicKey` in favour of `AppPublicKeyPV` (which already has an on-chain check), or
- Require that `respond_ckd` submissions include a threshold-aggregated proof (e.g., a BLS multi-signature over the response) that the contract can verify without knowing individual key shares.

---

### Proof of Concept

1. Alice calls `request_app_private_key` with `AppPublicKey(A)` and 1 yoctoNEAR deposit. A `CKDRequest` is stored in `pending_ckd_requests`. [5](#0-4) 

2. Mallory, a Byzantine attested participant, observes the pending request on-chain and immediately calls:

```
respond_ckd(
    request = <Alice's CKDRequest>,
    response = CKDResponse { big_y: [0u8; 48], big_c: [0u8; 48] }
)
```

3. `respond_ckd` passes `assert_caller_is_signer()` (Mallory signs directly) and `assert_caller_is_attested_participant_and_protocol_active()` (Mallory is a valid attested participant). The `AppPublicKey` arm executes no check. [6](#0-5) 

4. `resolve_yields_for` resolves all of Alice's pending yields with the fabricated response. Alice's contract callback receives `CKDResponse { big_y: [0; 48], big_c: [0; 48] }`. [2](#0-1) 

5. Honest participants subsequently attempt `respond_ckd` for the same request but find no pending yields — the request is already resolved. Alice has received a useless or attacker-chosen ciphertext instead of her legitimate derived key.

### Citations

**File:** crates/contract/src/lib.rs (L469-512)
```rust
    pub fn request_app_private_key(&mut self, request: CKDRequestArgs) {
        log!(
            "request_app_private_key: predecessor={:?}, request={:?}",
            env::predecessor_account_id(),
            request
        );

        let domain_id: DomainId = request.domain_id;
        let (_, predecessor) = self.check_request_preconditions(
            domain_id,
            DomainPurpose::CKD,
            Gas::from_tgas(self.config.ckd_call_gas_attachment_requirement_tera_gas),
            MINIMUM_CKD_REQUEST_DEPOSIT,
        );

        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(pk) => {
                if !app_public_key_check(pk) {
                    env::panic_str("app public key check failed")
                }
            }
        }

        let request = CKDRequest::new(
            request.app_public_key,
            domain_id,
            &predecessor,
            &request.derivation_path,
        );

        let callback_gas = Gas::from_tgas(
            self.config
                .return_ck_and_clean_state_on_success_call_tera_gas,
        );

        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_CK_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_ckd_request(request, id),
        );
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

**File:** crates/contract/README.md (L281-282)
```markdown
- `app_public_key`: the ephemeral public key to encrypt the generated confidential key. Accepts either a plain G1 point string (privately verifiable, legacy) or a tagged enum with `AppPublicKey` (single G1 point) or `AppPublicKeyPV` (a `{pk1, pk2}` pair for public verifiability).
- `domain_id` (integer): the domain ID that identifies the key and signature scheme to use to generate the confidential key
```
