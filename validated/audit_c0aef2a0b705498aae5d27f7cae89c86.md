### Title
Unprivileged Caller Can Exhaust `verify_foreign_transaction` Fan-Out Queue to Persistently Block Legitimate Users - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `verify_foreign_transaction` function does not bind the request key to the caller's identity, unlike `sign` and `request_app_private_key`. Any unprivileged caller can submit the same `VerifyForeignTransactionRequest` as a victim, filling the shared fan-out queue to the hard cap of 128 and preventing the legitimate user from ever enqueuing their own yield-resume promise.

---

### Finding Description

**Root cause — missing caller identity in the request key**

Both `sign` and `request_app_private_key` include `predecessor` (the caller's NEAR account ID) when constructing the request key, so each caller owns a distinct queue slot:

```rust
// lib.rs ~L379
let request = SignatureRequest::new(
    request.domain_id,
    request.payload,
    &predecessor,   // ← caller identity bound into key
    &request.path,
);
```

```rust
// lib.rs ~L493
let request = CKDRequest::new(
    request.app_public_key,
    domain_id,
    &predecessor,   // ← caller identity bound into key
    &request.derivation_path,
);
```

`verify_foreign_transaction` calls `check_request_preconditions` but **silently discards** the returned `(domain_config, predecessor)` tuple:

```rust
// lib.rs ~L526-L531
self.check_request_preconditions(
    request.domain_id,
    DomainPurpose::ForeignTx,
    Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
    MINIMUM_SIGN_REQUEST_DEPOSIT,
);
// ← return value (domain_config, predecessor) is dropped
```

The request key is then built without any caller identity:

```rust
// dto_mapping.rs ~L840-L848
pub fn args_into_verify_foreign_tx_request(
    args: dtos::VerifyForeignTransactionRequestArgs,
) -> dtos::VerifyForeignTransactionRequest {
    dtos::VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
        // ← no account_id field
    }
}
```

**Queue exhaustion mechanism**

`push_pending_yield` enforces a hard cap of `MAX_PENDING_REQUEST_FAN_OUT = 128`:

```rust
// pending_requests.rs ~L51-L58
if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
    env::panic_str(
        &RequestError::PendingRequestQueueFull {
            limit: MAX_PENDING_REQUEST_FAN_OUT,
        }
        .to_string(),
    );
}
```

Because the queue key for `verify_foreign_transaction` is shared across all callers submitting the same foreign-chain transaction data, an attacker who knows the target transaction (all foreign-chain transactions are public) can pre-fill or continuously re-fill the queue to 128 entries. The victim's subsequent `verify_foreign_transaction` call panics with `PendingRequestQueueFull`.

**Persistence of the block**

When the MPC nodes call `respond_verify_foreign_tx`, `resolve_yields_for` drains the entire queue in one pass. The attacker can immediately re-submit 128 copies in the next block, re-establishing the block before the victim can react. The cycle repeats indefinitely at a cost of 128 × gas per round, which is economically rational if the attacker profits from preventing the victim's bridge claim.

---

### Impact Explanation

**Medium — request-lifecycle manipulation breaking production safety invariants.**

A victim whose `verify_foreign_transaction` request is persistently blocked cannot obtain the MPC signature needed to complete a foreign-chain bridge flow. If the victim is waiting on a time-sensitive claim (e.g., a cross-chain deposit with an expiry), the persistent block causes the claim to expire and the funds to be unrecoverable. This breaks the production accounting invariant that every valid foreign-chain transaction submitted with sufficient gas and deposit will eventually be serviced. The attack does not require network-level DoS, operator misconfiguration, or threshold collusion — only the ability to call a public contract method.

---

### Likelihood Explanation

**Medium.** Foreign-chain transactions are publicly observable. An attacker monitoring the foreign chain (or the NEAR contract event log) can reconstruct the exact `VerifyForeignTransactionRequest` parameters (`domain_id`, `request`, `payload_version`) from on-chain data. Submitting 128 transactions per MPC response cycle is feasible for any attacker with a profit motive (e.g., front-running a bridge claim). The minimum deposit is only 1 yoctoNEAR per call, making the per-cycle cost negligible relative to the value of a bridge transaction.

---

### Recommendation

Bind the caller's identity into the `VerifyForeignTransactionRequest` key, mirroring the pattern used by `sign` and `request_app_private_key`. Concretely:

1. Use the `predecessor` returned by `check_request_preconditions` instead of discarding it.
2. Add an `account_id: AccountId` field to `VerifyForeignTransactionRequest` (or a wrapper type used as the map key).
3. Populate that field from `predecessor` inside `verify_foreign_transaction`, so each caller's request occupies a distinct queue entry.

---

### Proof of Concept

```
1. Victim calls verify_foreign_transaction({domain_id, tx_data, payload_version})
   → queue for key K = {domain_id, tx_data, payload_version} now has 1 entry.

2. Attacker observes the foreign-chain transaction (public data) and submits
   127 more calls with identical parameters.
   → queue for K now has 128 entries (at the cap).

3. Victim's NEAR yield times out; pop_oldest_pending_yield removes the
   victim's entry → queue has 127 attacker entries.

4. Victim retries verify_foreign_transaction.
   → push_pending_yield: queue.len() (127) < 128, push succeeds → queue = 128.

5. Attacker submits one more call.
   → push_pending_yield: queue.len() (128) >= 128 → PendingRequestQueueFull panic.
   Victim's retry is now blocked again.

6. MPC nodes respond, draining all 128 entries (attacker receives all responses).
   Attacker immediately re-fills to 128. Repeat from step 4.
```

The victim can never hold a stable queue slot because the attacker controls 127 of the 128 positions and can always reclaim the 128th after any drain. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L493-498)
```rust
        let request = CKDRequest::new(
            request.app_public_key,
            domain_id,
            &predecessor,
            &request.derivation_path,
        );
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
