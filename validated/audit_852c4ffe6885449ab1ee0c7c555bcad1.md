### Title
Caller-Agnostic Queue Key in `verify_foreign_transaction` Allows Any Unprivileged Caller to Saturate the Fan-Out Queue and Block Legitimate Bridge Verifications - (File: `crates/contract/src/lib.rs`, `crates/contract/src/pending_requests.rs`)

---

### Summary

The `verify_foreign_transaction` endpoint uses a queue key (`VerifyForeignTransactionRequest`) that contains no caller identity. Any unprivileged account can submit 128 identical requests for a specific foreign-chain transaction, saturating the `MAX_PENDING_REQUEST_FAN_OUT` cap and causing all subsequent legitimate callers to receive `PendingRequestQueueFull` for that transaction. The attacker can sustain this indefinitely at near-zero cost (1 yoctoNEAR per slot), permanently blocking bridge inbound flows for targeted transactions.

---

### Finding Description

The contract maintains a bounded fan-out queue for each pending request type. The cap is defined in `crates/contract/src/pending_requests.rs`:

```rust
pub const MAX_PENDING_REQUEST_FAN_OUT: u8 = 128;
``` [1](#0-0) 

When the queue for a given key is full, `push_pending_yield` panics with `PendingRequestQueueFull`, rejecting any further submissions under that key until slots drain via timeout or a `respond*` call. [2](#0-1) 

The critical asymmetry is in how the queue key is constructed for each request type:

**`sign()` — caller-bound key**: `SignatureRequest` includes a `tweak` derived from `(predecessor_id, path)`, so each caller's requests are isolated under their own key. [3](#0-2) 

**`verify_foreign_transaction()` — caller-agnostic key**: `VerifyForeignTransactionRequest` contains only `{request: ForeignChainRpcRequest, domain_id, payload_version}` — no caller identity whatsoever. [4](#0-3) 

The `verify_foreign_transaction` handler converts the user's args into this caller-agnostic key and enqueues the yield: [5](#0-4) 

The existing unit test explicitly documents this behavior — alice and bob's requests land in the **same** queue slot, and the test comment acknowledges the blocking consequence:

> "a different account would today be blocked from receiving a response by alice's submission" [6](#0-5) 

An attacker who submits 128 requests for a specific `(tx_id, domain_id, payload_version)` tuple fills the queue entirely. Every subsequent legitimate caller for that same foreign transaction receives `PendingRequestQueueFull` and their transaction reverts. The attacker can continuously re-saturate the queue as slots drain via the 200-block yield timeout, sustaining the block indefinitely.

---

### Impact Explanation

The `verify_foreign_transaction` endpoint is the on-chain gateway for the Omnibridge inbound flow (foreign chain → NEAR). A bridge user who has already committed funds on a foreign chain (e.g., Bitcoin, Ethereum) depends on this call succeeding to receive their NEAR-side assets. An attacker who knows the target `tx_id` (which is public on the foreign chain) can:

1. Saturate the queue for that specific transaction before or immediately after the bridge service submits its verification.
2. Force all legitimate verification attempts to fail with `PendingRequestQueueFull`.
3. Sustain the attack at ~128 yoctoNEAR per 200-block cycle (essentially free), permanently blocking the bridge inbound settlement for that transaction.

This constitutes **request-lifecycle and contract execution-flow manipulation that breaks production safety/accounting invariants** — specifically, it prevents the bridge from completing a verified foreign-chain event that has already been committed on the foreign chain, which can result in effective loss of user funds.

**Impact: Medium** (request-lifecycle manipulation breaking production bridge accounting invariants, without requiring network-level DoS or operator misconfiguration).

---

### Likelihood Explanation

- The attacker is a fully unprivileged NEAR account; no special role or key is required.
- The target `tx_id` is publicly visible on the foreign chain.
- The cost is 128 × 1 yoctoNEAR ≈ 0 NEAR per attack cycle, plus negligible gas.
- The attack can be scripted to re-saturate the queue as slots expire (every ~200 blocks ≈ ~4 minutes on NEAR mainnet).
- No collusion, TEE bypass, or threshold compromise is required.

**Likelihood: High** — trivially executable by any NEAR account with knowledge of a pending bridge transaction.

---

### Recommendation

Include the caller's `predecessor_account_id` in the `VerifyForeignTransactionRequest` key, analogous to how `SignatureRequest` incorporates the caller-derived `tweak`. This isolates each caller's queue slot so that one account cannot saturate the queue for another caller's verification of the same foreign transaction.

Alternatively, enforce a per-account rate limit or per-account slot cap within the fan-out map for `verify_foreign_transaction`, ensuring that a single account can hold at most one (or a small bounded number of) queue slots per request key.

---

### Proof of Concept

The existing unit test at `crates/contract/src/lib.rs:3209` already demonstrates the root cause — two different callers (alice, bob) share the same queue entry under the caller-agnostic key: [7](#0-6) 

**Attack steps:**

1. Observe a target Bitcoin `tx_id` on-chain that a bridge service is about to verify via `verify_foreign_transaction`.
2. From an attacker-controlled NEAR account, submit 128 calls to `verify_foreign_transaction` with the identical `{tx_id, domain_id, payload_version}` arguments, each with 1 yoctoNEAR deposit.
3. The queue for `VerifyForeignTransactionRequest { request: Bitcoin(tx_id), domain_id, payload_version }` is now at `MAX_PENDING_REQUEST_FAN_OUT = 128`.
4. Any subsequent call from the legitimate bridge service or user returns `PendingRequestQueueFull` and reverts.
5. After ~200 blocks, the 128 attacker slots time out. Repeat from step 2 to sustain the block.

The `push_pending_yield` enforcement confirms the cap is hard and non-bypassable: [2](#0-1)

### Citations

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

**File:** crates/near-mpc-crypto-types/src/sign.rs (L111-125)
```rust
pub struct SignatureRequest {
    pub tweak: Tweak,
    pub payload: Payload,
    pub domain_id: DomainId,
}

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
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
