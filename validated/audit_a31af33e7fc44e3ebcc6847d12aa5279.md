## Analog Finding

### Title
Unstaked balance is burned before the NEAR transfer is confirmed to succeed in `withdraw`/`withdraw_all` - (File: `staking-pool/src/internal.rs`)

### Summary
The external PoolTogether report describes a pattern where a contract updates its internal accounting (burning shares) assuming an asset transfer/redemption succeeded, then performs the actual transfer without checking or reverting on failure, permanently locking the user's funds. The `staking-pool` contract in this repository contains the same root-cause pattern in its withdrawal flow: `internal_withdraw` decrements the user's `unstaked` balance and `last_total_balance` synchronously, and only afterwards fires an unchecked `Promise::new(account_id).transfer(amount)` with no follow-up callback to verify success and roll back state if the transfer fails.

### Finding Description
`internal_withdraw`, invoked by the public entrypoints `withdraw` and `withdraw_all`, performs the balance deduction and account save *before* issuing the transfer promise, and never attaches a callback to check `is_promise_success()`: [1](#0-0) 

Specifically:
- `account.unstaked -= amount;` and `self.internal_save_account(&account_id, &account);` commit synchronously within the same function-call receipt.
- `Promise::new(account_id).transfer(amount);` is fired without `.then(...)` to a self-callback.
- `self.last_total_balance -= amount;` is also decremented unconditionally.

In NEAR, promise/receipt state changes are only rolled back if the *originating* function call itself panics; a separately scheduled `Transfer` action failing in its own receipt does **not** revert the state already committed by the calling function. This means if the `Transfer` action fails (e.g., the contract's actual liquid NEAR balance is insufficient to cover `amount` at execution time — which can occur due to rounding-driven divergence between `last_total_balance`/staked-share accounting and the real account balance, a scenario the code itself acknowledges by allocating `STAKE_SHARE_PRICE_GUARANTEE_FUND` to guard against rounding errors), the user's `unstaked` balance has already been irreversibly zeroed out and no compensating logic exists to restore it.

This is structurally identical to the reported PrizeVault bug: accounting is updated optimistically on the assumption that the paired asset movement succeeds, and there is no callback-based verification/rollback if it doesn't. Contrast this with the `lockup` contract's own staking-pool interactions, which correctly use `on_staking_pool_withdraw`/`is_promise_success()` callbacks before finalizing state changes: [2](#0-1) 

### Impact Explanation
If the transfer fails post-accounting-update, the affected user's `unstaked` balance is permanently and unrecoverably burned with no compensating on-chain record, and the NEAR remains stuck in the pool's balance without an accounting entry to reclaim it — matching the in-scope "Critical: permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in ... unstake-withdraw ... flows" impact.

### Likelihood Explanation
The likelihood is low under normal operation, since a plain NEAR `Transfer` to an already-existing account (the caller, who must exist to have signed the transaction) rarely fails. The realistic trigger is a divergence between the contract's internally tracked balances (`total_staked_balance`, `last_total_balance`, share-price rounding) and the actual liquid (unlocked, unstaked) NEAR held by the contract account at the moment the `Transfer` receipt executes — for example after prolonged operation with many small stake/unstake operations that erode the `STAKE_SHARE_PRICE_GUARANTEE_FUND`, or if a large share of the balance is still locked for staking when withdrawals are requested. This is an accounting-failure entry point reachable purely through the public `withdraw`/`withdraw_all` calls by any unprivileged delegator.

### Recommendation
Attach a callback to the transfer promise in `internal_withdraw` (mirroring the pattern already used in `lockup/src/owner_callbacks.rs`), and only finalize the balance deduction (or restore it) based on `is_promise_success()` in that callback, instead of decrementing `account.unstaked`/`last_total_balance` unconditionally before the transfer is known to succeed.

### Proof of Concept
Conceptual reproduction (would require simulating a promise `Transfer` failure via `testing_env_with_promise_results(..., PromiseResult::Failed)` as done elsewhere in the test suite, e.g. `test_restake_fail`):
1. Delegator deposits and unstakes an amount, waits `NUM_EPOCHS_TO_UNLOCK` epochs.
2. Delegator calls `withdraw(amount)`; `internal_withdraw` immediately sets `account.unstaked -= amount` and saves it, then fires `Promise::new(account_id).transfer(amount)`.
3. Simulate the `Transfer` receipt failing (e.g., insufficient real balance due to rounding drift).
4. Because there is no callback checking `is_promise_success()`, `account.unstaked` remains decremented and the delegator has no path to reclaim the amount — same terminal state as the PrizeVault PoC (`vault.balanceOf(alice) == 0` while assets never arrived). [1](#0-0)

### Citations

**File:** staking-pool/src/internal.rs (L42-68)
```rust
    pub(crate) fn internal_withdraw(&mut self, amount: Balance) {
        assert!(amount > 0, "Withdrawal amount should be positive");

        let account_id = env::predecessor_account_id();
        let mut account = self.internal_get_account(&account_id);
        assert!(
            account.unstaked >= amount,
            "Not enough unstaked balance to withdraw"
        );
        assert!(
            account.unstaked_available_epoch_height <= env::epoch_height(),
            "The unstaked balance is not yet available due to unstaking delay"
        );
        account.unstaked -= amount;
        self.internal_save_account(&account_id, &account);

        env::log(
            format!(
                "@{} withdrawing {}. New unstaked balance is {}",
                account_id, amount, account.unstaked
            )
            .as_bytes(),
        );

        Promise::new(account_id).transfer(amount);
        self.last_total_balance -= amount;
    }
```

**File:** lockup/src/owner_callbacks.rs (L105-119)
```rust
    pub fn on_staking_pool_withdraw(&mut self, amount: WrappedBalance) -> bool {
        assert_self();

        let withdraw_succeeded = is_promise_success();
        self.set_staking_pool_status(TransactionStatus::Idle);

        if withdraw_succeeded {
            {
                let staking_information = self.staking_information.as_mut().unwrap();
                // Due to staking rewards the deposit amount can become negative.
                staking_information.deposit_amount.0 = staking_information
                    .deposit_amount
                    .0
                    .saturating_sub(amount.0);
            }
```
