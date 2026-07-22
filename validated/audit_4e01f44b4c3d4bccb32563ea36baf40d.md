### Title
Gateway `skip_stateful_validations` Bypasses `__validate__` Signature Check for Invoke Transactions with Nonce=1 When Any Account Transaction Exists in Mempool — (File: `crates/apollo_gateway/src/stateful_transaction_validator.rs`)

---

### Summary

The `skip_stateful_validations` function in the gateway's stateful validator is designed to skip the `__validate__` entry-point call (which performs account-level signature verification) for invoke transactions with nonce=1 when a `deploy_account` transaction is pending in the mempool. However, the guard condition uses `account_tx_in_pool_or_recent_block`, which returns `true` for **any** transaction from that address — not specifically a `deploy_account`. An unprivileged attacker can exploit this to get an invoke transaction with an invalid signature admitted to the mempool without signature verification.

---

### Finding Description

The gateway's `extract_state_nonce_and_run_validations` flow calls `run_pre_validation_checks`, which in turn calls `skip_stateful_validations`:

```
extract_state_nonce_and_run_validations
  └─ run_pre_validation_checks
       ├─ validate_state_preconditions   (nonce range, resource bounds)
       ├─ validate_by_mempool            (nonce/fee-escalation only, no signature)
       └─ skip_stateful_validations      ← returns true → __validate__ is skipped
```

