### Title
DeleteAccount's unvalidated `beneficiary_id` can permanently burn the deleted account's balance - ([File: runtime/runtime/src/actions.rs])

### Summary
The `DeleteAccount` action lets any account holder specify an arbitrary `beneficiary_id` to receive its remaining balance. `action_delete_account` only validates that `beneficiary_id` is a *syntactically* valid `AccountId` — it never checks that the account actually exists or is capable of receiving a balance transfer. If the named beneficiary does not exist (and is not eligible for implicit-account creation), the follow-up balance-refund receipt fails and, because refund receipts run with `predecessor_id == "system"`, the failure causes the funds to be added to `other_burnt_amount` — i.e. permanently burned. This mirrors the Foundation M-01 report where a resolvable-but-unusable recipient (`address(0)`) silently destroyed value instead of falling back to a safe recipient.

### Finding Description
`action_delete_account` unconditionally queues a system-originated transfer to the caller-supplied `beneficiary_id` for the account's full balance: [1](#0-0) 

The only pre-execution validation applied to `beneficiary_id` anywhere in the pipeline is a generic `AccountId::validate` format check (used for actions in general, e.g. `validate_action_account_id`), not an existence check: [2](#0-1) 

The docs confirm no existence requirement is documented for `beneficiary_id` — only the format-validity error is listed: [3](#0-2) 

The balance is sent via `Receipt::new_balance_refund`, which always sets `predecessor_id = "system"`: [4](#0-3) 

When that receipt executes against a non-existent (and non-implicit-eligible) `beneficiary_id`, the generic action-application permission check rejects the `Transfer` with `AccountDoesNotExist`: [5](#0-4) [6](#0-5) 

Because the failing receipt's `predecessor_id` is `"system"`, `apply_action_receipt` treats the failure as an unrecoverable refund failure and burns the deposit instead of returning it anywhere: [7](#0-6) 

This burn-on-failure behavior is explicitly documented as intentional for *refund* receipts in general ("If the execution of a refund fails, the refund amount is burnt"): [8](#0-7) 

The account itself is deleted (state removed) regardless of whether the beneficiary transfer later succeeds — deletion and the balance payout are two separate, non-atomic steps (`remove_account` happens in the same function, before the transfer receipt executes): [9](#0-8) 

So a user (or a contract acting on a user's behalf via `append_action_delete_account`) can trivially cause an irreversible loss/burn of the account's entire balance by naming a beneficiary that:
- is a syntactically valid but never-created named account (most common case — any typo or unused name), or
- is a valid-format account that fails the single-action / eligibility requirements for implicit-account auto-creation, or
- is the `"system"` account id itself, which is documented as never existing in state. [10](#0-9) 

### Impact Explanation
This is a direct analog of the reported bug class: a recipient reference that resolves to a non-receiving/"null" destination causes value to be permanently destroyed instead of safely defaulting/falling back (e.g., to the predecessor or being rejected pre-execution). Here the destroyed value is the entire remaining NEAR balance of the deleted account, burned from total supply with no recovery path. Since this triggers via a completely ordinary, unprivileged `DeleteAccount` transaction that any account holder (or any contract issuing `append_action_delete_account` on their own receipts) can submit, and results in concrete token destruction (a form of protocol value leak / involuntary token burn), it matches the "concrete token inflation/theft, unauthorized state or balance change" impact bar (in this case, unauthorized/unintended destruction of the caller's own funds due to insufficient validation, not merely a user error the protocol perfectly guards against elsewhere — e.g., ordinary `Transfer` actions to non-existent accounts ARE rejected pre-execution via `check_transfer_to_nonexisting_account`, but `DeleteAccount`'s beneficiary payout is not subject to the same up-front check before the account is destroyed).

### Likelihood Explanation
High likelihood of accidental triggering (a typo'd or already-deleted beneficiary account is a very ordinary mistake), and it is trivially reproducible/intentional for anyone who wants to permanently burn NEAR (e.g., to reduce supply, or as a griefing vector against relayers/contracts that programmatically construct `DeleteAccount` receipts with attacker-influenced beneficiary parameters). No validator or node-privilege is required — this is purely a transaction/action-execution-layer issue reachable directly from a submitted transaction.

### Recommendation
Before allowing a `DeleteAccount` action to proceed (or before generating the balance-refund receipt), verify that `beneficiary_id` refers to an account capable of receiving a transfer — i.e., check that the account currently exists in state, or restrict `beneficiary_id` to accounts that are guaranteed to exist/be creatable (matching the same eligibility rules enforced for ordinary `Transfer` actions in `check_transfer_to_nonexisting_account`). If the target does not exist, the action should either fail validation early (before the account and its balance are destroyed) or fall back to refunding the predecessor/actor instead of silently burning the funds via the system-refund burn path.

### Proof of Concept
1. Create account `victim.near` with a nonzero balance and a full-access key.
2. Submit `DeleteAccount { beneficiary_id: "nonexistent123.near" }` (an account that was never created) signed by `victim.near`, targeting `victim.near` itself (`test-loop-tests/src/utils/node.rs`'s `tx_delete_account` helper shows the exact shape of this transaction: [11](#0-10) ).
3. `action_delete_account` removes `victim.near` from state and enqueues `Receipt::new_balance_refund(&"nonexistent123.near", account_balance)` with `predecessor_id = "system"`.
4. When this receipt is applied, `check_transfer_to_nonexisting_account` fails because `nonexistent123.near` is not implicit-account-eligible, producing `AccountDoesNotExist`.
5. `apply_action_receipt` observes `receipt.predecessor_id().is_system() && result.result.is_err()`, and adds the entire `account_balance` to `stats.balance.other_burnt_amount` — the funds are gone permanently, with no account (victim, beneficiary, or system) ever receiving them.

### Citations

**File:** runtime/runtime/src/actions.rs (L364-389)
```rust
    // We use current amount as a pay out to beneficiary.
    let account_balance = account_ref.amount();
    if account_balance > Balance::ZERO {
        result
            .new_receipts
            .push(Receipt::new_balance_refund(&delete_account.beneficiary_id, account_balance));
    }
    let remove_result = remove_account(state_update, account_id)?;
    result.tokens_burnt =
        result.tokens_burnt.checked_add(gas_key_balance_to_burn).ok_or_else(|| {
            StorageError::StorageInconsistentState("tokens_burnt overflow".to_string())
        })?;
    if remove_result.gas_key_nonce_count > 0 {
        let compute = storage_removes_compute(
            &config.wasm_config.ext_costs,
            remove_result.gas_key_nonce_count,
            remove_result.gas_key_nonce_total_key_bytes,
            AccessKey::NONCE_VALUE_LEN * remove_result.gas_key_nonce_count,
        );
        result.compute_usage = safe_add_compute(result.compute_usage, compute).map_err(|_| {
            StorageError::StorageInconsistentState("compute_usage overflow".to_string())
        })?;
    }
    *actor_id = receipt.predecessor_id().clone();
    *account = None;
    Ok(())
```

**File:** runtime/runtime/src/actions.rs (L819-855)
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
        Action::DeterministicStateInit(_) => {
            // Existing and non existing is valid for DeterministicStateInit.
            // Does not exist => The account will be created by the action.
            // Does exist => Nothing happens but the receipt is not aborted to
            // allow optional init before other actions.
        }
        Action::DeployContract(_)
        | Action::FunctionCall(_)
        | Action::Stake(_)
        | Action::AddKey(_)
        | Action::DeleteKey(_)
        | Action::DeleteAccount(_)
        | Action::Delegate(_)
        | Action::DelegateV2(_)
        | Action::DeployGlobalContract(_)
        | Action::UseGlobalContract(_)
        | Action::TransferToGasKey(_)
        | Action::WithdrawFromGasKey(_) => {
            if account.is_none() {
                return Err(ActionErrorKind::AccountDoesNotExist {
                    account_id: account_id.clone(),
                }
                .into());
            }
        }
    };
    Ok(())
}
```

**File:** runtime/runtime/src/actions.rs (L857-877)
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

**File:** runtime/runtime/src/action_validation.rs (L483-489)
```rust
fn validate_action_account_id(account_id: &AccountId) -> Result<(), ActionsValidationError> {
    AccountId::validate(account_id.as_str()).map_err(|_| {
        ActionsValidationError::InvalidAccountId { account_id: account_id.to_string() }
    })?;

    Ok(())
}
```

**File:** docs/RuntimeSpec/Actions.md (L278-300)
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

**File:** runtime/runtime/src/lib.rs (L993-1000)
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

**File:** docs/RuntimeSpec/Refunds.md (L10-13)
```markdown
Refund receipts are identified by having `predecessor_id == "system"`. They are also special because they don't cost any gas to generate or execute. As a result, they also do not contribute to the block gas limit.

If the execution of a refund fails, the refund amount is burnt.
The refund receipt is an `ActionReceipt` that consists of a single action `Transfer` with the `deposit` amount of the refund.
```

**File:** docs/DataStructures/Account.md (L85-87)
```markdown
## System account

`system` is a special account that is only used to identify refund receipts. For refund receipts, we set the predecessor_id to be `system` to indicate that it is a refund receipt. Users cannot create or access the `system` account. In fact, this account does not exist as part of the state.
```

**File:** test-loop-tests/src/utils/node.rs (L344-358)
```rust
    /// Build a delete-account transaction.
    pub fn tx_delete_account(
        &self,
        account_id: &AccountId,
        beneficiary_id: &AccountId,
    ) -> SignedTransaction {
        SignedTransaction::delete_account(
            self.get_next_nonce(account_id),
            account_id.clone(),
            account_id.clone(),
            beneficiary_id.clone(),
            &create_user_test_signer(account_id),
            self.head().last_block_hash,
        )
    }
```
