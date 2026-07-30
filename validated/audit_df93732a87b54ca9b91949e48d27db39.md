### Title
Slashing-induced permanent DoS in `internal_ping` freezes all delegator funds - (File: staking-pool/src/internal.rs)

### Summary
The external report describes a NEAR/ETH-analogous class of bug: a balance-comparison check that assumes validator balance can never decrease (i.e., never accounts for slashing), leading to broken accounting/availability of funds. In `core-contracts--007`'s `staking-pool/src/internal.rs`, `internal_ping()` contains an analogous unguarded assumption: it asserts the contract's current locked+unlocked balance is always `>=` the last recorded total balance, with no handling for the case where the underlying validator gets slashed by the NEAR protocol.

### Finding Description
`internal_ping()` recomputes the pool's current balance and compares it against the previously stored `last_total_balance`: [1](#0-0) 

If the validator represented by this staking pool is slashed by the NEAR protocol (e.g., for double-signing or being offline egregiously), `env::account_locked_balance() + env::account_balance()` will be strictly less than `self.last_total_balance` recorded from the prior epoch. The `assert!(total_balance >= self.last_total_balance, ...)` at line 208-211 will then always panic.

`internal_ping()` is invoked at the start of every state-changing entry point that any unprivileged delegator can call, including `deposit`, `deposit_and_stake`, `stake`, `stake_all`, `unstake`, `unstake_all`, `withdraw`, `withdraw_all`, and the public `ping` itself: [2](#0-1) 

Because `last_epoch_height` only updates once `internal_ping` successfully completes (line 199), and it panics before reaching that update on a slashing event, every subsequent call to any of these methods will re-trigger the same panic on the same epoch-height comparison forever — there is no code path to reset or reconcile `last_total_balance` downward after a slashing event.

This mirrors the root cause class of the referenced report: a balance check that implicitly assumes monotonic balance growth and does not have any accounting mechanism (e.g., a registry/marker of expected balance decreases due to validator penalties) to distinguish "legitimate" balance loss (slashing) from an invariant violation.

### Impact Explanation
Once slashing occurs on the underlying validator node, `internal_ping()` permanently panics on every call. Since it is invoked by all delegator-facing balance-changing methods (`deposit`, `stake`, `unstake`, `withdraw`, etc.) and the public `ping`, the entire pool becomes permanently unusable: delegators can no longer deposit, stake, unstake, or withdraw already-unstaked funds. This falls under "Critical: Permanent freezing, unrecoverable lock, or irrevocable loss of user or protocol funds in ... unstake-withdraw ... flows," since there is no owner or admin method in the contract to reset `last_total_balance` after a slashing event.

### Likelihood Explanation
The trigger condition (validator slashing) is outside the control of the pool's delegators and owner, but slashing is a normal, expected protocol-level event for NEAR validators (double-sign or extended downtime penalties), not a purely theoretical or attacker-must-be-privileged scenario. Any unprivileged delegator's routine call (e.g., `unstake` or `withdraw`) after a slashing event will trigger the permanent panic — no special privilege or crafted input is required to hit the bug once slashing has occurred. This is a realistic, protocol-native occurrence rather than a contrived edge case.

### Recommendation
Do not assume `total_balance` is monotonically non-decreasing. Instead of asserting `total_balance >= self.last_total_balance` and panicking on violation, handle slashing explicitly: detect a balance decrease and proportionally reduce `total_staked_balance` (and thus each account's implied share value) to reflect the loss, similar to how rewards are distributed on balance increases. This preserves the share-price invariant in both directions and prevents an unrecoverable panic loop. At minimum, add an explicit code path (rather than a blanket `assert!`) that reconciles a shrinking balance instead of aborting execution.

### Proof of Concept
1. Deploy the staking-pool contract and have delegators call `deposit_and_stake` normally; `last_total_balance` is recorded each epoch via `internal_ping` (`staking-pool/src/internal.rs:194-249`).
2. Suppose the validator behind this pool double-signs or otherwise incurs a NEAR protocol slashing penalty, reducing `env::account_locked_balance()` for the account below the previously recorded `last_total_balance`.
3. On the next epoch boundary, any account calls a public method that invokes `internal_ping` (e.g., `unstake`, `withdraw`, or `ping` itself, per `staking-pool/src/lib.rs:209-314`).
4. `total_balance = env::account_locked_balance() + env::account_balance() - env::attached_deposit()` computes to a value less than `self.last_total_balance`.
5. `assert!(total_balance >= self.last_total_balance, ...)` at `staking-pool/src/internal.rs:208-211` panics, aborting the transaction.
6. Because `self.last_epoch_height` is only updated after passing this assert, every future call to any delegator-facing method re-triggers the identical panic indefinitely, permanently freezing all staked/unstaked funds held by the contract.

### Citations

**File:** staking-pool/src/internal.rs (L192-212)
```rust
    /// Distributes rewards after the new epoch. It's automatically called before every action.
    /// Returns true if the current epoch height is different from the last epoch height.
    pub(crate) fn internal_ping(&mut self) -> bool {
        let epoch_height = env::epoch_height();
        if self.last_epoch_height == epoch_height {
            return false;
        }
        self.last_epoch_height = epoch_height;

        // New total amount (both locked and unlocked balances).
        // NOTE: We need to subtract `attached_deposit` in case `ping` called from `deposit` call
        // since the attached deposit gets included in the `account_balance`, and we have not
        // accounted it yet.
        let total_balance =
            env::account_locked_balance() + env::account_balance() - env::attached_deposit();

        assert!(
            total_balance >= self.last_total_balance,
            "The new total balance should not be less than the old total balance"
        );
        let total_reward = total_balance - self.last_total_balance;
```

**File:** staking-pool/src/lib.rs (L208-314)
```rust
    /// Distributes rewards and restakes if needed.
    pub fn ping(&mut self) {
        if self.internal_ping() {
            self.internal_restake();
        }
    }

    /// Deposits the attached amount into the inner account of the predecessor.
    #[payable]
    pub fn deposit(&mut self) {
        let need_to_restake = self.internal_ping();

        self.internal_deposit();

        if need_to_restake {
            self.internal_restake();
        }
    }

    /// Deposits the attached amount into the inner account of the predecessor and stakes it.
    #[payable]
    pub fn deposit_and_stake(&mut self) {
        self.internal_ping();

        let amount = self.internal_deposit();
        self.internal_stake(amount);

        self.internal_restake();
    }

    /// Withdraws the entire unstaked balance from the predecessor account.
    /// It's only allowed if the `unstake` action was not performed in the four most recent epochs.
    pub fn withdraw_all(&mut self) {
        let need_to_restake = self.internal_ping();

        let account_id = env::predecessor_account_id();
        let account = self.internal_get_account(&account_id);
        self.internal_withdraw(account.unstaked);

        if need_to_restake {
            self.internal_restake();
        }
    }

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

    /// Stakes all available unstaked balance from the inner account of the predecessor.
    pub fn stake_all(&mut self) {
        // Stake action always restakes
        self.internal_ping();

        let account_id = env::predecessor_account_id();
        let account = self.internal_get_account(&account_id);
        self.internal_stake(account.unstaked);

        self.internal_restake();
    }

    /// Stakes the given amount from the inner account of the predecessor.
    /// The inner account should have enough unstaked balance.
    pub fn stake(&mut self, amount: U128) {
        // Stake action always restakes
        self.internal_ping();

        let amount: Balance = amount.into();
        self.internal_stake(amount);

        self.internal_restake();
    }

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
