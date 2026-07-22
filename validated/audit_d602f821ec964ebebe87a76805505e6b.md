### Title
`skip_stateful_validations` skips `__validate__` for any address with a pending mempool entry, not just the legitimate deployer — (`crates/apollo_gateway/src/stateful_transaction_validator.rs`)

### Summary

`skip_stateful_validations` in the gateway's stateful validator is designed to let a user submit a `deploy_account` + `invoke(nonce=1)` pair simultaneously. However, the guard that enables the skip — `account_tx_in_pool_or_recent_block(sender_address)` — checks only whether *any* transaction exists in the mempool for that address, not whether the caller is the legitimate owner of the address. An attacker who observes a victim's pending `deploy_account` (or any pending transaction) in the public mempool can submit an `invoke` with `nonce=1` from the victim's address, an arbitrary signature, and arbitrary calldata. The gateway skips the `__validate__` entry-point check and admits the transaction to the mempool without verifying the signature.

### Finding Description

`skip_stateful_validations` is called inside `run_pre_validation_checks` after `validate_state_preconditions` and `validate_by_mempool`:

```
validate_state_preconditions  →  nonce range check (account_nonce=0, tx_nonce=1 passes)
validate_by_mempool           →  duplicate-hash check (new tx_hash passes)
skip_stateful_validations     →  returns true → run_validate_entry_point is SKIPPED
```

The skip condition is:

```rust
// crates/apollo_gateway/src/stateful_transaction_validator.rs  L437-L456
if tx.nonce() == Nonce(Felt::ONE) && account_nonce == Nonce(Felt::ZERO) {
    let account_address = tx.sender_address();
    return mempool_client
        .account_tx_in_pool_or_recent_block(tx.sender_address())
        .await
        ...
```

`account_tx_in_pool_or_recent_block` returns `true` if the address has **any** transaction in the pool or recent block:

```rust
// crates/apollo_mempool/src/mempool.rs  L697-L700
pub fn account_tx_in_pool_or_recent_block(&self, account_address: ContractAddress) -> bool {
    self.state.contains_account(account_address)
        || self.tx_pool.contains_account(account_address)
}
```

There is no check that:
1. The transaction in the pool is a `deploy_account` (it could be any transaction type).
2. The entity submitting the `invoke` is the same entity that submitted the pooled transaction.

**Attack path:**

1. Alice submits `deploy_account` for address X (nonce=0); it enters the mempool.
2. Attacker observes Alice's pending transaction (public mempool).
3. Attacker submits `invoke` with `sender_address=X`, `nonce=1`, arbitrary calldata, and an invalid/forged signature.
4. Gateway checks:
   - `validate_nonce`: `account_nonce=0 ≤ tx_nonce=1 ≤ max_allowed_nonce_gap` → passes.
   - `validate_by_mempool`: new `tx_hash`, no duplicate nonce=1 for X yet → passes.
   - `skip_stateful_validations`: X has a transaction in the pool → returns `true`.
   - `run_validate_entry_point`: **skipped**.
5. Attacker's transaction is admitted to the mempool without signature verification.

### Impact Explanation

This matches the allowed impact: **"High. Mempool/gateway/RPC admission accepts invalid transactions or rejects valid transactions before sequencing."**

Concrete consequences:
- **Nonce squatting**: The attacker occupies Alice's `nonce=1` slot in the mempool. If the mempool does not support fee-escalation replacement for the same nonce, Alice cannot submit her own `nonce=1` invoke until the attacker's transaction is evicted or executed (and fails).
- **Mempool pollution**: The attacker can repeat this for every address that has a pending transaction, flooding the mempool with transactions that will revert at execution time.
- **Griefing the deploy_account + invoke UX flow**: The feature is specifically designed to improve UX for the `deploy_account + invoke` pattern; the attack directly undermines that guarantee.

The attacker's transaction will revert at execution time (the batcher runs `__validate__` independently), so no funds are directly stolen. However, the gateway invariant — that only transactions whose `__validate__` passes (or whose skip is legitimately earned) enter the mempool — is broken.

