### Title
`respond_verify_foreign_tx` Does Not Bind `response.payload_hash` to the Submitted `request` — Enabling Cross-Request Signature Replay by a Single Attested Participant - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies that `response.signature` is a valid ECDSA signature over `response.payload_hash` using the root MPC public key, but it never checks that `response.payload_hash` was actually derived from the `request` argument that is being resolved. A single attested participant (below the signing threshold) can therefore replay any previously-observed `(payload_hash, signature)` pair — produced for a completely different foreign transaction — against any currently-pending `verify_foreign_transaction` request, causing the contract to resolve that request with a forged verification response.

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` performs the following validation:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

The check confirms only that `signature` is a valid ECDSA signature over `payload_hash` under the root public key. It does **not** re-derive the expected `payload_hash` from the `request` parameter and compare. The `payload_hash` is supposed to be `SHA-256(borsh(ForeignTxSignPayload))` where `ForeignTxSignPayload` commits to the specific `ForeignChainRpcRequest` and the extracted values observed on the foreign chain:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
``` [2](#0-1) 

Because the contract cannot re-derive the hash without the extracted values (which are off-chain), it relies entirely on the responding participant to supply the correct `payload_hash`. There is no binding between the `request` key used to look up the pending yield queue and the `payload_hash` supplied in the response.

Contrast this with the regular `respond` path, where the payload is taken directly from the `request` struct itself and the signature is verified against that canonical value — there is no caller-supplied hash:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,
)
``` [3](#0-2) 

Additionally, the `VerifyForeignTransactionRequest` key used for the pending-request map does **not** include the caller's account ID (unlike `SignatureRequest`), so the fan-out queue is caller-agnostic:

```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
``` [4](#0-3) 

This means a single `respond_verify_foreign_tx` call drains the entire fan-out queue for a given request key, resolving every queued caller simultaneously with the forged response. [5](#0-4) 

### Impact Explanation

A single attested participant (below the signing threshold) can:

1. Observe any past `VerifyForeignTransactionResponse` on-chain — the `(payload_hash_old, signature_old)` pair is the return value of the yield-resume callback and is publicly visible in NEAR transaction receipts.
2. Wait for a new `verify_foreign_transaction` request to be submitted for a **different** foreign transaction (different `tx_id`, different chain, or different extracted values).
3. Call `respond_verify_foreign_tx(request = new_request, response = {payload_hash_old, signature_old})`.
4. The contract accepts the call: `signature_old` is a valid signature over `payload_hash_old` under the root public key, and `new_request` exists in the pending map.
5. Every caller waiting on `new_request` receives `{payload_hash_old, signature_old}` — a cryptographically valid-looking response that actually commits to a **different** foreign transaction.

Any bridge contract or downstream consumer that trusts the returned `payload_hash` without independently reconstructing it from the original request will accept a forged attestation. The documentation states callers "can verify" the hash but does not mandate it, and the contract itself provides no enforcement. This enables fraudulent bridge execution: an attacker can make the MPC network appear to have attested to a foreign-chain event that it never verified.

The impact maps to: **High — forged foreign-chain verification that causes invalid bridge execution or double-spend conditions.**

### Likelihood Explanation

- The attacker must be a single attested participant (one compromised or Byzantine TEE node), which is explicitly within the allowed attacker model ("Byzantine participant strictly below the signing threshold").
- The required `(payload_hash, signature)` material is freely observable on-chain from any prior completed `verify_foreign_transaction` request.
- The attacker only needs to monitor the contract for a pending request and submit one transaction. No threshold cooperation is required.
- The fan-out design (caller-agnostic key) amplifies the impact: one malicious `respond_verify_foreign_tx` call poisons every queued caller simultaneously.

### Recommendation

Inside `respond_verify_foreign_tx`, re-derive the expected `payload_hash` from the `request` argument and compare it to `response.payload_hash` before accepting the response. Since the contract does not have the extracted values, the binding must be enforced differently — for example:

- Include the `ForeignChainRpcRequest` (or its hash) inside the signed payload in a way that the contract can verify independently, or
- Have the MPC nodes include the `request` hash as an additional authenticated field in the response that the contract checks against the pending-request key, or
- Store a commitment to the expected `payload_hash` in the pending-request map at submission time (requires the contract to know the expected extracted values, which is architecturally difficult), or
- At minimum, document that callers **must** reconstruct and verify the `payload_hash` against their original request, and consider adding an on-chain assertion that the `payload_hash` encodes the same `ForeignChainRpcRequest` as the `request` argument (by including the request hash in the signed payload and verifying it on-chain).

### Proof of Concept

```
1. Attested participant P observes a completed verify_foreign_transaction for
   Bitcoin tx_id=[0xAA;32], obtaining:
     payload_hash_old = SHA-256(borsh({request: Bitcoin{tx_id=[0xAA;32],...}, values: [...]}))
     signature_old    = valid MPC ECDSA signature over payload_hash_old

2. User U submits verify_foreign_transaction for Bitcoin tx_id=[0xBB;32].
   Contract stores pending yield for request_new = {Bitcoin{tx_id=[0xBB;32],...}}.

3. P calls:
     respond_verify_foreign_tx(
       request  = request_new,          // pending request for tx_id=[0xBB;32]
       response = { payload_hash: payload_hash_old,   // hash of tx_id=[0xAA;32]
                    signature:    signature_old }      // valid sig over old hash
     )

4. Contract checks:
     verify_ecdsa_signature(signature_old, payload_hash_old, root_pk) → OK  ✓
     pending_verify_foreign_tx_requests.get(request_new) → exists           ✓
   → resolves all queued yields with {payload_hash_old, signature_old}

5. U receives VerifyForeignTransactionResponse{
       payload_hash: payload_hash_old,   // commits to tx_id=[0xAA;32]
       signature:    signature_old       // valid under root_pk
   }
   The response is cryptographically valid but attests to the wrong transaction.
   Any bridge contract that does not independently reconstruct the expected
   payload_hash will accept this as proof that tx_id=[0xBB;32] was verified.
``` [6](#0-5)

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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L338-346)
```rust
            dtos::ForeignTxPayloadVersion::V1 => {
                dtos::ForeignTxSignPayload::V1(dtos::ForeignTxSignPayloadV1 {
                    request: request.clone(),
                    values,
                })
            }
            _ => bail!("unsupported payload_version"),
        };
        Ok(payload)
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
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
