### Title
Caller-Agnostic `verify_foreign_transaction` Queue Key Enables Fan-Out Queue Saturation DoS — (`crates/contract/src/lib.rs`, `crates/contract/src/pending_requests.rs`)

---

### Summary

The `verify_foreign_transaction` request key is constructed without the caller's account ID, making it caller-agnostic. Combined with the hard cap of `MAX_PENDING_REQUEST_FAN_OUT = 128` slots per key, an unprivileged attacker can saturate the fan-out queue for any specific foreign-chain transaction request at a cost of 128 yoctonear, permanently blocking legitimate users from queuing that same request until each slot times out (~200 blocks). Because the primary use case is the Omnibridge inbound flow, this breaks the request-lifecycle invariant that any user can submit a valid bridge verification request.

---

### Finding Description

The `sign` request key is constructed by `SignatureRequest::new` and explicitly includes the caller's `predecessor` account ID: [1](#0-0) 

This means one user cannot fill another user's `sign` queue slot.

By contrast, `verify_foreign_transaction` converts its arguments via `args_into_verify_foreign_tx_request` and stores the result under a key that contains only `(domain_id, payload_version, ForeignChainRpcRequest)` — no caller identity: [2](#0-1) 

The contract's own unit test documents this explicitly: "both yields are queued under the single (caller-agnostic) request key": [3](#0-2) 

The fan-out queue for every request key is capped at `MAX_PENDING_REQUEST_FAN_OUT = 128`. When the cap is reached, `push_pending_yield` panics with `PendingRequestQueueFull`: [4](#0-3) 

Each `verify_foreign_transaction` call requires only a 1 yoctonear deposit: [5](#0-4) 

Slots are freed only when each individual yield times out (one slot per timeout callback via `pop_oldest_pending_yield`) or when a valid `respond_verify_foreign_tx` drains the entire queue: [6](#0-5) 

The NEAR yield-resume timeout is ~200 blocks (`REQUEST_EXPIRATION_BLOCKS = 200`): [7](#0-6) 

---

### Impact Explanation

**Medium — request-lifecycle manipulation that breaks production safety/accounting invariants.**

The primary production use case for `verify_foreign_transaction` is the Omnibridge inbound flow: a bridge service submits a request to attest that a specific foreign-chain transaction (e.g., a Bitcoin deposit tx) finalized, and the MPC network signs the attestation so the NEAR contract can release funds.

An attacker who front-runs a bridge service's submission with 128 identical requests for the same `(domain_id, payload_version, tx_id, extractors)` tuple saturates the queue. The bridge service's subsequent call panics with `PendingRequestQueueFull`. The attacker's 128 slots drain one-by-one over ~200 blocks each; the attacker can immediately re-fill after each drain. The bridge operation is indefinitely stalled. Funds on the foreign chain remain locked until the attacker stops or the bridge service uses a different request key (which is not possible — the tx_id is fixed).

This is not a network-level DoS: it is a contract-state manipulation that exploits the absence of caller identity in the queue key.

---

### Likelihood Explanation

**High.** The attack requires no special privileges, no collusion, and no cryptographic capability. The cost is 128 yoctonear per ~200-block window (effectively zero). The attacker only needs to observe the target `tx_id` from the mempool or a pending NEAR transaction before the legitimate caller's request lands. Front-running on NEAR is straightforward because transaction ordering within a block is deterministic and observable.

---

### Recommendation

Include the caller's `predecessor_account_id` in the `VerifyForeignTransactionRequest` key, mirroring the `sign` path. This makes each caller's queue slot independent, so an attacker cannot saturate another user's slot. The fan-out feature (multiple callers sharing one MPC computation for the same tx) can be preserved by keeping the caller-agnostic key for the MPC node's perspective while using a per-caller key for the contract's yield-resume map.

Alternatively, if caller-agnostic fan-out is intentional for bridge efficiency, enforce a per-account rate limit or require a meaningful deposit (slashable on timeout) to raise the cost of saturation.

---

### Proof of Concept

1. Bridge service prepares a `verify_foreign_transaction` call for Bitcoin tx_id `[0xAB; 32]`, domain 0, `ForeignTxPayloadVersion::V1`, extractor `BlockHash`.

2. Attacker observes the pending transaction and submits 128 identical calls with the same parameters, each with 1 yoctonear deposit. Total cost: 128 yoctonear ≈ $0.

3. The fan-out queue for key `(domain=0, v1, Bitcoin([0xAB;32]), BlockHash)` is now at capacity: [8](#0-7) 

4. The bridge service's call panics: `"Pending-request queue is full for this request key (limit: 128)"`.

5. The attacker's 128 slots time out one-by-one over ~200 blocks each. The attacker re-submits 128 calls immediately after each drain. The bridge operation is permanently stalled at a cost of ~128 yoctonear per ~200-block window. [9](#0-8)

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

**File:** crates/contract/src/pending_requests.rs (L97-112)
```rust
pub(crate) fn pop_oldest_pending_yield<K>(requests: &mut LookupMap<K, Vec<YieldIndex>>, request: &K)
where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let Some(queue) = requests.get_mut(request) else {
        return;
    };
    if queue.is_empty() {
        requests.remove(request);
        return;
    }
    queue.remove(0);
    if queue.is_empty() {
        requests.remove(request);
    }
}
```

**File:** crates/node/src/requests/queue.rs (L32-33)
```rust
/// This is equal to the yield-resume timeout on the blockchain.
pub const REQUEST_EXPIRATION_BLOCKS: NumBlocks = 200;
```
