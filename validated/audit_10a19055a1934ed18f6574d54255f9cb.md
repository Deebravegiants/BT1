### Title
`verify_foreign_transaction` Signs All Foreign-Chain Attestations Under the Root Key (Zero Tweak) Instead of a Caller-Specific Derived Key — (File: `crates/node/src/providers/verify_foreign_tx/sign.rs`, `crates/contract/src/dto_mapping.rs`)

---

### Summary

The `verify_foreign_transaction` flow omits the caller's identity (`predecessor_account_id`) from the signing key derivation entirely. The design specification requires a `derivation_path` in the request args and a `tweak` derived from `(predecessor_id, derivation_path)` in the stored request, mirroring the `sign()` flow. The production implementation instead hardcodes a zero tweak (`[0u8; 32]`) on the node side and verifies the resulting signature against the **root public key** on the contract side. Every caller — regardless of account — receives a signature produced under the same root key, with no caller identity bound into the key material.

---

### Finding Description

**Design intent (from `docs/foreign-chain-transactions.md`):**

The design document specifies that `VerifyForeignTransactionRequestArgs` must carry a `derivation_path: String` and that the contract derives a caller-specific tweak via `derive_foreign_tx_tweak(predecessor_id, derivation_path)` before storing the request. This mirrors the `sign()` flow where `SignatureRequest::new(domain_id, payload, &predecessor, &path)` binds the caller's account into the tweak.

**What the code actually does:**