### Likelihood Explanation

- The mempool is public; any observer can detect a pending `deploy_account` for a target address.
- The attack requires only a single RPC call with a crafted transaction.
- No privileged access, no special network position, and no prior on-chain state is required.
- The condition `nonce=1 && account_nonce=0` is a narrow but well-known window (every new account deployment opens it).

### Recommendation

Replace the unchecked `account_tx_in_pool_or_recent_block` call with a check that verifies the pooled transaction is specifically a `deploy_account` for the same address, **and** that the `invoke` transaction's `sender_address` matches the address being deployed. Alternatively, require the gateway to verify that the `deploy_account` transaction hash is provided by the submitter (as the `native_blockifier` `PyValidator` already does via `deploy_account_tx_hash`):

```rust
// crates/native_blockifier/src/py_validator.rs  L101-L110
pub fn should_run_stateful_validations(
    &mut self,
    account_tx: &AccountTransaction,
    deploy_account_tx_hash: Option<TransactionHash>,  // explicit proof of ownership
) -> StatefulValidatorResult<bool> {
    ...
    let deploy_account_not_processed =
        deploy_account_tx_hash.is_some() && nonce == Nonce(Felt::ZERO);
```

The RPC/gateway path should adopt the same explicit `deploy_account_tx_hash` parameter rather than relying on the implicit mempool presence check.

### Proof of Concept

```
1. Alice submits:
     deploy_account { class_hash: C, salt: S, nonce: 0, sig: valid }
     → address X is deterministic from (C, S)
     → mempool now contains X

2. Attacker submits (before Alice submits her own invoke):
     invoke {
       sender_address: X,
       nonce: 1,
       calldata: [drain_alice_funds_selector, ...],
       signature: [0x1337, 0xdead]   // arbitrary, invalid
     }

3. Gateway stateful validator:
     account_nonce = get_nonce(X) = 0          ✓ (X not deployed yet)
     validate_nonce(nonce=1, account_nonce=0)   ✓ (within gap)
     validate_by_mempool(nonce=1)               ✓ (no duplicate)
     skip_stateful_validations:
       tx.nonce()==1 && account_nonce==0        ✓
       account_tx_in_pool_or_recent_block(X)    ✓ (Alice's deploy_account is there)
       → returns true (SKIP __validate__)
     run_validate_entry_point: SKIPPED

4. Attacker's transaction is now in the mempool at nonce=1 for address X.
   Alice's own invoke(nonce=1) is rejected as a duplicate nonce.
   At execution time, attacker's transaction reverts (__validate__ fails),
   but Alice's nonce=1 slot was squatted for the duration.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** crates/apollo_mempool/src/mempool.rs (L697-700)
```rust
    pub fn account_tx_in_pool_or_recent_block(&self, account_address: ContractAddress) -> bool {
        self.state.contains_account(account_address)
            || self.tx_pool.contains_account(account_address)
    }
```

**File:** crates/native_blockifier/src/py_validator.rs (L98-121)
```rust
    pub fn should_run_stateful_validations(
        &mut self,
        account_tx: &AccountTransaction,
        deploy_account_tx_hash: Option<TransactionHash>,
    ) -> StatefulValidatorResult<bool> {
        if account_tx.tx_type() != TransactionType::InvokeFunction {
            return Ok(true);
        }
        let tx_info = account_tx.create_tx_info();
        let nonce = self.stateful_validator.get_nonce(tx_info.sender_address())?;

        let deploy_account_not_processed =
            deploy_account_tx_hash.is_some() && nonce == Nonce(Felt::ZERO);
        let tx_nonce = tx_info.nonce();
        let is_post_deploy_nonce = Nonce(Felt::ONE) <= tx_nonce;
        let nonce_small_enough_to_qualify_for_validation_skip =
            tx_nonce <= self.max_nonce_for_validation_skip;

        let skip_validate = deploy_account_not_processed
            && is_post_deploy_nonce
            && nonce_small_enough_to_qualify_for_validation_skip;

        Ok(!skip_validate)
    }
```
