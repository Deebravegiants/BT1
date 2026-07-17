### Title
`DeleteAccount` beneficiary existence not validated at submission — funds permanently burnt on non-existent `beneficiary_id` - (File: `runtime/runtime/src/action_validation.rs`)

### Summary

`validate_delete_action` only checks that `beneficiary_id` is a syntactically valid account-ID string. It never verifies that the account actually exists. When the runtime executes `DeleteAccount`, it emits a system-origin balance-refund receipt (`predecessor_id == "system"`) carrying the deleted account's entire balance to `beneficiary_id`. If that account does not exist, the Transfer inside the refund receipt fails, and — per the documented refund semantics — **the refund amount is permanently burnt**. There is no recovery path: the account is already gone.

### Finding Description

`validate_delete_action` in `runtime/runtime/src/action_validation.rs` performs only a format check on `beneficiary_id`:

```rust
fn validate_delete_action(action: &DeleteAccountAction) -> Result<(), ActionsValidationError> {
    validate_action_account_id(&action.beneficiary_id)?;
    Ok(())
}
``` [1](#0-0) 

No state lookup is performed to confirm the account exists. The transaction is accepted and the nonce is consumed.

At execution time, `action_delete_account` unconditionally emits a `Receipt::new_balance_refund` to `beneficiary_id`:

```rust
if account_balance > Balance::ZERO {
    result.new_receipts.push(
        Receipt::new_balance_refund(&delete_account.beneficiary_id, account_balance)
    );
}
``` [2](#0-1) 

`Receipt::new_balance_refund` constructs a system-origin receipt (`predecessor_id == "system"`) containing a single `Transfer` action: [3](#0-2) 

When this receipt is applied, `check_account_existence` is called for the `Transfer`. Because the receipt is a system refund, `implicit_account_creation_eligible` is `false` (the docs explicitly state "Refunds don't automatically create accounts"). If `beneficiary_id` does not exist and is not an ETH-implicit address, `check_transfer_to_nonexisting_account` returns `AccountDoesNotExist`: [4](#0-3) 

The refund receipt then fails. Per the protocol specification:

> If the execution of a refund fails, the refund amount is burnt. [5](#0-4) 

The deleted account's entire balance is permanently destroyed. The `DeleteAccountAction` struct and its documentation do not warn of this outcome: [6](#0-5) [7](#0-6) 

### Impact Explanation

An unprivileged user who submits a `DeleteAccount` action with a `beneficiary_id` that does not exist (typo, stale reference, or a beneficiary account that was deleted in a concurrent transaction) will have their entire account balance permanently burnt. The account is already removed from state before the refund receipt is processed, so there is no rollback and no recovery path. The corrupted protocol value is the user's **balance**, which transitions from a positive amount to zero (burnt) rather than being credited to the intended beneficiary.

### Likelihood Explanation

The trigger is reachable by any unprivileged user through a standard signed transaction submitted via public RPC. Realistic scenarios include:

- A typo in the `beneficiary_id` string (e.g., `"alice.neer"` instead of `"alice.near"`).
- A beneficiary account that was deleted between the time the transaction was signed and the time it was executed (NEAR's asynchronous receipt model means the refund receipt is processed one or more blocks after the `DeleteAccount` receipt).
- A wallet or SDK that constructs the `DeleteAccount` action without first verifying the beneficiary exists.

The protocol documentation states the balance "is transferred to `beneficiary_id`" without warning that a non-existent beneficiary causes permanent loss, making user error more likely.

### Recommendation

1. **Validate beneficiary existence at execution time**: In `action_delete_account`, before emitting the balance-refund receipt, check that `beneficiary_id` exists in state. If it does not, abort the action with a new `ActionErrorKind` (e.g., `DeleteAccountBeneficiaryDoesNotExist`) rather than silently emitting a doomed refund receipt.
2. **Document the behavior explicitly**: Update `docs/RuntimeSpec/Actions.md` under `DeleteAccountAction` to state that if `beneficiary_id` does not exist at execution time, the balance is burnt.
3. **Optionally add a static validation hint**: `validate_delete_action` could be extended (in the state-aware validation path `validate_verify_and_charge_transaction`) to reject the transaction early if the beneficiary is provably absent.

### Proof of Concept

1. Alice has account `alice.near` with balance 100 NEAR.
2. Alice submits a `DeleteAccount` transaction with `beneficiary_id: "typo.near"` (a non-existent account).
3. `validate_delete_action` accepts the transaction — `"typo.near"` is a syntactically valid account ID.
4. The runtime executes `action_delete_account`: Alice's account is removed from state; a `Receipt::new_balance_refund("typo.near", 100 NEAR)` is emitted.
5. The refund receipt is routed to the shard owning `"typo.near"`. The `Transfer` action fails with `AccountDoesNotExist`.
6. Because the failed receipt has `predecessor_id == "system"`, the 100 NEAR is burnt — no further refund is generated.
7. Alice's 100 NEAR is permanently lost. There is no recovery mechanism.

### Citations

**File:** runtime/runtime/src/action_validation.rs (L377-381)
```rust
fn validate_delete_action(action: &DeleteAccountAction) -> Result<(), ActionsValidationError> {
    validate_action_account_id(&action.beneficiary_id)?;

    Ok(())
}
```

**File:** runtime/runtime/src/actions.rs (L350-355)
```rust
    let account_balance = account_ref.amount();
    if account_balance > Balance::ZERO {
        result
            .new_receipts
            .push(Receipt::new_balance_refund(&delete_account.beneficiary_id, account_balance));
    }
```

**File:** runtime/runtime/src/actions.rs (L829-848)
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
```

**File:** core/primitives/src/receipt.rs (L496-510)
```rust
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

**File:** docs/RuntimeSpec/Refunds.md (L12-12)
```markdown
If the execution of a refund fails, the refund amount is burnt.
```

**File:** core/primitives/src/action/mod.rs (L71-73)
```rust
pub struct DeleteAccountAction {
    pub beneficiary_id: AccountId,
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
