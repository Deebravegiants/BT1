### Title
Single Attested Participant Can Submit Forged CKD Response for `AppPublicKey` Variant, Bypassing Threshold Authorization — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function in `MpcContract` performs **no cryptographic verification** of the `CKDResponse` content when the request uses the legacy `AppPublicKey` variant. Any single attested participant can front-run the legitimate threshold-computed CKD output and deliver a forged confidential key derivation result to the user, bypassing the threshold-signature requirement entirely.

---

### Finding Description

The `respond_ckd` function at `crates/contract/src/lib.rs` conditionally verifies the response:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← NO VERIFICATION
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For the `AppPublicKeyPV` variant the contract calls `ckd_output_check`, which cryptographically verifies the response against the BLS12-381 root public key and the user's app public key pair. For the `AppPublicKey` (legacy, privately verifiable) variant, the match arm is a no-op — **any `CKDResponse` with arbitrary `big_y` and `big_c` BLS12-381 G1 points is unconditionally accepted**.

The only guards that `respond_ckd` enforces are:

1. Caller is an attested participant (`assert_caller_is_attested_participant_and_protocol_active`)
2. Protocol is Running or Resharing
3. Domain is BLS12-381 [2](#0-1) 

There is no requirement that the response was produced by the threshold CKD protocol. After the check (or lack thereof), the contract immediately resolves all pending yields for the request:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [3](#0-2) 

This is structurally identical to the external report's root cause: a two-step flow (user submits `request_app_private_key` → MPC nodes collectively compute and submit `respond_ckd`) where multiple holders of the same privileged role (attested participants) can call the second step, and the contract does not verify that the caller actually performed the required computation.

The `AppPublicKey` variant is still exposed in the production ABI: [4](#0-3) 

And the README explicitly documents it as a supported (if legacy) input format: [5](#0-4) 

---

### Impact Explanation

A single malicious attested participant (strictly below the signing threshold) can:

1. Observe a pending `CKDRequest` with `AppPublicKey` variant in `pending_ckd_requests`.
2. Call `respond_ckd` with a forged `CKDResponse { big_y: <attacker-chosen G1 point>, big_c: <attacker-chosen G1 point> }` before the legitimate threshold computation completes.
3. The contract accepts the forged response with no cryptographic check.
4. The pending yield is resolved and the user receives the forged CKD output.
5. The legitimate threshold-computed response, when it arrives, finds no pending yield and is silently dropped.

The user's TEE application receives an unauthorized confidential key derivation output — one that was never produced by the threshold protocol. If the attacker constructs `big_y = s·G1` and `big_c = s·app_public_key` for an attacker-chosen scalar `s`, the decrypted key is `s`, which the attacker knows, enabling them to control any assets the user subsequently places under that derived key.

**Impact class:** Critical — *confidential key derivation output without the required participant authorization* (threshold bypass for CKD).

---

### Likelihood Explanation

**Medium.** The attacker must be a legitimate attested participant (an honest-but-curious or compromised MPC node). The `AppPublicKey` variant is marked legacy but remains in the production ABI and is reachable by any client that has not migrated to `AppPublicKeyPV`. The attack requires only a single NEAR transaction submitted before the legitimate `respond_ckd` call lands — a straightforward front-run on NEAR's public mempool.

---

### Recommendation

1. **Immediate:** Reject `AppPublicKey` variant requests in `respond_ckd` (or add equivalent verification). The `AppPublicKeyPV` path already has `ckd_output_check`; the `AppPublicKey` branch must not be a no-op.
2. **Medium-term:** Deprecate and remove the `AppPublicKey` variant from the public API, requiring all callers to use `AppPublicKeyPV`, which is publicly verifiable on-chain.
3. **Defense-in-depth:** Consider requiring a quorum of participants to submit matching responses before a CKD yield is resolved, mirroring the threshold guarantee that the signing protocol provides off-chain.

---

### Proof of Concept

```
// Step 1 — user submits a CKD request with the legacy AppPublicKey variant
request_app_private_key({
  derivation_path: "my-app",
  app_public_key: { AppPublicKey: "bls12381g1:<user_pk>" },
  domain_id: 2
})
// → pending CKDRequest stored in pending_ckd_requests

// Step 2 — malicious attested participant front-runs the legitimate response
respond_ckd(
  request = CKDRequest { app_public_key: AppPublicKey("bls12381g1:<user_pk>"), domain_id: 2, ... },
  response = CKDResponse {
    big_y: bls12381g1:<attacker_s * G1>,   // attacker-chosen scalar s
    big_c: bls12381g1:<attacker_s * user_pk>  // ECDH-style: s * app_public_key
  }
)
// → contract accepts with no verification (AppPublicKey branch is a no-op)
// → yield resolved; user receives forged output
// → legitimate threshold response arrives, finds no pending yield, is dropped
// → user's TEE decrypts to scalar s, which attacker knows → attacker controls derived key
```

The contract's own unit test confirms that an attested participant can successfully call `respond_ckd` and resolve a pending request in a single transaction, with no additional threshold gate: [6](#0-5)

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

**File:** crates/contract/src/lib.rs (L4510-4521)
```rust
        // --- Step 4: Verify that a participant can still respond successfully ---
        with_active_participant_and_attested_context(&contract); // sets env to a real attested participant

        let valid_response = CKDResponse {
            big_y: dtos::Bls12381G1PublicKey([1u8; 48]),
            big_c: dtos::Bls12381G1PublicKey([2u8; 48]),
        };

        // This should succeed (attested participant)
        contract
            .respond_ckd(ckd_request.clone(), valid_response.clone())
            .expect("Participant should be allowed to respond_ckd");
```

**File:** crates/contract/tests/snapshots/abi__abi_has_not_changed.snap (L1290-1315)
```text
        "name": "respond_ckd",
        "kind": "call",
        "params": {
          "serialization_type": "json",
          "args": [
            {
              "name": "request",
              "type_schema": {
                "$ref": "#/definitions/CKDRequest"
              }
            },
            {
              "name": "response",
              "type_schema": {
                "$ref": "#/definitions/CKDResponse"
              }
            }
          ]
        },
        "result": {
          "serialization_type": "json",
          "type_schema": {
            "type": "null"
          }
        }
      },
```

**File:** crates/contract/README.md (L119-120)
```markdown
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
```
