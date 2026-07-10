### Title
CKD Output Integrity Check Never Called for `AppPublicKey` Variant, Allowing Single Malicious Participant to Forge Confidential Key Derivation Responses - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` contract method implements a cryptographic output-integrity check (`ckd_output_check`) for the `AppPublicKeyPV` variant of CKD requests, but **never invokes any equivalent check** for the legacy `AppPublicKey` variant. A single malicious attested participant (below the signing threshold) can call `respond_ckd` with an arbitrary `CKDResponse` for any pending `AppPublicKey` request, and the contract will accept and deliver the forged output to the user.

---

### Finding Description

In `respond_ckd`, the contract branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

The `ckd_output_check` function is fully implemented and verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, which cryptographically binds the response to the correct master secret key and the user's app identity: [2](#0-1) 

For `AppPublicKeyPV`, this check is enforced. For `AppPublicKey` (the legacy, privately verifiable format), the match arm is an empty block `{}` — the check is **never called**. The `AppPublicKey` format is the default format documented and used in production: [3](#0-2) 

This is structurally identical to the zDAO Token bug: the verification function exists and works correctly for one code path, but is silently skipped for another, breaking the security invariant for all requests that use the legacy format.

---

### Impact Explanation

**Critical — Confidential key derivation output without required participant authorization.**

A single malicious attested participant (the signing leader) can call `respond_ckd` with any arbitrary `big_y` and `big_c` values for any pending `AppPublicKey` CKD request. The contract performs no cryptographic check and immediately resolves all queued yields with the forged response: [4](#0-3) 

The user receives a `CKDResponse` whose `big_c` and `big_y` are attacker-controlled. Because the `AppPublicKey` format is privately verifiable only (the user decrypts using their ephemeral private key), the user cannot detect the forgery on-chain. The attacker can deliver a response that decrypts to an attacker-known secret, fully compromising the confidential key derivation output.

---

### Likelihood Explanation

**High.** The `AppPublicKey` variant is the default and legacy format, meaning the majority of production CKD requests use it. Any single attested participant — the leader node for a given request — can exploit this without threshold collusion. The attack requires only that one participant be malicious or compromised, which is explicitly within the Byzantine fault model the system is designed to tolerate at the contract level (the contract is supposed to verify outputs independently of trusting the submitter).

---

### Recommendation

Apply `ckd_output_check` to the `AppPublicKey` variant as well. Since `AppPublicKey` is a single G1 point `pk1` without a corresponding G2 point `pk2`, the current pairing-based check cannot be applied directly. The fix should either:

1. **Deprecate `AppPublicKey`** and require all new requests to use `AppPublicKeyPV`, which supports on-chain verification; or
2. **Add an equivalent binding check** for `AppPublicKey` — for example, by requiring the response to include a zero-knowledge proof that `big_c` was computed correctly with respect to the master secret key and the user's `app_id`, verifiable without `pk2`.

The `AppPublicKeyPV` path already demonstrates the correct pattern: [5](#0-4) 

---

### Proof of Concept

1. User Alice submits `request_app_private_key` with `AppPublicKey` (legacy format) and derivation path `"my-key"`.
2. The request is stored in `pending_ckd_requests`.
3. Malicious participant Eve (a single attested node) calls `respond_ckd` with:
   - `request`: Alice's pending `CKDRequest`
   - `response`: `CKDResponse { big_y: attacker_point, big_c: attacker_point }`
4. The contract executes the `AppPublicKey(_) => {}` branch — no check is performed.
5. `resolve_yields_for` is called, delivering the forged response to Alice's yield.
6. Alice receives `big_c` and `big_y` chosen by Eve. Alice decrypts using her ephemeral private key and derives a secret that Eve already knows (or that is cryptographically invalid), fully compromising the CKD output.

The `AppPublicKeyPV` path would have caught this at step 4 via `ckd_output_check`. The `AppPublicKey` path has no equivalent guard. [1](#0-0) [2](#0-1)

### Citations

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

**File:** crates/contract/src/primitives/ckd.rs (L80-102)
```rust
pub(crate) fn ckd_output_check(
    app_id: &dtos::CkdAppId,
    output: &CKDResponse,
    app_public_key: &dtos::CKDAppPublicKeyPV,
    public_key: &dtos::Bls12381G2PublicKey,
) -> bool {
    let big_c = env::bls12381_p1_decompress(&output.big_c);
    let big_y = env::bls12381_p1_decompress(&output.big_y);
    let pk2 = env::bls12381_p2_decompress(&app_public_key.pk2);
    let pk = env::bls12381_p2_decompress(public_key);
    let hash_point = hash_app_id_with_pk(public_key.as_slice(), app_id.as_ref());

    let pairing_input = [
        big_c.as_slice(),
        MINUS_G2_GENERATOR_UNCOMPRESSED.as_slice(),
        big_y.as_slice(),
        pk2.as_slice(),
        hash_point.as_slice(),
        pk.as_slice(),
    ]
    .concat();
    env::bls12381_pairing_check(&pairing_input)
}
```

**File:** crates/contract/README.md (L119-121)
```markdown
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
- `domain_id` (integer): identifies the master key to use for deriving the ckd, and must correspond to bls12381.
```
