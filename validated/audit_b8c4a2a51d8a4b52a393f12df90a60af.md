### Title
Missing CKD Response Validation for `AppPublicKey` Variant Allows Single Byzantine Participant to Deliver Forged Key Derivation Output - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_ckd` performs cryptographic output validation only when the request uses the `AppPublicKeyPV` variant. When the legacy `AppPublicKey` variant is used, the contract accepts any `CKDResponse` from any single attested participant without verification, bypassing the threshold requirement for confidential key derivation.

### Finding Description

In `respond_ckd`, the response validation branch is:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no validation at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies that the encrypted output is correctly derived from the MPC master key using the publicly-verifiable key pair. For `AppPublicKey`, the arm is a no-op — the contract accepts any `CKDResponse` bytes unconditionally.

`respond_ckd` requires only **one** attested participant to call it; there is no on-chain threshold enforcement for the response submission: [2](#0-1) 

Once `resolve_yields_for` is called, the entire pending queue for that request is drained and the response is delivered to all waiting callers: [3](#0-2) 

The first `respond_ckd` call that succeeds wins. A Byzantine attested participant can race honest nodes and submit a crafted `CKDResponse` before them.

### Impact Explanation

A single Byzantine attested participant (strictly below the signing threshold) can:

1. Observe a pending `request_app_private_key` call using `AppPublicKey`.
2. Craft a `CKDResponse` where `big_c` is an encryption of an attacker-chosen key under the user's `app_public_key`.
3. Call `respond_ckd` before honest nodes, delivering the forged response.
4. The user decrypts the response and obtains a key the attacker already knows — a full confidential key compromise.

This is "confidential key derivation output without the required participant authorization" — a Critical impact under the allowed scope. [2](#0-1) 

### Likelihood Explanation

- Any single attested participant can exploit this; no threshold collusion is required.
- The `AppPublicKey` (legacy) variant is still accepted by `request_app_private_key` and is the default for existing integrations. [4](#0-3) 

- The attacker only needs to submit their transaction before the honest leader node, which is feasible given NEAR's public mempool and variable block times.

### Recommendation

Either:

1. **Require `AppPublicKeyPV`** in `respond_ckd` and reject `AppPublicKey` requests at the `respond_ckd` entry point (analogous to the Cantina Managed fix of "not supporting empty `CallbackParams`").
2. **Or**, add an equivalent off-chain commitment scheme so the contract can verify `AppPublicKey` responses without the user's secret — e.g., require the submitting node to include a zero-knowledge proof of correct derivation.

The `AppPublicKeyPV` path already demonstrates the correct pattern: [5](#0-4) 

### Proof of Concept

1. User calls `request_app_private_key` with `AppPublicKey(pk)` where `pk = a·G1` (user's BLS secret `a`).
2. Byzantine attested participant constructs `CKDResponse { big_y: arbitrary, big_c: encrypt(attacker_key, pk) }`.
3. Byzantine participant calls `respond_ckd(request, forged_response)` — passes all on-chain checks because the `AppPublicKey` arm is a no-op.
4. `resolve_yields_for` drains the queue; the user's yield resumes with the forged response.
5. User decrypts `big_c` using secret `a` and obtains `attacker_key` — a key the attacker already knows.
6. Honest nodes' subsequent `respond_ckd` calls return `Err(RequestNotFound)` — the queue is already drained. [6](#0-5)

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

**File:** crates/contract/README.md (L118-120)
```markdown
- `app_public_key`: the ephemeral public key for the CKD request. Two formats are supported:
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
```
