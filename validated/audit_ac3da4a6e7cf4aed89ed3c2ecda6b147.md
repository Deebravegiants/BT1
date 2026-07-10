### Title
`respond_verify_foreign_tx` Accepts Caller-Supplied `payload_hash` Without Binding It to the Pending Request — (`File: crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies that `response.signature` is a valid ECDSA signature over `response.payload_hash`, but never checks that `response.payload_hash` was actually computed from the `request` argument. A single Byzantine attested participant can replay a threshold signature produced for a previous foreign-chain verification request to resolve a completely different pending request with forged observed values.

### Finding Description

In `respond_verify_foreign_tx` (lines 691–754 of `crates/contract/src/lib.rs`), the contract performs the following signature check:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;   // taken from caller

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,          // never verified against `request`
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

The `payload_hash` is the hash of `ForeignTxSignPayloadV1 { request: ForeignChainRpcRequest, values: Vec<ExtractedValue> }`, as shown in the test that constructs a valid response:

```rust
let payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: vec![ExtractedValue::BitcoinExtractedValue(
        BitcoinExtractedValue::BlockHash([42u8; 32].into()),
    )],
});
let payload_hash = payload.compute_msg_hash().unwrap().0;
``` [2](#0-1) 

The contract has the `request` in scope (it is the first argument to `respond_verify_foreign_tx` and is used to look up the pending yield in `resolve_yields_for`), but it never reconstructs or checks the expected `payload_hash` from that request. It simply trusts whatever 32-byte value the caller places in `response.payload_hash`.

Compare this to the regular `respond` function, which derives the payload hash directly from the request object and never accepts it from the caller:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,           // derived from request, not from response
    &expected_public_key,
)
``` [3](#0-2) 

This is the direct analog of the `_stethToWsteth` bug: instead of using the value returned by the computation (the hash derived from the actual request and observed values), the contract reads an ambient caller-supplied value (`response.payload_hash`) that can be substituted with any previously valid hash.

### Impact Explanation

A single Byzantine attested participant can:

1. Observe a legitimately completed foreign-chain verification for **Request A** (e.g., Bitcoin tx A), obtaining the threshold signature `sig_A` over `H_A = hash(request_A, observed_values_A)`.
2. Wait for **Request B** (e.g., Bitcoin tx B) to be pending in the contract.
3. Call `respond_verify_foreign_tx(request_B, { payload_hash: H_A, signature: sig_A })`.
4. The contract verifies `sig_A` is a valid threshold signature over `H_A` — which it is — and resolves Request B with the forged response.

The user who submitted Request B receives a valid MPC signature over `H_A`, which encodes the observed values from Request A (e.g., Bitcoin tx A's block hash), not Request B's. A downstream bridge contract that trusts this response would process an event based on incorrect foreign-chain state, enabling double-spend or invalid bridge execution.

**Impact category:** High — forged foreign-chain verification causing invalid bridge execution.

### Likelihood Explanation

- Requires only **one** Byzantine attested participant (strictly below the signing threshold).
- No new cryptographic material needs to be forged; the attacker reuses a legitimately produced threshold signature.
- Any participant who was part of a previous `verify_foreign_transaction` computation has the necessary `(sig, hash)` pair.
- The attack is silent: the contract emits no log distinguishing a replayed hash from a fresh one.

### Recommendation

The contract must bind the `payload_hash` to the `request` it is resolving. Since `ForeignTxSignPayloadV1` encodes the `ForeignChainRpcRequest` inside the hash, the contract should:

1. Extend `VerifyForeignTransactionResponse` to include the raw `observed_values` alongside `payload_hash`.
2. In `respond_verify_foreign_tx`, recompute the expected hash as `hash(request.request, observed_values)` and assert it equals `response.payload_hash` before accepting the signature.

This mirrors how `respond` derives `payload_hash` directly from `request.payload` rather than accepting it from the caller.

### Proof of Concept

```
// Setup: MPC network has already completed verification of Request A.
// Attacker (single Byzantine participant) holds (H_A, sig_A).

// Step 1: User submits Request B (different Bitcoin tx).
contract.verify_foreign_transaction(request_args_B);  // pending

// Step 2: Attacker replays Request A's signature against Request B.
contract.respond_verify_foreign_tx(
    request_B,                                    // correct pending request key
    VerifyForeignTransactionResponse {
        payload_hash: H_A,                        // hash from Request A
        signature: sig_A,                         // valid threshold sig over H_A
    }
);
// Contract checks: is sig_A valid over H_A under root key? YES.
// Contract resolves Request B with forged payload_hash H_A.
// User's bridge contract receives a valid MPC attestation encoding
// Request A's observed values (e.g., Bitcoin tx A's block hash),
// not Request B's — causing invalid bridge execution.
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

**File:** crates/contract/src/lib.rs (L3687-3706)
```rust
        let payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
            request: request.request.clone(),
            values: vec![ExtractedValue::BitcoinExtractedValue(
                BitcoinExtractedValue::BlockHash([42u8; 32].into()),
            )],
        });
        let payload_hash = payload.compute_msg_hash().unwrap().0;
        // simulate signature with the root key (no tweak for foreign tx)
        let secret_key_ec: elliptic_curve::SecretKey<Secp256k1> =
            elliptic_curve::SecretKey::from_bytes(&secret_key.to_bytes()).unwrap();
        let secret_key = SigningKey::from_bytes(&secret_key_ec.to_bytes()).unwrap();
        let (signature, recovery_id) = secret_key.sign_prehash_recoverable(&payload_hash).unwrap();
        let signature = dtos::SignatureResponse::Secp256k1(
            dtos::K256Signature::from_ecdsa_recoverable(&signature, recovery_id),
        );

        let payload_hash = payload.compute_msg_hash().unwrap();
        let response = VerifyForeignTransactionResponse {
            payload_hash,
            signature,
```
