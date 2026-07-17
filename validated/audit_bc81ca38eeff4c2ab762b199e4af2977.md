### Title
Account Deletion Before In-Flight Cross-Shard Refund Receipt Causes Permanent Balance Loss - (File: `runtime/runtime/src/lib.rs`)

---

### Summary

When a cross-shard action receipt fails and generates a deposit refund receipt (with `predecessor_id = "system"`), if the recipient account is deleted before the refund arrives, the refund deposit is permanently burnt. This is the NEAR analog of the "irreversible action executes before prerequisite completes" vulnerability class from the external report.

---

### Finding Description

Two interacting behaviors in the NEAR runtime create this vulnerability:

**Behavior 1 — `action_delete_account` only captures the current balance.**
In `runtime/runtime/src/actions.rs`, `action_delete_account` transfers only the account's *current* balance to the beneficiary. It does not check for, nor account for, any in-flight refund receipts that are already routed to the account but have not yet arrived. [1](#0-0) 

**Behavior 2 — Failed refund receipts burn the deposit.**
In `runtime/runtime/src/lib.rs`, `apply_action_receipt` checks whether the incoming receipt is a system refund (`predecessor_id().is_system()`). If such a refund fails to execute (e.g., because the receiver account no longer exists), the deposit is permanently added to `other_burnt_amount` — it is not re-routed or re-refunded. [2](#0-1) 

This is also explicitly documented: [3](#0-2) 

The combination means: a user can delete their account while a deposit refund receipt is in-flight toward it. When the refund arrives, the account is gone, the refund fails, and the funds are permanently burnt.

---

### Impact Explanation

The corrupted protocol value is **Alice's token balance**. The deposit she attached to a cross-shard call is permanently destroyed (added to `stats.balance.other_burnt_amount`) rather than returned to her. This is a direct, irreversible loss of user funds with no recovery path.

---

### Likelihood Explanation

Low-to-medium. The scenario requires:

1. A cross-shard call with an attached deposit (the refund is delayed by at least one block due to cross-shard routing).
2. The called contract failing (Bob can control this by deploying a contract that always reverts).
3. Alice deleting her account before the refund receipt is processed — plausible if Alice's contract is designed to self-destruct after a failed callback, or if Alice submits a delete transaction believing the call already settled.

Cross-shard receipt delays are a normal part of NEAR's sharded execution model, making the timing window real and not hypothetical.

---

### Recommendation

1. **Document the risk prominently**: Warn users and contract authors that deleting an account while cross-shard refund receipts are in-flight will permanently burn those refunds.
2. **Defensive contract design**: Contracts that self-delete in callbacks should verify no deposits are in-flight before issuing `DeleteAccount`.
3. **Protocol-level mitigation**: Consider re-routing a failed system-refund to the `signer_id` of the original receipt rather than burning, or tracking pending refund receipts per account to block premature deletion.

---

### Proof of Concept

**Step-by-step:**

1. Alice's contract (shard A) calls Bob's malicious contract (shard B) with an attached deposit. This creates a cross-shard action receipt.
2. Bob's contract is designed to always fail. It fails, and the runtime generates a deposit refund receipt: `predecessor_id = "system"`, `receiver_id = Alice's contract`.
3. Alice's contract (or Alice directly) issues a `DeleteAccount` transaction. `action_delete_account` transfers only Alice's *current* balance to the beneficiary and removes the account from state.
4. The deposit refund receipt (from step 2) arrives at shard A in a subsequent block. Alice's account no longer exists.
5. `apply_action_receipt` processes the refund. Because `predecessor_id().is_system()` is true and `result.result.is_err()` (account does not exist), the deposit is added to `other_burnt_amount` and permanently destroyed.

**Root cause — burn path:** [4](#0-3) 

**Root cause — deletion ignores in-flight receipts:** [5](#0-4) 

**Refund receipt construction (predecessor = "system"):** [6](#0-5)

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

**File:** docs/RuntimeSpec/Refunds.md (L12-13)
```markdown
If the execution of a refund fails, the refund amount is burnt.
The refund receipt is an `ActionReceipt` that consists of a single action `Transfer` with the `deposit` amount of the refund.
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
