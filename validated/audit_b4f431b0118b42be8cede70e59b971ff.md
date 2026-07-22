### Title
Gateway `skip_stateful_validations` Bypasses `__validate__` Signature Check for Invoke Transactions with Nonce=1 When Any Account Transaction Exists in Mempool — (`crates/apollo_gateway/src/stateful_transaction_validator.rs`)

---

### Summary

`skip_stateful_validations` in the Apollo gateway is intended to skip the `__validate__` entry point only when a `deploy_account` transaction is pending for an undeployed account. However, the guard condition uses `account_tx_in_pool_or_recent_block`, which returns `true` for **any** transaction from that address in the pool or a recent committed block — not specifically a `deploy_account`. An attacker who observes a legitimate user's pending `deploy_account` can submit an invoke transaction with nonce=1 and an **invalid signature** for the same address, and the gateway will admit it to the mempool without running `__validate__` (signature verification). This is the direct analog of the LiFi "latent balance" bypass: a guard condition that should always enforce a check is skipped when a pre-existing state condition is satisfied, allowing unauthorized use of a resource (here: execution slot / nonce) without proper authorization.

---

### Finding Description

**Root cause — `skip_stateful_validations`:** [1](#0-0) 

The function returns `true` (skip `__validate__`) when all three conditions hold:

1. The incoming transaction is an `Invoke` with `tx.nonce() == Nonce(Felt::ONE)`
2. The on-chain account nonce is `Nonce(Felt::ZERO)` (account not yet deployed)
3. `account_tx_in_pool_or_recent_block(sender_address)` returns `true`

The comment claims condition 3 implies a `deploy_account` is present. That is false.

**`account_tx_in_pool_or_recent_block` implementation:** [2](#0-1) 

It returns `true` if the address appears in `self.state` (any committed block) **or** `self.tx_pool` (any pending transaction of any type). There is no filter for `deploy_account`.

**What is skipped when `skip_validate = true`:** [3](#0-2) 

`ExecutionFlags { validate: false, ... }` is set, which causes `perform_validations` to return immediately: [4](#0-3) 

The `__validate__` entry point — which is the account contract's signature verification — is never called.

**The config field `max_nonce_for_validation_skip` is defined but unused in this path:** [5](#0-4) 

The field exists in `StatefulTransactionValidatorConfig` and is used in the legacy Python-binding path (`PyValidator::should_run_stateful_validations`), but `skip_stateful_validations` hardcodes the nonce threshold to `Nonce(Felt::ONE)` and never reads `self.config.max_nonce_for_validation_skip`. An operator cannot disable the skip by setting this config to 0.

---

### Impact Explanation

**Admission of invalid (unsigned) transactions — High.**

An attacker can submit an invoke transaction with nonce=1 and an **invalid or forged signature** for any account that has a pending `deploy_account` in the mempool. The gateway admits it without running `__validate__`. The admitted transaction:

- Occupies the nonce=1 slot in the mempool for the victim account.
- Can replace the legitimate owner's nonce=1 invoke via fee escalation (by paying a higher tip), causing the legitimate transaction to be evicted.
- When the batcher later executes it, `__validate__` runs with `validate=true` and the transaction reverts — but the nonce has already been incremented by `perform_pre_validation_stage` (nonce increment is a pre-validation step that is not rolled back on revert).
- The victim's original nonce=1 transaction is gone; the victim must resubmit at nonce=2.

This satisfies: **"Mempool/gateway/RPC admission accepts invalid transactions or rejects valid transactions before sequencing."**

---

### Likelihood Explanation

- Requires no privileged access. Any unprivileged user can submit transactions to the gateway.
- The trigger condition (a pending `deploy_account` in the mempool) is observable on-chain/via RPC and is a normal, common state during account onboarding.
- The attacker only needs to submit one transaction with a higher fee than the victim's invoke.
- The attack is cheap: the attacker's transaction reverts, so only the fee for the reverted execution is lost (and the attacker can set a low fee since the transaction reverts quickly on `__validate__` failure).

---

### Recommendation

1. **Filter by transaction type**: In `skip_stateful_validations`, replace the `account_tx_in_pool_or_recent_block` check with a check that specifically verifies a `deploy_account` transaction is pending for the address. Add a dedicated mempool query such as `deploy_account_in_pool(address)`.

2. **Use the config field**: Wire `self.config.max_nonce_for_validation_skip` into `skip_stateful_validations` so operators can set it to `0` to disable the skip entirely, consistent with how `PyValidator::should_run_stateful_validations` uses it. [6](#0-5) 

3. **Defense in depth**: Even when skipping `__validate__` at the gateway, consider recording the skip decision so the batcher can enforce that the transaction is only executed after the corresponding `deploy_account` has been committed.

---

### Proof of Concept

**Setup:**
- Legitimate user `Alice` controls account address `A` (not yet deployed, `account_nonce = 0`).
- Alice submits `deploy_account` (nonce=0, tip=T) → admitted to mempool. `account_tx_in_pool_or_recent_block(A)` now returns `true`.
- Alice also submits `invoke` (nonce=1, tip=T, valid signature, calldata=transfer funds).

**Attack:**
1. Attacker observes Alice's pending `deploy_account` via mempool/RPC.
2. Attacker constructs `invoke` for address `A`, nonce=1, tip=T+1, **invalid signature** (e.g., all-zero signature bytes), arbitrary calldata.
3. Attacker submits to gateway. In `skip_stateful_validations`:
   - `tx.nonce() == 1` ✓
   - `account_nonce == 0` ✓
   - `account_tx_in_pool_or_recent_block(A) == true` ✓ (Alice's deploy_account is in pool)
   - Returns `true` → `validate = false` → `__validate__` is NOT called.
4. Mempool fee-escalation logic accepts attacker's invoke (higher tip) and evicts Alice's invoke.
5. Batcher executes: `deploy_account` (nonce → 1), then attacker's `invoke` (nonce → 2, reverts on `__validate__` failure).
6. Alice's original invoke (nonce=1) is gone. Alice must resubmit at nonce=2.

**Corrupted value**: Alice's nonce is advanced to 2 without her authorization; her nonce=1 transaction is permanently lost from the mempool. [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L302-312)
```rust
    #[sequencer_latency_histogram(GATEWAY_VALIDATE_TX_LATENCY, true)]
    async fn run_validate_entry_point(
        &mut self,
        executable_tx: &ExecutableTransaction,
        skip_validate: bool,
    ) -> StatefulTransactionValidatorResult<()> {
        let only_query = false;
        let charge_fee = enforce_fee(executable_tx, only_query);
        let strict_nonce_check = false;
        let execution_flags =
            ExecutionFlags { only_query, charge_fee, validate: !skip_validate, strict_nonce_check };
```

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L429-461)
```rust
async fn skip_stateful_validations(
    tx: &ExecutableTransaction,
    account_nonce: Nonce,
    mempool_client: SharedMempoolClient,
) -> StatefulTransactionValidatorResult<bool> {
    if let ExecutableTransaction::Invoke(ExecutableInvokeTransaction { tx, .. }) = tx {
        // check if the transaction nonce is 1, meaning it is post deploy_account, and the
        // account nonce is zero, meaning the account was not deployed yet.
        if tx.nonce() == Nonce(Felt::ONE) && account_nonce == Nonce(Felt::ZERO) {
            let account_address = tx.sender_address();
            debug!("Checking if deploy_account transaction exists for account {account_address}.");
            // We verify that a deploy_account transaction exists for this account. It is sufficient
            // to check if the account exists in the mempool since it means that either it has a
            // deploy_account transaction or transactions with future nonces that passed
            // validations.
            return mempool_client
                .account_tx_in_pool_or_recent_block(tx.sender_address())
                .await
                .map_err(|err| mempool_client_err_to_deprecated_gw_err(&tx.signature(), err))
                .inspect(|exists| {
                    if *exists {
                        debug!("Found deploy_account transaction for account {account_address}.");
                    } else {
                        debug!(
                            "No deploy_account transaction found for account {account_address}."
                        );
                    }
                });
        }
    }

    Ok(false)
}
```

**File:** crates/apollo_mempool/src/mempool.rs (L697-700)
```rust
    pub fn account_tx_in_pool_or_recent_block(&self, account_address: ContractAddress) -> bool {
        self.state.contains_account(account_address)
            || self.tx_pool.contains_account(account_address)
    }
```

**File:** crates/blockifier/src/blockifier/stateful_validator.rs (L76-81)
```rust
            ApiTransaction::Invoke(_) => {
                let tx_context = Arc::new(self.tx_executor.block_context.to_tx_context(&tx));
                tx.perform_pre_validation_stage(self.state(), &tx_context)?;
                if !tx.execution_flags.validate {
                    return Ok(());
                }
```

**File:** crates/apollo_gateway_config/src/config.rs (L283-295)
```rust
    pub max_nonce_for_validation_skip: Nonce,
    pub versioned_constants_overrides: Option<VersionedConstantsOverrides>,
    // Minimum gas price as percentage of threshold to accept transactions.
    pub min_gas_price_percentage: u8, // E.g., 80 to require 80% of threshold.
}

impl Default for StatefulTransactionValidatorConfig {
    fn default() -> Self {
        StatefulTransactionValidatorConfig {
            validate_resource_bounds: true,
            max_allowed_nonce_gap: 200,
            reject_future_declare_txs: true,
            max_nonce_for_validation_skip: Nonce(Felt::ONE),
```

**File:** crates/native_blockifier/src/py_validator.rs (L112-120)
```rust
        let is_post_deploy_nonce = Nonce(Felt::ONE) <= tx_nonce;
        let nonce_small_enough_to_qualify_for_validation_skip =
            tx_nonce <= self.max_nonce_for_validation_skip;

        let skip_validate = deploy_account_not_processed
            && is_post_deploy_nonce
            && nonce_small_enough_to_qualify_for_validation_skip;

        Ok(!skip_validate)
```
