### Title
Missing `derivation_path`/`tweak` Fields in `VerifyForeignTransactionRequest` Breaks Key Isolation for Foreign-Tx Signing — (`File: crates/near-mpc-contract-interface/src/types/foreign_chain.rs`)

### Summary

The `VerifyForeignTransactionRequestArgs` and `VerifyForeignTransactionRequest` structs are missing the `derivation_path` and `tweak` fields that the design document explicitly specifies. As a result, all foreign-tx signing uses a hardcoded zero tweak (root key), breaking the design's intended per-caller key isolation and domain-separation invariant. This is the direct analog to the LSP8Burnable issue: a type is "incomplete" relative to its specification, causing missing security-critical functionality.

### Finding Description

The design document (`docs/foreign-chain-transactions.md`) specifies the following types:

```rust
// Design-specified (docs/foreign-chain-transactions.md lines 98-110)
pub struct VerifyForeignTransactionRequestArgs {
    pub request: ForeignChainRpcRequest,
    pub derivation_path: String,   // ← KEY ISOLATION FIELD
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}

pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub tweak: Tweak,              // ← KEY ISOLATION FIELD
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

The design further states (lines 254–286): *"The contract derives the tweak internally from `request.derivation_path` (callers do not submit raw tweaks). This ensures key material used for validated foreign transactions is **always** distinct from general-purpose `sign()` keys, even if the same account and derivation path are reused."*

The actual implementation omits both fields entirely:

```rust
// Actual implementation (crates/near-mpc-contract-interface/src/types/foreign_chain.rs lines 101-128)
pub struct VerifyForeignTransactionRequestArgs {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
    // derivation_path: MISSING
}

pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
    // tweak: MISSING
}
```

The conversion function propagates the omission:

```rust
// crates/contract/src/dto_mapping.rs lines 840-848
pub fn args_into_verify_foreign_tx_request(
    args: dtos::VerifyForeignTransactionRequestArgs,
) -> dtos::VerifyForeignTransactionRequest {
    dtos::VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
        // No tweak derivation at all
    }
}
```

The node-side signing hardcodes a zero tweak (root key):

```rust
// crates/node/src/providers/verify_foreign_tx/sign.rs lines 39-47
Ok(SignatureRequest {
    id: request.id,
    receipt_id: request.receipt_id,
    payload: Payload::Ecdsa(payload_bytes),
    tweak: Tweak::new([0u8; 32]),   // ← HARDCODED ZERO = ROOT KEY
    entropy: request.entropy,
    timestamp_nanosec: request.timestamp_nanosec,
    domain: request.domain_id,
})
```

The contract-side `respond_verify_foreign_tx` verifies against the **root** public key, not a derived key:

```rust
// crates/contract/src/lib.rs lines 718-734
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
            &secp_pk,   // ← ROOT KEY, no tweak derivation
        )
        .is_ok()
    }
```

Compare this with `respond()` for regular signatures, which correctly derives the expected key:

```rust
// crates/contract/src/lib.rs lines 597-608
let expected_public_key =
    derive_key_secp256k1(&affine, &request.tweak).map_err(RespondError::from)?;
// ...
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,   // ← DERIVED KEY with tweak
)
```

The test comment at line 3694 confirms this is a known deviation: *"simulate signature with the root key (no tweak for foreign tx)"*.

### Impact Explanation

The design's stated security invariant — *"key material used for validated foreign transactions is always distinct from general-purpose `sign()` keys, even if the same account and derivation path are reused"* — is broken. Concretely:

1. **No per-caller key isolation**: All callers of `verify_foreign_transaction` share the same root key for their attestations. The design intended each `(predecessor_id, derivation_path)` pair to produce a unique derived key via the foreign-tx prefix, preventing cross-caller key confusion.
2. **Root key exposure**: The MPC root key for the ForeignTx domain is used directly for all foreign-tx attestations. Any bridge contract or NEAR smart contract using `verify_foreign_transaction` receives attestations signed with the same root key, regardless of caller identity or derivation path.
3. **Domain-separation invariant broken**: The design's `FOREIGN_TX_TWEAK_DERIVATION_PREFIX` mechanism is entirely absent. The contract execution flow for foreign-tx signing is materially different from the specified design, breaking the production safety invariant of key isolation.

This maps to **Medium** impact: contract execution-flow manipulation that breaks production safety/accounting invariants (key isolation) without requiring network-level DoS or operator misconfiguration.

### Likelihood Explanation

This is a confirmed, unconditional implementation gap. Every call to `verify_foreign_transaction` is affected — no special conditions are required. Any unprivileged NEAR account can call `verify_foreign_transaction` and observe that the resulting attestation is signed with the root key rather than a caller-specific derived key.

### Recommendation

1. Add `derivation_path: String` to `VerifyForeignTransactionRequestArgs` in `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`.
2. Add `tweak: Tweak` to `VerifyForeignTransactionRequest` in the same file.
3. In `args_into_verify_foreign_tx_request` (`crates/contract/src/dto_mapping.rs`), derive the tweak from `(predecessor_id, derivation_path)` using the foreign-tx-specific prefix (`"near-mpc-recovery v0.1.0 foreign-tx epsilon derivation:"`).
4. In `build_signature_request` (`crates/node/src/providers/verify_foreign_tx/sign.rs`), use `request.tweak` instead of `Tweak::new([0u8; 32])`.
5. In `respond_verify_foreign_tx` (`crates/contract/src/lib.rs`), derive the expected public key using `derive_key_secp256k1(&affine, &request.tweak)` and verify against the derived key, mirroring the `respond()` function.

### Proof of Concept

**Step 1**: Observe the design specification in `docs/foreign-chain-transactions.md` lines 98–110 and 254–286, which explicitly requires `derivation_path` in `VerifyForeignTransactionRequestArgs` and `tweak` in `VerifyForeignTransactionRequest`.

**Step 2**: Observe the actual struct definitions in `crates/near-mpc-contract-interface/src/types/foreign_chain.rs` lines 101–128 — neither field is present.

**Step 3**: Observe `args_into_verify_foreign_tx_request` in `crates/contract/src/dto_mapping.rs` lines 840–848 — no tweak derivation occurs.

**Step 4**: Observe `build_signature_request` in `crates/node/src/providers/verify_foreign_tx/sign.rs` lines 39–47 — `tweak: Tweak::new([0u8; 32])` is hardcoded.

**Step 5**: Observe `respond_verify_foreign_tx` in `crates/contract/src/lib.rs` lines 718–734 — verification uses the root public key (`secp_pk`) with no tweak derivation, unlike `respond()` at lines 597–608 which correctly uses `derive_key_secp256k1(&affine, &request.tweak)`.

**Step 6**: The test at `crates/contract/src/lib.rs` line 3694 explicitly confirms: *"simulate signature with the root key (no tweak for foreign tx)"* — acknowledging the deviation from the design. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L101-128)
```rust
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

**File:** crates/contract/src/lib.rs (L597-608)
```rust
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
