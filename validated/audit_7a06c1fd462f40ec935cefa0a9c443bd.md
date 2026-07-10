### Title
`respond_verify_foreign_tx` Accepts Caller-Supplied `payload_hash` Without Binding It to the Request, Enabling Cross-Request Signature Replay — (`crates/contract/src/lib.rs`)

---

### Summary

The `respond_verify_foreign_tx` function verifies that the submitted ECDSA signature is valid over the caller-supplied `response.payload_hash` using the **root** public key, but never checks that `payload_hash` was actually derived from the `request` content. A single Byzantine attested participant (below the signing threshold) can replay a previously valid on-chain signature — obtained by observing a prior `respond_verify_foreign_tx` transaction — against a different pending request, causing the contract to resolve that request with a forged foreign-chain verification result.

---

### Finding Description

**Asymmetry between `respond` and `respond_verify_foreign_tx`**

`respond` (regular signing) verifies the signature against the **derived** key, binding the signature to the specific request via `request.tweak`:

```rust
// crates/contract/src/lib.rs:597-607
let expected_public_key =
    derive_key_secp256k1(&affine, &request.tweak).map_err(RespondError::from)?;
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,
)
```

`respond_verify_foreign_tx` verifies against the **root** key with no tweak, and takes `payload_hash` directly from the caller-supplied response without any cross-check against the request:

```rust
// crates/contract/src/lib.rs:722-734
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

The comment itself says "root public key." The test confirms this design: `// simulate signature with the root key (no tweak for foreign tx)`.

**`VerifyForeignTransactionRequest` carries no caller identity and no tweak**

`args_into_verify_foreign_tx_request` converts the user-supplied args into the request key without binding any caller identity or derivation path:

```rust
// crates/contract/src/dto_mapping.rs:840-848
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

The design document (`docs/foreign-chain-transactions.md:105-110`) shows `VerifyForeignTransactionRequest` was intended to carry a `tweak` field derived from `(predecessor_id, derivation_path)`, but this field is absent from the production struct.

**Attack path (single Byzantine attested participant)**

1. Legitimate request for foreign-chain transaction X is processed. The MPC network produces `sig(H_X)` where `H_X = hash(ForeignTxSignPayload{request_X, extracted_values_X})`. The response is submitted on-chain and is publicly visible.
2. A new `verify_foreign_transaction` request for a different transaction Y is submitted by any user.
3. The malicious attested participant, before the honest MPC nodes respond, calls:
   ```
   respond_verify_foreign_tx(
       request = request_Y,          // matches the pending map entry
       response = {
           payload_hash: H_X,        // hash from the prior transaction X response
           signature:    sig(H_X),   // valid signature, already on-chain
       }
   )
   ```
4. The contract checks: (a) caller is attested participant ✓, (b) `sig(H_X)` is valid over `H_X` under the root key ✓. It then calls `resolve_yields_for(&mut self.pending_verify_foreign_tx_requests, &request_Y, …)`, draining all yields queued under `request_Y` with the forged response.
5. Every caller who submitted `verify_foreign_transaction` for transaction Y receives `{payload_hash: H_X, signature: sig(H_X)}` — a valid MPC signature, but over the payload of a completely different transaction.

---

### Impact Explanation

The `VerifyForeignTransactionResponse` returned to callers contains `payload_hash` and `signature`. Bridge contracts and other consumers that do not independently recompute `payload_hash` from the raw request will accept the forged attestation as proof that transaction Y was verified, when in fact the signature covers transaction X. This enables:

- **Forged bridge inbound flow**: a bridge contract mints or releases assets on NEAR in response to a foreign-chain event that was never actually verified.
- **Double-spend / replay**: the same prior signature can be replayed against multiple distinct pending requests, each receiving the same forged attestation.

This matches the allowed High impact: *"Cross-chain replay, forged foreign-chain verification … that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

The attacker must be a TEE-attested participant in the active set. However:
- The prior signature `sig(H_X)` is fully public (it appears in the on-chain `respond_verify_foreign_tx` transaction).
- The attacker only needs to win a race against the honest MPC nodes for a single block.
- A single Byzantine node below the signing threshold is sufficient; no collusion is required.
- The `pending_verify_foreign_tx_requests` map is caller-agnostic (fan-out design), so any pending request is a valid target.

---

### Recommendation

1. **Bind `payload_hash` to the request on-chain.** The contract should recompute the expected `payload_hash` prefix from the `request` fields it already holds (chain, tx_id, domain, payload_version) and reject any response whose `payload_hash` does not begin with or commit to those fields. Alternatively, require the response to include the full `ForeignTxSignPayload` so the contract can verify the hash itself.

2. **Introduce a per-request tweak (as the design doc intended).** Add a `tweak` field to `VerifyForeignTransactionRequest` derived from `(predecessor_id, derivation_path)` — as shown in `docs/foreign-chain-transactions.md:105-110` — and verify the signature against the **derived** key (mirroring `respond`). This cryptographically binds each signature to exactly one request, making cross-request replay impossible.

---

### Proof of Concept

```
// Step 1: observe a prior on-chain respond_verify_foreign_tx for tx_id_X
let H_X   = prior_response.payload_hash;   // public, from chain
let sig_X = prior_response.signature;      // public, from chain

// Step 2: a new verify_foreign_transaction for tx_id_Y is pending
let request_Y = VerifyForeignTransactionRequest {
    request: ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest {
        tx_id: tx_id_Y, ...
    }),
    domain_id: ...,
    payload_version: V1,
};

// Step 3: malicious attested participant calls respond_verify_foreign_tx
contract.respond_verify_foreign_tx(
    request_Y,
    VerifyForeignTransactionResponse {
        payload_hash: H_X,   // ← hash of tx_X, not tx_Y
        signature:    sig_X, // ← valid sig over H_X, root key
    }
);
// Contract accepts: sig_X is valid over H_X under root key ✓
// Yields for request_Y are resolved with the forged response.
// Callers waiting on tx_Y receive attestation for tx_X.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 
<cite repo="Alyssadaypin/mpc--009" path="crates/contract/src/lib.rs" start="3693" end="3694"

### Citations

**File:** crates/contract/src/lib.rs (L594-608)
```rust
                let affine = *k256::PublicKey::try_from(&secp_pk)
                    .expect("stored key is always valid")
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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```
