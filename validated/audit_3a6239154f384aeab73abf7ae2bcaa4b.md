### Title
`respond_verify_foreign_tx` Accepts Arbitrary `payload_hash` Without Binding It to the Pending Request, Enabling Byzantine-Participant Response Injection — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies only that the submitted signature is cryptographically valid for the submitted `payload_hash` under the root public key. It never checks that `payload_hash` is actually derived from the pending `request`. A single Byzantine participant (strictly below the signing threshold) can reuse a legitimately-produced threshold signature from *any* prior signing session to resolve a *different* pending request with a mismatched payload hash, delivering a forged foreign-chain attestation to the waiting caller.

---

### Finding Description

The on-chain verification in `respond_verify_foreign_tx` is:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;
// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
```