### Title
Deposit refunds are permanently burned instead of retried when the refund recipient account no longer exists - (File: `runtime/runtime/src/lib.rs`)

### Summary
When an action receipt fails, NEAR generates a "deposit refund" — a system `Transfer` receipt sending the failed receipt's attached deposit back to the predecessor account. If that predecessor account has since been deleted (e.g., self-deletion via `DeleteAccount`), the refund's `Transfer` action fails with `AccountDoesNotExist` because refund receipts are deliberately excluded from implicit-account (re)creation. The runtime then treats this second failure as unrecoverable and permanently burns the deposit amount rather than retrying or re-routing it, exactly mirroring the VUSD `processWithdrawals` failure mode where a failed payout is dropped and the funds are lost forever.

### Finding Description
Refund receipts are `ActionReceipt`s with `predecessor_id == "system"`, consisting of a single `Transfer` action carrying the deposit amount [1](#0-0) .

When a refund's own execution fails, `apply_action_receipt` does not attempt any further retry or alternate payout path — it burns the entire deposit into `other_burnt_amount`: [2](#0-1) 

The refund can fail because refund transfers are explicitly barred from triggering implicit account (re)creation. `apply_action` computes `implicit_account_creation_eligible = is_the_only_action && !is_refund`, so for any refund `is_refund == true` disables the implicit-creation path: [3](#0-2) 

`check_account_existence` then routes a `Transfer` to a missing account through `check_transfer_to_nonexisting_account`, which explicitly documents that refunds do not get to (re)create the destination account: [4](#0-3) 

Deposit refunds target `receipt.balance_refund_receiver()`, which by default is the predecessor of the failed receipt — i.e., the account that originally sent the receipt and paid the attached deposit. If that account is deleted (self-deletion via `Action::DeleteAccount`, which any account holder can trigger unilaterally to move its remaining balance to a beneficiary) between the time the original receipt is sent and the time the deposit refund is processed (receipts are processed asynchronously, often in a later block and/or on a different shard), the refund's `Transfer` action hits `account.is_none()`, fails with `AccountDoesNotExist`, and the whole refund receipt fails. Because the refund receipt itself has `predecessor_id == "system"`, this failure is caught by the burn branch shown above instead of generating a further refund or notification — the tokens are gone permanently.

### Impact Explanation
This is a concrete, permanent loss of tokens for a completely ordinary, unprivileged sequence of actions: (1) submit a `FunctionCall`/action receipt with an attached deposit that is expected to fail (or races another shard's execution) and (2) delete the sending account before the resulting deposit-refund receipt is processed. The deposit that should be returned to the user is instead burned via `other_burnt_amount`, i.e., it is removed from the user's control and from circulating token flow with no path to recovery, directly mirroring the "funds lost forever" impact described in the report. Unlike ordinary rent/fee burning, this loss is not proportional to any service rendered — it is the user's own principal deposit that vanishes due to an ordering race that is trivially reachable by any account holder (including unintentionally, e.g., a wallet or bot that deletes an idle account shortly after firing off a transaction).

### Likelihood Explanation
The precondition — a receiver that no longer exists when a system-predecessor refund receipt executes — requires only two unprivileged actions available to any account: sending a receipt carrying a deposit that is likely to fail (e.g., calling a nonexistent method, exceeding balance, or racing a receiver-side failure), and deleting the sender account shortly afterward via the ordinary `DeleteAccount` action. Because receipts execute asynchronously (cross-shard, possibly delayed by congestion or multiple blocks), the timing window is realistic without any validator or network-layer collusion, and no special permissions are needed. This makes the scenario feasible for any wallet/bot pattern that closes out unused accounts soon after use.

### Recommendation
When a deposit-refund `Transfer` fails because the recipient account no longer exists, avoid unconditionally burning the deposit. Options include: (a) redirecting unclaimed refunds to a well-defined fallback (e.g., burn is acceptable only if this is documented/expected as an inherent economic cost, but consider crediting it to the receipt's `refund_to_account_id` beneficiary, once that mechanism is implemented, or to the account-deletion beneficiary if traceable), or (b) making account self-deletion check/hold back for any outstanding receipts targeting the account before allowing deletion, or (c) explicitly documenting and bounding this as an accepted design trade-off (as `actions.rs` comments already partially do) so it is not treated as a latent fund-loss bug, and adding metrics/telemetry so the burnt amount from this specific cause is observable and can be reasoned about for economic accounting.

### Proof of Concept
1. Account `alice.near` sends a `FunctionCall` receipt with a nonzero `deposit` to `bob.near` where the call is designed to fail (e.g., calling a non-existent method, or a method that will panic due to insufficient gas/logic), producing a deposit-refund receipt back to `alice.near` (`predecessor_id = "system"`, single `Transfer` action with the deposit) as described in `docs/RuntimeSpec/Refunds.md`.
2. Before that refund receipt is processed (it can be delayed across blocks/shards, per `runtime/runtime/src/lib.rs:2441` delayed-receipt processing), `alice.near` submits `Action::DeleteAccount` to remove itself, transferring its remaining balance to a beneficiary.
3. When the refund receipt for the earlier failed call finally executes, `apply_action` finds `account.is_none()` for `alice.near`, and because `is_refund == true`, `implicit_account_creation_eligible` is `false`, so `check_transfer_to_nonexisting_account` (`runtime/runtime/src/actions.rs:857-877`) returns `ActionErrorKind::AccountDoesNotExist`.
4. The refund receipt result becomes `Err`; since `receipt.predecessor_id().is_system()` is true, `apply_action_receipt` (`runtime/runtime/src/lib.rs:993-1000`) adds the full deposit amount to `stats.balance.other_burnt_amount`, permanently burning the original deposit that should have gone back to `alice.near`.

### Citations

**File:** docs/RuntimeSpec/Refunds.md (L10-18)
```markdown
Refund receipts are identified by having `predecessor_id == "system"`. They are also special because they don't cost any gas to generate or execute. As a result, they also do not contribute to the block gas limit.

If the execution of a refund fails, the refund amount is burnt.
The refund receipt is an `ActionReceipt` that consists of a single action `Transfer` with the `deposit` amount of the refund.

## Deposit Refunds

Deposit refunds are generated when an action receipt fails to execute. All attached deposit amounts are summed together and
sent as a refund to a `predecessor_id` (because only the predecessor can attach deposits).
```

**File:** runtime/runtime/src/lib.rs (L547-562)
```rust
        let account_id = receipt.receiver_id();
        let is_refund = receipt.predecessor_id().is_system();
        let is_the_only_action = actions.len() == 1;
        let implicit_account_creation_eligible = is_the_only_action && !is_refund;

        // Account validation
        if let Err(e) = check_account_existence(
            action,
            account,
            account_id,
            &apply_state.config,
            implicit_account_creation_eligible,
        ) {
            result.result = Err(e);
            return Ok(result);
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
