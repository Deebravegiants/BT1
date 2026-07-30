### Title
`unstake`/`unstake_all` Resets Withdrawal Cooldown For a Delegator's Entire Unstaked Balance, Not Just the Newly Unstaked Portion - (File: staking-pool/src/internal.rs)

### Summary
The staking-pool's `inner_unstake` function unconditionally overwrites `account.unstaked_available_epoch_height` on every call to `unstake`/`unstake_all`, resetting the withdrawal cooldown for the delegator's **entire** unstaked balance — including any portion that had already matured and was ready to withdraw — instead of only the newly-unstaked amount. This mirrors the `VaderBond.deposit()` root cause: a state-updating public entrypoint (deposit / unstake) overwrites a single "vesting/cooldown" timestamp field that governs the whole accrued balance, silently penalizing anyone who calls it again before claiming/withdrawing prior proceeds.

### Finding Description
`inner_unstake` computes the newly unstaked amount and then does: [1](#0-0) 

```
account.stake_shares -= num_shares;
account.unstaked += receive_amount;
account.unstaked_available_epoch_height = env::epoch_height() + NUM_EPOCHS_TO_UNLOCK;
```

This is exposed through the public, unprivileged methods `unstake` and `unstake_all`: [2](#0-1) 

The `Account` struct only tracks a single `unstaked_available_epoch_height` for the whole `unstaked` balance rather than per-unstake-batch tracking: [3](#0-2) 

Consequently, if a delegator has an already-matured `unstaked` balance (past its `unstaked_available_epoch_height`) and calls `unstake` again — even for a tiny additional amount, e.g. to unstake newly accrued rewards or a remaining sliver of stake — the entire combined unstaked balance's withdrawal timer is pushed forward by `NUM_EPOCHS_TO_UNLOCK` (4 epochs), including the funds that were already withdrawable. `internal_withdraw` then rejects any withdrawal until the new cooldown elapses: [4](#0-3) 

This is functionally identical to the reported Vader bug pattern: a public state-mutating call (`deposit`/`unstake`) overwrites a single vesting/cooldown marker that governs the account's whole accrued balance instead of being scoped to only the newly added portion, delaying access to funds a user could otherwise already claim.

### Impact Explanation
This falls under the "Replay/cooldown failure ... breaks single-execution or rightful redemption guarantees" High-impact category: an unprivileged delegator's already-matured unstaked balance becomes locked again for up to 4 additional epochs purely due to normal use of the public `unstake`/`unstake_all` entrypoints, with no warning in the contract that this happens. It does not cause permanent loss (funds remain in the account and can eventually be withdrawn), but it breaks the expected redemption guarantee that already-available funds stay available.

### Likelihood Explanation
This is highly likely to occur in practice: a delegator who unstakes some tokens, waits, and later performs a second partial `unstake` call (e.g., to unstake newly earned rewards or additional stake) before withdrawing the first batch will trigger this reset. No special privileges or race conditions are required — it's reachable through the normal, documented staking flow.

### Recommendation
Track the unstaked balance's available-withdrawal epoch on a per-batch basis (or only extend the epoch height for the newly-added unstaked amount while allowing withdrawal of the already-matured portion), similar to the Vader team's suggested mitigation of not resetting existing accrued state on subsequent calls, or explicitly documenting/warning delegators about this cooldown-reset behavior before they take further unstake actions.

### Proof of Concept
1. Delegator deposits and stakes `X` NEAR via `deposit_and_stake`.
2. Delegator calls `unstake(X)` — `unstaked_available_epoch_height` is set to `current_epoch + 4`.
3. Delegator waits 4+ epochs; balance `X` is now withdrawable (`is_account_unstaked_balance_available` returns true).
4. Before withdrawing, delegator earns/stakes a small extra amount and calls `unstake(small_amount)` again.
5. `inner_unstake` overwrites `unstaked_available_epoch_height` to `current_epoch + 4` for the **combined** unstaked balance (`X + small_amount`).
6. Delegator's call to `withdraw`/`withdraw_all` for the previously-matured `X` now fails with `"The unstaked balance is not yet available due to unstaking delay"` until the new cooldown elapses. [5](#0-4)

### Citations

**File:** staking-pool/src/internal.rs (L42-54)
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
```

**File:** staking-pool/src/internal.rs (L124-157)
```rust
    pub(crate) fn inner_unstake(&mut self, amount: u128) {
        assert!(amount > 0, "Unstaking amount should be positive");

        let account_id = env::predecessor_account_id();
        let mut account = self.internal_get_account(&account_id);

        assert!(
            self.total_staked_balance > 0,
            "The contract doesn't have staked balance"
        );
        // Calculate the number of shares required to unstake the given amount.
        // NOTE: The number of shares the account will pay is rounded up.
        let num_shares = self.num_shares_from_staked_amount_rounded_up(amount);
        assert!(
            num_shares > 0,
            "Invariant violation. The calculated number of \"stake\" shares for unstaking should be positive"
        );
        assert!(
            account.stake_shares >= num_shares,
            "Not enough staked balance to unstake"
        );

        // Calculating the amount of tokens the account will receive by unstaking the corresponding
        // number of "stake" shares, rounding up.
        let receive_amount = self.staked_amount_from_num_shares_rounded_up(num_shares);
        assert!(
            receive_amount > 0,
            "Invariant violation. Calculated staked amount must be positive, because \"stake\" share price should be at least 1"
        );

        account.stake_shares -= num_shares;
        account.unstaked += receive_amount;
        account.unstaked_available_epoch_height = env::epoch_height() + NUM_EPOCHS_TO_UNLOCK;
        self.internal_save_account(&account_id, &account);
```

**File:** staking-pool/src/lib.rs (L42-56)
```rust
/// Inner account data of a delegate.
#[derive(BorshDeserialize, BorshSerialize, Debug, PartialEq)]
pub struct Account {
    /// The unstaked balance. It represents the amount the account has on this contract that
    /// can either be staked or withdrawn.
    pub unstaked: Balance,
    /// The amount of "stake" shares. Every stake share corresponds to the amount of staked balance.
    /// NOTE: The number of shares should always be less or equal than the amount of staked balance.
    /// This means the price of stake share should always be at least `1`.
    /// The price of stake share can be computed as `total_staked_balance` / `total_stake_shares`.
    pub stake_shares: NumStakeShares,
    /// The minimum epoch height when the withdrawn is allowed.
    /// This changes after unstaking action, because the amount is still locked for 3 epochs.
    pub unstaked_available_epoch_height: EpochHeight,
}
```

**File:** staking-pool/src/lib.rs (L289-314)
```rust
    /// Unstakes all staked balance from the inner account of the predecessor.
    /// The new total unstaked balance will be available for withdrawal in four epochs.
    pub fn unstake_all(&mut self) {
        // Unstake action always restakes
        self.internal_ping();

        let account_id = env::predecessor_account_id();
        let account = self.internal_get_account(&account_id);
        let amount = self.staked_amount_from_num_shares_rounded_down(account.stake_shares);
        self.inner_unstake(amount);

        self.internal_restake();
    }

    /// Unstakes the given amount from the inner account of the predecessor.
    /// The inner account should have enough staked balance.
    /// The new total unstaked balance will be available for withdrawal in four epochs.
    pub fn unstake(&mut self, amount: U128) {
        // Unstake action always restakes
        self.internal_ping();

        let amount: Balance = amount.into();
        self.inner_unstake(amount);

        self.internal_restake();
    }
```
