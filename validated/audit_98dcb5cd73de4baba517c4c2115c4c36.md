### Title
Missing CKD Response Verification for `AppPublicKey` Variant Allows Single Byzantine Participant to Forge Key Derivation Output - (File: crates/contract/src/lib.rs)

### Summary

The `respond_ckd` function in the MPC contract enforces cryptographic output verification (`ckd_output_check`) only for the `AppPublicKeyPV` variant of CKD requests. For the `AppPublicKey` variant, no verification of the response is performed at the contract level. A single Byzantine attested participant — strictly below the signing threshold — can race to submit an arbitrary CKD response for any pending `AppPublicKey` request, delivering forged key material to the requesting user without the threshold protocol having been executed.

### Finding Description

The `request_app_private_key` entry point accepts two variants of the app public key: [1](#0-0) 

At request time, `AppPublicKey` receives no validation while `AppPublicKeyPV` is checked via `app_public_key_check`. The same asymmetry is reproduced in `respond_ckd`: [2](#0-1) 

For `AppPublicKeyPV`, `ckd_output_check` verifies the cryptographic correctness of the CKD response against the BLS root public key and the app public key, enforcing that the response was produced by the threshold protocol. For `AppPublicKey`, this block is a no-op — the contract performs **zero cryptographic verification** of the response content before resolving the yield: [3](#0-2) 

The `resolve_yields_for` helper removes the pending entry and resumes all queued yields with whatever bytes the caller supplied: [4](#0-3) 

The only gate on `respond_ckd` is `assert_caller_is_attested_participant_and_protocol_active()`, which any single attested participant satisfies: [5](#0-4) 

**Attack path:**
1. Attacker is one attested participant (below threshold).
2. A user submits `request_app_private_key` with `AppPublicKey` variant and the minimum 1 yoctoNEAR deposit.
3. The request is enqueued as a pending CKD yield.
4. Before the honest MPC nodes complete the threshold protocol and submit a legitimate response, the Byzantine participant calls `respond_ckd` with an arbitrary `CKDResponse` containing attacker-chosen key material.
5. `resolve_yields_for` drains the queue and resumes the user's yield with the forged response — no cryptographic check is performed.
6. The user receives attacker-controlled key material as their derived private key.

This is a direct analog to the ERC20 `_mint` pattern: just as writing directly to `_balances` bypasses `_totalSupply` and event invariants, accepting a CKD response for `AppPublicKey` without `ckd_output_check` bypasses the invariant that every CKD output must be cryptographically bound to the threshold BLS key and the app public key.

### Impact Explanation

**Critical.** A single Byzantine attested participant can deliver arbitrary key material to any user who submits a CKD request using the `AppPublicKey` variant. The threshold requirement — the core security property of the MPC network — is entirely bypassed at the contract level for this request type. The user's derived private key is under attacker control, enabling theft of any assets or secrets protected by that key. This maps directly to: *"Unauthorized confidential key derivation output without the required participant authorization."*

### Likelihood Explanation

Any single attested MPC participant can execute this attack. Attestation is a prerequisite but not a high bar — it is the normal operational state for every node in the network. The attack requires only that the Byzantine node submits its forged `respond_ckd` call before the honest nodes complete the threshold protocol and submit the legitimate response. Given that the threshold protocol involves multiple rounds of P2P communication, a Byzantine node that deliberately stalls its participation in the protocol can trivially win this race. The `AppPublicKey` variant is a documented, supported request type reachable by any user.

### Recommendation

Apply `ckd_output_check` unconditionally for both `AppPublicKey` and `AppPublicKeyPV` variants in `respond_ckd`, or — if `AppPublicKey` responses cannot be verified against a known app public key — require that all CKD requests use `AppPublicKeyPV` so that every response is cryptographically bound to the threshold key. The check should mirror the `AppPublicKeyPV` branch:

```rust
// In respond_ckd, replace the match with:
if !ckd_output_check(&request.app_id, &response, &derived_app_pk, &public_key) {
    env::panic_str("CKD output check failed");
}
```

If `AppPublicKey` semantically cannot carry a verifiable app public key, the variant should be removed from the CKD flow entirely, or the contract must document and accept that `AppPublicKey` CKD responses are unverified (and adjust the threat model accordingly).

### Proof of Concept

1. Deploy the MPC contract in `Running` state with at least one attested participant (`alice.near`).
2. As any user (`bob.near`), call `request_app_private_key` with `app_public_key: AppPublicKey(some_pk)`, attaching 1 yoctoNEAR.
3. As `alice.near` (a single attested participant, below threshold), immediately call `respond_ckd` with the matching `CKDRequest` key and a `CKDResponse` containing attacker-chosen key bytes.
4. Observe that `respond_ckd` succeeds (no panic, `Ok(())` returned) and `bob.near`'s yield is resumed with the forged response — without the threshold BLS protocol having been executed and without any cryptographic verification at the contract level. [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L484-491)
```rust
        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(pk) => {
                if !app_public_key_check(pk) {
                    env::panic_str("app public key check failed")
                }
            }
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
