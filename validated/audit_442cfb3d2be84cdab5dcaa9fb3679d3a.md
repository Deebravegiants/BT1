### Title
`respond_verify_foreign_tx` Accepts `payload_hash` Not Linked to the Pending Request Content — (`File: crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that `response.signature` is a valid ECDSA signature over `response.payload_hash` under the domain's root public key, but it never verifies that `payload_hash` is actually derived from the content of the `request` being resolved. A single Byzantine attested participant (below the signing threshold) can replay a `(payload_hash, signature)` pair from any previously completed foreign-tx verification as a response to a different pending request, causing the victim's bridge contract to receive a cryptographically valid MPC attestation that corresponds to a different foreign transaction than the one it requested.

---

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` performs two checks before resolving a pending yield:

1. The caller is an attested participant.
2. `response.signature` is a valid ECDSA signature over `response.payload_hash` under the domain's root public key. [1](#0-0) 

What it does **not** check is that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload { request, values }))` for the specific `request` being resolved. The `payload_hash` field is a free caller-supplied parameter; the contract only verifies the signature over it, not its preimage. [2](#0-1) 

By contrast, the regular `respond` function for sign requests verifies the signature against the **derived key** (using `request.tweak`) and the **payload taken directly from the request struct**, so the signature is cryptographically bound to both the specific payload and the specific derivation path of that request. [3](#0-2) 

For foreign-tx responses, the root key is used (no tweak), and the `payload_hash` is not re-derived from the request. This means any valid `(payload_hash, sig)` pair produced by the MPC network for **any** prior foreign-tx verification can be replayed against **any** pending foreign-tx request.

The `ForeignTxSignPayloadV1` struct that defines what `payload_hash` is supposed to commit to: [4](#0-3) 

The contract never reconstructs this struct from the `request` to verify the hash.

---

### Impact Explanation

A Byzantine attested participant (a single node, strictly below the signing threshold) can:

1. Observe a legitimately completed `verify_foreign_transaction` response on-chain for request A (tx\_id=X), obtaining `(payload_hash_A, sig_A)` — both are public.
2. Wait for (or cause) a victim to submit a new `verify_foreign_transaction` request B (tx\_id=Y).
3. Call `respond_verify_foreign_tx(request=B, response={payload_hash_A, sig_A})`.
4. The contract accepts: `sig_A` is valid over `payload_hash_A` under the root key ✓, and request B exists in `pending_verify_foreign_tx_requests` ✓.
5. The victim's bridge contract receives `{payload_hash_A, sig_A}` — a valid MPC attestation — but `payload_hash_A` encodes the extracted values of tx\_id=X, not tx\_id=Y.

Any bridge contract that verifies only the signature (which is what the MPC contract itself enforces) will accept this as a valid attestation of tx\_id=Y's state, enabling invalid bridge execution or double-spend conditions. This matches the **High** allowed impact: *"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass … that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

- The attacker needs only to be a single attested participant — one Byzantine node below the threshold.
- The `(payload_hash, sig)` pairs from completed requests are publicly visible on-chain.
- No threshold collusion, no key leakage, and no privileged operator access is required.
- The attack is executable any time a victim has a pending `verify_foreign_transaction` request for a chain that has had at least one prior completed verification.

---

### Recommendation

Include the extracted `values` in the `respond_verify_foreign_tx` call and have the contract recompute `SHA-256(borsh(ForeignTxSignPayload { request, values }))` on-chain, then assert it equals `response.payload_hash` before accepting the response. This binds the `payload_hash` to the specific `request` being resolved and eliminates the replay surface.

Alternatively, bind the signature to the request by incorporating the `request` hash into the signed payload at the protocol level (e.g., as a domain-separation tag), so that a signature produced for request A cannot verify under request B's context.

---

### Proof of Concept

**Setup**: Domain with `DomainPurpose::ForeignTx` and root key `K`. Two Bitcoin requests are submitted:
- Request A: `tx_id = [0xAA; 32]`, pending → completes → on-chain response: `{payload_hash_A, sig_A}`.
- Request B: `tx_id = [0xBB; 32]`, pending.

**Attack** (single Byzantine attested participant):

```rust
// Replay sig_A (from completed request A) against pending request B
contract.respond_verify_foreign_tx(
    request_B,  // pending request for tx_id=0xBB
    VerifyForeignTransactionResponse {
        payload_hash: payload_hash_A,  // hash of tx_id=0xAA's data
        signature: sig_A,              // valid sig over payload_hash_A under root key K
    },
)
// Returns Ok(()) — contract accepts it
```

**Result**: The yield for request B is resolved with `{payload_hash_A, sig_A}`. The victim's bridge contract receives a valid MPC signature attesting to the extracted values of `tx_id=0xAA`, not `tx_id=0xBB`. [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L596-608)
```rust
                    .as_affine();
                let expected_public_key =
                    derive_key_secp256k1(&affine, &request.tweak).map_err(RespondError::from)?;

                let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");

                // Check the signature is correct
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    payload_hash,
                    &expected_public_key,
                )
                .is_ok()
```

**File:** crates/contract/src/lib.rs (L718-747)
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
            }
            (signature_response, public_key_requested) => {
                return Err(RespondError::SignatureSchemeMismatch {
                    mpc_scheme: Box::new(signature_response.clone()),
                    user_scheme: Box::new(public_key_requested),
                }
                .into());
            }
        };

        if !signature_is_valid {
            return Err(RespondError::InvalidSignature.into());
        }
```

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1509)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}

impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```
