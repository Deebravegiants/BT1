### Title
Caller-Agnostic `verify_foreign_transaction` Request Key Allows Queue Saturation, Blocking Legitimate Users — (File: `crates/contract/src/lib.rs`, `crates/contract/src/pending_requests.rs`)

---

### Summary

The `verify_foreign_transaction` endpoint uses a request key that does **not** include the caller's account ID. Any unprivileged NEAR account can flood the 128-slot fan-out queue for a specific foreign-chain transaction, causing every subsequent legitimate submission of that same request to be rejected with `PendingRequestQueueFull` until the queue drains via timeout (~200 blocks). The cost is 128 × 1 yoctonear — effectively free.

---

### Finding Description

`sign` and `request_app_private_key` both embed the caller's `predecessor` account ID into their request key, so each caller gets an independent queue slot: [1](#0-0) 

`verify_foreign_transaction` does **not** do this. It converts the raw args directly into a `VerifyForeignTransactionRequest` that contains only `domain_id`, `payload_version`, and the chain-specific RPC request — no caller identity: [2](#0-1) 

All callers who submit the same foreign-chain transaction share a single `LookupMap` entry in `pending_verify_foreign_tx_requests`: [3](#0-2) 

The fan-out queue is capped at `MAX_PENDING_REQUEST_FAN_OUT = 128`. Once that cap is reached, `push_pending_yield` panics and the transaction reverts: [4](#0-3) 

The contract's own test acknowledges this behavior explicitly: [5](#0-4) 

---

### Impact Explanation

An attacker who knows a target Bitcoin/EVM/Starknet transaction ID (all public on-chain) can submit 128 `verify_foreign_transaction` calls for that exact transaction at a cost of 128 yoctonear + gas. The queue is saturated. Every subsequent legitimate user who needs to verify that same transaction — for example, to release bridged funds on NEAR — receives `PendingRequestQueueFull` and their yield-resume promise is never created. The attacker can re-saturate the queue immediately after each ~200-block timeout window, creating a persistent block on any specific foreign-chain transaction verification. This breaks the request-lifecycle invariant that any user should be able to submit a valid foreign-chain verification request and receive a response.

**Allowed impact match:** Medium — request-lifecycle manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration.

---

### Likelihood Explanation

- **Attacker entry point:** Any unprivileged NEAR account; no special role required.
- **Cost:** 128 × 1 yoctonear ≈ free; gas is the only real cost.
- **Target information:** Foreign-chain transaction IDs are public.
- **Persistence:** The attacker can re-saturate the queue every ~200 blocks indefinitely.
- **Likelihood: High** — trivially executable by any NEAR account with negligible cost.

---

### Recommendation

Include the caller's `predecessor_account_id()` in the `VerifyForeignTransactionRequest` key, mirroring the pattern used by `sign` and `request_app_private_key`. This gives each caller an independent queue entry, eliminating cross-caller queue saturation. If caller-agnostic fan-out is intentional (so multiple callers waiting on the same tx share one MPC round), enforce a per-caller sub-limit or require a meaningful deposit that makes saturation economically infeasible.

---

### Proof of Concept

1. Alice has a Bitcoin transaction `tx_id = 0xABCD…` she needs verified to release bridged funds on NEAR.
2. Eve (attacker) submits `verify_foreign_transaction({ chain: Bitcoin, tx_id: 0xABCD…, … })` 128 times from a single NEAR account, paying 128 yoctonear total.
3. The `pending_verify_foreign_tx_requests` queue for that request key is now at `MAX_PENDING_REQUEST_FAN_OUT`.
4. Alice submits the same request — `push_pending_yield` panics with `PendingRequestQueueFull`; Alice's transaction reverts and she receives no yield-resume promise.
5. Eve repeats step 2 every ~200 blocks. Alice can never get her verification queued.

The caller-agnostic key construction is confirmed by the contract's own test `verify_foreign_transaction__should_queue_duplicates_from_different_callers`: [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L155-155)
```rust
    pending_verify_foreign_tx_requests: LookupMap<VerifyForeignTransactionRequest, Vec<YieldIndex>>,
```

**File:** crates/contract/src/lib.rs (L379-384)
```rust
        let request = SignatureRequest::new(
            request.domain_id,
            request.payload,
            &predecessor,
            &request.path,
        );
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

**File:** crates/contract/src/lib.rs (L3208-3263)
```rust
    #[test]
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

**File:** crates/contract/src/pending_requests.rs (L37-59)
```rust
pub const MAX_PENDING_REQUEST_FAN_OUT: u8 = 128;

/// Append a yield index to the pending-request fan-out queue for `request`.
///
/// Panics with `RequestError::PendingRequestQueueFull` if the resulting queue would
/// exceed `MAX_PENDING_REQUEST_FAN_OUT`.
pub(crate) fn push_pending_yield<K>(
    requests: &mut LookupMap<K, Vec<YieldIndex>>,
    request: K,
    data_id: CryptoHash,
) where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let queue = requests.entry(request).or_default();
    if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
        env::panic_str(
            &RequestError::PendingRequestQueueFull {
                limit: MAX_PENDING_REQUEST_FAN_OUT,
            }
            .to_string(),
        );
    }
    queue.push(YieldIndex { data_id });
```
