### Title
Missing CKD Response Verification for `AppPublicKey` Variant Allows Forged Key Derivation Output — (`crates/contract/src/lib.rs`)

### Summary

The `respond_ckd` function in the MPC contract applies `ckd_output_check` only for the `AppPublicKeyPV` variant of a CKD request, leaving the `AppPublicKey` variant completely unverified. This is the direct analog of the `PhiNFT1155` bug: a verification mechanism is declared and implemented for one code path but silently omitted from another, allowing a Byzantine participant acting as the designated responder to submit an arbitrary forged CKD output that the contract will accept and deliver to the user.

### Finding Description

In `respond_ckd`, after the caller is authenticated as an attested participant, the contract retrieves the BLS12-381 master public key and then branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check at all
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
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` cryptographically verifies that the submitted `CKDResponse` is the correct derivation of the network's master key for the given `app_id` and app public key. For `AppPublicKey`, the arm is a no-op (`{}`), and `resolve_yields_for` is called unconditionally with whatever bytes the caller supplied. The contract's only other defense — `assert_caller_is_attested_participant_and_protocol_active` — confirms the caller is a current, TEE-attested participant, but does not verify the *content* of the response. [2](#0-1) 

The `request_app_private_key` entry point accepts both variants: [3](#0-2) 

Both variants are stored identically in `pending_ckd_requests` and resolved by the same `resolve_yields_for` call, so the missing check is not compensated elsewhere.

### Impact Explanation

**Critical — Confidential key derivation output without required participant authorization.**

The threshold MPC protocol is designed so that no single node can unilaterally determine the CKD output; t+1 nodes must collaborate. The on-chain `ckd_output_check` is the contract's enforcement of this property: it verifies the submitted result against the network's public key, ensuring the output is the one the threshold actually computed. Omitting this check for `AppPublicKey` requests means a single Byzantine participant acting as the designated responder can:

1. Participate honestly in the off-chain MPC round (to satisfy the threshold and obtain a valid share).
2. Discard the honest aggregate and call `respond_ckd` with an arbitrary `CKDResponse`.
3. The contract accepts and delivers the forged output to the user.

The user receives a key that the attacker chose, not the one the threshold computed. Depending on the application, this enables the attacker to know (or control) the user's derived application key, breaking the confidentiality guarantee of the CKD scheme.

### Likelihood Explanation

Any single attested participant that wins the role of designated responder for a CKD request using the `AppPublicKey` variant can exploit this. The attacker does not need to compromise the threshold; they only need to be one of the current participants (already a realistic Byzantine assumption the system is designed to tolerate at the threshold level). The `AppPublicKey` variant is a documented, production-facing API path.

### Recommendation

Apply `ckd_output_check` to the `AppPublicKey` arm in the same way it is applied to `AppPublicKeyPV`. If the check's signature needs to be adapted for the `AppPublicKey` type, a dedicated verification function should be introduced. The fix mirrors the recommendation in the external report: the verification mechanism already exists — it simply needs to be wired into the missing code path.

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

### Proof of Concept

1. Deploy the contract in `Running` state with a BLS12-381 CKD domain.
2. User calls `request_app_private_key` with an `AppPublicKey` variant and attaches the minimum deposit. The contract enqueues a yield.
3. A Byzantine attested participant (any single node) calls `respond_ckd` with the correct `CKDRequest` but a fabricated `CKDResponse` containing an arbitrary encrypted blob.
4. The contract executes the `AppPublicKey` arm (`{}`), skips all verification, and calls `resolve_yields_for` with the fabricated bytes.
5. The user's yield resumes and they receive the attacker-chosen key material — not the threshold-computed derivation.

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
