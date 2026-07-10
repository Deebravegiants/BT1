### Title
Unverified CKD Response for `AppPublicKey` (Non-PV) Allows Single Byzantine Participant to Forge Confidential Key Output - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_ckd` in the MPC contract performs no cryptographic output verification when the CKD request uses the `AppPublicKey` (non-publicly-verifiable) variant. Any single attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary, attacker-crafted `CKDResponse` and the contract will accept it, drain the pending-request queue, and deliver the fake key to every waiting caller. This is the direct analog of the OracleLess "unspent approval not reset" class: a capability (the right to resolve a pending request) is granted to any attested participant, but for non-PV CKD requests the contract never verifies that the response is the genuine output of the threshold computation, leaving a residual, unchecked resolution path that a single Byzantine node can exploit.

### Finding Description

In `respond_ckd` (`crates/contract/src/lib.rs`, lines 675–682), the contract branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← NO CHECK
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

For `AppPublicKeyPV`, `ckd_output_check` verifies that the encrypted output is consistent with the BLS12-381 master public key and the app's ephemeral key pair — a check that requires only public data and is therefore feasible on-chain. For `AppPublicKey` (non-PV), the arm is empty: the response bytes `big_y` and `big_c` are accepted unconditionally and immediately forwarded to all queued callers via `pending_requests::resolve_yields_for`.

The only gate before this branch is `assert_caller_is_attested_participant_and_protocol_active()`, which requires the caller to be a single attested participant — not a threshold quorum. A Byzantine node that has passed TEE attestation satisfies this check alone.

Attack path:
1. User calls `request_app_private_key` with `AppPublicKey` (non-PV). The request is stored in `pending_ckd_requests` and all fields (`app_public_key`, `domain_id`, `predecessor_account_id`, `derivation_path`) are visible on-chain.
2. Byzantine participant reconstructs the `CKDRequest` key from on-chain data.
3. Byzantine participant crafts a `CKDResponse { big_y, big_c }` where `big_y` and `big_c` are BLS12-381 G1 points that encrypt a key the attacker already knows, using the user's public `app_public_key`.
4. Byzantine participant calls `respond_ckd(request, fake_response)` before any honest node responds.
5. The contract accepts the response (no check for `AppPublicKey`), removes the entry from `pending_ckd_requests`, and resumes all queued yields with the attacker-controlled bytes.
6. The user decrypts the response with their app secret key and obtains a key that the attacker also knows. The confidentiality guarantee of CKD is broken.

### Impact Explanation

The user believes they have received a private confidential key known only to the MPC network and themselves. In reality, the attacker crafted the ciphertext and knows the plaintext. Any secret material the user derives from or protects with this key (e.g., application-specific private keys, encrypted data) is compromised. This maps directly to the allowed Critical impact: **unauthorized confidential key derivation output without the required participant authorization** and **bypass of threshold-signature requirements**.

### Likelihood Explanation

The attack requires only one Byzantine participant that has passed TEE attestation — strictly below the signing threshold. The attacker races honest nodes to call `respond_ckd` first. Because the attacker is an on-chain participant with a function-call key already registered, they can submit the transaction in the same block as the user's `request_app_private_key` call. No collusion, no leaked key, and no network-level DoS is required.

### Recommendation

Apply the same on-chain output check to `AppPublicKey` requests that is already applied to `AppPublicKeyPV` requests, or reject `AppPublicKey` (non-PV) requests at the contract level and require callers to use `AppPublicKeyPV` so the contract can always verify the response before delivering it. If `AppPublicKey` must remain supported for backwards compatibility, the contract should at minimum verify that the response points are valid BLS12-381 G1 elements and are consistent with the master public key and the request's `app_id`, even if full decryption-correctness cannot be checked without the app secret key.

### Proof of Concept

```
1. Alice calls request_app_private_key({
       derivation_path: "my-path",
       app_public_key: AppPublicKey(alice_bls_pk),
       domain_id: 0
   }) with 1 yoctoNEAR attached.

2. Contract stores CKDRequest in pending_ckd_requests.
   All fields are visible on-chain.

3. Mallory (attested participant, account mallory.near) reads the request.
   Mallory picks a known BLS scalar s, computes:
       big_y = s * alice_bls_pk   (encryption of s to Alice's key)
       big_c = s * G1             (commitment)
   (exact BLS12-381 CKD encryption formula)

4. Mallory calls respond_ckd(ckd_request, CKDResponse { big_y, big_c }).
   Contract checks: caller is attested participant ✓
   Contract checks: AppPublicKey branch → no check ✓
   Contract calls resolve_yields_for → Alice's yield is resumed with Mallory's bytes.

5. Alice decrypts big_y with her app secret key and obtains s.
   Mallory already knows s.
   Alice's "confidential" key is known to Mallory.
``` [1](#0-0) [2](#0-1) [3](#0-2)

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
