### Title
Mode-Dependent CKD Output Validation Bypass Allows Single Byzantine Participant to Forge Confidential Key Derivation Output - (`File: crates/contract/src/lib.rs`)

### Summary

The `respond_ckd` function in the MPC contract applies a cryptographic output check (`ckd_output_check`) only when the request uses the `AppPublicKeyPV` (publicly verifiable) variant, but performs **no output verification** for the legacy `AppPublicKey` variant. A single Byzantine attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary forged `CKDResponse` for any pending `AppPublicKey` request, and the contract will accept and deliver the forged key material to the user without any cryptographic check.

---

### Finding Description

In `respond_ckd`, the contract branches on the `app_public_key` variant of the pending `CKDRequest`:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← NO CHECK
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies that the encrypted output in `response` is correctly formed under the app's public key pair `(pk1, pk2) = (a·G1, a·G2)` and the MPC root key — this is possible on-chain because the `pk2 = a·G2` component enables pairing-based verification without knowing the secret `a`.

For `AppPublicKey` (legacy), only `pk1 = a·G1` is provided. The contract cannot perform the same pairing check, so the match arm is empty — the response is accepted unconditionally.

The only gate before this branch is `assert_caller_is_attested_participant_and_protocol_active`, which requires the caller to be a current attested participant. A single Byzantine participant satisfies this requirement. Once past that gate, for any pending `AppPublicKey` CKD request, the Byzantine participant can supply any `CKDResponse` value — including one encrypting a key of the attacker's choice — and `resolve_yields_for` will drain the entire fan-out queue, delivering the forged material to every waiting caller:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

Because `resolve_yields_for` removes the request from the map on first call, the honest nodes' subsequent `respond_ckd` calls return `RequestNotFound` — the forged response is the only one the user ever receives. [3](#0-2) 

This is structurally analogous to the referenced external report: in that report, a minimum-credit check was applied uniformly regardless of the `exactAmountIn` mode, causing the wrong unit to be compared. Here, the output-validity check is applied only for `AppPublicKeyPV` and is entirely absent for `AppPublicKey`, causing the wrong (zero) validation to be applied for the legacy mode.

---

### Impact Explanation

A single Byzantine attested participant (below the signing threshold) can deliver forged confidential key derivation output to any user who submits a CKD request using the legacy `AppPublicKey` mode. The user receives an encrypted blob that, when decrypted with their ephemeral secret `a`, yields a key chosen by the attacker rather than the MPC-derived key. Any assets or secrets the user subsequently protects with that derived key are under the attacker's control.

This matches the allowed critical impact: **"Unauthorized transaction execution, threshold signature issuance, or confidential key derivation output without the required participant authorization."**

The attack requires only one malicious participant — well below the reconstruction threshold — and no threshold collusion.

---

### Likelihood Explanation

- The `AppPublicKey` (legacy) mode is the default single-point form documented in the contract README and is the path most existing integrations use.
- A pending CKD request is observable on-chain by all participants.
- The Byzantine participant only needs to call `respond_ckd` before the honest nodes do. In a network with any latency variance, a racing malicious node can reliably win.
- No special cryptographic capability is required: the attacker supplies an arbitrary `CKDResponse` struct; the contract imposes no structural constraint on it for `AppPublicKey` requests.

---

### Recommendation

1. **Require `AppPublicKeyPV` for all new CKD requests** and deprecate `AppPublicKey`. The publicly verifiable variant already exists precisely to close this gap.
2. If `AppPublicKey` must remain supported, document explicitly that it provides no on-chain integrity guarantee and that users accept the risk of a single Byzantine participant forging the output.
3. Consider adding a quorum requirement: require that at least `threshold` participants submit identical `CKDResponse` values before resolving the yield, analogous to how threshold signing works for ECDSA/EdDSA.

---

### Proof of Concept

**Setup**: Contract is `Running`, one CKD domain (BLS12-381) exists, and participant `mallory` is an attested participant (Byzantine, below threshold).

**Step 1 — User submits a legacy CKD request:**
```json
{
  "derivation_path": "my-app-key",
  "domain_id": 2,
  "app_public_key": { "AppPublicKey": "bls12381g1:<user_pk1>" }
}
```
The contract stores the request in `pending_ckd_requests` and issues a yield promise to the user.

**Step 2 — Mallory observes the pending request on-chain** (via `get_pending_ckd_request` view call or chain indexer).

**Step 3 — Mallory calls `respond_ckd` with a forged response:**
```json
{
  "request": { /* exact CKDRequest matching the pending entry */ },
  "response": { /* CKDResponse encrypting mallory's chosen key */ }
}
```

**Step 4 — Contract execution in `respond_ckd`:**
- `assert_caller_is_attested_participant_and_protocol_active` → passes (mallory is attested)
- `public_key_extended(domain_id)` → returns BLS12-381 key → passes
- `match &request.app_public_key { AppPublicKey(_) => {} }` → **empty arm, no check**
- `resolve_yields_for` → removes the request, resumes the user's yield with the forged response

**Step 5 — Honest nodes' `respond_ckd` calls** return `RequestNotFound` — the forged response has already been delivered.

**Step 6 — User decrypts the response** with their ephemeral secret `a` and obtains a key controlled by mallory, not the MPC network. [4](#0-3) [5](#0-4)

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

**File:** crates/contract/src/pending_requests.rs (L43-59)
```rust
pub(crate) fn push_pending_yield<K>(
    requests: &mut LookupMap<K, Vec<YieldIndex>>,
    request: K,
    data_id: CryptoHash,
) where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let queue = requests.entry(request).or_default();
    if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
        env::panic_str(
            &RequestError::PendingRequestQueueFull {
                limit: MAX_PENDING_REQUEST_FAN_OUT,
            }
            .to_string(),
        );
    }
    queue.push(YieldIndex { data_id });
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
