### Title
Unvalidated Caller-Supplied `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Signature Replay — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` accepts a caller-supplied `payload_hash` and only checks that the submitted signature is cryptographically valid over it, without verifying that the hash actually corresponds to the pending request's foreign-chain data. A single Byzantine attested participant can reuse a valid MPC root-key signature from any previously completed foreign-tx request to forge a verification result for a different pending request.

---

### Finding Description

In `respond_verify_foreign_tx` (lines 718–734), the contract extracts `payload_hash` directly from the caller-supplied `response` and uses it as the message for signature verification against the domain's root public key:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;   // ← fully attacker-controlled

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,                                            // root key, no derivation
)
.is_ok()
``` [1](#0-0) 

The contract never reconstructs the expected payload hash from the stored request and compares it. Contrast this with the regular `respond` function, which correctly derives the payload from the stored `request` object rather than from the caller-supplied response:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
``` [2](#0-1) 

The MPC node code confirms that foreign-tx signing uses a **zero tweak** (root key, no derivation):

```rust
tweak: Tweak::new([0u8; 32]),
``` [3](#0-2) 

Because every foreign-tx signature is produced under the same root key, any valid signature `S` from a completed request A is also a valid signature under the root key for the hash of A's payload. A Byzantine attested participant can therefore:

1. Observe completed request A's signature `S` (public on-chain after `respond_verify_foreign_tx` is called).
2. Call `respond_verify_foreign_tx(request=B, response={payload_hash=hash(A's payload), signature=S})` for a different pending request B.
3. The contract verifies `S` is valid over `hash(A's payload)` — **passes** — and resolves request B with the wrong payload hash. [4](#0-3) 

The `resolve_yields_for` call then delivers the forged `VerifyForeignTransactionResponse` to every caller waiting on request B. [5](#0-4) 

---

### Impact Explanation

The user who submitted request B receives a `VerifyForeignTransactionResponse` whose `payload_hash` corresponds to a completely different foreign-chain transaction (request A's `tx_id`). The MPC SDK's `ForeignChainSignatureVerifier::verify_signature` does check the payload hash client-side: [6](#0-5) 

However, bridge smart contracts that consume the response on-chain and do not independently reconstruct and compare the expected `payload_hash` will accept the forged result as a valid verification of their own transaction. This enables an invalid bridge execution or double-spend: a Byzantine participant can make the MPC contract attest that transaction Y was verified when the signature actually covers transaction X's data.

This matches the **High** allowed impact: *forged foreign-chain verification that causes invalid bridge execution*.

---

### Likelihood Explanation

**Medium.** The attacker must be an attested participant — realistic in a Byzantine fault model strictly below the signing threshold. Valid signatures from prior requests are permanently public on-chain. The attacker must submit the forged response before honest nodes submit the correct one. This is achievable without any race if the attacker is the designated leader for request B (leader rotation means any participant can be leader), or by front-running honest nodes on NEAR's mempool. No threshold collusion is required; a single Byzantine participant suffices.

---

### Recommendation

Do not accept `payload_hash` from the caller in `respond_verify_foreign_tx`. Instead, require the responder to supply the raw `extracted_values`, reconstruct `ForeignTxSignPayload` from the stored request plus those values, compute the expected hash on-chain, and verify the signature against the reconstructed hash. This mirrors how `respond` derives the payload from the stored request rather than from the caller-supplied response.

---

### Proof of Concept

1. Request A (`tx_id=X`) is submitted and completed. The MPC network produces signature `S` over `SHA-256(borsh(ForeignTxSignPayload{request=A, values=[...]}))`. `S` is submitted via `respond_verify_foreign_tx` and is now public on-chain.
2. Request B (`tx_id=Y`) is submitted and is pending in `pending_verify_foreign_tx_requests`.
3. Byzantine attested participant calls:
   ```
   respond_verify_foreign_tx(
     request = B,
     response = { payload_hash = hash(A's payload), signature = S }
   )
   ```
4. Contract checks:
   - `S` valid over `hash(A's payload)`? **YES** (it was produced by the MPC network for request A under the same root key).
   - Request B in pending map? **YES**.
5. Contract resolves request B with `{payload_hash=hash(A's payload), signature=S}`.
6. The user who submitted request B receives a response claiming `tx_id=Y` was verified, but the signature covers `tx_id=X`'s data.
7. A bridge contract that does not verify `payload_hash` against the expected transaction accepts this as valid verification of `tx_id=Y` and authorizes an invalid bridge transaction.

### Citations

**File:** crates/contract/src/lib.rs (L600-608)
```rust
                let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");

                // Check the signature is correct
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    payload_hash,
                    &expected_public_key,
                )
                .is_ok()
```

**File:** crates/contract/src/lib.rs (L718-734)
```rust
        let signature_is_valid = match (&response.signature, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");

                let payload_hash: [u8; 32] = response.payload_hash.0;

                // Check the signature is correct against the root public key
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    &payload_hash,
                    &secp_pk,
                )
                .is_ok()
```

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L39-47)
```rust
    Ok(SignatureRequest {
        id: request.id,
        receipt_id: request.receipt_id,
        payload: Payload::Ecdsa(payload_bytes),
        tweak: Tweak::new([0u8; 32]),
        entropy: request.entropy,
        timestamp_nanosec: request.timestamp_nanosec,
        domain: request.domain_id,
    })
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

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L57-64)
```rust
        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
        }
```
