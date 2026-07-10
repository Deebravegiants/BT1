### Title
Caller Identity Dropped from `verify_foreign_transaction` Request Key, Enabling Cross-Caller Signature Sharing and Cross-Chain Replay — (File: `crates/contract/src/lib.rs`)

---

### Summary

`verify_foreign_transaction` discards the caller's account ID before storing the pending request. Because `VerifyForeignTransactionRequest` carries no caller identity or derived tweak, any unprivileged account that submits the same `(domain_id, request, payload_version)` tuple receives the identical MPC-signed response. The resulting signature is issued against the **root public key** with no per-caller derivation, making it universally replayable by anyone who observed the original on-chain call.

---

### Finding Description

In `sign()`, the caller's identity is cryptographically bound into the stored request via a tweak:

```rust
// lib.rs:379-384
let request = SignatureRequest::new(
    request.domain_id,
    request.payload,
    &predecessor,       // ← predecessor bound into tweak
    &request.path,
);
```

`SignatureRequest` stores `tweak = derive_tweak(predecessor_id, path)`, so two different callers with the same path produce different request keys and different derived signing keys.

`verify_foreign_transaction` does the opposite. `check_request_preconditions` returns `(DomainConfig, AccountId)` but the return value is **silently discarded**:

```rust
// lib.rs:526-531
self.check_request_preconditions(   // ← return value dropped; predecessor never captured
    request.domain_id,
    DomainPurpose::ForeignTx,
    Gas::from_tgas(...),
    MINIMUM_SIGN_REQUEST_DEPOSIT,
);
```

The request is then converted without the caller:

```rust
// dto_mapping.rs:840-848
pub fn args_into_verify_foreign_tx_request(
    args: dtos::VerifyForeignTransactionRequestArgs,
) -> dtos::VerifyForeignTransactionRequest {
    dtos::VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
        // ← no predecessor_id, no tweak
    }
}
```

`VerifyForeignTransactionRequest` itself has no caller field:

```rust
// foreign_chain.rs:124-128
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
    // ← no predecessor_id, no tweak
}
```

The contract's own test explicitly confirms the caller-agnostic key:

```rust
// lib.rs:3255
// Then: both yields are queued under the single (caller-agnostic) request key.
assert_eq!(
    contract.pending_verify_foreign_tx_requests.get(&request).map(|q| q.len()),
    Some(2),
    "duplicate foreign-tx requests from different callers should fan out",
);
```

When `respond_verify_foreign_tx` resolves the request, it verifies the signature against the **root public key** (no tweak applied):

```rust
// lib.rs:728-733
// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,   // ← root key, no per-caller derivation
)
.is_ok()
```

All callers queued under the same request key receive the identical `VerifyForeignTransactionResponse` (same `payload_hash` + same root-key signature) via `resolve_yields_for`.

---

### Impact Explanation

**High — Cross-chain replay / forged foreign-chain verification enabling invalid bridge execution.**

The MPC-signed response is a proof that the network verified a specific foreign-chain transaction. Because the signature is issued under the root key with no caller binding, it is structurally identical regardless of who submitted the request. Any party that obtains this signature — including an adversary who simply front-ran or duplicated the on-chain call — holds a valid, indistinguishable credential.

Bridge contracts that gate fund releases on a `verify_foreign_transaction` response (the intended use-case) cannot distinguish a legitimate caller's response from one obtained by an adversary who submitted the same request. An attacker can:

1. Observe Alice's `verify_foreign_transaction` call on-chain.
2. Submit the identical `(domain_id, request, payload_version)` tuple.
3. Receive the same root-key signature as Alice.
4. Present that signature to any bridge contract to claim the same foreign-chain event was verified on their behalf.

This enables double-spend conditions: a single foreign-chain transaction (e.g., a Bitcoin UTXO spend) can be used to unlock bridge funds multiple times across different callers or different bridge contract invocations, because the MPC credential is not scoped to the original submitter.

---

### Likelihood Explanation

**High.** The entry path requires no special privilege: any NEAR account can call `verify_foreign_transaction`. The attacker only needs to observe a pending request on-chain (all NEAR transactions are public) and submit the same arguments. The 1 yoctoNEAR deposit is negligible. The test at `lib.rs:3208-3263` demonstrates the behavior is reachable and reproducible with two ordinary accounts.

---

### Recommendation

**Short term:** Capture the predecessor returned by `check_request_preconditions` and include it in `VerifyForeignTransactionRequest`, mirroring the `sign()` pattern. Derive a per-caller tweak (using the foreign-tx prefix already described in `docs/foreign-chain-transactions.md`) and store it in the request struct. `respond_verify_foreign_tx` should then verify the signature against the **derived** key (tweak applied), not the root key.

**Long term:** Add a property-based test asserting that two different callers submitting the same foreign-chain transaction arguments produce **different** pending request keys and receive **different** signatures, analogous to the existing `sign()` isolation guarantees.

---

### Proof of Concept

```
1. Alice calls verify_foreign_transaction({
       domain_id: 0,
       request: Bitcoin { tx_id: X, confirmations: 2, extractors: [BlockHash] },
       payload_version: V1
   })
   with 1 yoctoNEAR attached.

2. Eve calls verify_foreign_transaction with the identical arguments
   (observed from Alice's on-chain transaction).

3. Both are queued under the same VerifyForeignTransactionRequest key
   (confirmed by lib.rs:3255 test assertion).

4. MPC nodes call respond_verify_foreign_tx once.
   resolve_yields_for delivers the identical VerifyForeignTransactionResponse
   (payload_hash + root-key signature) to BOTH Alice's and Eve's yield callbacks.

5. Eve now holds a valid MPC root-key signature over the Bitcoin transaction payload.

6. Eve presents this signature to a bridge contract that releases NEAR/tokens
   upon receiving a valid verify_foreign_transaction credential for tx_id X.
   The bridge contract cannot distinguish Eve's credential from Alice's —
   both are byte-for-byte identical root-key signatures.

7. The bridge releases funds to Eve for a transaction that was intended to
   credit Alice, constituting a double-spend.
```

**Root cause lines:**
- `crates/contract/src/lib.rs:526–531` — predecessor return value discarded
- `crates/contract/src/dto_mapping.rs:840–848` — predecessor excluded from request
- `crates/near-mpc-contract-interface/src/types/foreign_chain.rs:124–128` — no caller field in struct
- `crates/contract/src/lib.rs:728–733` — root key used instead of derived key [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L379-384)
```rust
        let request = SignatureRequest::new(
            request.domain_id,
            request.payload,
            &predecessor,
            &request.path,
        );
```

**File:** crates/contract/src/lib.rs (L526-531)
```rust
        self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::ForeignTx,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );
```

**File:** crates/contract/src/lib.rs (L728-733)
```rust
                // Check the signature is correct against the root public key
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    &payload_hash,
                    &secp_pk,
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
