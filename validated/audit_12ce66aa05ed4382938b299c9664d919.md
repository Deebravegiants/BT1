### Title
Byzantine Participant Can Replay Any Past `VerifyForeignTransactionResponse` Against a Different Pending Request — (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies only that the submitted signature is cryptographically valid over `response.payload_hash`, but never checks that `response.payload_hash` is actually the hash of a `ForeignTxSignPayload` whose embedded `request` field matches the pending `request` argument. A single Byzantine attested participant (below signing threshold) can replay any previously produced, on-chain-visible `VerifyForeignTransactionResponse` to resolve any currently pending `verify_foreign_transaction` request, delivering a forged attestation to the caller.

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` performs two checks before resolving pending yields:

1. The caller is an attested participant.
2. `response.signature` is a valid ECDSA signature over `response.payload_hash` under the domain's root public key. [1](#0-0) 

It then calls `resolve_yields_for` keyed on `request`: [2](#0-1) 

**What is never checked**: that `response.payload_hash` is the hash of a `ForeignTxSignPayload` whose inner `request` field equals the `request` argument passed to `respond_verify_foreign_tx`. The signed payload is defined as: [3](#0-2) 

`payload_hash = SHA-256(borsh(ForeignTxSignPayload { request: ForeignChainRpcRequest, values: Vec<ExtractedValue> }))`. The contract never reconstructs or compares this hash against the pending `request`.

The pending-request map key (`VerifyForeignTransactionRequest`) contains only `domain_id`, `request`, and `payload_version` — no caller identity, no nonce, no timestamp: [4](#0-3) 

The conversion from args to request key also drops the caller's account ID entirely: [5](#0-4) 

This is intentional for the fan-out design (different callers submitting the same chain request share one MPC computation), but it means any pending entry for a given `ForeignChainRpcRequest` can be resolved by any valid signature over any `payload_hash` — including one produced for a completely different transaction.

**Attack path**:

1. At time T₁, a legitimate `verify_foreign_transaction` for Bitcoin tx `R_A` completes. The MPC network signs `ForeignTxSignPayload{request=R_A, values=[BlockHash=H_A]}` → `payload_hash_A`. The response `{payload_hash_A, sig_A}` is publicly visible on-chain as a promise result.

2. At time T₂, any user submits `verify_foreign_transaction` for a different Bitcoin tx `R_B`. A pending entry for `R_B` is created in `pending_verify_foreign_tx_requests`.

3. The Byzantine participant calls `respond_verify_foreign_tx(request=R_B, response={payload_hash=payload_hash_A, sig=sig_A})`.

4. The contract verifies: `sig_A` is a valid ECDSA signature over `payload_hash_A` under the root public key → **passes**. There is a pending entry for `R_B` → **passes**. The contract resolves the yield for `R_B` with `{payload_hash_A, sig_A}`.

5. The caller of `R_B` receives a `VerifyForeignTransactionResponse` whose `payload_hash` is the hash of `R_A`'s payload, not `R_B`'s. The caller cannot detect this because `payload_hash` is opaque — the extracted values are not returned separately.

The honest MPC nodes' subsequent `respond_verify_foreign_tx` calls for `R_B` will fail with `RequestNotFound` because the entry was already drained.

### Impact Explanation

A single Byzantine attested participant (below signing threshold) can deliver a forged `VerifyForeignTransactionResponse` to any caller of `verify_foreign_transaction`. The caller's on-chain contract receives a `payload_hash` that was produced for a different foreign transaction (or the same transaction with different extracted values, e.g., after a reorg). Because the extracted values are not included in the response, the caller cannot distinguish a genuine attestation from a replayed one. Bridge contracts that release funds or update state based on the MPC attestation will act on incorrect foreign-chain data, enabling invalid bridge execution or double-spend conditions. This maps to the **High** allowed impact: *cross-chain replay / forged foreign-chain verification that causes invalid bridge execution or double-spend conditions*.

### Likelihood Explanation

The preconditions are low-friction:
- Past `VerifyForeignTransactionResponse` objects are publicly observable on-chain (returned as NEAR promise results).
- Any pending `verify_foreign_transaction` request is also publicly observable via `get_pending_verify_foreign_tx_request`.
- The attacker needs only to be a single attested participant — no threshold collusion is required.
- The attack is a simple on-chain function call with no off-chain computation.

The fan-out design (confirmed by the test `verify_foreign_transaction__should_queue_duplicates_from_different_callers`) explicitly allows different callers to share one pending map entry, widening the attack surface: a single replayed response can drain all queued yields simultaneously. [6](#0-5) 

### Recommendation

In `respond_verify_foreign_tx`, after verifying the signature, reconstruct the expected `payload_hash` prefix by verifying that `response.payload_hash` is the hash of a `ForeignTxSignPayload` whose `request` field matches the `request` argument. Concretely:

- Extend `VerifyForeignTransactionResponse` to include the full `ForeignTxSignPayload` (or at minimum the `Vec<ExtractedValue>`), not just the hash.
- In `respond_verify_foreign_tx`, recompute `expected_hash = ForeignTxSignPayload{request, values}.compute_msg_hash()` and assert `expected_hash == response.payload_hash` before accepting the response.

This mirrors the fix applied to `SpokePoolPeriphery` (adding a nonce to prevent reuse): here the binding between the signed payload and the pending request must be enforced on-chain, not just assumed.

### Proof of Concept

```
// Step 1: observe a past valid response for tx R_A on-chain (payload_hash_A, sig_A)

// Step 2: wait for a pending request for tx R_B
let r_b_pending = contract.get_pending_verify_foreign_tx_request(&request_r_b);
assert!(r_b_pending.is_some());

// Step 3: Byzantine participant calls respond_verify_foreign_tx with the old response
contract.respond_verify_foreign_tx(
    request_r_b,                          // pending request for R_B
    VerifyForeignTransactionResponse {
        payload_hash: payload_hash_a,     // hash of R_A's payload, not R_B's
        signature: sig_a,                 // valid signature over payload_hash_a
    }
);
// → succeeds: sig_a is valid over payload_hash_a under the root key
// → pending entry for R_B is drained with R_A's payload_hash

// Step 4: caller of R_B receives {payload_hash_a, sig_a}
// payload_hash_a = SHA-256(borsh(ForeignTxSignPayload{request=R_A, values=[H_A]}))
// caller cannot detect mismatch; bridge contract acts on H_A instead of H_B
```

The contract's own test infrastructure confirms the signature check is the only guard: [7](#0-6) 

and that `resolve_yields_for` drains the queue unconditionally once the signature check passes: [8](#0-7)

### Citations

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

**File:** crates/contract/src/lib.rs (L3255-3263)
```rust
        // Then: both yields are queued under the single (caller-agnostic) request key.
        assert_eq!(
            contract
                .pending_verify_foreign_tx_requests
                .get(&request)
                .map(|q| q.len()),
            Some(2),
            "duplicate foreign-tx requests from different callers should fan out",
        );
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
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

**File:** crates/contract/src/dto_mapping.rs (L840-848)
```rust
pub fn args_into_verify_foreign_tx_request(
    args: dtos::VerifyForeignTransactionRequestArgs,
) -> dtos::VerifyForeignTransactionRequest {
    dtos::VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
    }
}
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
