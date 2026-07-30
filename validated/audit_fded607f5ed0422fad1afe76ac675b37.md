### Title
Unstake withdrawal transfer result is never checked, permanently burning user funds on transfer failure - (File: staking-pool/src/internal.rs)

### Summary
`StakingContract::internal_withdraw` fires a native NEAR transfer to return a user's unstaked balance but never attaches a callback to verify the transfer succeeded, unlike every other cross-contract/transfer flow in this codebase (staking, deposit, unstake, termination-withdraw), which all check `is_promise_success()` before finalizing accounting.

### Finding Description
`internal_withdraw` decrements the user's `account.unstaked` balance and the contract's `last_total_balance`, then issues `Promise::new(account_id).transfer(amount)` with no `.then(...)` callback attached: [1](#0-0) 

Every other state-changing async action in the same contract (and in the sibling `lockup` contract) always attaches an `ext_self::...` callback that calls `is_promise_success()` and rolls back or fixes the internal state on failure — e.g. `on_staking_pool_deposit`, `on_staking_pool_withdraw`, `on_staking_pool_stake`, `on_staking_pool_unstake` in `lockup/src/owner_callbacks.rs`: [2](#0-1) 

and the termination flow's `on_withdraw_unvested_amount` in `lockup/src/foundation_callbacks.rs`, which explicitly resets `TerminationStatus::ReadyToWithdraw` if `is_promise_success()` is false so the withdrawal can be retried: [3](#0-2) 

By contrast, `internal_withdraw` in `staking-pool/src/internal.rs` mutates state (`account.unstaked -= amount`, `self.last_total_balance -= amount`) synchronously and irrevocably before knowing whether the outbound `Promise::new(account_id).transfer(amount)` will actually succeed. On NEAR, a `transfer` action promise can fail (e.g., insufficient gas is provisioned for the receipt processing/refund handling in edge cases, or the receiver account is deleted between when the transaction is signed and when the receipt executes). If the transfer fails, the protocol has already deducted the user's internal unstaked balance and reduced `last_total_balance`, but the tokens are not delivered to the user and there is no compensating callback to restore the accounting or allow re-withdrawal.

### Impact Explanation
This falls under "Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in ... unstake-withdraw ... flows," since a failed transfer results in the user's unstaked balance being silently erased with no recovery path — the funds are lost from the user's perspective while the contract's internal accounting (`last_total_balance`) also permanently understates the actual locked/available balance, creating a lasting accounting divergence between `last_total_balance` and the real account balance held by the contract.

### Likelihood Explanation
Likelihood is lower than a directly attacker-triggerable exploit because normal `transfer` actions to an existing, non-full account rarely fail on NEAR. It is nonetheless a real, reachable code path that can be hit under adversarial or degraded conditions and represents a genuine deviation from the safe pattern used everywhere else in this same codebase; the fact that all sibling transfer/withdraw flows explicitly guard against this exact failure mode (checking `is_promise_success()`) indicates the developers were aware of and mitigated this risk elsewhere but missed it in `internal_withdraw`.

### Recommendation
Attach a callback (e.g., `ext_self::on_withdraw`) to the `Promise::new(account_id).transfer(amount)` call in `internal_withdraw`, mirroring the pattern used in `lockup/src/owner_callbacks.rs`'s `on_staking_pool_withdraw`. On failure, restore `account.unstaked += amount` and `self.last_total_balance += amount` so the user can retry the withdrawal instead of losing the funds permanently.

### Proof of Concept
1. A delegator calls `withdraw`/`withdraw_all`, which routes into `internal_withdraw`.
2. `internal_withdraw` deducts `amount` from `account.unstaked`, decreases `self.last_total_balance`, and fires `Promise::new(account_id).transfer(amount)` with no callback. [4](#0-3) 
3. If the transfer promise fails for any reason at the protocol/runtime level, the receipt fails silently from the contract's perspective — there is no `.then()` callback to detect this.
4. The user's `unstaked` balance is already zeroed/reduced and cannot be re-withdrawn, while they never received the NEAR tokens, resulting in irrecoverable fund loss and a permanent divergence in `last_total_balance` accounting.

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

**File:** lockup/src/owner_callbacks.rs (L105-145)
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

**File:** lockup/src/foundation_callbacks.rs (L188-241)
```rust
    pub fn on_withdraw_unvested_amount(
        &mut self,
        amount: WrappedBalance,
        receiver_id: AccountId,
    ) -> bool {
        assert_self();

        let withdraw_succeeded = is_promise_success();
        if withdraw_succeeded {
            env::log(
                format!(
                    "Termination Step: The withdrawal of the terminated unvested amount of {} to @{} succeeded.",
                    amount.0, receiver_id
                )
                    .as_bytes(),
            );
            // Decreasing lockup amount after withdrawal.
            self.lockup_information.termination_withdrawn_tokens += amount.0;
            let unvested_amount = self.get_terminated_unvested_balance().0;
            if unvested_amount > amount.0 {
                // There is still unvested balance remaining.
                let remaining_balance = unvested_amount - amount.0;
                self.vesting_information =
                    VestingInformation::Terminating(TerminationInformation {
                        unvested_amount: remaining_balance.into(),
                        status: TerminationStatus::ReadyToWithdraw,
                    });
                env::log(
                    format!(
                        "Termination Step: There is still terminated unvested balance of {} remaining to be withdrawn",
                        remaining_balance
                    )
                        .as_bytes(),
                );
                if self.get_account_balance().0 == 0 {
                    env::log(b"The withdrawal is completed: no more balance can be withdrawn in a future call");
                }
            } else {
                self.foundation_account_id = None;
                self.vesting_information = VestingInformation::None;
                env::log(b"Vesting schedule termination and withdrawal are completed");
            }
        } else {
            self.set_termination_status(TerminationStatus::ReadyToWithdraw);
            env::log(
                format!(
                    "Termination Step: The withdrawal of the terminated unvested amount of {} to @{} failed",
                    amount.0, receiver_id,
                )
                .as_bytes(),
            );
        }
        withdraw_succeeded
    }
```
