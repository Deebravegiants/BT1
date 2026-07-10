### Title
Unverified CKD Response for `AppPublicKey` Variant Allows Single Attested Participant to Inject Arbitrary Key Derivation Output — (File: `crates/contract/src/lib.rs`)

### Summary
`respond_ckd` skips all cryptographic output verification when the pending request uses the `CKDAppPublicKey::AppPublicKey` variant. A single attested participant (strictly below the signing threshold) can race to call `respond_ckd` with a fabricated `CKDResponse` for any live `AppPublicKey`-typed CKD request, causing the contract to resolve the user's yield with attacker-controlled key material — without any threshold of nodes agreeing on the result.

### Finding Description
In `respond_ckd`, the contract branches on the `app_public_key` field of the pending `CKDRequest`:

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

For the `AppPublicKeyPV` variant, `ckd_output_check` cryptographically binds the response to the BLS12-381 root public key and the requester's app public key. For the `AppPublicKey` variant, the empty arm `{}` means **no binding whatsoever** — the contract accepts any `CKDResponse` the caller supplies. The only gate before this branch is `assert_caller_is_attested_participant_and_protocol_active`, which requires only a single valid TEE attestation, not a threshold quorum. [2](#0-1) 

The `assert_caller_is_attested_participant_and_protocol_active` helper confirms the signer holds a valid attestation and is in the active participant set, but it does not require any threshold agreement. [3](#0-2) 

After the (absent) check, `resolve_yields_for` immediately serialises the attacker-supplied `response` and calls `env::promise_yield_resume` for every queued yield under that request key, delivering the fabricated key material to all waiting callers. [4](#0-3) 

### Impact Explanation
The CKD flow is designed to deliver a threshold-computed confidential derived key to the requester. By injecting a fabricated `CKDResponse`, a single malicious participant can:

- Deliver a derived key the attacker controls (e.g., one whose private scalar the attacker knows), enabling decryption of any data the victim subsequently encrypts under it, or theft of any funds the victim deposits to an address derived from it.
- Deliver an identity/zero key, permanently destroying the confidentiality guarantee for that derivation.

This directly matches the allowed Critical impact: *"Unauthorized … confidential key derivation output without the required participant authorization."*

### Likelihood Explanation
Every attested participant can observe all pending `CKDRequest` entries on-chain (they are stored in `pending_ckd_requests` and emitted in logs). A malicious participant simply monitors for a new `AppPublicKey`-typed request and races to call `respond_ckd` before the legitimate leader. No special privilege, no key material, and no threshold collusion is required — only a valid TEE attestation, which every participant already holds by definition.

### Recommendation
Apply the same cryptographic output binding to the `AppPublicKey` variant that is already applied to `AppPublicKeyPV`. If a suitable on-chain check cannot be constructed for `AppPublicKey` (because no app-side proof is available), the contract should require that `respond_ckd` be called only after a threshold of participants have voted on the same `(request, response)` pair, mirroring the off-chain consensus that governs `respond` for signatures.

### Proof of Concept

1. User calls `request_app_private_key` with `app_public_key = AppPublicKey(some_pk)`, attaching 1 yoctoNEAR. The contract stores the `CKDRequest` in `pending_ckd_requests` and creates a yield.
2. Malicious attested participant `M` observes the pending request on-chain.
3. `M` constructs a `CKDResponse` containing a derived key whose private scalar `M` knows.
4. `M` calls `respond_ckd(request, fabricated_response)` directly from its NEAR account (satisfying `assert_caller_is_signer` and `assert_caller_is_attested_participant_and_protocol_active`).
5. The `AppPublicKey` branch executes the empty arm — no check fires.
6. `resolve_yields_for` resumes the user's yield with the fabricated response.
7. The user receives attacker-controlled key material; `M` can decrypt or spend anything the user does with it.

The legitimate leader's subsequent `respond_ckd` call returns `Err(RequestNotFound)` because the entry was already drained in step 6, so the attack leaves no on-chain trace of the substitution. [5](#0-4) [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L654-688)
```rust
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
