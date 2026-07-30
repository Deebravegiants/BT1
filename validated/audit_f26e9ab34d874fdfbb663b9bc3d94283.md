### Title
Validator Slashing Permanently Bricks the Staking Pool, Freezing All Delegator Funds - (File: staking-pool/src/internal.rs)

### Summary
The external ZetaChain finding describes a state-machine that can be permanently halted by an externally-triggered validator slashing event, requiring manual multi-step recovery that may never happen. The NEAR staking-pool contract has an analogous, self-contained root cause: an unconditional invariant check inside `internal_ping` that assumes the contract's total balance can never decrease. A validator slashing event (a normal NEAR protocol consequence of double-signing or extended downtime by the validator running the pool) violates this invariant and permanently reverts every subsequent call into the contract, with no recovery method available to anyone.

### Finding Description
`internal_ping` computes the pool's current total balance and asserts it is never smaller than the last recorded value: [1](#0-0) 

```
let total_balance =
    env::account_locked_balance() + env::account_balance() - env::attached_deposit();

assert!(
    total_balance >= self.last_total_balance,
    "The new total balance should not be less than the old total balance"
);
```

NEAR's protocol can slash a validator's locked stake for malicious or faulty behavior (e.g., double signing). When the staking pool's own validator key is slashed, `env::account_locked_balance()` drops, causing `total_balance < self.last_total_balance` and triggering the `assert!` panic.

`internal_ping` is invoked unconditionally as the very first operation of every state-changing public method: `ping`, `deposit`, `deposit_and_stake`, `withdraw`, `withdraw_all`, `stake`, `stake_all`, `unstake`, and `unstake_all`: [2](#0-1) 

Because `self.last_total_balance` is never lowered anywhere else in the contract and there is no owner or admin method to reset it, once the assertion fails on one call it will fail identically on every future call, for as long as the locked balance remains below the last recorded value (which, absent a reward event large enough to offset the slash — and typically slashing removes a large fraction of stake — is effectively forever).

### Impact Explanation
This permanently bricks the staking pool contract: no delegator can `withdraw`, `unstake`, `stake`, or even `ping` again. All staked and unstaked balances become irrecoverably frozen inside the contract, matching the "Permanent freezing, unrecoverable lock ... of user or protocol funds in ... unstake-withdraw ... flows" critical impact category. This also affects `lockup` contracts that have delegated funds to the pool, since the lockup's `refresh_staking_pool_balance`/`unstake`/`withdraw_all_from_staking_pool` flows depend on the pool responding successfully.

### Likelihood Explanation
Triggering this bug does not require any privileged role, key, or malicious insider — it happens automatically whenever the NEAR protocol slashes the pool's staking key (a real, network-level penalty for validator misbehavior/downtime), which is out of any individual delegator's control. Once the slash occurs, *any* unprivileged user simply calling a normal, public method (e.g., `ping` or `withdraw`) will hit the frozen state; no attacker action is required beyond ordinary usage. Given that slashing conditions are a recognized part of the NEAR protocol's validator security model, this is a realistic, non-theoretical failure mode for any staking pool with meaningful stake.

### Recommendation
Do not `assert!` on a balance decrease. Instead, detect the shortfall and account for it explicitly (e.g., treat a decrease as a negative "reward"/slashing event that proportionally reduces `total_staked_balance` and `last_total_balance`, or clamp/reset `last_total_balance` to the new lower total balance) so the pool can continue operating and delegators can still unstake/withdraw their (reduced) balances rather than being permanently locked out.

### Proof of Concept
1. Deploy `staking-pool` and have delegators stake NEAR normally; `last_total_balance` tracks the pool's locked+unlocked balance.
2. The validator key associated with the pool's `stake_public_key` gets slashed by the NEAR protocol (e.g., due to double signing), reducing `env::account_locked_balance()`.
3. Any user calls any state-mutating method (`ping`, `deposit`, `stake`, `unstake`, `withdraw`, etc.).
4. `internal_ping` computes `total_balance = account_locked_balance() + account_balance() - attached_deposit()`, which is now `< self.last_total_balance`.
5. The `assert!` in [3](#0-2)  panics, reverting the transaction.
6. Because `last_total_balance` is unchanged after a revert, every future call to every public method repeats step 4–5 forever — the contract, and all funds inside it, are permanently frozen.

### Citations

**File:** staking-pool/src/internal.rs (L192-211)
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