1. `VerifyForeignTransactionRequestArgs` has **no `derivation_path` field**: [1](#0-0) 

2. `VerifyForeignTransactionRequest` has **no `tweak` field**: [2](#0-1) 

3. `args_into_verify_foreign_tx_request` performs a direct field copy with **no tweak derivation and no capture of `predecessor_account_id`**: [3](#0-2) 

4. `verify_foreign_transaction` logs the predecessor but **never uses it** to bind the caller into the request key: [4](#0-3) 

5. On the node side, `build_signature_request` hardcodes a **zero tweak**, meaning the MPC network signs with the root key: [5](#0-4) 

6. `respond_verify_foreign_tx` verifies the signature against the **root public key** (comment in code confirms this): [6](#0-5) 

Because `VerifyForeignTransactionRequest` contains no caller identity, the pending-request map key is **caller-agnostic**. The unit test explicitly confirms that Alice and Bob submitting the same foreign-tx request are queued under the **same map entry** and both receive the same signature from a single `respond_verify_foreign_tx` call: [7](#0-6) 

---

### Impact Explanation

**Impact: Medium** (breaks production safety/accounting invariants in the bridge execution flow).

The `verify_foreign_transaction` feature is explicitly designed for bridge use cases (Omnibridge inbound flow: foreign chain → NEAR). The returned `VerifyForeignTransactionResponse` — containing `payload_hash` and a signature — is the on-chain attestation that a foreign transaction finalized. Because the signature is always under the root key (zero tweak) and the request key carries no caller identity:

- **Cross-caller signature reuse**: A signature obtained by Alice for Bitcoin tx X is cryptographically identical to the one Bob would receive for the same tx. Any party who observes the signature on-chain can replay it to any bridge contract that accepts `verify_foreign_transaction` responses.
- **No per-caller key isolation**: The design's security property — that each caller's `verify_foreign_transaction` uses a distinct derived key, preventing one caller's attestation from being used by another — is entirely absent in production code.
- **Root key used for arbitrary attestations**: The root MPC key (the most sensitive key in the system) signs all foreign-chain attestations directly, rather than through caller-specific derivation. This contradicts the explicit design goal stated in `docs/foreign-chain-transactions.md` lines 254–286.
- **Bridge double-spend vector**: A bridge contract that uses `verify_foreign_transaction` to authorize minting (e.g., "mint NEAR tokens because Bitcoin tx X confirmed") cannot distinguish Alice's request from Bob's. An attacker who front-runs Alice's deposit by submitting the same `verify_foreign_transaction` request receives the same valid root-key signature and can use it to claim Alice's deposit before she does.

---

### Likelihood Explanation

**Likelihood: Medium.**

- Any unprivileged NEAR account can call `verify_foreign_transaction` with a deposit of 1 yoctoNEAR.
- The fan-out behavior (caller-agnostic request key) is confirmed by both unit tests and sandbox integration tests.
- The zero-tweak is hardcoded in production node code, not a test stub.
- The attack requires only observing a pending `verify_foreign_transaction` receipt on-chain (publicly visible) and submitting the same request args — no privileged access, no threshold collusion, no TEE bypass.
- The impact materializes as soon as any bridge contract is deployed that relies on `verify_foreign_transaction` for authorization, which is the stated primary use case.

---

### Recommendation

1. Add `derivation_path: String` to `VerifyForeignTransactionRequestArgs` and `tweak: Tweak` to `VerifyForeignTransactionRequest`, as specified in the design doc.
2. In `args_into_verify_foreign_tx_request` (or directly in `verify_foreign_transaction`), capture `env::predecessor_account_id()` and derive the tweak via a foreign-tx-specific prefix (e.g., `derive_foreign_tx_tweak(predecessor_id, derivation_path)`) to ensure key isolation from the `sign()` domain.
3. On the node side, replace `Tweak::new([0u8; 32])` in `build_signature_request` with the tweak stored in `VerifyForeignTxRequest`.
4. In `respond_verify_foreign_tx`, verify the signature against the **derived** public key (applying the tweak), not the root public key.
5. Include the tweak in the `VerifyForeignTransactionRequest` map key so that different callers' requests are stored separately.

---

### Proof of Concept

**Step 1 — Alice submits a `verify_foreign_transaction` for Bitcoin tx X:**
```
alice.near → mpc_contract.verify_foreign_transaction({
    request: BitcoinRpcRequest { tx_id: X, confirmations: 6, extractors: [BlockHash] },
    domain_id: foreign_tx_domain,
    payload_version: V1,
})
```

**Step 2 — Bob submits the identical request:**
```
bob.near → mpc_contract.verify_foreign_transaction({ same args })
```

Both are queued under the same `VerifyForeignTransactionRequest` key (no caller identity in the key). The contract's `pending_verify_foreign_tx_requests` map now has a queue of length 2 under one entry.

**Step 3 — MPC nodes respond:**
Nodes call `build_signature_request` with `tweak: Tweak::new([0u8; 32])` and produce a signature under the root key. `respond_verify_foreign_tx` verifies against the root public key and resolves both yields with the **same** `VerifyForeignTransactionResponse`.

**Step 4 — Both Alice and Bob hold an identical valid root-key attestation** for Bitcoin tx X. Bob can now present this attestation to any bridge contract to claim Alice's deposit, since the signature carries no binding to Alice's account.

The fan-out behavior is confirmed by the sandbox test at: [8](#0-7) 

and the zero-tweak root cause is at: [9](#0-8)

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L101-105)
```rust
pub struct VerifyForeignTransactionRequestArgs {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
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

**File:** crates/contract/src/lib.rs (L519-557)
```rust
    pub fn verify_foreign_transaction(&mut self, request: VerifyForeignTransactionRequestArgs) {
        log!(
            "verify_foreign_transaction: predecessor={:?}, request={:?}",
            env::predecessor_account_id(),
            request
        );

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
    }
```

**File:** crates/contract/src/lib.rs (L728-734)
```rust
                // Check the signature is correct against the root public key
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    &payload_hash,
                    &secp_pk,
                )
                .is_ok()
```

**File:** crates/contract/src/lib.rs (L3242-3263)
```rust
        // And: caller bob submits the identical request — a different account would today
        // be blocked from receiving a response by alice's submission.
        let bob = AccountId::from_str("bob.near").unwrap();
        testing_env!(
            VMContextBuilder::new()
                .signer_account_id(bob.clone())
                .predecessor_account_id(bob)
                .current_account_id(context.current_account_id.clone())
                .attached_deposit(NearToken::from_yoctonear(1))
                .build()
        );
        contract.verify_foreign_transaction(request_args);

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

**File:** crates/contract/tests/sandbox/foreign_chain_request.rs (L104-193)
```rust
#[tokio::test]
async fn verify_foreign_transaction__should_fan_out_response_to_duplicates_from_different_callers()
{
    // Given
    let rpc_request = bitcoin_request();
    let extracted_values = bitcoin_extracted_values();
    let chain = rpc_request.chain();
    let setup = SandboxTestSetup::builder()
        .with_foreign_tx_domain()
        .build()
        .await;
    let foreign_tx_key = setup.foreign_tx_key();
    register_foreign_chain_configuration(chain, &setup.contract, &setup.mpc_signer_accounts).await;

    let alice = setup.worker.dev_create_account().await.unwrap();
    let bob = setup.worker.dev_create_account().await.unwrap();
    let domain_id = dtos::DomainId(foreign_tx_key.domain_id().0);
    let request_args = dtos::VerifyForeignTransactionRequestArgs {
        domain_id,
        payload_version: ForeignTxPayloadVersion::V1,
        request: rpc_request.clone(),
    };
    let verify_request = VerifyForeignTransactionRequest {
        domain_id,
        payload_version: ForeignTxPayloadVersion::V1,
        request: rpc_request,
    };

    // When
    let status_alice = alice
        .call(
            setup.contract.id(),
            method_names::VERIFY_FOREIGN_TRANSACTION,
        )
        .args_json(json!({ "request": request_args }))
        .deposit(NearToken::from_yoctonear(1))
        .max_gas()
        .transact_async()
        .await
        .unwrap();
    let status_bob = bob
        .call(
            setup.contract.id(),
            method_names::VERIFY_FOREIGN_TRANSACTION,
        )
        .args_json(json!({ "request": request_args }))
        .deposit(NearToken::from_yoctonear(1))
        .max_gas()
        .transact_async()
        .await
        .unwrap();
    await_pending_foreign_tx_request_observed_on_contract(&setup.contract, &verify_request).await;

    let (payload, response) = sign_foreign_tx_response(
        &verify_request.request,
        extracted_values,
        foreign_tx_key.as_secp256k1(),
    );
    let respond_result = setup.mpc_signer_accounts[0]
        .call(setup.contract.id(), method_names::RESPOND_VERIFY_FOREIGN_TX)
        .args_json(json!({
            "request": verify_request,
            "response": response,
        }))
        .max_gas()
        .transact()
        .await
        .unwrap()
        .into_result();

    // Then
    assert!(
        respond_result.is_ok(),
        "single respond_verify_foreign_tx should drain both queued yields: {respond_result:?}",
    );
    let expected_payload_hash = payload.compute_msg_hash().unwrap();

    let exec_alice = status_alice.await.unwrap().into_result().unwrap();
    let returned_alice: VerifyForeignTransactionResponse = exec_alice.json().unwrap();
    assert_eq!(
        returned_alice.payload_hash, expected_payload_hash,
        "alice's tx should receive the fanned-out response",
    );

    let exec_bob = status_bob.await.unwrap().into_result().unwrap();
    let returned_bob: VerifyForeignTransactionResponse = exec_bob.json().unwrap();
    assert_eq!(
        returned_bob.payload_hash, expected_payload_hash,
        "bob's tx should receive the same fanned-out response and not be displaced by alice",
    );
```