`skip_stateful_validations` returns `true` (skip) when all three conditions hold:
1. The transaction is an `Invoke`.
2. `tx.nonce() == Nonce(Felt::ONE)`.
3. `account_nonce == Nonce(Felt::ZERO)` (account not yet deployed on-chain).
4. `mempool_client.account_tx_in_pool_or_recent_block(sender)` returns `true`. [1](#0-0) 

The comment in the code says the check is sufficient because the account "either has a deploy_account transaction or transactions with future nonces that passed validations." But `account_tx_in_pool_or_recent_block` is implemented as:

```rust
pub fn account_tx_in_pool_or_recent_block(&self, account_address: ContractAddress) -> bool {
    self.state.contains_account(account_address)
        || self.tx_pool.contains_account(account_address)
}
``` [2](#0-1) 

This returns `true` for **any** transaction type from that address — including a plain invoke with nonce=0 that the attacker themselves submitted. It does not verify that the pending transaction is specifically a `deploy_account`.

When `skip_stateful_validations` returns `true`, `run_validate_entry_point` is called with `skip_validate = true`, which sets `execution_flags.validate = false`:

```rust
let execution_flags =
    ExecutionFlags { only_query, charge_fee, validate: !skip_validate, strict_nonce_check };
``` [3](#0-2) 

With `validate = false`, `blockifier_validator.validate(account_tx)` returns `Ok(())` immediately without running the `__validate__` entry point:

```rust
if !tx.execution_flags.validate {
    return Ok(());
}
``` [4](#0-3) 

The mempool's `validate_tx` only checks nonce validity and fee escalation — it performs no signature check:

```rust
pub fn validate_tx(&mut self, args: ValidationArgs) -> MempoolResult<()> {
    let tx_reference = (&args).into();
    self.validate_incoming_tx(tx_reference, args.account_nonce)?;
    self.validate_fee_escalation(tx_reference)?;
    Ok(())
}
``` [5](#0-4) 

Therefore, a forged invoke with nonce=1 and an invalid signature passes all gateway and mempool checks and is admitted to the mempool.

---

### Impact Explanation

**Impact: High — Mempool/gateway admission accepts invalid transactions before sequencing.**

An invoke transaction carrying an invalid (or entirely forged) signature is admitted to the mempool without any account-level signature verification. The broken invariant is:

> Every invoke transaction admitted to the mempool must have passed `__validate__` (signature verification) OR have a legitimate reason to skip it (i.e., a `deploy_account` transaction is pending for the same account).

The actual check is too broad: it returns `true` for any transaction from that address, not just `deploy_account` transactions.

During block execution, `ExecutionFlags::default()` has `validate: true`, so `__validate__` will run and the forged transaction will fail/revert. However, the damage occurs at admission:
- The forged transaction occupies a mempool slot for the target account at nonce=1.
- Via fee escalation, the attacker can displace a legitimate nonce=1 transaction from the victim account.
- The forged transaction will be included in a block, fail `__validate__`, and waste block space and sequencer execution resources. [6](#0-5) 

---

### Likelihood Explanation

**Likelihood: Medium.**

The preconditions are:
1. The target account has nonce=0 on-chain (not yet deployed, or freshly deployed).
2. The target account has **any** transaction in the mempool (e.g., a `deploy_account` or a nonce=0 invoke).

Condition 2 is observable by monitoring the public mempool. Any account in the process of being deployed satisfies both conditions simultaneously. The attacker needs only to submit a well-formed invoke transaction (correct chain_id, valid resource bounds, nonce=1) with an arbitrary/invalid signature for the target address. No privileged access is required.

---

### Recommendation

**Short term:** In `skip_stateful_validations`, replace the broad `account_tx_in_pool_or_recent_block` check with a specific check that verifies a `deploy_account` transaction (not just any transaction) is pending for the sender address. Add a dedicated mempool API such as `deploy_account_in_pool(address)` that inspects the transaction type.

**Long term:** Require minimum proof of account ownership (e.g., a valid ECDSA pre-image or a deploy-account hash commitment) before skipping `__validate__`, so the skip cannot be triggered by an unrelated transaction from the same address. [7](#0-6) 

---

### Proof of Concept

**Setup:** Account `A` has nonce=0 on-chain (not yet deployed). A legitimate user submits `deploy_account(A, nonce=0)` to the gateway; it is admitted to the mempool. `account_tx_in_pool_or_recent_block(A)` now returns `true`.

**Attack steps:**

1. Attacker constructs `invoke_tx` with:
   - `sender_address = A`
   - `nonce = 1`
   - `signature = [0x0, 0x0]` (invalid/forged)
   - valid `chain_id`, `resource_bounds`, `calldata`

2. Attacker submits `invoke_tx` to the gateway RPC endpoint.

3. Gateway calls `run_pre_validation_checks`:
   - `validate_state_preconditions`: nonce=1 is in range `[0, max_gap]` → **passes**.
   - `validate_by_mempool`: mempool checks nonce/fee-escalation only → **passes**.
   - `skip_stateful_validations`: `tx.nonce()==1`, `account_nonce==0`, `account_tx_in_pool_or_recent_block(A)==true` → **returns `true`**.

4. `run_validate_entry_point` is called with `skip_validate=true` → `execution_flags.validate=false` → `__validate__` is **not called** → returns `Ok(())`.

5. The forged `invoke_tx` is forwarded to the mempool and admitted.

6. **Corrupted value:** The mempool now contains a nonce=1 invoke for account `A` with an invalid signature. If the attacker offered a higher fee than the legitimate nonce=1 invoke, the legitimate transaction is displaced via fee escalation.

7. When the batcher executes the forged transaction in a block, `__validate__` runs (default `validate=true`), the signature check fails, the transaction reverts, and block space is wasted. [8](#0-7) [2](#0-1)

### Citations

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L308-312)
```rust
        let only_query = false;
        let charge_fee = enforce_fee(executable_tx, only_query);
        let strict_nonce_check = false;
        let execution_flags =
            ExecutionFlags { only_query, charge_fee, validate: !skip_validate, strict_nonce_check };
```

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L399-410)
```rust
    async fn run_pre_validation_checks(
        &self,
        executable_tx: &ExecutableTransaction,
        account_nonce: Nonce,
        mempool_client: SharedMempoolClient,
    ) -> StatefulTransactionValidatorResult<bool> {
        self.validate_state_preconditions(executable_tx, account_nonce).await?;
        validate_by_mempool(executable_tx, account_nonce, mempool_client.clone()).await?;
        let skip_validate =
            skip_stateful_validations(executable_tx, account_nonce, mempool_client.clone()).await?;
        Ok(skip_validate)
    }
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

**File:** crates/apollo_mempool/src/mempool.rs (L402-408)
```rust
    pub fn validate_tx(&mut self, args: ValidationArgs) -> MempoolResult<()> {
        let tx_reference = (&args).into();
        self.validate_incoming_tx(tx_reference, args.account_nonce)?;
        self.validate_fee_escalation(tx_reference)?;

        Ok(())
    }
```

**File:** crates/apollo_mempool/src/mempool.rs (L697-700)
```rust
    pub fn account_tx_in_pool_or_recent_block(&self, account_address: ContractAddress) -> bool {
        self.state.contains_account(account_address)
            || self.tx_pool.contains_account(account_address)
    }
```

**File:** crates/blockifier/src/blockifier/stateful_validator.rs (L79-81)
```rust
                if !tx.execution_flags.validate {
                    return Ok(());
                }
```

**File:** crates/blockifier/src/transaction/account_transaction.rs (L98-101)
```rust
impl Default for ExecutionFlags {
    fn default() -> Self {
        Self { only_query: false, charge_fee: true, validate: true, strict_nonce_check: true }
    }
```
