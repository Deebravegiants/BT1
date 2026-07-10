### Title
Caller-Agnostic `ForeignTxSignPayload` Enables Front-Running and Cross-Chain Replay of Foreign Transaction Attestations - (File: `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`, `crates/contract/src/dto_mapping.rs`, `crates/node/src/providers/verify_foreign_tx/sign.rs`)

---

### Summary

The MPC network's signed attestation for foreign chain transaction verification (`ForeignTxSignPayload`) contains no caller identity (NEAR account ID) and no nonce. The pending-request map key (`VerifyForeignTransactionRequest`) is also caller-agnostic. Any unprivileged NEAR account can submit an identical `verify_foreign_transaction` request and receive the same MPC-signed `VerifyForeignTransactionResponse` as the original requester. The resulting attestation is globally replayable: it can be presented to any bridge contract that accepts it, enabling front-running and double-spend conditions.

---

### Finding Description

**Root cause 1 — Signed payload carries no caller identity.**

`ForeignTxSignPayloadV1` contains only the chain query and extracted values:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```

The 32-byte `msg_hash` the MPC network signs is `SHA-256(borsh(ForeignTxSignPayload))`. No NEAR account ID, no nonce, no per-request unique binding is included. [1](#0-0) 

**Root cause 2 — Zero tweak: signing uses the root key, not a caller-derived key.**

`build_signature_request` hard-codes `Tweak::new([0u8; 32])`. Unlike the regular `sign()` flow — where the tweak is `SHA3-256(prefix || predecessor_id || path)` — the foreign-tx flow signs with the undifferentiated root key:

```rust
Ok(SignatureRequest {
    ...
    tweak: Tweak::new([0u8; 32]),   // ← zero tweak, root key
    ...
})
``` [2](#0-1) 

`respond_verify_foreign_tx` verifies the signature against `self.public_key_extended(domain)` — the root public key — confirming the signature is not caller-scoped. [3](#0-2) 

**Root cause 3 — Pending-request map key is caller-agnostic.**

`args_into_verify_foreign_tx_request` drops `env::predecessor_account_id()` entirely when building the map key:

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
``` [4](#0-3) 

`VerifyForeignTransactionRequest` has no `predecessor_id` field: [5](#0-4) 

**Root cause 4 — Fan-out is explicitly supported across different callers.**

The contract intentionally queues all callers who submit the same `(chain_request, domain_id, payload_version)` tuple under one map entry and drains all of them with a single `respond_verify_foreign_tx` call. This is confirmed by the production test:

> "duplicate foreign-tx requests from different callers should fan out" [6](#0-5) 

The sandbox integration test also confirms that Alice and Bob both receive the identical `VerifyForeignTransactionResponse`: [7](#0-6) 

---

### Impact Explanation

**Impact: High — Cross-chain replay / double-spend enabling invalid bridge execution.**

The `VerifyForeignTransactionResponse` (`payload_hash` + `signature`) is a globally valid, replayable attestation. Because the signed payload contains no caller identity and no nonce, the same `(payload_hash, signature)` pair is cryptographically valid for any NEAR account and any downstream contract.

**Concrete double-spend scenario (bridge inbound flow):**

1. Alice sends Bitcoin to a bridge address and submits `verify_foreign_transaction(bitcoin_tx_id=X)` to claim bridged tokens.
2. Bob observes Alice's confirmed on-chain call (public NEAR data) and immediately submits an identical `verify_foreign_transaction(bitcoin_tx_id=X)` request.
3. Both requests are queued under the same caller-agnostic key.
4. MPC nodes verify Bitcoin tx X and submit `respond_verify_foreign_tx`. The single response drains both yields.
5. Both Alice and Bob receive the identical `VerifyForeignTransactionResponse`.
6. Bob presents his copy to the bridge contract and claims the bridged tokens before or alongside Alice — double-spend.

Additionally, any party who obtains a `VerifyForeignTransactionResponse` from on-chain history can replay it to any contract that accepts such attestations, with no expiry or binding to a specific beneficiary.

---

### Likelihood Explanation

**Likelihood: High.**

- The attack requires only a standard NEAR account and the ability to read on-chain transactions — no privileged access, no key material, no TEE bypass.
- The fan-out behavior is explicitly implemented and tested as a feature, meaning the contract actively delivers the same response to any caller who races in.
- Foreign chain transaction IDs are public (Bitcoin, Ethereum, etc.), so an attacker does not need to observe Alice's NEAR transaction first — they can submit the same request speculatively for any foreign tx they wish to front-run.
- No nonce, no expiry, and no caller binding exist anywhere in the signed payload or the response.

---

### Recommendation

1. **Include the caller's NEAR account ID in `ForeignTxSignPayload`.** Add `predecessor_id: AccountId` to `ForeignTxSignPayloadV1` so the MPC signature cryptographically binds the attestation to the requesting account. This is the direct analog of the NFT auction fix (adding a nonce to the signed data).

2. **Include the caller's account ID in `VerifyForeignTransactionRequest`** (the pending-request map key) so that requests from different callers are stored and resolved independently, preventing the fan-out delivery of the same attestation to unrelated parties.

3. **Use a caller-derived tweak** (as `sign()` does via `derive_tweak(predecessor_id, path)`) instead of the zero tweak, so the MPC signature is produced under a key that is cryptographically scoped to the requesting account.

4. **Add a nonce or unique request ID** to `ForeignTxSignPayload` to prevent replay of a valid attestation across different bridge contracts or invocations.

---

### Proof of Concept

**Step 1.** Alice submits:
```
verify_foreign_transaction({ request: Bitcoin(tx_id=X, ...), domain_id: 0, payload_version: V1 })
```
This is confirmed on-chain and visible to all observers.

**Step 2.** Bob (attacker) immediately submits the identical call from his own account. Both are queued under the same `VerifyForeignTransactionRequest` key (no caller field). [8](#0-7) 

**Step 3.** MPC nodes verify Bitcoin tx X. `build_signature_request` constructs a `SignatureRequest` with `tweak = [0u8; 32]` and `payload = SHA-256(borsh(ForeignTxSignPayloadV1{request: Bitcoin(X), values: [BlockHash(H)]}))`. [9](#0-8) 

**Step 4.** An MPC node calls `respond_verify_foreign_tx(request, response)`. The contract verifies the signature against the root public key and calls `resolve_yields_for`, which drains **all** queued yields — Alice's and Bob's — with the identical `VerifyForeignTransactionResponse`. [10](#0-9) 

**Step 5.** Both Alice and Bob receive `VerifyForeignTransactionResponse { payload_hash: H, signature: σ }`. Bob presents his copy to the bridge contract. Since `σ` is a valid MPC root-key signature over `H = SHA-256(borsh(ForeignTxSignPayloadV1{Bitcoin(X), [BlockHash(H)]}))` and the payload contains no caller identity, the bridge contract cannot distinguish Bob's attestation from Alice's. Bob claims the bridged tokens — double-spend achieved.

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1509)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}

impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-48)
```rust
fn build_signature_request(
    request: &VerifyForeignTxRequest,
    foreign_tx_payload: &dtos::ForeignTxSignPayload,
) -> anyhow::Result<SignatureRequest> {
    let payload_hash: [u8; ECDSA_PAYLOAD_SIZE_BYTES] =
        foreign_tx_payload.compute_msg_hash()?.into();
    let payload_bytes: BoundedVec<u8, ECDSA_PAYLOAD_SIZE_BYTES, ECDSA_PAYLOAD_SIZE_BYTES> =
        payload_hash.into();

    Ok(SignatureRequest {
        id: request.id,
        receipt_id: request.receipt_id,
        payload: Payload::Ecdsa(payload_bytes),
        tweak: Tweak::new([0u8; 32]),
        entropy: request.entropy,
        timestamp_nanosec: request.timestamp_nanosec,
        domain: request.domain_id,
    })
}
```

**File:** crates/contract/src/lib.rs (L549-556)
```rust
        let request = args_into_verify_foreign_tx_request(request);
        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_VERIFY_FOREIGN_TX_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_verify_foreign_tx_request(request, id),
        );
```

**File:** crates/contract/src/lib.rs (L715-734)
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
```

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
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

**File:** crates/contract/tests/sandbox/foreign_chain_request.rs (L104-194)
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
}
```
