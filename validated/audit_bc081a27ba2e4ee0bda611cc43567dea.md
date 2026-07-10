Now I have enough context to write the full finding. Let me verify one more detail about the `SignatureRequest::new` to confirm the contrast with `sign()`.

### Title
Caller Identity Not Bound in `verify_foreign_transaction` Request — Any Account Can Obtain the Same MPC-Signed Foreign-Chain Attestation - (File: `crates/contract/src/lib.rs`)

---

### Summary

`verify_foreign_transaction` omits the caller's `predecessor_account_id` from the stored `VerifyForeignTransactionRequest`. Because the request key is caller-agnostic, any account that submits the same foreign-chain query receives the identical MPC-signed attestation. An adversary who observes a legitimate bridge user's pending request can submit the same request and obtain the same signature, then race to present it to a downstream bridge contract and claim the bridged funds before the legitimate user.

---

### Finding Description

`sign()` and `request_app_private_key()` both bind the caller's identity into the stored request by passing `&predecessor` into `SignatureRequest::new(...)` and `CKDRequest::new(...)` respectively. This derives a caller-specific `tweak`, making the request key and the signing key unique to that account.

`verify_foreign_transaction()` does not do this. The `predecessor` returned by `check_request_preconditions` is silently discarded:

```rust
// crates/contract/src/lib.rs  lines 526-556
self.check_request_preconditions(          // returns (domain_config, predecessor)
    request.domain_id,
    DomainPurpose::ForeignTx,
    ...
);
// predecessor is never used below
let request = args_into_verify_foreign_tx_request(request);   // no caller field
self.enqueue_yield_request(..., move |this, id| this.add_verify_foreign_tx_request(request, id));
```

`args_into_verify_foreign_tx_request` copies only `domain_id`, `request`, and `payload_version` — no caller identity:

```rust
// crates/contract/src/dto_mapping.rs  lines 840-848
pub fn args_into_verify_foreign_tx_request(args: ...) -> VerifyForeignTransactionRequest {
    VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
    }
}
```

`VerifyForeignTransactionRequest` itself has no caller field:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs  lines 124-128
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

The contract's own test explicitly documents and exercises this property — different callers (alice, bob) submitting the same request are queued under the **same** map key and both receive the same response:

```rust
// crates/contract/src/lib.rs  lines 3255-3262
// Then: both yields are queued under the single (caller-agnostic) request key.
assert_eq!(
    contract.pending_verify_foreign_tx_requests.get(&request).map(|q| q.len()),
    Some(2),
    "duplicate foreign-tx requests from different callers should fan out",
);
```

Additionally, `respond_verify_foreign_tx` verifies the signature against the **root public key with no tweak** — confirming the attestation is completely caller-agnostic:

```rust
// crates/contract/src/lib.rs  lines 728-734
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,   // root key, no caller-derived tweak
)
```

---

### Impact Explanation

The primary production use case of `verify_foreign_transaction` is the **Omnibridge inbound flow** (foreign chain → NEAR): a user proves a foreign-chain deposit finalized so a NEAR bridge contract can release funds. The `VerifyForeignTransactionResponse` contains `(payload_hash, signature)` — an MPC attestation that a specific foreign-chain transaction occurred. Because this attestation carries no caller binding, any account that obtains it can present it to the bridge contract.

Attack path:
1. Alice sends BTC to the bridge deposit address and submits `verify_foreign_transaction` referencing her Bitcoin `tx_id`.
2. Attacker observes Alice's pending request in the public NEAR chain state (or mempool).
3. Attacker submits the identical `VerifyForeignTransactionRequestArgs`.
4. Both Alice and Attacker are queued under the same caller-agnostic key; when MPC nodes respond, both receive the same `VerifyForeignTransactionResponse`.
5. Attacker submits the response to the bridge contract before Alice and claims Alice's bridged funds.

This matches the allowed impact: **cross-chain replay / forged foreign-chain verification bypass that causes invalid bridge execution or double-spend conditions**.

