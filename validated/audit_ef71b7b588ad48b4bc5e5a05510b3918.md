Based on my examination of the actual code, this vulnerability is real and demonstrable.

**Contract side — confirmed empty arm:** [1](#0-0) 

The `AppPublicKey` match arm performs zero validation on the 48-byte G1 encoding. The `AppPublicKeyPV` arm, by contrast, calls `app_public_key_check`, which uses `env::bls12381_p1_decompress` (aborts on malformed encoding) and a pairing check (rejects non-subgroup points). [2](#0-1) 

**Node side — confirmed hard failure:** [3](#0-2) 

`ElementG1::try_from(&pk)?` at line 159 propagates an error for any invalid encoding. This error bubbles up through `make_ckd_leader` via the `?` at line 76: [4](#0-3) 

Because the invalid bytes are stored in the request and never change, every retry attempt by the node will hit the same `ElementG1::try_from` failure deterministically. The node never calls `respond_ckd`, so the yield enqueued by `enqueue_yield_request` times out without resolution. [5](#0-4) 

The callback registered is `RETURN_CK_AND_CLEAN_STATE_ON_SUCCESS` — a success-only path. There is no timeout/failure callback that would refund the deposit, so the user's attached deposit (enforced by `check_request_preconditions` against `MINIMUM_CKD_REQUEST_DEPOSIT`) is consumed permanently.

**The asymmetry is structural:** `AppPublicKeyPV` is protected by a pairing check at contract ingress; `AppPublicKey` has no guard at all, yet the node applies the same cryptographic deserialization to both variants.

---

### Title
Missing G1 Point Validation for `AppPublicKey` Variant Allows Deposit Consumption for Unprocessable CKD Requests — (`crates/contract/src/lib.rs`)

### Summary
An unprivileged caller can submit a `CKDRequestArgs` with `AppPublicKey` containing an invalid compressed G1 encoding. The contract accepts and enqueues the request (consuming the deposit), but the node's `CKDComputation::compute` fails deterministically at `ElementG1::try_from(&pk)?`, never resolves the yield, and the deposit is permanently lost when the yield times out.

### Finding Description
`request_app_private_key` validates `AppPublicKeyPV` inputs via `app_public_key_check` (decompression + pairing check) but leaves the `AppPublicKey` match arm empty:

```rust
// crates/contract/src/lib.rs lines 484-491
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no validation
    dtos::CKDAppPublicKey::AppPublicKeyPV(pk) => {
        if !app_public_key_check(pk) {
            env::panic_str("app public key check failed")
        }
    }
}
```

The node's `CKDComputation::compute` then calls `ElementG1::try_from(&pk)?` for both variants identically. Any bytes that are not a valid, prime-order-subgroup G1 point (e.g., `[0u8; 48]`, a point with no compression flag, or a non-subgroup point) will cause a hard error. Because the stored bytes never change, every node retry fails identically, the yield callback (`RETURN_CK_AND_CLEAN_STATE_ON_SUCCESS`) is never invoked, and no refund path exists on timeout.

### Impact Explanation
The user's deposit (enforced at contract ingress by `check_request_preconditions`) is permanently consumed for a request that can never be processed. This breaks the accounting invariant that deposits are only consumed for processable requests. Impact is **Medium**: request-lifecycle and balance manipulation without requiring any privileged access.

### Likelihood Explanation
Any unprivileged account can trigger this by calling `request_app_private_key` with `AppPublicKey([0u8; 48])` and attaching the minimum required deposit. No collusion, operator access, or network-level attack is needed.

### Recommendation
Add G1 point validation to the `AppPublicKey` arm before enqueuing the yield. Use `env::bls12381_p1_decompress` (which aborts on malformed/off-curve encodings) and verify subgroup membership (e.g., via a pairing check or a dedicated host function), mirroring the existing `AppPublicKeyPV` guard. Alternatively, move the validation into a shared helper called for both variants.

### Proof of Concept
**Contract unit test (pseudo):**
```rust
// Submit AppPublicKey with all-zero bytes
let request = CKDRequestArgs {
    app_public_key: CKDAppPublicKey::AppPublicKey(Bls12381G1PublicKey([0u8; 48])),
    domain_id: valid_domain,
    derivation_path: "path".to_string(),
};
// Assert: contract accepts (no panic), yield is enqueued
contract.request_app_private_key(request); // succeeds, deposit consumed
```

**Node unit test (pseudo):**
```rust
let pk = dtos::Bls12381G1PublicKey([0u8; 48]);
let result = ElementG1::try_from(&pk);
assert!(result.is_err()); // node fails deterministically
```

The gap between these two assertions is the vulnerability: the contract accepts what the node cannot process, and no refund path exists on yield timeout.

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

**File:** crates/contract/src/lib.rs (L506-511)
```rust
        self.enqueue_yield_request(
            method_names::RETURN_CK_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_ckd_request(request, id),
        );
```

**File:** crates/contract/src/primitives/ckd.rs (L62-74)
```rust
pub(crate) fn app_public_key_check(app_public_key: &dtos::CKDAppPublicKeyPV) -> bool {
    let pk1 = env::bls12381_p1_decompress(&app_public_key.pk1);
    let pk2 = env::bls12381_p2_decompress(&app_public_key.pk2);

    let pairing_input = [
        pk1.as_slice(),
        MINUS_G2_GENERATOR_UNCOMPRESSED.as_slice(),
        G1_GENERATOR_UNCOMPRESSED.as_slice(),
        pk2.as_slice(),
    ]
    .concat();
    env::bls12381_pairing_check(&pairing_input)
}
```

**File:** crates/node/src/providers/ckd/sign.rs (L60-76)
```rust
        let result = CKDComputation {
            keygen_output,
            app_public_key: ckd_request.app_public_key,
            app_id: ckd_request.app_id,
        }
        .perform_leader_centric_computation(
            channel,
            Duration::from_secs(self.config.ckd.timeout_sec),
        )
        .await
        .inspect_err(|_| {
            participants.iter().for_each(|id| {
                metrics::PARTICIPANT_TOTAL_TIMES_SEEN_IN_FAILED_SIGNATURE_COMPUTATION_LEADER
                    .with_label_values(&[&id.raw().to_string()])
                    .inc();
            });
        })?;
```

**File:** crates/node/src/providers/ckd/sign.rs (L151-163)
```rust
        let result = match self.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(pk) => {
                let protocol = ckd(
                    cs_participants.as_slice(),
                    leader,
                    my_id,
                    self.keygen_output,
                    app_id,
                    ElementG1::try_from(&pk)?,
                    OsRng,
                )?;
                run_protocol("ckd", channel, protocol).await?
            }
```
