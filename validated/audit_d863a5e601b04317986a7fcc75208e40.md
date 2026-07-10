### Title
Caller-Agnostic Queue Key in `verify_foreign_transaction` Enables Targeted DoS of Bridge Verification Requests - (File: `crates/contract/src/lib.rs`)

### Summary

The `verify_foreign_transaction` endpoint uses a queue key that omits the caller's account ID. Any unprivileged account can fill the 128-slot fan-out queue for a specific foreign transaction, permanently blocking legitimate bridge services from verifying that transaction until the queue drains via timeout — a cycle the attacker can repeat indefinitely at near-zero cost.

### Finding Description

When `verify_foreign_transaction` is called, the contract converts `VerifyForeignTransactionRequestArgs` into a `VerifyForeignTransactionRequest` via `args_into_verify_foreign_tx_request()`:

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

The resulting `VerifyForeignTransactionRequest` struct contains no caller identity:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs:124-128
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

This struct is used as the map key in `pending_verify_foreign_tx_requests`. All callers submitting the same foreign transaction share the same queue slot. The queue is hard-capped at `MAX_PENDING_REQUEST_FAN_OUT = 128`:

```rust
// crates/contract/src/pending_requests.rs:51-57
if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
    env::panic_str(
        &RequestError::PendingRequestQueueFull {
            limit: MAX_PENDING_REQUEST_FAN_OUT,
        }
        .to_string(),
    );
}
```

This is in direct contrast to `sign`, where `SignatureRequest` embeds a `tweak` derived from `(predecessor_id, path)`, giving each caller a distinct queue key. The codebase's own test acknowledges the caller-agnostic behavior for foreign-tx requests:

> "And: caller bob submits the identical request — a different account would today be blocked from receiving a response by alice's submission."

An attacker who knows a bridge service is about to verify a specific Bitcoin/Ethereum/Solana transaction can:
1. Submit 128 `verify_foreign_transaction` calls for that exact `(tx_id, domain_id, payload_version)` tuple, each costing only 1 yoctoNEAR deposit.
2. The queue is now full. Any subsequent call from the legitimate bridge service panics with `PendingRequestQueueFull`.
3. The queue drains only via per-yield timeouts (~200 blocks, ≈ 4 minutes). The attacker refills it before it drains.
4. The bridge service can never get a response for that transaction.

### Impact Explanation

A bridge service that depends on `verify_foreign_transaction` to release funds on NEAR (e.g., after a confirmed Bitcoin deposit) is permanently blocked from completing that verification for a targeted transaction. The bridge's NEAR-side settlement for that specific cross-chain transfer is frozen for as long as the attacker maintains the spam. This is a request-lifecycle manipulation that breaks the production safety invariant that any valid foreign-chain transaction can be verified and settled.

**Impact: Medium** — matches "request-lifecycle manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration."

### Likelihood Explanation

**Likelihood: Medium.** The attacker needs to know the target transaction ID in advance (observable on the foreign chain before the bridge service submits). The cost is 128 × 1 yoctoNEAR + gas per refill cycle — economically negligible. No privileged access is required; any NEAR account can call `verify_foreign_transaction`.

### Recommendation

Include the caller's `predecessor_account_id` in the `VerifyForeignTransactionRequest` map key, analogous to how `SignatureRequest` incorporates a per-caller tweak. Alternatively, derive a per-caller tweak from `(predecessor_id, tx_id)` and embed it in the stored request, so each caller occupies a distinct queue slot and cannot fill another caller's queue.

### Proof of Concept

The existing unit test at `crates/contract/src/lib.rs:3208–3263` already demonstrates the shared-queue behavior: Alice and Bob submitting the same request land in the same queue. Extending this to 128 submissions from a single attacker account saturates the queue and causes the 129th call (from the legitimate bridge service) to panic with `PendingRequestQueueFull`.

**Attacker steps:**
1. Observe a target Bitcoin `tx_id` on-chain before the bridge service submits.
2. Call `verify_foreign_transaction({ request: BitcoinRpcRequest { tx_id, ... }, domain_id, payload_version })` 128 times (batched across multiple transactions to stay within per-receipt gas limits).
3. The queue for that `(tx_id, domain_id, payload_version)` key is now full.
4. The bridge service's call panics with `PendingRequestQueueFull`.
5. Repeat every ~200 blocks to maintain the DoS.

---

**Key code references:**

`verify_foreign_transaction` drops the caller before storing the request: [1](#0-0) 

`args_into_verify_foreign_tx_request` omits `predecessor_account_id`: [2](#0-1) 

`VerifyForeignTransactionRequest` has no caller field (unlike `SignatureRequest` which has `tweak`): [3](#0-2) 

Queue cap and enforcement: [4](#0-3) 

Test acknowledging caller-agnostic queue behavior: [5](#0-4)

### Citations

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

**File:** crates/contract/src/lib.rs (L3242-3255)
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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** crates/contract/src/pending_requests.rs (L37-58)
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
```
