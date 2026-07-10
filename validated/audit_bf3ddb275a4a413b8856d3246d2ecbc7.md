### Title
Caller-Agnostic `verify_foreign_transaction` Request Key Enables Fan-Out Queue Saturation DoS — (File: `crates/contract/src/lib.rs`, `crates/contract/src/pending_requests.rs`)

### Summary
The `verify_foreign_transaction` function constructs its pending-request map key without binding it to the caller's account ID. Combined with the hard cap of 128 entries per queue slot (`MAX_PENDING_REQUEST_FAN_OUT`), an unprivileged attacker can saturate the queue for any specific foreign transaction with 128 cheap calls, causing all subsequent legitimate `verify_foreign_transaction` submissions for that same transaction to panic with `PendingRequestQueueFull`, permanently blocking the request lifecycle for targeted bridge verifications.

### Finding Description

**Asymmetric request-key construction.** The `sign()` function binds its pending-request map key to the caller's account ID via `SignatureRequest::new(..., &predecessor, &request.path)`, giving every caller an isolated queue slot. By contrast, `verify_foreign_transaction()` constructs its key through `args_into_verify_foreign_tx_request()`: [1](#0-0) 

The resulting `VerifyForeignTransactionRequest` contains only `{domain_id, request, payload_version}` — no caller identity. Every caller submitting the same foreign transaction therefore shares a single queue slot. The sandbox test explicitly acknowledges this design: [2](#0-1) 

**Hard cap enforcement.** `push_pending_yield` enforces a ceiling of 128 entries per slot: [3](#0-2) 

Once the queue reaches 128, every subsequent call for the same request key panics unconditionally. There is no fallback, no timeout bypass, and no way for a legitimate user to reclaim a slot without waiting for MPC nodes to drain the queue via `respond_verify_foreign_tx`.

**Attack path.** An attacker submits 128 `verify_foreign_transaction` calls for a targeted foreign transaction (e.g., a specific Bitcoin `tx_id`), each attaching the minimum 1 yoctoNEAR deposit: [4](#0-3) 

The queue is now saturated. Any legitimate user calling `verify_foreign_transaction` with the same parameters receives a `PendingRequestQueueFull` panic. When MPC nodes eventually drain the queue via `respond_verify_foreign_tx`, the attacker immediately re-saturates it, sustaining the DoS indefinitely at the cost of 128 × gas per cycle.

### Impact Explanation

This breaks the request lifecycle for `verify_foreign_transaction`: legitimate bridge users are denied the ability to submit foreign transaction verification requests for any transaction the attacker chooses to target. Because `verify_foreign_transaction` is the gateway for verified cross-chain bridge execution, sustained queue saturation on a targeted transaction prevents that bridge transfer from ever being authorized through the MPC network. This is a request-lifecycle manipulation that breaks a production safety invariant — the guarantee that any user can submit a foreign transaction verification — without relying on network-level DoS or operator misconfiguration.

**Impact: Medium** — request-lifecycle manipulation breaking production accounting/flow invariants.

### Likelihood Explanation

The attack cost is low: 128 transactions × (1 yoctoNEAR + gas). The target parameters (foreign chain, `tx_id`, `domain_id`) are observable on-chain. The attacker can automate re-saturation immediately after each MPC drain cycle. No privileged access, collusion, or TEE bypass is required. Any unprivileged NEAR account can execute this.

**Likelihood: Medium** — cheap, repeatable, and automatable by any unprivileged caller.

### Recommendation

Include the caller's account ID (`env::predecessor_account_id()`) in the `VerifyForeignTransactionRequest` key, mirroring the design of `SignatureRequest::new(..., &predecessor, ...)`. This gives each caller an isolated queue slot, making it impossible for one account to saturate another account's queue for the same foreign transaction.

Alternatively, enforce a per-account submission limit within the shared queue to bound the number of slots any single account can occupy.

### Proof of Concept

1. Attacker identifies a target foreign transaction: e.g., Bitcoin `tx_id = [0xAB; 32]`, `domain_id = 0`.
2. Attacker submits 128 `verify_foreign_transaction` calls with identical `{domain_id, request, payload_version}`, each with 1 yoctoNEAR.
3. `push_pending_yield` appends 128 `YieldIndex` entries to the shared queue slot.
4. Legitimate bridge user submits `verify_foreign_transaction` with the same parameters.
5. `push_pending_yield` evaluates `queue.len() >= 128` → `true` → `env::panic_str("Pending-request queue is full …")`.
6. Legitimate user's transaction is reverted; they receive no yield and no response.
7. MPC nodes call `respond_verify_foreign_tx`, draining all 128 attacker yields (attacker receives 128 copies of the signature).
8. Attacker immediately re-submits 128 calls. Legitimate user remains blocked indefinitely. [5](#0-4) [6](#0-5)

### Citations

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

**File:** crates/contract/src/pending_requests.rs (L43-60)
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
}
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