---

### Likelihood Explanation

- No special privileges, collusion, or leaked keys are required.
- NEAR chain state is fully public; pending requests are visible to anyone querying `get_pending_verify_foreign_tx_request`.
- The attacker only needs to copy the request arguments and submit a single transaction.
- The fan-out queue (`MAX_PENDING_REQUEST_FAN_OUT`) is bounded but large enough to accommodate the attacker's entry alongside the victim's.
- The attack is profitable whenever the bridged value exceeds the cost of one NEAR transaction (1 yoctoNEAR deposit + gas).

---

### Recommendation

Include the caller's `predecessor_account_id` in `VerifyForeignTransactionRequest` (and its stored key), mirroring the pattern used by `sign()` and `request_app_private_key()`. The `predecessor` is already available from `check_request_preconditions` but is currently discarded. Binding it into the request key ensures that only the original submitter's yield is resolved by a given MPC response, and that the MPC-signed attestation is scoped to the submitting account — preventing any other account from obtaining or reusing it.

---

### Proof of Concept

**Step 1 — Alice submits a legitimate bridge request:**
```rust
// Alice calls verify_foreign_transaction with her Bitcoin tx_id
let request_args = VerifyForeignTransactionRequestArgs {
    domain_id: foreign_tx_domain_id,
    payload_version: ForeignTxPayloadVersion::V1,
    request: ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest {
        tx_id: alice_btc_tx_id,
        confirmations: 6.into(),
        extractors: vec![BitcoinExtractor::BlockHash],
    }),
};
alice.call(contract_id, "verify_foreign_transaction")
    .args_json(json!({ "request": request_args }))
    .deposit(1)
    .transact_async().await;
```

**Step 2 — Attacker copies the identical request:**
```rust
// Attacker submits the same request_args (read from public chain state)
attacker.call(contract_id, "verify_foreign_transaction")
    .args_json(json!({ "request": request_args }))  // identical
    .deposit(1)
    .transact_async().await;
```

**Step 3 — Both are queued under the same caller-agnostic key** (confirmed by the existing test at `crates/contract/src/lib.rs:3255`):
```
pending_verify_foreign_tx_requests[VerifyForeignTransactionRequest { tx_id: alice_btc_tx_id, ... }]
  → [alice_yield_id, attacker_yield_id]
```

**Step 4 — MPC nodes respond once; both yields are resolved** with the same `VerifyForeignTransactionResponse { payload_hash, signature }`.

**Step 5 — Attacker submits the response to the bridge contract first**, claiming Alice's bridged funds. Alice's transaction also resolves but the bridge contract has already processed the claim.

The root cause is confirmed at:
- [1](#0-0)  — `predecessor` discarded, no caller binding in the stored request
- [2](#0-1)  — `args_into_verify_foreign_tx_request` omits caller identity
- [3](#0-2)  — `VerifyForeignTransactionRequest` has no caller field
- [4](#0-3)  — contrast: `sign()` binds `predecessor` into `SignatureRequest::new`
- [5](#0-4)  — test explicitly confirms caller-agnostic fan-out across different accounts
- [6](#0-5)  — `respond_verify_foreign_tx` uses root key with no caller-derived tweak

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

**File:** crates/contract/src/lib.rs (L526-556)
```rust
        self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::ForeignTx,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );

        let requested_chain = request.request.chain();
        let supported_chains = self.get_supported_foreign_chains();
        if !supported_chains.contains(&requested_chain) {
            env::panic_str(
                &InvalidParameters::ForeignChainNotSupported {
                    requested: requested_chain,
                }
                .to_string(),
            );
        }

        let callback_gas = Gas::from_tgas(
            self.config
                .return_signature_and_clean_state_on_success_call_tera_gas,
        );

        let request = args_into_verify_foreign_tx_request(request);
        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_VERIFY_FOREIGN_TX_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_verify_foreign_tx_request(request, id),
        );
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
