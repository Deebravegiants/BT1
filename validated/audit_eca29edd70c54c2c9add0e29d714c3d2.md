### Title
Caller-Agnostic `verify_foreign_transaction` Queue Pre-Saturation Permanently Blocks Specific Foreign Transaction Verification - (File: `crates/contract/src/pending_requests.rs`, `crates/contract/src/lib.rs`)

---

### Summary

The `pending_verify_foreign_tx_requests` map uses a **caller-agnostic** key (`VerifyForeignTransactionRequest` = `{request, domain_id, payload_version}` — no predecessor/caller field). Any unprivileged account can pre-fill the 128-slot fan-out queue for any known foreign transaction ID before a legitimate bridge service submits its own request. Once the queue is saturated, every subsequent `verify_foreign_transaction` call for that transaction panics with `PendingRequestQueueFull`, permanently blocking the bridge inbound flow for that transaction at a cost of 128 yoctoNEAR per timeout cycle.

---

### Finding Description

`MpcContract::verify_foreign_transaction` converts the caller's `VerifyForeignTransactionRequestArgs` into a `VerifyForeignTransactionRequest` via `args_into_verify_foreign_tx_request`, which strips the caller identity entirely:

```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
    // ← no predecessor / caller field
}
``` [1](#0-0) 

This is in direct contrast to `sign()`, which folds the caller's account ID into the key via `derive_tweak(predecessor_id, path)`, making each user's queue private:

```rust
let request = SignatureRequest::new(
    request.domain_id,
    request.payload,
    &predecessor,   // ← caller is part of the key
    &request.path,
);
``` [2](#0-1) 

The fan-out queue is capped at `MAX_PENDING_REQUEST_FAN_OUT = 128`. `push_pending_yield` panics when the cap is reached:

```rust
if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
    env::panic_str(
        &RequestError::PendingRequestQueueFull { limit: MAX_PENDING_REQUEST_FAN_OUT }.to_string(),
    );
}
``` [3](#0-2) 

The codebase itself acknowledges the caller-agnostic nature in a test comment: *"a different account would today be blocked from receiving a response by alice's submission"*: [4](#0-3) 

---

### Impact Explanation

Foreign transaction IDs (Bitcoin `tx_id`, EVM `tx_id`, etc.) are publicly visible on-chain the moment a transaction is broadcast. An attacker monitoring a bridge's inbound flow can:

1. Observe a foreign-chain transaction that a bridge service will need to verify.
2. Submit 128 `verify_foreign_transaction` calls for that exact `(tx_id, domain_id, payload_version)` from 128 cheap accounts (or the same account 128 times).
3. The queue for that request key is now full.
4. When the bridge service submits its own `verify_foreign_transaction`, the contract panics with `PendingRequestQueueFull` and the transaction reverts.
5. The bridge cannot obtain the MPC-signed attestation needed to release funds on NEAR.

Each attacker slot times out via the NEAR yield-resume mechanism (calling `pop_oldest_pending_yield`), but the attacker can continuously re-submit at 128 yoctoNEAR per cycle — essentially free — to maintain the blockade indefinitely.

This breaks the request-lifecycle invariant: a legitimate caller with a valid foreign transaction and correct deposit cannot obtain service. In a bridge context, this freezes inbound user funds.

**Impact class:** Medium — request-lifecycle manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration. [5](#0-4) 

---

### Likelihood Explanation

- Foreign transaction IDs are fully public and predictable from the moment a transaction is broadcast on the foreign chain.
- The attack requires only 128 yoctoNEAR (≈ $0) per timeout window.
- No privileged access, no threshold collusion, no TEE bypass required.
- Any NEAR account can call `verify_foreign_transaction`.
- The attacker can automate re-filling the queue to sustain the blockade indefinitely.

---

### Recommendation

Include the caller's `predecessor_account_id` in the `VerifyForeignTransactionRequest` key, mirroring the approach used by `sign()` and `request_app_private_key`. This makes each caller's queue slot private and prevents cross-caller queue saturation:

```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
    pub predecessor: AccountId,  // ← add caller identity
}
```

`args_into_verify_foreign_tx_request` should populate this field from `env::predecessor_account_id()`. The fan-out deduplication feature (multiple callers sharing one MPC computation) can be preserved at the node layer without exposing the on-chain queue to cross-caller saturation. [6](#0-5) 

---

### Proof of Concept

```
// Attacker observes Bitcoin tx_id = [0xAB; 32] about to be submitted by a bridge.
// Attacker submits 128 verify_foreign_transaction calls from 128 accounts:
for i in 0..128 {
    attacker_account_i.call(mpc_contract, "verify_foreign_transaction")
        .args_json({"request": {
            "request": {"Bitcoin": {"tx_id": "0xABAB...AB", "confirmations": 2, "extractors": ["BlockHash"]}},
            "domain_id": 0,
            "payload_version": 1
        }})
        .deposit(1)  // 1 yoctoNEAR
        .transact();
}

// Queue for (Bitcoin tx_id=0xAB..., domain_id=0, V1) is now at 128/128.

// Bridge service submits its legitimate request:
bridge.call(mpc_contract, "verify_foreign_transaction")
    .args_json({...same request...})
    .deposit(1)
    .transact();
// → PANICS: "Pending-request queue is full (limit: 128)"
// Bridge cannot obtain MPC attestation; inbound funds are frozen.
``` [7](#0-6) [8](#0-7)

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
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

**File:** crates/contract/src/lib.rs (L3242-3243)
```rust
        // And: caller bob submits the identical request — a different account would today
        // be blocked from receiving a response by alice's submission.
```

**File:** crates/contract/src/lib.rs (L3300-3344)
```rust
    #[test]
    fn add_signature_request__should_panic_when_pending_queue_is_full() {
        // Given: a contract with a queue already at the fan-out cap for some request key.
        let (context, mut contract, _) = basic_setup(Curve::Secp256k1, &mut OsRng);
        let signature_request = SignatureRequest::new(
            DomainId::default(),
            Payload::from_legacy_ecdsa([3u8; 32]),
            &context.predecessor_account_id,
            "m/44'\''/60'\''/0'\''/0/0",
        );
        for i in 0..MAX_PENDING_REQUEST_FAN_OUT {
            contract.add_signature_request(signature_request.clone(), [i; 32]);
        }
        assert_eq!(
            contract
                .pending_signature_requests
                .get(&signature_request)
                .map(|q| q.len()),
            Some(usize::from(MAX_PENDING_REQUEST_FAN_OUT)),
        );

        // When: one more append is attempted.
        let result = panic::catch_unwind(panic::AssertUnwindSafe(|| {
            contract.add_signature_request(signature_request.clone(), [0xff; 32]);
        }));

        // Then: it panics with the typed cap-exceeded error and leaves the queue untouched.
        let err = result.expect_err("appending past the cap should panic");
        let msg = err
            .downcast_ref::<String>()
            .map(String::as_str)
            .or_else(|| err.downcast_ref::<&str>().copied())
            .unwrap_or_default();
        assert!(
            msg.contains("Pending-request queue is full"),
            "unexpected panic message: {msg}",
        );
        assert_eq!(
            contract
                .pending_signature_requests
                .get(&signature_request)
                .map(|q| q.len()),
            Some(usize::from(MAX_PENDING_REQUEST_FAN_OUT)),
            "queue should not have grown past the cap",
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

**File:** crates/contract/src/pending_requests.rs (L43-59)
```rust
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
