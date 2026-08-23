### Title
Permanent burning of account balance when `DeleteAccount`'s `beneficiary_id` does not exist or is unreachable - (File: `runtime/runtime/src/actions.rs`)

### Summary
The `DeleteAccount` action lets any account holder specify an arbitrary `beneficiary_id` to receive the account's remaining balance upon deletion. The protocol validates only that `beneficiary_id` is a *syntactically* valid `AccountId` — it never checks that the account actually exists or is reachable. If the account is deleted, the balance-refund receipt to a non-existent `beneficiary_id` fails, and because it is a system-refund receipt, the deposited tokens are unconditionally burned rather than returned. This mirrors the Gearbox `CreditManager` pattern where a caller-controlled destination parameter (`to`) is never checked against a "black hole" value, so a benign mistake destroys the caller's funds.

### Finding Description
`DeleteAccountAction` carries a `beneficiary_id: AccountId` field [1](#0-0) . Validation for this action is performed by `validate_delete_action`, which only ensures the ID parses as a valid `AccountId` — no existence check is performed: [2](#0-1) 

This is confirmed by the codebase's own unit test, which explicitly treats a `beneficiary_id` equal to the account being deleted (or any arbitrary account) as a "valid action" without regard to existence: [3](#0-2) 

At execution time, `action_delete_account` unconditionally deletes the account (`*account = None;`) and enqueues a `Receipt::new_balance_refund(&delete_account.beneficiary_id, account_balance)` carrying the entire account balance to `beneficiary_id`, with no existence check and no rollback path once the deleting account is gone: [4](#0-3) 

`Receipt::new_balance_refund` builds this as a system-refund receipt (`predecessor_id: "system"`, a plain `Transfer` action): [5](#0-4) 

When this refund receipt is later applied to `beneficiary_id`, `check_account_existence` is invoked for the `Transfer` action. If the target account doesn't exist and is not implicit-account-creation-eligible (i.e. it's a named account, e.g. mistyped, deleted, or never created), the action fails with `AccountDoesNotExist`: [6](#0-5) [7](#0-6) 

Critically, when a receipt whose predecessor is `system` (i.e. any refund, including this balance refund) fails, the runtime does **not** attempt to return the funds anywhere else — it permanently burns them: [8](#0-7) 

This is directly analogous to the reported Gearbox bug: a caller-supplied destination parameter (`beneficiary_id` here, `to` there) is never checked for validity/reachability, so a benign mistake (e.g. a typo, deleting the intended beneficiary account beforehand, or specifying an account that was never created) irreversibly destroys the funds of the account owner who called `DeleteAccount`. There is no recommended check equivalent to Gearbox's suggested `to != address(0)` — nearcore never checks `beneficiary_id` account existence before allowing the source account (and its balance) to be irrevocably deleted.

### Impact Explanation
Any regular (unprivileged) account holder can lose their entire account balance by mistake when calling `DeleteAccount` with a `beneficiary_id` that does not correspond to an existing (or account-creation-eligible) account. Because the source account is deleted in the same action as the refund is scheduled, and the failed refund is burned rather than reverted or returned to the original account, this is an irreversible, permanent loss of funds triggered purely by a user error — no malicious actor is required. This matches the "concrete token... theft/loss" and "unauthorized state or balance change" impact classes for in-scope Ask findings.

### Likelihood Explanation
This requires no special privileges, no validator/node compromise, and no unusual conditions — it is triggered by an ordinary user submitting a normal transaction with a `DeleteAccount` action and a mistaken/incorrect (but syntactically valid) `beneficiary_id`. This is a plausible and fairly common user mistake (typos in account IDs, specifying an account that has itself been deleted, or an account that was never created), making the likelihood of accidental triggering non-trivial for a chain that processes untrusted user-submitted transactions.

### Recommendation
Before permitting an account to be deleted, validate that `beneficiary_id` refers to an account that exists (or is eligible for implicit-account creation), similarly to how `check_transfer_to_nonexisting_account` already gates ordinary transfers. If `beneficiary_id` does not exist and cannot receive an implicit-account-creation transfer, the `DeleteAccount` action should fail validation/execution with an explicit error (e.g., a new `ActionErrorKind::DeleteAccountBeneficiaryDoesNotExist`) rather than silently scheduling a refund that is destined to fail and be burned.

### Proof of Concept
1. Account `alice.near` holds a nonzero balance and owns a full-access key.
2. `alice.near` submits a transaction with a single `DeleteAccountAction { beneficiary_id: "nonexistent.near" }`, where `nonexistent.near` is a syntactically valid but never-created named account (not implicit).
3. `validate_delete_action` passes because `nonexistent.near` is a syntactically valid `AccountId` [2](#0-1) .
4. `action_delete_account` executes, deletes `alice.near`'s account state, and enqueues `Receipt::new_balance_refund(&"nonexistent.near", alice_balance)` [4](#0-3) .
5. When this refund receipt is applied, `check_account_existence` for the `Transfer` action to `nonexistent.near` returns `ActionErrorKind::AccountDoesNotExist` because the account doesn't exist and is not implicit [6](#0-5) [7](#0-6) .
6. Because the receipt's predecessor is `system`, the failed refund's deposit is added to `stats.balance.other_burnt_amount` and permanently destroyed [8](#0-7) .
7. `alice.near`'s account no longer exists and the funds are irrecoverably burned — comparable to a Gearbox liquidator losing assets by mistakenly sending them `to = address(0)`.

### Citations

**File:** core/primitives/src/action/mod.rs (L70-73)
```rust
#[cfg_attr(feature = "schemars", derive(schemars::JsonSchema))]
pub struct DeleteAccountAction {
    pub beneficiary_id: AccountId,
}
```

**File:** runtime/runtime/src/action_validation.rs (L377-381)
```rust
fn validate_delete_action(action: &DeleteAccountAction) -> Result<(), ActionsValidationError> {
    validate_action_account_id(&action.beneficiary_id)?;

    Ok(())
}
```

**File:** runtime/runtime/src/action_validation.rs (L1025-1034)
```rust
    #[test]
    fn test_validate_action_valid_delete_account() {
        validate_action(
            &test_limit_config(),
            &Action::DeleteAccount(DeleteAccountAction { beneficiary_id: alice_account() }),
            &"alice.near".parse().unwrap(),
            PROTOCOL_VERSION,
        )
        .expect("valid action");
    }
```

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

**File:** runtime/runtime/src/actions.rs (L791-799)
```rust
        Action::Transfer(_) => {
            if account.is_none() {
                return check_transfer_to_nonexisting_account(
                    config,
                    account_id,
                    implicit_account_creation_eligible,
                );
            }
        }
```

**File:** runtime/runtime/src/actions.rs (L829-849)
```rust
fn check_transfer_to_nonexisting_account(
    config: &RuntimeConfig,
    account_id: &AccountId,
    implicit_account_creation_eligible: bool,
) -> Result<(), ActionError> {
    if implicit_account_creation_eligible
        && account_is_implicit(account_id, config.wasm_config.eth_implicit_accounts)
    {
        // OK. It's implicit account creation.
        // Notes:
        // - Transfer action has to be the only action in the transaction to avoid
        // abuse by hijacking this account with other public keys or contracts.
        // - Refunds don't automatically create accounts, because refunds are free and
        // we don't want some type of abuse.
        // - Account deletion with beneficiary creates a refund, so it'll not create a
        // new account.
        Ok(())
    } else {
        Err(ActionErrorKind::AccountDoesNotExist { account_id: account_id.clone() }.into())
    }
}
```

**File:** core/primitives/src/receipt.rs (L493-510)
```rust
    /// Generates a receipt with a transfer from system for a given balance without a receipt_id.
    /// This should be used for token refunds instead of gas refunds.
    /// It doesn't refund the allowance of the access key. For gas refunds use `new_gas_refund`.
    pub fn new_balance_refund(receiver_id: &AccountId, refund: Balance) -> Self {
        Receipt::V0(ReceiptV0 {
            predecessor_id: "system".parse().unwrap(),
            receiver_id: receiver_id.clone(),
            receipt_id: CryptoHash::default(),
            receipt: ReceiptEnum::Action(ActionReceipt {
                signer_id: "system".parse().unwrap(),
                signer_public_key: PublicKey::empty(KeyType::ED25519),
                gas_price: Balance::ZERO,
                output_data_receivers: vec![],
                input_data_ids: vec![],
                actions: vec![Action::Transfer(TransferAction { deposit: refund })],
            }),
        })
    }
```

**File:** runtime/runtime/src/lib.rs (L914-921)
```rust
        let gas_refund_result = if receipt.predecessor_id().is_system() {
            // If the refund fails tokens are burned.
            if result.result.is_err() {
                stats.balance.other_burnt_amount = safe_add_balance(
                    stats.balance.other_burnt_amount,
                    total_deposit(&action_receipt.actions())?,
                )?
            }
```
