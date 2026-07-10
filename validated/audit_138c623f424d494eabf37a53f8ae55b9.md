### Title
`predecessor_id` Discarded and Zero Tweak Hardcoded in `verify_foreign_transaction` — (`File: crates/contract/src/lib.rs`, `crates/node/src/providers/verify_foreign_tx/sign.rs`)

---

### Summary

`verify_foreign_transaction()` captures the caller's `predecessor_id` via `check_request_preconditions()` but immediately discards it. The resulting `VerifyForeignTransactionRequest` carries no caller identity and no tweak. The MPC node then signs with a hardcoded zero tweak `Tweak::new([0u8; 32])`, meaning every foreign-transaction verification shares the same derived signing key and the same pending-request map key regardless of who submitted it. This is the direct analog of the external report: state (the stored request) is created for no party instead of the correct party, breaking the per-caller accounting invariant the design requires.

---

### Finding Description

In `sign()` and `request_app_private_key()`, the `predecessor` returned by `check_request_preconditions()` is bound and forwarded into `SignatureRequest::new(…, &predecessor, …)` / `CKDRequest::new(…, &predecessor, …)`, so the stored request key and the signing tweak are both caller-specific.

In `verify_foreign_transaction()` the same helper is called but its return value is **silently discarded**:

```rust
// lib.rs ~L526-531
self.check_request_preconditions(          // ← return value thrown away
    request.domain_id,
    DomainPurpose::ForeignTx,
    …
);
…
let request = args_into_verify_foreign_tx_request(request);  // predecessor never passed in
```

`VerifyForeignTransactionRequest` carries no `predecessor_id` and no `tweak`:

```rust
// foreign_chain.rs L124-128
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
    // ← no predecessor_id, no tweak
}
```

The design document (`docs/foreign-chain-transactions.md`) explicitly specifies that the struct **should** contain a `tweak` derived from `(predecessor_id, derivation_path)` and that `VerifyForeignTransactionRequestArgs` should carry a `derivation_path` field — neither exists in the production code.

Consequently, the MPC node's signing path hard-codes a zero tweak:

```rust
// node/src/providers/verify_foreign_tx/sign.rs L43
tweak: Tweak::new([0u8; 32]),   // ← always zero, never caller-derived
```

---

### Impact Explanation

**Request-lifecycle accounting invariant broken (Medium):**

1. **Shared pending-request key.** Because `VerifyForeignTransactionRequest` contains no caller identity, two distinct callers submitting the same foreign transaction produce an identical map key. Their yield indices are queued under the same entry and both receive the response — a caller can free-ride on another caller's paid request, and the contract cannot distinguish whose request is whose.

2. **Fixed signing key for all callers.** The zero tweak means every `verify_foreign_transaction` call is signed under the same derived key: `derive_key(ForeignTx_root, [0u8;32])`. The design intended per-caller key isolation (via `derivation_path`); the implementation collapses all callers onto one key, breaking the accounting invariant that each caller controls a distinct signing identity.

3. **Signature does not bind to caller.** A signature produced for caller A's request is cryptographically indistinguishable from one produced for caller B's request over the same foreign transaction. Any downstream consumer that relies on the signature being caller-specific (as the design implies) will be deceived.

---

### Likelihood Explanation

The entry path is fully unprivileged: any NEAR account can call `verify_foreign_transaction()` with 1 yoctoNEAR deposit and 10 Tgas. The discarded return value and the hardcoded zero tweak are present in the current production code with no conditional guard. Any two callers submitting the same foreign transaction ID will trigger the collision immediately.

---

### Recommendation

Mirror the pattern used by `sign()` and `request_app_private_key()`:

1. Bind the return value of `check_request_preconditions()` and pass `predecessor` into `args_into_verify_foreign_tx_request()`.
2. Add `derivation_path: String` to `VerifyForeignTransactionRequestArgs` and `tweak: Tweak` to `VerifyForeignTransactionRequest`, deriving the tweak with the foreign-tx-specific prefix already specified in the design doc.
3. In the node's `build_signature_request()`, replace `Tweak::new([0u8; 32])` with the tweak carried in `VerifyForeignTxRequest`.

```rust
// lib.rs – fix
let (_, predecessor) = self.check_request_preconditions(…);
let request = args_into_verify_foreign_tx_request(request, &predecessor);
```

```rust
// node – fix
tweak: request.tweak,   // derived from (predecessor_id, derivation_path)
```

---

### Proof of Concept

**Step 1 – Discard of predecessor (contract):** [1](#0-0) 

Compare with the correct pattern in `sign()`: [2](#0-1) 

**Step 2 – `VerifyForeignTransactionRequest` has no tweak/predecessor field:**
<cite repo

### Citations

**File:** crates/contract/src/lib.rs (L352-384)
```rust
        let (domain_config, predecessor) = self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::Sign,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );

        // ensure the signer sent a valid signature request
        // It's important we fail here because the MPC nodes will fail in an identical way.
        // This allows users to get the error message
        match domain_config.protocol {
            Protocol::CaitSith | Protocol::DamgardEtAl => {
                let hash = *request.payload.as_ecdsa().expect("Payload is not Ecdsa");
                k256::Scalar::from_repr(hash.into())
                    .into_option()
                    .expect("Ecdsa payload cannot be converted to Scalar");
            }
            Protocol::Frost => {
                request.payload.as_eddsa().expect("Payload is not EdDSA");
            }
            Protocol::ConfidentialKeyDerivation => {
                env::panic_str(
                    "ConfidentialKeyDerivation is not supported for signature responses",
                );
            }
        }

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
