### Title
Caller-Agnostic `verify_foreign_transaction` Queue Key Enables Targeted DoS on Foreign-Chain Verification Requests - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `verify_foreign_transaction` function stores pending requests under a caller-agnostic key (`VerifyForeignTransactionRequest` contains no caller account ID). Any unprivileged caller can saturate the 128-entry fan-out queue for a specific foreign transaction, permanently blocking legitimate bridge callers from submitting the same request until the queue drains.

---

### Finding Description

`SignatureRequest` binds the caller's identity into its map key via a `tweak` field derived from `(predecessor_id, path)`:

```rust
// crates/near-mpc-crypto-types/src/sign.rs:118-125
pub fn new(domain: DomainId, payload: Payload, predecessor_id: &AccountId, path: &str) -> Self {
    let tweak = crate::kdf::derive_tweak(predecessor_id, path);
    SignatureRequest { domain_id: domain, tweak, payload }
}
```

`VerifyForeignTransactionRequest`, by contrast, contains no caller field at all:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs:124-128
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

The conversion function `args_into_verify_foreign_tx_request` simply copies the three fields and discards `env::predecessor_account_id()`:

```rust
// crates/contract/src/dto_mapping.rs:840-848
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

This caller-agnostic key is then used as the map key in `pending_verify_foreign_tx_requests`, which is bounded by `MAX_PENDING_REQUEST_FAN_OUT = 128`:

```rust
// crates/contract/src/pending_requests.rs:51-58
if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
    env::panic_str(
        &RequestError::PendingRequestQueueFull { limit: MAX_PENDING_REQUEST_FAN_OUT }.to_string(),
    );
}
```

The codebase itself acknowledges the caller-agnostic behavior in a unit test comment:

> "a different account would today be blocked from receiving a response by alice's submission"

and confirms both callers share one queue entry:

```rust
// crates/contract/src/lib.rs:3255-3263
// Then: both yields are queued under the single (caller-agnostic) request key.
assert_eq!(
    contract.pending_verify_foreign_tx_requests.get(&request).map(|q| q.len()),
    Some(2),
    "duplicate foreign-tx requests from different callers should fan out",
);
```

**Attack steps:**

1. Attacker monitors the foreign chain (e.g., Bitcoin mempool) for a pending bridge deposit transaction that a bridge service will soon submit to `verify_foreign_transaction`.
2. Attacker front-runs by submitting 128 identical `verify_foreign_transaction` calls for the same `(tx_id, domain_id, payload_version)` tuple, each with the required 1 yoctonear deposit.
3. The queue for that request key is now at `MAX_PENDING_REQUEST_FAN_OUT`; the bridge service's subsequent call panics with `PendingRequestQueueFull`.
4. When MPC nodes respond and drain the queue, the attacker immediately re-fills it with another 128 submissions, sustaining the DoS indefinitely.

---

### Impact Explanation

Bridge services that rely on `verify_foreign_transaction` to obtain MPC-signed attestations of foreign-chain events (e.g., to release NEAR-side funds) are blocked from submitting their requests. The bridge's request-lifecycle invariant is broken: a valid, well-formed request from a legitimate caller is rejected not because of any fault of its own, but because an adversary saturated the shared queue. Funds awaiting cross-chain confirmation are temporarily frozen for as long as the attacker sustains the queue saturation.

---

### Likelihood Explanation

The cost is trivially low: 128 × 1 yoctonear + gas per cycle. The target transaction is publicly observable on the foreign chain before the bridge service submits it. No privileged access, threshold collusion, or TEE compromise is required — any NEAR account can call `verify_foreign_transaction`. The attack can be automated and sustained indefinitely.

---

### Recommendation

Include the caller's account ID in the `VerifyForeignTransactionRequest` key, mirroring the `sign` flow where `predecessor_id` is hashed into the `tweak`. Concretely, `args_into_verify_foreign_tx_request` should accept `predecessor_id: &AccountId` and embed it (or a hash of it) into the returned struct, so each caller's request occupies its own queue entry and an adversary cannot exhaust another caller's slot budget.

---

### Proof of Concept

The existing unit test `verify_foreign_transaction__should_queue_duplicates_from_different_callers` (crates/contract/src/lib.rs:3208–3298) already demonstrates the shared-queue behavior. Extending it to 128 attacker submissions before the victim's call reproduces the `PendingRequestQueueFull` panic:

```rust
// Attacker fills the queue to the cap
for _ in 0..MAX_PENDING_REQUEST_FAN_OUT {
    testing_env!(/* attacker context */);
    contract.verify_foreign_transaction(request_args.clone()); // succeeds
}

// Victim's legitimate call now panics
testing_env!(/* victim context */);
contract.verify_foreign_transaction(request_args.clone()); // panics: PendingRequestQueueFull
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

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
