### Title
Incomplete Payload-Hash Binding in `respond_verify_foreign_tx` Allows Byzantine Leader to Deliver Forged Foreign-Chain Verification Results - (File: crates/contract/src/lib.rs)

### Summary

`respond_verify_foreign_tx` verifies that the submitted signature is cryptographically valid over the caller-supplied `payload_hash`, but never checks that `payload_hash` is actually the correct hash for the submitted `request`. A single Byzantine leader node can substitute a legitimately-obtained threshold signature over a different hash (from a different request) and have the contract resolve a victim's pending request with fabricated foreign-chain attestation data.

### Finding Description

In `respond_verify_foreign_tx` the contract performs two checks before resolving the pending request:

1. The caller is an attested participant.
2. The ECDSA signature in `response.signature` is valid over `response.payload_hash` under the root public key. [1](#0-0) 

Critically, `payload_hash` is taken directly from the caller-supplied `response` struct — the contract never independently derives or constrains what that hash must be for the given `request`. Compare this to the regular `respond` path for sign requests, where the payload to verify against is read from the `request` itself (the user-submitted payload), not from the response: [2](#0-1) 

For `respond_verify_foreign_tx`, the `payload_hash` is supposed to be `ForeignTxSignPayload::compute_msg_hash()` over `(request, extracted_values)`, but the contract has no way to enforce this — it cannot independently query the foreign chain. The contract therefore accepts any `(payload_hash, signature)` pair where the signature is valid over the hash, regardless of whether the hash encodes the correct foreign-chain data for the pending request.

`resolve_yields_for` then delivers this unchecked `response` (including the attacker-controlled `payload_hash`) to every caller waiting on that request key: [3](#0-2) 

### Impact Explanation

A Byzantine leader node can:

1. Submit two `verify_foreign_transaction` requests: T1 (victim's or attacker's own, with modest extracted values) and T2 (attacker-controlled, with favorable extracted values such as a larger bridged amount).
2. Participate honestly in the MPC signing for T2, obtaining a valid threshold signature `sig2` over `H2 = hash(T2_request, favorable_values)`.
3. When assigned as leader for T1's signing round, instead of running the MPC protocol for T1, call `respond_verify_foreign_tx` with `request = T1_key`, `payload_hash = H2`, `signature = sig2`.
4. The contract verifies `sig2` over `H2` — valid — and resolves T1's pending yield queue with the fabricated response.

Every caller waiting on T1 receives a `VerifyForeignTransactionResponse` whose `payload_hash` encodes T2's data (e.g., a different block hash, a different extracted amount). A downstream bridge contract that trusts this attestation to release funds would release funds based on T2's data rather than T1's, enabling invalid bridge execution or double-spend conditions.

### Likelihood Explanation

The leader for a given request is determined by a hash of the request ID. An attacker controlling a single MPC node can submit many `verify_foreign_transaction` requests until they are assigned as leader for one. They need only one prior legitimately-obtained threshold signature (from any other request they participated in) to execute the substitution. No threshold collusion is required — a single Byzantine participant below the signing threshold is sufficient.

### Recommendation

The contract must bind `payload_hash` to `request` before accepting the response. Since the contract cannot independently compute the foreign-chain hash, the binding must be enforced structurally:

- **Option A**: Include the `request` key (or a deterministic commitment to it) inside the signed payload at the MPC-node level, so that a signature over `H2` is cryptographically bound to T2's request and cannot be reused for T1. The contract would then verify that the signed payload encodes the correct request key.
- **Option B**: Have the contract store a commitment to the expected `payload_hash` at request submission time (if the hash can be partially pre-computed from on-chain data), and check `response.payload_hash == stored_commitment` in `respond_verify_foreign_tx`.
- **Option C**: Require the MPC nodes to include the `request` hash inside `ForeignTxSignPayload` and verify on-chain that `response.payload_hash` decodes to a payload whose embedded request matches the pending `request` key.

### Proof of Concept

```
1. Attacker node A submits verify_foreign_transaction(T1) → pending_verify_foreign_tx_requests[K1] = [yield1]
2. Attacker node A submits verify_foreign_transaction(T2) → pending_verify_foreign_tx_requests[K2] = [yield2]
3. MPC network (honest) runs signing for T2; A participates honestly.
   Result: sig2 over H2 = hash(T2_request, extracted_values_T2).
4. A is elected leader for T1's signing round (by request-hash assignment).
   Instead of running MPC for T1, A calls:
     respond_verify_foreign_tx(
       request = K1,                          // T1's pending key — exists in map
       response = { payload_hash: H2,         // T2's hash — NOT T1's
                    signature:    sig2 }       // valid sig over H2 under root key
     )
5. Contract checks:
   - K1 in pending map? YES ✓
   - verify_ecdsa(sig2, H2, root_pk)? YES ✓  (no check that H2 ↔ K1)
   - resolve_yields_for(K1, serialize({H2, sig2})) → yield1 resumed with T2's data
6. Caller of T1 receives VerifyForeignTransactionResponse{payload_hash=H2, signature=sig2}
   and presents it to the bridge contract, which releases funds based on T2's extracted values.
```

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

**File:** crates/contract/src/lib.rs (L718-753)
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

        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
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
