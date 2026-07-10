### Title
Single Attested Participant Can Submit Arbitrary CKD Response for Privately Verifiable Variant — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` contract method performs **no cryptographic verification** of the CKD response when the request uses the `AppPublicKey` (privately verifiable) variant. A single malicious attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary `CKDResponse`, resolve all pending yields for that request, and deliver a forged key derivation output to the user. This bypasses the threshold requirement for confidential key derivation.

---

### Finding Description

In `respond_ckd`, the contract branches on the `app_public_key` type:

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

For `AppPublicKeyPV`, `ckd_output_check` enforces a BLS12-381 pairing equation that proves the response encodes `msk · H(pk, app_id)` correctly. For `AppPublicKey`, the arm is empty — the contract accepts any `(big_y, big_c)` pair unconditionally.

The only guards before this branch are:

1. `assert_caller_is_signer()` — caller's signer equals predecessor (no contract forwarding).
2. `is_running_or_resharing()` — protocol is active.
3. `accept_requests` — TEE validation flag is set.
4. `assert_caller_is_attested_participant_and_protocol_active()` — caller is **one** attested participant. [2](#0-1) 

None of these checks verify that the response was produced by the threshold CKD protocol. After the branch, `resolve_yields_for` immediately drains **all** pending yields for the request and delivers the (potentially forged) response to every waiting caller: [3](#0-2) 

Once resolved, the request is removed from `pending_ckd_requests`. The legitimate coordinator cannot overwrite it.

The analog to the external report's finding is exact: in the delegation system, the threshold is enforced for *creating* a delegation but a single party suffices for *redemption*. Here, the threshold is enforced for key generation and governance votes, but a **single** attested participant suffices to *respond* to a CKD request — without any proof that the threshold protocol was run.

The `AppPublicKey` variant is the default/legacy path documented in the contract README and used in the `ckd-example-cli`: [4](#0-3) [5](#0-4) 

---

### Impact Explanation

A single malicious attested participant can:

1. Watch the chain for any pending `AppPublicKey` CKD request.
2. Call `respond_ckd` with arbitrary `big_y` and `big_c` values before the legitimate coordinator does.
3. The contract accepts the call (no pairing check), resolves all queued yields, and delivers the forged `(big_y, big_c)` to the user's developer contract.

The user's TEE app receives a response that does not satisfy `e(C − a·Y, G₂) = e(H(pk, app_id), pk)`. If the developer contract does not perform this verification (which the MPC contract explicitly does not enforce — it delegates that responsibility to the developer), the app derives a key from attacker-controlled material. Even if the app does verify and rejects the response, the legitimate coordinator's correct response can never be submitted (the request is already resolved), constituting a permanent denial of the CKD service for that request.

This matches the allowed Critical impact: **confidential key derivation output without the required participant authorization**.

---

### Likelihood Explanation

- The attacker must be a single attested MPC participant — strictly below the signing threshold.
- No collusion with other participants is required.
- No physical TEE attack is required; the attacker is a legitimately attested node that chooses to misbehave.
- The attack window is the time between a user submitting `request_app_private_key` and the legitimate coordinator calling `respond_ckd`. An attacker monitoring the NEAR indexer can front-run the coordinator's response.
- The `AppPublicKey` variant is the legacy/default path, so it is the most commonly used variant in practice.

---

### Recommendation

1. **Deprecate `AppPublicKey` in `respond_ckd`** and require all new CKD requests to use `AppPublicKeyPV`, for which `ckd_output_check` already enforces the pairing equation on-chain.
2. If `AppPublicKey` must be retained for backwards compatibility, add a threshold-vote mechanism: require at least `threshold` distinct attested participants to submit agreeing `(big_y, big_c)` values before the yield is resolved, analogous to how `vote_pk` accumulates votes before transitioning state.
3. Document clearly in the contract ABI that `AppPublicKey` responses carry no on-chain integrity guarantee, so developer contracts know they must perform the BLS verification themselves.

---

### Proof of Concept

```
1. Alice (TEE app) calls request_app_private_key({
       derivation_path: "mykey",
       app_public_key: AppPublicKey(<A = a·G1>),   // privately verifiable
       domain_id: 2
   }) with 1 yoctoNEAR deposit.

2. Contract stores the pending CKD request and emits a yield.

3. Malicious attested participant Eve (one node, below threshold) calls:
       respond_ckd(
           request = <the CKDRequest for Alice>,
           response = CKDResponse {
               big_y: [0u8; 48],   // arbitrary G1 point
               big_c: [0u8; 48],   // arbitrary G1 point
           }
       )

4. Contract executes lines 675-682:
       match &request.app_public_key {
           AppPublicKey(_) => {}   // no check — falls through
           ...
       }
   Then calls resolve_yields_for, draining Alice's yield with Eve's forged response.

5. Alice's developer contract receives (big_y=[0;48], big_c=[0;48]).
   If it does not run the pairing check, it derives a key from attacker-controlled
   material. The legitimate coordinator's correct response can never be submitted.
```

### Citations

**File:** crates/contract/src/lib.rs (L654-666)
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

**File:** crates/contract/README.md (L128-138)
```markdown
_Privately verifiable ckd request (legacy)_

```Json
{
  "request": {
    "derivation_path": "mykey",
    "app_public_key": "bls12381g1:6KtVVcAAGacrjNGePN8bp3KV6fYGrw1rFsyc7cVJCqR16Zc2ZFg3HX3hSZxSfv1oH6",
    "domain_id": 2
  }
}
```
```

**File:** crates/ckd-example-cli/src/ckd.rs (L31-34)
```rust
    } else {
        let (scalar, pk) = generate_ephemeral_key(&mut OsRng);
        (scalar, CKDAppPublicKey::AppPublicKey(pk))
    };
```
