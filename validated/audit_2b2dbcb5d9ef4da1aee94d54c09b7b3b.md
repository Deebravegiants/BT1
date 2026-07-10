### Title
Caller-Agnostic `verify_foreign_transaction` Queue Key Allows Unprivileged Attacker to Saturate Per-Request Fan-Out Cap and Block Legitimate Bridge Verifications - (File: `crates/contract/src/pending_requests.rs`, `crates/contract/src/lib.rs`)

---

### Summary

The `pending_verify_foreign_tx_requests` map uses a `VerifyForeignTransactionRequest` key that contains no caller identity. Any unprivileged NEAR account can submit the same foreign-chain transaction verification request 128 times (the `MAX_PENDING_REQUEST_FAN_OUT` cap), saturating the fan-out queue for that specific request key. Once the queue is full, every subsequent legitimate caller attempting to verify the same foreign transaction receives `PendingRequestQueueFull` and is rejected. Because the attacker can immediately re-saturate the queue after each MPC response drains it, this enables a sustained, low-cost denial of the `verify_foreign_transaction` flow for any targeted foreign transaction.

---

### Finding Description

`MAX_PENDING_REQUEST_FAN_OUT` is set to 128 in `crates/contract/src/pending_requests.rs`. [1](#0-0) 

`push_pending_yield` enforces this cap and panics with `PendingRequestQueueFull` when it is reached: [2](#0-1) 

The queue key for `verify_foreign_transaction` is `VerifyForeignTransactionRequest`, which contains only `request`, `domain_id`, and `payload_version` — **no caller account ID**: [3](#0-2) 

This is in direct contrast to `sign()`, where `SignatureRequest::new` derives a `tweak` from `(predecessor_id, path)`, making each caller's queue key unique: [4](#0-3) 

The `verify_foreign_transaction` handler converts the user-supplied args into this caller-agnostic key and enqueues the yield: [5](#0-4) 

The codebase itself acknowledges this property in a test comment: *"a different account would today be blocked from receiving a response by alice's submission"* — both alice's and bob's yields land under the **single caller-agnostic request key**: [6](#0-5) 

**Attack flow:**

1. Attacker identifies a foreign-chain transaction `tx_id` that a bridge service (or victim) needs to verify via `verify_foreign_transaction`.
2. Attacker submits 128 `verify_foreign_transaction` calls with the identical `(request, domain_id, payload_version)` tuple, each attaching the required 1 yoctonear deposit.
3. The queue for that request key is now at `MAX_PENDING_REQUEST_FAN_OUT = 128`.
4. The victim's `verify_foreign_transaction` call panics with `PendingRequestQueueFull`.
5. MPC nodes eventually respond, draining all 128 attacker yields at once via `resolve_yields_for`.
6. Attacker immediately re-submits 128 calls, re-saturating the queue before the victim can retry.

The cost per saturation cycle is 128 transactions × (~7 TGas + 1 yoctonear). On NEAR, this is negligible.

---

### Impact Explanation

This breaks the **request-lifecycle** of `verify_foreign_transaction` without requiring network-level DoS or operator misconfiguration. Bridge services that rely on this endpoint to release cross-chain funds (e.g., confirming a Bitcoin or Ethereum deposit before minting wrapped tokens) can have specific transactions permanently stalled as long as the attacker maintains the queue saturation. The victim cannot bypass this by using a different account, because the queue key is caller-agnostic. This constitutes a **Medium** impact: contract execution-flow manipulation that breaks production safety/accounting invariants for the foreign-chain verification path.

---

### Likelihood Explanation

The attack requires no special privileges — any NEAR account can call `verify_foreign_transaction`. The cost is trivially low (128 cheap NEAR transactions per ~200-block cycle). The attacker only needs to know the target `tx_id` and `domain_id`, both of which are observable on-chain. A motivated attacker (e.g., a competing bridge, a front-runner, or a griever targeting a specific cross-chain settlement) can sustain this indefinitely.

---

### Recommendation

Include the caller's `predecessor_account_id` in the `VerifyForeignTransactionRequest` queue key, mirroring the approach used by `sign()` (which incorporates the caller via `derive_tweak(predecessor_id, path)`). This ensures each caller's yield occupies its own queue slot, making it impossible for one account to saturate another account's queue entry. Alternatively, enforce a per-account submission limit for the same foreign-tx request key.

---

### Proof of Concept

The existing unit test `verify_foreign_transaction__should_queue_duplicates_from_different_callers` already demonstrates the caller-agnostic queue behavior: alice and bob's submissions land under the same key. [7](#0-6) 

Extending this to a saturation attack requires only looping to 128 submissions:

```rust
// Attacker saturates the queue for a target foreign tx
for _ in 0..MAX_PENDING_REQUEST_FAN_OUT {
    // Each call from any account with the same request args
    contract.verify_foreign_transaction(target_request_args.clone());
}

// Victim's call now panics with PendingRequestQueueFull
let result = std::panic::catch_unwind(|| {
    contract.verify_foreign_transaction(target_request_args.clone());
});
assert!(result.is_err()); // "Pending-request queue is full"
```

The cap enforcement in `push_pending_yield` confirms the panic path: [2](#0-1)

### Citations

**File:** crates/contract/src/pending_requests.rs (L37-37)
```rust
pub const MAX_PENDING_REQUEST_FAN_OUT: u8 = 128;
```

**File:** crates/contract/src/pending_requests.rs (L50-58)
```rust
    let queue = requests.entry(request).or_default();
    if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
        env::panic_str(
            &RequestError::PendingRequestQueueFull {
                limit: MAX_PENDING_REQUEST_FAN_OUT,
            }
            .to_string(),
        );
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
