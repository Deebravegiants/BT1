### Title
No Completed-Verification State Recorded After Successful `respond_verify_foreign_tx` Enables Repeated Foreign-Transaction Signing — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `verify_foreign_transaction` / `respond_verify_foreign_tx` flow does not maintain any persistent record of completed verifications. After a successful `respond_verify_foreign_tx` removes the request from `pending_verify_foreign_tx_requests`, the same foreign transaction can be re-submitted via `verify_foreign_transaction` and re-signed by the MPC network indefinitely. This is the direct analog of `_userInfo.liquidated` never being set: the "done" flag is absent, so the operation can be repeated without limit.

---

### Finding Description

`verify_foreign_transaction` (lib.rs:519) enqueues a yield request and inserts the request key into `pending_verify_foreign_tx_requests`. [1](#0-0) 

When MPC nodes respond via `respond_verify_foreign_tx` (lib.rs:692–753), the function validates the signature and then calls `pending_requests::resolve_yields_for`, which **removes** the entry from `pending_verify_foreign_tx_requests` and resumes all queued yields. [2](#0-1) 

`resolve_yields_for` does exactly one thing after draining the queue: it returns `Ok(())`. No "completed" record is written anywhere. [3](#0-2) 

Because `verify_foreign_transaction` performs **no check against a completed-verifications set**, the same `VerifyForeignTransactionRequest` (same chain, same `tx_id`, same extractors, same `domain_id`) can be re-submitted the moment the first round finishes. The contract's only guard is the `MAX_PENDING_REQUEST_FAN_OUT` cap on *concurrent* duplicates; it does not prevent sequential re-submissions after completion. [4](#0-3) 

MPC nodes will observe the new pending request, re-query the foreign chain (the transaction is still finalized), and call `respond_verify_foreign_tx` again, producing a second cryptographically valid MPC signature over the same `payload_hash`.

The `VerifyForeignTransactionRequest` key is also **caller-agnostic** — different accounts submitting the same foreign-tx request share one queue entry and all receive the same response — so the re-submission can come from any account. [5](#0-4) 

---

### Impact Explanation

The design document explicitly states the primary use case is the **Omnibridge inbound flow**: a NEAR bridge contract releases funds upon receiving a valid MPC attestation that a foreign-chain deposit finalized. [6](#0-5) 

Each `VerifyForeignTransactionResponse` carries a `payload_hash` and a threshold signature over it, signed with the MPC root key. [7](#0-6) 

Because the MPC contract never records that a given foreign transaction was already attested, an attacker can obtain an unbounded number of valid attestations for a single foreign-chain deposit. Any bridge contract that does not independently deduplicate by `tx_id` will release funds for every attestation presented — a direct **double-spend** enabled by the missing state update. This matches the allowed High impact: *cross-chain replay / forged foreign-chain verification that causes invalid bridge execution or double-spend conditions*.

---

### Likelihood Explanation

- **Unprivileged entry**: any NEAR account can call `verify_foreign_transaction` with 1 yoctoNEAR deposit.
- **No collusion required**: honest MPC nodes re-verify and re-sign because the foreign transaction is genuinely finalized on the foreign chain.
- **Minimal cost**: 1 yoctoNEAR + gas per round, negligible relative to bridge fund values.
- **Bounded wait**: each round completes within ~200 blocks; the attacker simply re-submits after each completion.

---

### Recommendation

Add a persistent `completed_verify_foreign_tx_requests: LookupSet<VerifyForeignTransactionRequest>` to the contract state. In `respond_verify_foreign_tx`, after `resolve_yields_for` returns `Ok(())`, insert the request key into this set. In `verify_foreign_transaction`, check the set before enqueuing and reject with an appropriate error if the request is already present. This mirrors the pattern used for `_userInfo.liquidated = true` in the referenced report.

---

### Proof of Concept

1. Alice calls `verify_foreign_transaction({ chain: Bitcoin, tx_id: X, extractors: [BlockHash], domain_id: 0, payload_version: V1 })` with 1 yoctoNEAR.
2. MPC nodes verify Bitcoin tx X is finalized; `respond_verify_foreign_tx` is called → `resolve_yields_for` removes the key from `pending_verify_foreign_tx_requests`; Alice receives `VerifyForeignTransactionResponse { payload_hash: H, signature: S1 }`. [8](#0-7) 
3. Alice immediately calls `verify_foreign_transaction` again with identical arguments. No guard exists — `pending_verify_foreign_tx_requests` no longer contains the key, and there is no completed-set — so the request is enqueued as a fresh pending entry. [1](#0-0) 
4. MPC nodes re-verify Bitcoin tx X (still finalized); `respond_verify_foreign_tx` is called again → Alice receives `VerifyForeignTransactionResponse { payload_hash: H, signature: S2 }`.
5. Alice submits S1 to the Omnibridge NEAR contract → receives bridged funds.
6. Alice submits S2 to the Omnibridge NEAR contract → receives bridged funds a second time (if the bridge contract does not independently deduplicate by `tx_id`).
7. Steps 3–6 repeat indefinitely.

### Citations

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

**File:** crates/contract/src/lib.rs (L646-651)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_signature_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
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

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/contract/src/lib.rs (L3209-3263)
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
```

**File:** crates/contract/src/pending_requests.rs (L24-37)
```rust
/// Maximum number of concurrent yield-resume promises that can be queued for a single
/// request key (i.e. the number of duplicate submissions whose responses fan out from
/// one MPC reply).
///
/// The ceiling is needed because `respond*` drains the entire queue in one call: every
/// queued yield triggers a host-side `promise_yield_resume`, paid for out of the
/// responder's 300 TGas budget. Without a cap, an attacker could enqueue enough
/// duplicates to make `respond*` run out of gas and strand every queued caller.
///
/// 128 is validated empirically by the sandbox test
/// `test_contract_request_duplicate_requests_fan_out`, which fills the queue to this
/// cap across all four signature schemes and confirms `respond*` drains it inside its
/// 300 TGas budget.
pub const MAX_PENDING_REQUEST_FAN_OUT: u8 = 128;
```

**File:** crates/contract/src/pending_requests.rs (L66-88)
```rust
pub(crate) fn resolve_yields_for<K>(
    requests: &mut LookupMap<K, Vec<YieldIndex>>,
    request: &K,
    response_bytes: Vec<u8>,
) -> Result<(), Error>
where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let resumed = requests
        .remove(request)
        .unwrap_or_default()
        .into_iter()
        .map(|YieldIndex { data_id }| {
            env::promise_yield_resume(&data_id, response_bytes.clone());
        })
        .count();

    if resumed > 0 {
        Ok(())
    } else {
        Err(InvalidParameters::RequestNotFound.into())
    }
}
```

**File:** docs/foreign-chain-transactions.md (L7-10)
```markdown
This feature lets the MPC network sign payloads only after verifying a specific foreign-chain transaction, so NEAR contracts can react to external chain events without a trusted relayer. Primary use cases:

* Omnibridge inbound flow (foreign chain -> NEAR) where Chain Signatures are required to attest that a foreign transaction finalized successfully.
* Broader chain abstraction: a single MPC network verifies foreign chain state and returns small, typed observations that contracts can interpret.
```
