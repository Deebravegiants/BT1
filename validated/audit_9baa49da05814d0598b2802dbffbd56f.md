### Title
Permanent loss of an account's entire balance if `DeleteAccountAction.beneficiary_id` names a non-existent account - (File: `runtime/runtime/src/actions.rs`)

### Summary
`DeleteAccountAction` lets a user specify an arbitrary `beneficiary_id` to receive the deleted account's remaining balance. The runtime never verifies that `beneficiary_id` actually exists (only that it is a syntactically valid `AccountId`) before deleting the source account and issuing the transfer. If the beneficiary account does not exist (e.g., mistyped, never created, or later deleted), the resulting balance-transfer receipt fails and the tokens are permanently burned, exactly analogous to the reported `PANTHEON.sol` bug where an unset/incorrect `FEE_ADDRESS` causes fees to be irrecoverably lost to the zero address.

### Finding Description
`DeleteAccountAction` is defined with an unchecked-for-existence `beneficiary_id`: [1](#0-0) 

In `action_delete_account`, the runtime pays out the full account balance to `beneficiary_id` via a "system" balance-refund receipt, then unconditionally deletes the source account, with no check that `beneficiary_id` is a live account: [2](#0-1) 

Per the documented action-level errors, `DeleteAccountAction` validation only rejects a **malformed** `beneficiary_id` string (`InvalidAccountId`); there is no check that the account exists: [3](#0-2) 

When the resulting refund receipt is later executed, if the beneficiary account does not exist, the transfer fails (as demonstrated for ordinary transfers to non-existent accounts): [4](#0-3) 

Because refund/system receipts (`predecessor_id().is_system()`) are used for this payout, a failed refund is explicitly burned rather than retried or bounced back to the original owner: [5](#0-4) 

This mirrors the reported bug class precisely: value is routed to a destination that was never validated to be capable of receiving/holding it (the zero address in the Solidity report; a non-existent NEAR account here), and once the sending action is committed, the funds are irrecoverably destroyed with no recovery path — same permanent-loss-of-funds root cause (missing existence/validity check on a fee/beneficiary destination before an irreversible transfer + state deletion).

### Impact Explanation
Any unprivileged account holder who calls `DeleteAccount` (directly or via `promise_batch_action_delete_account`) with a `beneficiary_id` that does not exist as an account permanently burns their entire remaining NEAR balance. This is a real, concrete, irreversible balance loss triggered purely by a standard user transaction/receipt, reducing total supply via `other_burnt_amount` with no path to recovery — matching the "permanent loss of fees/funds" impact class from the source report.

### Likelihood Explanation
Likelihood is moderate: this requires user error (typo, wrong account, or targeting a not-yet-created/soon-to-be-deleted account) rather than a directly exploitable third-party attack for profit. It is self-inflicted, similar to the original report's scenario where the *owner* forgot to configure `FEE_ADDRESS`. It is trivially reachable by any account via a single `DeleteAccount` action and requires no special privileges — but it does not give an attacker a way to steal *other* users' funds, only to (perhaps be tricked into, via a malicious dApp/relayer suggesting a bogus beneficiary) destroy the caller's own balance.

### Recommendation
Before permanently deleting the source account and issuing the balance-refund receipt in `action_delete_account` (`runtime/runtime/src/actions.rs:314-390`), verify that `beneficiary_id` corresponds to an existing account (or is a valid implicit-account form capable of receiving funds), and reject the action (e.g., with a new `ActionErrorKind::BeneficiaryAccountDoesNotExist`) if it does not. Alternatively, document this behavior extremely clearly at the SDK/wallet/CLI layer and have wallets/CLIs perform a pre-flight existence check on `beneficiary_id` before submitting the transaction, since a protocol-level state read of the beneficiary account inside `apply_action` (which already has `state_update` in scope) is feasible without introducing cross-shard complications for local beneficiaries; for cross-shard beneficiaries this would need a design that accepts the existing async-refund/burn semantics or moves the check to transaction validation with best-effort local-shard verification.

### Proof of Concept
1. Create account `alice.near` with a positive balance.
2. Have `alice.near` submit a `DeleteAccount` action with `beneficiary_id = "nonexistent-account.near"` (an account that has never been created).
3. The runtime executes `action_delete_account`, which unconditionally issues `Receipt::new_balance_refund(&"nonexistent-account.near", account_balance)` and deletes `alice.near` (`runtime/runtime/src/actions.rs:364-371`).
4. The refund receipt is processed with `predecessor_id() == "system"`; since `nonexistent-account.near` does not exist, the inner transfer fails with `AccountDoesNotExist` (analogous to `test_refund_on_send_money_to_non_existent_account`, `integration-tests/src/tests/standard_cases/mod.rs:784-822`).
5. Per `runtime/runtime/src/lib.rs:993-1001`, because the refund failed, the deposit is added to `stats.balance.other_burnt_amount` — the tokens are permanently burned, and `alice.near`'s account no longer exists to reclaim them.

### Citations

**File:** core/primitives/src/action/mod.rs (L70-73)
```rust
#[cfg_attr(feature = "schemars", derive(schemars::JsonSchema))]
pub struct DeleteAccountAction {
    pub beneficiary_id: AccountId,
}
```

**File:** runtime/runtime/src/actions.rs (L364-371)
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

**File:** docs/RuntimeSpec/Actions.md (L278-314)
```markdown
## DeleteAccountAction

```rust
pub struct DeleteAccountAction {
    /// The remaining account balance will be transferred to the AccountId below
    pub beneficiary_id: AccountId,
}
```

**Outcomes**:

- The account, as well as all the data stored under the account, is deleted and the tokens are transferred to `beneficiary_id`.

### Errors

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

**File:** integration-tests/src/tests/standard_cases/mod.rs (L784-822)
```rust
pub fn test_refund_on_send_money_to_non_existent_account(node: impl Node) {
    let account_id = &node.account_id().unwrap();
    let node_user = node.user();
    let root = node_user.get_state_root();
    let money_used = Balance::from_yoctonear(10);
    // Successful atomic transfer has the same cost as failed atomic transfer.
    let fee_helper = fee_helper(&node);
    let transfer_cost = fee_helper.transfer_cost();
    let transaction_result =
        node_user.send_money(account_id.clone(), eve_dot_alice_account(), money_used).unwrap();
    assert_eq!(
        transaction_result.status,
        FinalExecutionStatus::Failure(
            ActionError {
                index: Some(0),
                kind: ActionErrorKind::AccountDoesNotExist { account_id: eve_dot_alice_account() }
            }
            .into()
        )
    );
    assert_eq!(transaction_result.receipts_outcome.len(), 2 + extra_refund_outcomes());
    let new_root = node_user.get_state_root();
    assert_ne!(root, new_root);
    let result1 = node_user.view_account(account_id).unwrap();
    assert_eq!(
        (result1.amount, result1.locked),
        (
            TESTING_INIT_BALANCE
                .checked_sub(TESTING_INIT_STAKE)
                .unwrap()
                .checked_sub(transfer_cost)
                .unwrap(),
            TESTING_INIT_STAKE
        )
    );
    assert_eq!(node_user.get_access_key_nonce_for_signer(account_id).unwrap(), 1);
    let result2 = node_user.view_account(&eve_dot_alice_account());
    assert!(result2.is_err());
}
```

**File:** runtime/runtime/src/lib.rs (L993-1001)
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
