### Title
Single Attested Participant Can Deliver Forged CKD Output for Legacy `AppPublicKey` Requests — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function performs **no cryptographic validation** of the response payload when the CKD request uses the legacy `AppPublicKey` variant. A single attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary, attacker-fabricated `CKDResponse`, which the contract accepts and delivers to the waiting user without any verification. This is the direct analog of M-05: just as `gib` allowed a privileged actor to drain vault funds without any collateral-ratio condition, `respond_ckd` allows a single participant to deliver arbitrary confidential key derivation output without any cryptographic condition.

---

### Finding Description

In `respond_ckd`, after confirming the caller is an attested participant, the contract branches on the `app_public_key` variant:

```rust
// crates/contract/src/lib.rs  lines 675-682
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← empty: no validation
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For the `AppPublicKeyPV` (publicly verifiable) variant, `ckd_output_check` verifies the response against the app's public key and the MPC root public key using a BLS12-381 pairing check. For the legacy `AppPublicKey` variant, the match arm is **completely empty** — no check of any kind is performed. The response is then immediately forwarded to `resolve_yields_for`, which resumes the yield and delivers the payload to the waiting user:

```rust
// crates/contract/src/lib.rs  lines 684-688
pending_requests::resolve_yields_for(
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

The full `respond_ckd` function, showing the attested-participant gate followed by the unguarded legacy branch: [3](#0-2) 

The `AppPublicKey` variant is the legacy format documented in the contract README and is still accepted by the live contract: [4](#0-3) 

---

### Impact Explanation

**Impact: Critical — Confidential key derivation output without the required participant authorization.**

A `CKDResponse` carries `big_y` and `big_c` — the encrypted confidential key material the user's application uses to derive a private key. If these values are attacker-controlled, the derived key is controlled by the attacker, not the MPC network. Any assets, secrets, or cross-chain accounts protected by that derived key are immediately at risk of theft. The attack is unconditional: the contract imposes no cryptographic bound on what a single participant may submit for a legacy request.

---

### Likelihood Explanation

Any single attested participant can execute this attack without any additional collusion. The attacker only needs to:

1. Be an active attested participant in the MPC network (a role reachable without threshold-level collusion — one node out of n).
2. Observe a pending legacy `AppPublicKey` CKD request in contract state (public on-chain).
3. Race the honest nodes by calling `respond_ckd` with fabricated `big_y`/`big_c` values.

The `request_app_private_key` endpoint is open to any NEAR account with 1 yoctoNEAR, so the pool of exploitable requests is large. The legacy variant is still the default for many integrations.

---

### Recommendation

Add cryptographic validation for the `AppPublicKey` branch in `respond_ckd`. At minimum, verify that the response is consistent with the MPC root public key and the request's `app_id`. The `AppPublicKeyPV` path already demonstrates the correct pattern via `ckd_output_check`. Alternatively, deprecate the legacy `AppPublicKey` variant and require all new requests to use `AppPublicKeyPV`, which is publicly verifiable on-chain.

---

### Proof of Concept

1. Attacker is an attested participant (`attacker.near`).
2. User submits a CKD request using the legacy `AppPublicKey` variant via `request_app_private_key`.
3. Attacker calls `respond_ckd` with a fabricated response:
   ```rust
   respond_ckd(
       ckd_request,                          // matches the pending request
       CKDResponse {
           big_y: Bls12381G1PublicKey([0u8; 48]),  // attacker-chosen
           big_c: Bls12381G1PublicKey([0u8; 48]),  // attacker-chosen
       }
   )
   ```
4. The contract reaches the `AppPublicKey(_) => {}` branch — no validation fires.
5. `resolve_yields_for` resumes the user's yield with the forged payload.
6. The user's application receives attacker-controlled key material and derives a key the attacker already knows. [1](#0-0) [2](#0-1)

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

**File:** crates/contract/README.md (L109-125)
```markdown
### Submitting a confidential key derivation (ckd) request

Users can submit a ckd request to the MPC network via the
`request_app_private_key` endpoint of this contract. A **deposit of 1
yoctonear is required** (see [Deposit requirement](#deposit-requirement)).

The ckd request takes the following arguments:

- `derivation_path` (String): the derivation path (used to derive different keys from the same account).
- `app_public_key`: the ephemeral public key for the CKD request. Two formats are supported:
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
- `domain_id` (integer): identifies the master key to use for deriving the ckd, and must correspond to bls12381.

Submitting a ckd request costs approximately 7 Tgas, but the contract requires
that at least 10 Tgas are attached to the transaction.

```
