### Title
Unbound `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Replay by a Single Byzantine Participant — (`crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the MPC signature is valid over `response.payload_hash`, but never verifies that `response.payload_hash` was actually derived from the stored `VerifyForeignTransactionRequest`. A single Byzantine attested MPC participant (strictly below the signing threshold) can replay a previously computed `(payload_hash, signature)` pair — produced for a different request — to resolve any pending foreign-tx verification with incorrect data, breaking the invariant that each response corresponds to the actual foreign-chain state for its request.

---

### Finding Description

The vulnerability class from the external report is **inconsistent values between two related operations**: a pre-transformation value is used in one computation while the post-transformation value is used in the actual stored/executed operation. The analog here is that the contract stores the original `VerifyForeignTransactionRequest` as the pending-request key, but the signature verification is performed over an **arbitrary node-supplied `payload_hash`** that is never bound back to the stored request.

In `respond_verify_foreign_tx`:

```rust
// crates/contract/src/lib.rs ~L726-L734
let payload_hash: [u8; 32] = response.payload_hash.0;

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,          // ← node-supplied; never checked against stored request
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

After this check passes, the full `response` (including the unchecked `payload_hash`) is serialised and delivered to every queued yield for that request:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),   // ← response.payload_hash is unverified
)
``` [2](#0-1) 

The `ForeignTxSignPayload` that nodes actually sign is:

```
payload_hash = SHA-256(borsh(ForeignTxSignPayload { request, values }))
``` [3](#0-2) 

The `values` field (extracted from the foreign chain) is **not stored on-chain**; only the `ForeignChainRpcRequest` is stored. The contract therefore cannot recompute the expected `payload_hash` itself. The result is a structural inconsistency:

| What is stored | What is verified |
|---|---|
| `VerifyForeignTransactionRequest` (the original RPC request) | `sig(response.payload_hash)` — an arbitrary hash supplied by the responding node |

The contract never checks that `response.payload_hash == SHA-256(borsh({stored_request, values}))`.

---

### Impact Explanation

A single Byzantine attested MPC participant (below threshold) can replay any previously computed `(payload_hash_A, sig_A)` pair — legitimately produced for request A — as the response to a different pending request B:

1. Request A is processed honestly; the MPC network produces `(payload_hash_A, sig_A)`.
2. Request B is submitted and is pending in `pending_verify_foreign_tx_requests`.
3. The Byzantine node calls `respond_verify_foreign_tx(request = request_B, response = {payload_hash_A, sig_A})`.
4. The contract finds `request_B` in the map ✓, verifies `sig_A` over `payload_hash_A` against the root key ✓ (valid, previously produced), and resolves request B with the response for request A.
5. Every caller waiting on request B receives `{payload_hash_A, sig_A}` — data that corresponds to request A's foreign-chain state, not request B's.

Bridge contracts that do not independently re-verify `payload_hash` against their expected extracted values (as the SDK's `ForeignChainSignatureVerifier` does) will accept a forged foreign-chain verification, enabling invalid bridge execution. Even bridge contracts that do re-verify will have their request permanently resolved with wrong data, causing a denial of the legitimate verification result (the yield is consumed and cannot be retried). [4](#0-3) 

---

### Likelihood Explanation

- Requires only **one** Byzantine attested MPC participant — strictly below the signing threshold. This is within the explicit Byzantine fault-tolerance model of the system.
- The attacker does not forge a new signature; they replay a legitimately produced one. No cryptographic break is needed.
- Any previously completed `verify_foreign_transaction` request for the same domain provides a usable `(payload_hash, signature)` pair.
- The attack is executable in a single on-chain transaction.

---

### Recommendation

The contract must bind the response to the stored request. Two complementary approaches:

1. **Include the request hash in the signed payload**: Change the signing payload to `SHA-256(borsh(request) || SHA-256(borsh(values)))` or add the `request` as a top-level field in `ForeignTxSignPayload` and have the contract verify that the `request` embedded in the payload matches the stored one. Since the contract only receives `payload_hash` (not the full payload), this requires either passing the full payload in the response or changing the hash construction so the contract can verify the request binding independently.

2. **Short-term mitigation**: Require the responding node to also supply the `ForeignChainRpcRequest` in the response, and have the contract verify it matches the stored request before accepting the `payload_hash`.

The root fix is to ensure the contract can independently confirm that `response.payload_hash` commits to the same `ForeignChainRpcRequest` that is stored under the pending-request key.

---

### Proof of Concept

```
Setup:
  - Domain D with root key K (threshold t=2, n=3)
  - Nodes: N1 (honest), N2 (honest), N3 (Byzantine)

Step 1 — Legitimate request A:
  User calls verify_foreign_transaction(request_A = Bitcoin tx_A, confirmations=6)
  N1 + N2 inspect the chain, extract block_hash_A, compute:
    payload_hash_A = SHA256(borsh(ForeignTxSignPayload{request_A, [block_hash_A]}))
    sig_A = MPC_sign(payload_hash_A, K)
  N3 observes (payload_hash_A, sig_A) from the on-chain respond_verify_foreign_tx call.

Step 2 — Victim request B:
  Bridge calls verify_foreign_transaction(request_B = Bitcoin tx_B, confirmations=6)
  request_B is now pending in pending_verify_foreign_tx_requests.

Step 3 — Replay attack by N3 (single Byzantine node):
  N3 calls respond_verify_foreign_tx(
    request = request_B,          // valid pending request
    response = {
      payload_hash: payload_hash_A,  // from request A
      signature:    sig_A,           // valid sig over payload_hash_A under K
    }
  )

Step 4 — Contract accepts:
  - Finds request_B in pending map ✓
  - verify_ecdsa_signature(sig_A, payload_hash_A, K) → Ok ✓
  - Resolves request_B with {payload_hash_A, sig_A}

Step 5 — Bridge receives forged response:
  Bridge gets {payload_hash_A, sig_A} for its request about tx_B.
  payload_hash_A encodes block_hash_A (tx_A's block), not tx_B's block.
  A bridge that does not re-verify payload_hash accepts this as proof that tx_B
  was confirmed — enabling invalid bridge execution / double-spend.
```

### Citations

**File:** crates/contract/src/lib.rs (L726-734)
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

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1504-1509)
```rust
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L47-64)
```rust
    ) -> Result<(), VerifyForeignChainError> {
        let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
            request: self.request,
            values: self.expected_extracted_values,
        });

        let expected_payload_hash = expected_payload
            .compute_msg_hash()
            .map_err(|_| VerifyForeignChainError::FailedToComputeMsgHash)?;

        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
        }
```
