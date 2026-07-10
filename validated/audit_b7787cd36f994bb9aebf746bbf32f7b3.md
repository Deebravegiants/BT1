### Title
Caller-Agnostic `VerifyForeignTransactionResponse` Signed with Root Key Enables Cross-Chain Replay and Double-Spend — (File: `crates/contract/src/lib.rs`)

### Summary

The `verify_foreign_transaction` flow produces a `VerifyForeignTransactionResponse` signed by the MPC network over a payload that contains no caller identity, nonce, or expiry. Unlike `sign()`, which binds the response to the caller via a per-account tweak, `verify_foreign_transaction` uses a caller-agnostic request key and signs with the **root key** directly. Any party who obtains a valid response can replay it indefinitely against any consuming bridge contract, enabling double-spend conditions. The design document (`docs/foreign-chain-transactions.md`) explicitly specified a `tweak` field in `VerifyForeignTransactionRequest`, but the production implementation omitted it entirely.

---

### Finding Description

**Root cause — missing caller binding in the request key**

`sign()` constructs a `SignatureRequest` that incorporates the caller's identity via a tweak:

```rust
// crates/near-mpc-crypto-types/src/sign.rs:118-124
pub fn new(domain: DomainId, payload: Payload, predecessor_id: &AccountId, path: &str) -> Self {
    let tweak = crate::kdf::derive_tweak(predecessor_id, path);
    SignatureRequest { domain_id: domain, tweak, payload }
}
``` [1](#0-0) 

`verify_foreign_transaction()` does the opposite — `args_into_verify_foreign_tx_request` drops the caller entirely:

```rust
// crates/contract/src/dto_mapping.rs:840-848
pub fn args_into_verify_foreign_tx_request(
    args: dtos::VerifyForeignTransactionRequestArgs,
) -> dtos::VerifyForeignTransactionRequest {
    dtos::VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
        // predecessor_id / tweak: absent
    }
}
``` [2](#0-1) 

The resulting `VerifyForeignTransactionRequest` struct has no `tweak`, no `predecessor_id`, and no nonce:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs:124-128
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

<cite repo="Alyssadaypin/mpc--005" path="crates/near-mpc-contract-interface/src/types/

### Citations

**File:** crates/near-mpc-crypto-types/src/sign.rs (L117-125)
```rust
impl SignatureRequest {
    pub fn new(domain: DomainId, payload: Payload, predecessor_id: &AccountId, path: &str) -> Self {
        let tweak = crate::kdf::derive_tweak(predecessor_id, path);
        SignatureRequest {
            domain_id: domain,
            tweak,
            payload,
        }
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
