### Title
Missing Payload-Hash-to-Request Binding in `respond_verify_foreign_tx` Enables Cross-Request Signature Substitution - (File: crates/contract/src/lib.rs)

### Summary
In `respond_verify_foreign_tx`, the contract verifies that `response.signature` is a valid ECDSA signature over `response.payload_hash` using the domain's root public key, but never verifies that `response.payload_hash` is actually derived from the `request` argument supplied in the same call. A single Byzantine attested participant below the signing threshold can reuse a legitimate MPC signature produced for one foreign-chain verification request to resolve an entirely different pending request, delivering a cryptographically valid but semantically false attestation to the waiting caller.

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` (lines 691–754) accepts two independent arguments: a `VerifyForeignTransactionRequest` (containing `domain_id`, `payload_version`, and the chain-specific `ForeignChainRpcRequest` with `tx_id`, `chain`, `extractors`) and a `VerifyForeignTransactionResponse` (containing `payload_hash` and `signature`). [1](#0-0) 

The only cryptographic check performed is:

```
verify_ecdsa_signature(response.signature, response.payload_hash, domain_root_pk)
```

There is no check that `response.payload_hash == SHA-256(borsh(ForeignTxSignPayload { request: request.request, values: <observed_values> }))`. The `request` argument is used solely as a lookup key into `pending_verify_foreign_tx_requests`; the `payload_hash` in the response is accepted verbatim. [2](#0-1) 

Contrast this with `respond` for regular sign requests, where the signature is verified directly against `request.payload` — a field that is part of the request itself and therefore cryptographically bound to it: [3](#0-2) 

The `ForeignTxSignPayload` that nodes actually sign is: [4](#0-3) 

Because `payload_hash` is the SHA-256 of `borsh(ForeignTxSignPayload { request, values })`, it encodes the specific `tx_id`, `chain`, and extracted values. The contract never reconstructs or checks this binding.

**Attack path:**

1. Request_A (`tx_id_A`, `chain_A`) is submitted and processed legitimately. The MPC network produces `signature_A` over `payload_hash_A = SHA-256(borsh({ request_A, values_A }))`. The Byzantine participant, having participated in the threshold signing round, receives `signature_A`.
2. Request_B (`tx_id_B`, `chain_B`) is pending in `pending_verify_foreign_tx_requests`.
3. The Byzantine participant calls `respond_verify_foreign_tx(request_B, { payload_hash: payload_hash_A, signature: signature_A })`.
4. The contract: (a) looks up `request_B` — found; (b) verifies `signature_A` over `payload_hash_A` against the domain root key — passes; (c) calls `resolve_yields_for` with `request_B` as key, delivering `{ payload_hash_A, signature_A }` to the caller who submitted request_B.

The caller of request_B receives a cryptographically valid MPC signature, but it attests to the verification of `tx_id_A` on `chain_A`, not their `tx_id_B` on `chain_B`.

### Impact Explanation

The caller of request_B receives a `VerifyForeignTransactionResponse` whose `signature` is genuinely valid under the MPC network's root public key, but whose `payload_hash` encodes a different transaction's verification result. Any downstream NEAR contract (e.g., an Omnibridge inbound handler) that trusts the signature without independently recomputing the expected `payload_hash` from the original `tx_id` and known extracted values will accept a false attestation. This enables invalid bridge execution: funds could be released on NEAR in response to a foreign-chain transaction that was never actually verified by the MPC network for that specific request. This matches the "forged foreign-chain verification … that causes invalid bridge execution or double-spend conditions" impact class.

### Likelihood Explanation

A single Byzantine attested participant below the signing threshold can execute this attack. Prerequisites are all realistic in production:

- The attacker must be an attested participant (they hold a valid TEE attestation and are in the active set).
- They participate in every signing round, so they receive every final signature the network produces.
- Multiple `verify_foreign_transaction` requests are routinely pending simultaneously (fan-out queue supports up to 128 per key).

No threshold collusion, key leakage, or privileged operator access is required.

### Recommendation

The contract must bind `response.payload_hash` to `request`. Since the contract does not store extracted values on-chain, the most practical fix is to include the full `ForeignTxSignPayload` in the response (not just its hash), allowing the contract to:

1. Verify `SHA-256(borsh(payload)) == response.payload_hash`.
2. Verify `payload.request == request.request` (the chain-specific request fields match).

Alternatively, the signed payload could be restructured so that the `ForeignChainRpcRequest` (including `tx_id` and `chain`) is hashed separately and committed to in a way the contract can verify without knowing the extracted values — for example, `payload_hash = SHA-256(borsh(tx_id) || SHA-256(borsh(values)))`, where the contract checks the first component against `request.request`.

### Proof of Concept

```
// Setup: two pending requests with different tx_ids
let request_a = VerifyForeignTransactionRequest { request: Bitcoin { tx_id: [0xAA; 32], ... }, domain_id, ... };
let request_b = VerifyForeignTransactionRequest { request: Bitcoin { tx_id: [0xBB; 32], ... }, domain_id, ... };

// Legitimate MPC signing for request_a produces:
//   payload_hash_a = SHA-256(borsh(ForeignTxSignPayload { request: request_a.request, values: [...] }))
//   signature_a    = ECDSA_sign(payload_hash_a, mpc_root_key)

// Byzantine participant calls:
contract.respond_verify_foreign_tx(
    request_b,                                          // lookup key → resolves request_b's yield
    VerifyForeignTransactionResponse {
        payload_hash: payload_hash_a,                   // hash of a DIFFERENT transaction
        signature:    signature_a,                      // valid signature — passes verify_ecdsa_signature
    },
);
// Result: caller of request_b receives { payload_hash_a, signature_a }
// The signature is valid, but attests to tx_id_A, not tx_id_B.
```

The contract's only check — `verify_ecdsa_signature(signature_a, payload_hash_a, root_pk)` — passes because `signature_a` is a genuine MPC signature. No check exists that `payload_hash_a` encodes `request_b.request`. [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L715-747)
```rust
        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain.0.into())?;

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L84-128)
```rust
#[derive(
    Debug,
    Clone,
    Eq,
    PartialEq,
    Ord,
    PartialOrd,
    Hash,
    Serialize,
    Deserialize,
    BorshSerialize,
    BorshDeserialize,
)]
#[cfg_attr(
    all(feature = "abi", not(target_arch = "wasm32")),
    derive(schemars::JsonSchema, borsh::BorshSchema)
)]
pub struct VerifyForeignTransactionRequestArgs {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}

#[derive(
    Debug,
    Clone,
    Eq,
    PartialEq,
    Ord,
    PartialOrd,
    Hash,
    Serialize,
    Deserialize,
    BorshSerialize,
    BorshDeserialize,
)]
#[cfg_attr(
    all(feature = "abi", not(target_arch = "wasm32")),
    derive(schemars::JsonSchema, borsh::BorshSchema)
)]
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```
