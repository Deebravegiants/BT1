### Title
Caller-Agnostic `verify_foreign_transaction` Queue Can Be Saturated by Any Unprivileged Caller, Permanently Blocking Legitimate Bridge Requests - (File: `crates/contract/src/pending_requests.rs`)

### Summary

The `verify_foreign_transaction` pending-request queue uses a **caller-agnostic** map key (`VerifyForeignTransactionRequest`, which contains no `predecessor_account_id`). Any unprivileged account can submit 128 identical `verify_foreign_transaction` calls to saturate the shared queue for a given foreign-chain transaction. Once full, every subsequent legitimate caller's transaction panics with `PendingRequestQueueFull` and is reverted. An attacker who monitors the chain and immediately re-saturates the queue after each MPC `respond_verify_foreign_tx` drain can permanently prevent a bridge service from ever getting a specific foreign-chain transaction verified, freezing the cross-chain fund flow that depends on it.

### Finding Description

`push_pending_yield` enforces a hard cap of `MAX_PENDING_REQUEST_FAN_OUT = 128` per request key: [1](#0-0) 

When the queue is full it calls `env::panic_str`, reverting the caller's transaction entirely — no graceful partial handling, no per-caller sub-limit: [2](#0-1) 

For `sign()`, the map key is `SignatureRequest`, which is constructed with the caller's `predecessor_account_id`, so each account has its own isolated queue: [3](#0-2) 

For `verify_foreign_transaction()`, the map key is `VerifyForeignTransactionRequest`, which contains only `request`, `domain_id`, and `payload_version` — **no caller identity**: [4](#0-3) 

The contract itself converts the user-supplied args into this caller-agnostic key and enqueues it: [5](#0-4) 

The test suite explicitly acknowledges the shared-queue design and notes the blocking risk in a comment: [6](#0-5) 

Because the queue is shared across all callers for the same foreign-tx request, an attacker who submits 128 identical `verify_foreign_transaction` calls saturates the slot for that request key. Any subsequent legitimate caller (e.g., a bridge service) receives `PendingRequestQueueFull` and their transaction is reverted. When MPC nodes eventually call `respond_verify_foreign_tx` and drain the queue, the attacker immediately re-saturates it. The cost per saturation round is 128 yoctonear (the minimum deposit per call). [7](#0-6) 

### Impact Explanation

A bridge service that relies on `verify_foreign_transaction` to confirm a foreign-chain deposit before releasing funds on NEAR can be permanently prevented from queuing its verification request. As long as the attacker maintains the saturation loop, the bridge's cross-chain fund release is frozen. This is a **Medium** impact: request-lifecycle manipulation that breaks the production safety invariant (any authorized caller must be able to submit a foreign-tx verification) without requiring network-level DoS or operator misconfiguration — only 128 cheap NEAR transactions per MPC response cycle.

### Likelihood Explanation

The attack is cheap (128 yoctonear per round ≈ negligible), requires no privileged access, and is straightforward to automate: watch for `respond_verify_foreign_tx` events on-chain and immediately re-saturate the target queue. The attacker needs no cryptographic capability and no collusion with MPC participants.

### Recommendation

Apply one or more of the following mitigations:

1. **Include `predecessor_account_id` in the `VerifyForeignTransactionRequest` map key**, mirroring the `sign()` design. This gives each caller an isolated queue slot and eliminates cross-caller interference. The fan-out optimization (multiple callers sharing one MPC computation) can be preserved separately via a secondary index.

2. **Enforce a per-caller sub-limit** within the shared queue so a single account cannot consume more than a small fraction (e.g., 4) of the 128 slots.

3. **Replace the hard `env::panic_str` with a graceful `Err` return** (analogous to the LPDA mitigation of capping instead of reverting), so that a full queue causes the caller's yield to be skipped rather than the entire transaction to be reverted. This alone does not prevent saturation but eliminates the abrupt revert that makes the attack reliable.

### Proof of Concept

1. Attacker identifies a Bitcoin tx `0xABCD…` that bridge service Alice needs to verify to release 10 BTC worth of wrapped tokens on NEAR.
2. Attacker submits 128 calls to `verify_foreign_transaction({request: Bitcoin(tx_id=0xABCD…), domain_id: 0, payload_version: V1})`, each with 1 yoctonear deposit. Total cost: 128 yoctonear.
3. Alice submits `verify_foreign_transaction` for the same tx. The contract calls `push_pending_yield`, finds `queue.len() == 128 >= MAX_PENDING_REQUEST_FAN_OUT`, and calls `env::panic_str("Pending-request queue is full…")`. Alice's transaction is reverted; her deposit is refunded but her bridge release is blocked.
4. MPC nodes observe the 128 attacker requests, compute the signature, and call `respond_verify_foreign_tx`, draining the queue. The attacker's 128 yield-resume promises resolve (attacker receives the verification response they didn't need).
5. Attacker immediately submits another 128 calls. Alice retries and is again reverted.
6. This loop continues indefinitely at ~128 yoctonear per MPC response cycle, permanently freezing Alice's cross-chain fund release. [8](#0-7) [9](#0-8)

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

**File:** crates/contract/src/lib.rs (L379-397)
```rust
        let request = SignatureRequest::new(
            request.domain_id,
            request.payload,
            &predecessor,
            &request.path,
        );

        let callback_gas = Gas::from_tgas(
            self.config
                .return_signature_and_clean_state_on_success_call_tera_gas,
        );

        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_SIGNATURE_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_signature_request(request, id),
        );
```

**File:** crates/contract/src/lib.rs (L514-557)
```rust
    /// Submit a verification + signing request for a foreign chain transaction.
    /// MPC nodes will verify the transaction on the foreign chain before signing.
    /// The signed payload is derived from the transaction ID (hash of tx_id).
    #[handle_result]
    #[payable]
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

**File:** crates/contract/src/lib.rs (L3242-3243)
```rust
        // And: caller bob submits the identical request — a different account would today
        // be blocked from receiving a response by alice's submission.
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```
