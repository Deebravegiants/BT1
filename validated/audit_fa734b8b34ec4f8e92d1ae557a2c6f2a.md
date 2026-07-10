### Title
Unvalidated CKD Response for `AppPublicKey` Variant Allows Single Byzantine Node to Inject Attacker-Controlled Key Material - (File: crates/contract/src/lib.rs)

### Summary

`respond_ckd` in the MPC contract performs no cryptographic validation of the `CKDResponse` when the request uses the `AppPublicKey` variant of `CKDAppPublicKey`. A single Byzantine attested participant (below threshold) can call `respond_ckd` with an arbitrary, attacker-chosen `CKDResponse`, which the contract unconditionally accepts and delivers to the waiting user via the yield-resume mechanism. The user receives attacker-controlled key material instead of the legitimately derived key.

### Finding Description

In `respond_ckd` (`crates/contract/src/lib.rs`, lines 675–682), the contract branches on the `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no validation at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

When the request carries `AppPublicKey`, the arm is an empty block: the `CKDResponse` (`big_y`, `big_c`) is never checked against the BLS12-381 master public key or the request's `app_id`. The function then immediately calls:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
```

This resolves the NEAR yield-resume promise and delivers the unvalidated response to the original caller. There is no threshold aggregation step before resolution; a single node's call to `respond_ckd` is sufficient to settle the request.

By contrast, `respond` (signature requests, lines 586–650) always cryptographically verifies the signature against the derived public key before resolving, and `respond_ckd` with `AppPublicKeyPV` calls `ckd_output_check`. The `AppPublicKey` branch is the only path that skips all output validation.

The analog to the external Ethereum bridge report is direct: just as `token.transfer()` was called without checking its return value—allowing the bridge to emit a `Withdrawal` event even when the transfer silently failed—`respond_ckd` resolves the yield and returns a response to the user without checking whether the response is cryptographically consistent with the MPC network's master key and the original request.

### Impact Explanation

A Byzantine attested participant who calls `respond_ckd` with a crafted `CKDResponse` causes the user to receive:

- A `big_y` (derived public key) that the attacker chose and whose corresponding private key the attacker knows.
- A `big_c` commitment that is likewise attacker-controlled.

Any data the user subsequently encrypts to `big_y` is decryptable by the attacker. Any signature scheme relying on the derived key is forgeable by the attacker. The user has no on-chain signal that the key material is illegitimate; the contract returns `Ok` and the yield resolves successfully.

This constitutes **unauthorized key derivation output without the required participant authorization** — a Critical impact under the allowed scope.

### Likelihood Explanation

The attacker must be a single attested participant (i.e., pass TEE attestation and be registered in the contract). The exploit requires no threshold collusion: one node's `respond_ckd` call is sufficient to resolve the yield. The `AppPublicKey` variant is a publicly documented, user-selectable option, so any pending `AppPublicKey` CKD request is a valid target. A participant whose TEE is compromised, or a malicious operator who passes attestation, can exploit this against any user who submits a `request_app_private_key` with `AppPublicKey`.

### Recommendation

Add the same cryptographic output check for the `AppPublicKey` branch that already exists for `AppPublicKeyPV`. If the contract cannot verify the output without a proof-of-validity (because `AppPublicKey` carries no verifiable commitment), the `AppPublicKey` variant should either be removed or the contract should require that all CKD responses include a verifiable proof before the yield is resolved.

### Proof of Concept

1. User calls `request_app_private_key` with `app_public_key: AppPublicKey(some_bls_pk)`. The contract enqueues a yield and stores the request in `pending_ckd_requests`.
2. A Byzantine attested participant constructs a `CKDResponse { big_y: attacker_pk, big_c: attacker_commitment }` where `attacker_pk` is a BLS12-381 public key whose private key the attacker knows.
3. The attacker calls `respond_ckd(request, forged_response)`. The contract passes the `assert_caller_is_attested_participant_and_protocol_active` check, enters the `AppPublicKey(_) => {}` branch (no validation), and calls `resolve_yields_for` with the forged response.
4. The user's NEAR transaction resumes with `big_y = attacker_pk`. The user encrypts sensitive data to `attacker_pk`. The attacker decrypts it using the known private key.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** crates/contract/src/lib.rs (L653-656)
```rust
    #[handle_result]
    pub fn respond_ckd(&mut self, request: CKDRequest, response: CKDResponse) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();
        log!("respond_ckd: signer={}, request={:?}", &signer, &request);
```

**File:** crates/contract/src/lib.rs (L675-688)
```rust
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

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L57-63)
```rust
        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
```
