### Title
`DeleteAccountAction` Missing Self-Beneficiary Validation Causes Permanent Balance Burn - (File: runtime/runtime/src/actions.rs)

### Summary
`action_delete_account` in nearcore's runtime does not validate that `beneficiary_id != account_id`. When a user (or a smart contract) submits a `DeleteAccount` action with `beneficiary_id` equal to the account being deleted, the account's entire balance is permanently burnt instead of being transferred to any beneficiary.

### Finding Description
`action_delete_account` in `runtime/runtime/src/actions.rs` processes a `DeleteAccountAction` by:
1. Creating a `Receipt::new_balance_refund(&delete_account.beneficiary_id, account_balance)` — a system-predecessor receipt targeting `beneficiary_id`
2. Calling `remove_account(state_update, account_id)` — permanently deleting the account from state [1](#0-0) 

When `beneficiary_id == account_id`, the refund receipt is addressed to the account that was just deleted. When that receipt is later applied, the account no longer exists. The runtime's `action_transfer_or_implicit_account_creation` takes the `else` branch (account is `None`), which contains only a `debug_assert!(!is_refund)` — a no-op in release builds — and then calls `action_implicit_account_creation_transfer`. [2](#0-1) 

For a named account (e.g. `alice.near`), implicit account creation fails. Since the receipt has `predecessor_id == "system"`, the runtime's failure path explicitly burns the deposit: [3](#0-2) 

The action validation layer checks only that `beneficiary_id` is a syntactically valid account ID, that `DeleteAccount` is the last action, and that the account is not staking. There is no check that `beneficiary_id != account_id`. [4](#0-3) 

### Impact Explanation
The account's entire liquid balance is permanently burnt (removed from total supply) rather than transferred to any beneficiary. The corrupted protocol value is the account balance: it is debited from the deleted account but never credited to any live account, violating the token conservation invariant. The `debug_assert!(!is_refund)` in the non-existent-account transfer path confirms the developers did not intend for system refund receipts to arrive at non-existent accounts.

### Likelihood Explanation
An unprivileged user can trigger this by submitting a signed `DeleteAccount` transaction with `beneficiary_id` set to their own `account_id`. This passes all current transaction and action validation. A buggy or malicious smart contract can also trigger this via the `promise_batch_action_delete_account` host function, causing any account that calls it to permanently lose its balance.

### Recommendation
Add a validation check in `action_delete_account` (or in `validate_action` for `Action::DeleteAccount`) that rejects the action when `delete_account.beneficiary_id == account_id`. This mirrors the fix applied to PSP22Wrapper (PR #140) and prevents the self-referential address from breaking the balance accounting invariant.

### Proof of Concept
1. Alice has account `alice.near` with 100 NEAR.
2. Alice submits a transaction:
   ```
   signer_id: "alice.near"
   receiver_id: "alice.near"
   actions: [DeleteAccount { beneficiary_id: "alice.near" }]
   ```
3. `action_delete_account` creates `Receipt::new_balance_refund("alice.near", 100 NEAR)` then calls `remove_account` — `alice.near` is gone from state.
4. The system refund receipt arrives at `alice.near`. The account does not exist. `action_transfer_or_implicit_account_creation` enters the `else` branch; `action_implicit_account_creation_transfer` fails for a named account.
5. Because `predecessor_id == "system"` and `result.result.is_err()`, the runtime adds 100 NEAR to `stats.balance.other_burnt_amount`.
6. Alice's 100 NEAR is permanently burnt. No account receives the balance.

### Citations

**File:** runtime/runtime/src/actions.rs (L349-356)
```rust
    // We use current amount as a pay out to beneficiary.
    let account_balance = account_ref.amount();
    if account_balance > Balance::ZERO {
        result
            .new_receipts
            .push(Receipt::new_balance_refund(&delete_account.beneficiary_id, account_balance));
    }
    let remove_result = remove_account(state_update, account_id)?;
```

**File:** runtime/runtime/src/lib.rs (L914-922)
```rust
        let gas_refund_result = if receipt.predecessor_id().is_system() {
            // If the refund fails tokens are burned.
            if result.result.is_err() {
                stats.balance.other_burnt_amount = safe_add_balance(
                    stats.balance.other_burnt_amount,
                    total_deposit(&action_receipt.actions())?,
                )?
            }
            GasRefundResult::default()
```

**File:** runtime/runtime/src/lib.rs (L2842-2878)
```rust
    Ok(if let Some(account) = account.as_mut() {
        let is_gas_refund = is_refund && action_receipt.signer_id() == receipt.receiver_id();
        // For gas refunds, try to refund to the gas key first. If the signer key is a gas key,
        // the refund goes to the gas key balance and we skip crediting the account balance.
        if is_gas_refund
            && try_refund_gas_key_balance(
                state_update,
                receipt.receiver_id(),
                &action_receipt.signer_public_key(),
                deposit,
            )?
        {
            return Ok(());
        }
        action_transfer(account, deposit)?;
        if is_gas_refund {
            try_refund_allowance(
                state_update,
                receipt.receiver_id(),
                &action_receipt.signer_public_key(),
                deposit,
            )?;
        }
    } else {
        debug_assert!(!is_refund);
        action_implicit_account_creation_transfer(
            state_update,
            &apply_state,
            &apply_state.config.fees,
            account,
            actor_id,
            receipt.receiver_id(),
            deposit,
            apply_state.block_height,
            epoch_info_provider,
        );
    })
```

**File:** docs/RuntimeSpec/Actions.md (L293-314)
```markdown
**Validation Error**:

- If `beneficiary_id` is not a valid account id, the following error will be returned

```rust
/// Invalid account ID.
InvalidAccountId { account_id: AccountId },
```

- If this action is not the last action in the action list of a receipt, the following error will be returned

```rust
/// The delete action must be a final action in transaction
DeleteActionMustBeFinal
```

- If the account still has locked balance due to staking, the following error will be returned

```rust
/// Account is staking and can not be deleted
DeleteAccountStaking { account_id: AccountId }
```
```
