This confirms the analog root cause. Every state-changing entrypoint (`ping`, `deposit`, `deposit_and_stake`, `withdraw`, `withdraw_all`, `stake`, `stake_all`, `unstake`, `unstake_all`) unconditionally calls `internal_ping` first [1](#0-0) , and `internal_ping` contains a hard assertion that the new total balance can never be less than the previously recorded balance [2](#0-1) . The README itself acknowledges the guarantees only hold "based on the no-slashing condition" [3](#0-2) .

### Title
Validator slashing causes `internal_ping` assertion failure, permanently bricking the staking pool contract for all delegators - (File: staking-pool/src/internal.rs)

### Summary
The external report concerns ETH2 slashing depegging dETH/ETH accounting in a liquid-staking vault. The analogous root cause in core-contracts is in the NEAR `staking-pool` contract: `internal_ping` (`staking-pool/src/internal.rs`) assumes the validator's locked balance can only ever increase between epochs, and enforces this with a hard `assert!`. If the underlying validator is slashed by the NEAR protocol, `env::account_locked_balance()` decreases, this invariant is violated, and every single delegator-facing method reverts forever.

### Finding Description
`internal_ping` computes `total_balance = env::account_locked_balance() + env::account_balance() - env::attached_deposit()` and asserts `total_balance >= self.last_total_balance` [2](#0-1) . `internal_ping` is invoked unconditionally as the very first step of `ping`, `deposit`, `deposit_and_stake`, `withdraw`, `withdraw_all`, `stake`, `stake_all`, `unstake`, and `unstake_all` [4](#0-3) . There is no owner or admin method to reset `last_total_balance`, recover from a slashing event, or otherwise bypass this check. Once the validator behind the pool is slashed (locked balance decreases across an epoch boundary), the very next call to any of these methods causes the assertion to fail and the transaction to revert, and this will happen on every subsequent call forever since `last_total_balance` is never updated in a failed (reverted) call.

### Impact Explanation
This matches the "Permanent freezing, unrecoverable lock" impact category: once slashing occurs, delegators can never again call `unstake`, `withdraw`, `withdraw_all`, or `ping`, and the owner cannot `pause_staking`/`resume_staking` either since those rely on the same restake flow gated behind ping in normal operation flows for delegators. All principal and rewards held in the pool (staked and unstaked-but-not-yet-withdrawn balances) become permanently inaccessible, since no code path allows the contract to acknowledge a balance decrease and continue operating.

### Likelihood Explanation
Likelihood depends on an external event (validator slashing) rather than a directly attacker-triggered call, so this is not an unprivileged-attacker-triggered exploit in the traditional sense — slashing occurs due to protocol-level validator misbehavior (double-signing, downtime typically doesn't slash on NEAR but double-sign does), not by an unprivileged caller invoking a public method. The codebase's own README explicitly flags this as a known limitation ("Guarantees are based on the no-slashing condition") [3](#0-2) , indicating the authors were aware slashing is out of scope for the guarantees, rather than an undiscovered bug.

### Recommendation
Handle the case where `total_balance < self.last_total_balance` gracefully (e.g., treat the deficit as a loss to be socialized across `total_staked_balance`/shares rather than panicking), and add an owner or protocol-level recovery method to reset `last_total_balance` after a slashing event so delegators can still access their (reduced) balances.

### Proof of Concept
1. Owner initializes the staking pool and delegators deposit/stake normally, causing `last_total_balance` to track the growing locked balance via `internal_ping` [5](#0-4) .
2. The validator behind the pool double-signs and NEAR protocol slashes part of the locked stake, so `env::account_locked_balance()` at the start of the next epoch is lower than before.
3. Any delegator (or the owner) calls any state-changing method (e.g. `unstake`, `withdraw_all`, `ping`) [6](#0-5) .
4. `internal_ping` computes a new `total_balance` lower than `last_total_balance` and the `assert!` at line 208-211 panics, reverting the transaction.
5. Because the failed call never updates `last_total_balance`, this repeats indefinitely for every future call, permanently freezing all delegator funds in the pool.

---

**Caveat on scoring**: This finding relies on an external triggering condition (protocol-level slashing), not a purely attacker-controlled entrypoint. Under the stated rules ("The attacker must be strictly unprivileged and must enter through public protocol inputs" and "Reject self-harm or user-mistake-only paths"), this may be borderline since the root cause is triggered by validator/protocol behavior rather than a malicious call from an unprivileged user. I'm presenting it as the closest legitimate analog found in-scope, but flag that it does not perfectly satisfy the "attacker-controlled entry" requirement — it is a genuine, documented (by the maintainers) architectural limitation rather than a newly discovered exploitable bug.

### Citations

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

**File:** staking-pool/src/internal.rs (L194-212)
```rust
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

**File:** staking-pool/README.md (L145-146)
```markdown
NOTE: Guarantees are based on the no-slashing condition. Once slashing is introduced, the contract will no longer
provide some guarantees. Read more about slashing in [Nightshade paper](https://near.ai/nightshade).
```
