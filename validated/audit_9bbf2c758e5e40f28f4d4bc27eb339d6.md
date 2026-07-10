### Title
Caller-Agnostic `VerifyForeignTransactionRequest` Key Enables Cross-Caller MPC Signature Sharing — (File: `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`)

---

### Summary

`verify_foreign_transaction()` uses a `VerifyForeignTransactionRequest` struct as its pending-request map key that contains no caller identity. Unlike `sign()`, which folds the caller's `predecessor_account_id` into the key via `derive_tweak`, the foreign-tx path omits the caller entirely. Any NEAR account that submits an identical `(request, domain_id, payload_version)` tuple is queued under the same map entry and receives the same MPC signature. This makes the produced attestation caller-agnostic, enabling a malicious actor to obtain a valid MPC signature for a foreign-chain transaction they did not initiate and use it to claim funds in a bridge contract before the legitimate user can.

---

### Finding Description

`VerifyForeignTransactionRequest`, the struct used as the map key in `pending_verify_foreign_tx_requests`, is defined as:

```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
``` [1](#0-0) 

There is no `predecessor_account_id` or caller-derived tweak field. Compare this to `SignatureRequest::new()`, which explicitly calls `derive_tweak(&predecessor, &path)` to bind the key to the caller.

Inside `verify_foreign_transaction()`, the predecessor is logged but never incorporated into the request key:

```rust
pub fn verify_foreign_transaction(&mut self, request: VerifyForeignTransactionRequestArgs) {
    log!("verify_foreign_transaction: predecessor={:?}, ...", env::predecessor_account_id(), ...);
    ...
    let request = args_into_verify_foreign_tx_request(request);  // caller dropped here
    ...
    move |this, id| this.add_verify_foreign_tx_request(request, id),
``` [2](#0-1) 

The node-side signing path compounds this: `build_signature_request` uses a **zero tweak** (`Tweak::new([0u8; 32])`), meaning the MPC network always signs with the root ForeignTx domain key regardless of who called the contract: [3](#0-2) 

The signed payload (`ForeignTxSignPayload::V1 { request, values }`) contains only the foreign-chain RPC request and extracted values — no caller identity. The resulting signature is therefore a global, reusable attestation.

The codebase itself acknowledges the cross-caller collision in a unit test comment:

> "caller bob submits the identical request — **a different account would today be blocked from receiving a response by alice's submission**." [4](#0-3) 

The fan-out feature introduced to address the blocking behavior now causes both callers to receive the **same** MPC signature, which is the root of the security issue.

---

### Impact Explanation

The MPC signature returned by `verify_foreign_transaction` is a threshold-signed attestation that a specific foreign-chain transaction occurred with specific extracted values. Because the signature is not bound to any caller, any NEAR account that submits the same `(tx_id, chain, extractors, domain_id)` tuple — before or concurrently with the legitimate user — receives an identical, valid MPC signature.

A bridge contract that accepts this signature as authorization to release funds (e.g., "prove you sent 1 ETH on Ethereum, receive 1 NEAR-ETH") and does not independently verify that the claimer is the intended recipient is vulnerable to fund theft. The attacker presents the stolen signature first, drains the bridge payout, and the legitimate user's claim fails.

This matches: **High — cross-chain replay / forged foreign-chain verification that causes invalid bridge execution or double-spend conditions.**

---

### Likelihood Explanation

- The attack requires no privileged access, no threshold collusion, and no key material — only the ability to submit a NEAR transaction with a 1 yoctonear deposit.
- The attacker can observe the victim's `verify_foreign_transaction` call in the NEAR transaction pool and submit an identical call before the MPC nodes respond (a window of several seconds to minutes depending on MPC signing latency).
- Bridge contracts that rely on the MPC attestation as the sole authorization signal are a realistic deployment target; the NEAR MPC SDK (`crates/near-mpc-sdk`) provides `ForeignChainSignatureVerifier` helpers that verify the signature but do not enforce caller binding.
- Likelihood: **Medium** — requires a bridge contract that does not independently enforce caller-to-recipient binding, but such contracts are the primary intended consumers of this API.

---

### Recommendation

1. **Include the caller's identity in `VerifyForeignTransactionRequest`**: Add `predecessor_account_id: AccountId` (or a caller-derived tweak) to the struct and to the signed payload, mirroring the `sign()` path's use of `derive_tweak(&predecessor, &path)`.
2. **Bind the MPC signature to the caller**: The `ForeignTxSignPayload` should commit to the caller's account ID so that a signature obtained by one account cannot be replayed by another.
3. **SDK guidance**: Document in `near-mpc-sdk` that `VerifyForeignTransactionResponse` signatures are currently caller-agnostic and that bridge contracts must independently verify caller authorization until the above fix is deployed.

---

### Proof of Concept

```
1. Alice calls verify_foreign_transaction({ request: Bitcoin(tx_id=X, ...), domain_id: 0, payload_version: V1 })
   on the MPC contract, attaching 1 yoctonear.

2. Bob observes Alice's NEAR transaction in the mempool and submits an identical call.

3. The contract queues both under the same VerifyForeignTransactionRequest key
   (no caller field → same key for Alice and Bob).

4. MPC nodes sign ForeignTxSignPayload::V1 { request: Bitcoin(tx_id=X,...), values: [BlockHash(H)] }
   with tweak=[0u8;32] (root ForeignTx key). One respond_verify_foreign_tx() call drains both yields.

5. Both Alice and Bob receive VerifyForeignTransactionResponse { payload_hash: H, signature: S }.

6. Bob calls the bridge contract with (tx_id=X, signature=S) before Alice.
   The bridge contract verifies S against the MPC public key, confirms tx_id=X is valid,
   and releases 1 BTC-equivalent to Bob.

7. Alice's subsequent claim is rejected: the bridge contract has already processed tx_id=X.
```

The contract-level evidence is the unit test `verify_foreign_transaction__should_queue_duplicates_from_different_callers` which explicitly demonstrates that Alice and Bob receive the same response under the same map key: [5](#0-4)

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
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

**File:** crates/contract/src/lib.rs (L3209-3298)
```rust
    fn verify_foreign_transaction__should_queue_duplicates_from_different_callers() {
        // Given: two different callers will submit the same foreign-tx verification request.
        let mut rng = rand::rngs::StdRng::from_seed([42u8; 32]);
        let (context, mut contract, secret_key) =
            basic_setup_with_protocol(Protocol::CaitSith, DomainPurpose::ForeignTx, &mut rng);
        register_supported_chains(&mut contract, [dtos::ForeignChain::Bitcoin]);
        let SharedSecretKey::Secp256k1(secret_key) = secret_key else {
            unreachable!();
        };

        let request_args = VerifyForeignTransactionRequestArgs {
            domain_id: DomainId::default().0.into(),
            payload_version: ForeignTxPayloadVersion::V1,
            request: dtos::ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest {
                tx_id: [7u8; 32].into(),
                confirmations: 2.into(),
                extractors: vec![BitcoinExtractor::BlockHash],
            }),
        };
        let request = args_into_verify_foreign_tx_request(request_args.clone());

        // When: caller alice submits the request.
        let alice = AccountId::from_str("alice.near").unwrap();
        testing_env!(
            VMContextBuilder::new()
                .signer_account_id(alice.clone())
                .predecessor_account_id(alice)
                .current_account_id(context.current_account_id.clone())
                .attached_deposit(NearToken::from_yoctonear(1))
                .build()
        );
        contract.verify_foreign_transaction(request_args.clone());

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

        // When: a single valid response is delivered.
        let payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
            request: request.request.clone(),
            values: vec![ExtractedValue::BitcoinExtractedValue(
                BitcoinExtractedValue::BlockHash([42u8; 32].into()),
            )],
        });
        let payload_hash_arr = payload.compute_msg_hash().unwrap().0;
        let secret_key_ec: elliptic_curve::SecretKey<Secp256k1> =
            elliptic_curve::SecretKey::from_bytes(&secret_key.to_bytes()).unwrap();
        let signing_key = SigningKey::from_bytes(&secret_key_ec.to_bytes()).unwrap();
        let (signature, recovery_id) = signing_key
            .sign_prehash_recoverable(&payload_hash_arr)
            .unwrap();
        let response = VerifyForeignTransactionResponse {
            payload_hash: payload.compute_msg_hash().unwrap(),
            signature: dtos::SignatureResponse::Secp256k1(
                dtos::K256Signature::from_ecdsa_recoverable(&signature, recovery_id),
            ),
        };

        with_active_participant_and_attested_context(&contract);
        contract
            .respond_verify_foreign_tx(request.clone(), response)
            .expect("respond_verify_foreign_tx should succeed");

        // Then: both queued yields are drained from the single map entry.
        assert!(
            contract
                .pending_verify_foreign_tx_requests
                .get(&request)
                .is_none()
        );
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
