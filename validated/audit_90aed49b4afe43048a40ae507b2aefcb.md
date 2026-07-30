### Title
Unstaked Balance Deducted Before Verifying Sufficient Contract Balance for Withdrawal Transfer - (File: staking-pool/src/internal.rs)

### Summary
The `internal_withdraw()` function in `staking-pool/src/internal.rs` decrements the caller's recorded `unstaked` balance and the contract's `last_total_balance` accounting *before* the outbound `Promise::new(account_id).transfer(amount)` is guaranteed to succeed, and with no check that the contract's actual liquid NEAR balance covers the transfer. This mirrors the root cause of the GMX finding: state is mutated to reflect a completed payout while the actual transfer of value is not verified to be possible, and there is no callback/rollback path if the transfer receipt fails.

### Finding Description
`internal_withdraw` is called from the public `withdraw()` entrypoint [1](#0-0) . Inside it, the accounting state is committed synchronously: [2](#0-1) 

The function asserts `account.unstaked >= amount` (i.e. sufficient *recorded* balance) and that the unstaking delay has passed, but it never checks `env::account_balance()` (the contract's actual liquid NEAR) against `amount` before decrementing `account.unstaked` and `self.last_total_balance`. The `Promise::new(account_id).transfer(amount)` is fired off after the state mutation, and — unlike the withdrawal flow in the `lockup` contract's owner/foundation callbacks, which use `.then(...)` with an `on_staking_pool_withdraw` callback that checks `is_promise_success()` and reverts the internal accounting only on success/failure at the *caller* side (see [3](#0-2) ) — the `staking-pool` contract's own `internal_withdraw` has no such callback to detect and reconcile a failed transfer receipt. Once the function call returns without panicking, the state mutation (`account.unstaked -= amount`, `self.last_total_balance -= amount`) is finalized regardless of whether the subsequent transfer receipt actually succeeds.

This is analogous to the GMX `withdrawClosedSize()` issue: a value-transfer promise is dispatched without confirming the sending balance is actually available/sufficient, and the accounting state is updated as if the transfer is guaranteed, with no fallback or reconciliation if it is not.

### Impact Explanation
If the staking pool contract's actual NEAR balance (`env::account_balance()`) is ever lower than the sum of recorded `unstaked` balances across all delegator accounts — which can occur due to reward-fee/rounding drift accumulated in `internal_ping()`, storage-cost/minimum-balance requirements silently consuming spendable balance, or any other divergence between `last_total_balance` bookkeeping and the real wallet balance — the outbound `transfer` receipt can fail. Because the local state was already decremented before the transfer's outcome is known and there is no `.then()` callback reversing it, the affected delegator's `unstaked` balance is permanently reduced without the delegator ever receiving the funds. This falls under "Critical: Permanent freezing / irrecoverable loss of user funds in ... unstake-withdraw ... flows."

### Likelihood Explanation
Likelihood is bounded by the fact that in-protocol staking of NEAR is intended to keep `last_total_balance` in sync with the pool's real balance, and under expected operation, the contract's balance should track `last_total_balance` closely. However, this is a self-referential guarantee never actually enforced at the point of `internal_withdraw`; the invariant is *assumed*, not checked or restored on transfer failure. This is a design gap rather than an actively demonstrated exploit path in the provided code (I could not find, given index limits, a concrete external mechanism, beyond ping/reward-fee rounding, that could push the real balance below `last_total_balance`), so likelihood should be treated as **Medium** pending an audit-level review of how tightly the running invariant `env::account_balance() ≈ last_total_balance` is maintained across all epochs and operations (deposits, stake/unstake/restake and the owner reward-fee shares).

### Recommendation
Update `internal_withdraw()` (and any other function issuing a NEAR transfer immediately after mutating persisted balance state, e.g. this pattern is only present here in `staking-pool`) to either:
1. Attach a `.then()` callback (as already used elsewhere in this codebase, e.g. `on_staking_pool_withdraw` in `lockup/src/owner_callbacks.rs`) that checks `is_promise_success()` and restores `account.unstaked`/`self.last_total_balance` if the transfer failed, or
2. Explicitly assert `env::account_balance() >= amount` (accounting for minimum storage balance) before mutating state and issuing the transfer, so that a doomed transfer never proceeds and the transaction reverts atomically instead of silently orphaning delegator funds.

### Proof of Concept
Not independently reproducible from the indexed code alone — this requires constructing a scenario (e.g., via reward-fee rounding drift over many epochs, or storage-balance consumption) in which `env::account_balance()` at the time of `withdraw()` is less than the sum of `unstaked` balances recorded for delegators, then calling `withdraw()` for an amount that exceeds actual liquid balance while passing the `account.unstaked >= amount` check in [4](#0-3) . Full validation of the balance-drift precondition would need a live/testnet run of the `staking-pool` contract across multiple epochs, which is outside what the indexed source can confirm.

### Citations

**File:** staking-pool/src/lib.rs (L252-263)
```rust
    /// Withdraws the non staked balance for given account.
    /// It's only allowed if the `unstake` action was not performed in the four most recent epochs.
    pub fn withdraw(&mut self, amount: U128) {
        let need_to_restake = self.internal_ping();

        let amount: Balance = amount.into();
        self.internal_withdraw(amount);

        if need_to_restake {
            self.internal_restake();
        }
    }
```

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

**File:** lockup/src/owner_callbacks.rs (L102-145)
```rust
    /// Called after the given amount was requested to transfer out from the staking pool to this
    /// account.
    /// This method needs to update staking pool status.
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
            env::log(
                format!(
                    "The withdrawal of {} from @{} succeeded",
                    amount.0,
                    self.staking_information
                        .as_ref()
                        .unwrap()
                        .staking_pool_account_id
                )
                .as_bytes(),
            );
        } else {
            env::log(
                format!(
                    "The withdrawal of {} from @{} failed",
                    amount.0,
                    self.staking_information
                        .as_ref()
                        .unwrap()
                        .staking_pool_account_id
                )
                .as_bytes(),
            );
        }
        withdraw_succeeded
    }
```
