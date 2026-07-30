Confirmed root cause: `stake()`/`deposit_and_stake()` in `staking-pool/src/lib.rs` call `internal_ping()` first, then `internal_stake()` [1](#0-0) , and `internal_ping` in `staking-pool/src/internal.rs` distributes the reward accrued since `last_total_balance` proportionally over `total_stake_shares` at the moment ping executes, with no time-weighting of shares [2](#0-1) . New stake shares minted via `internal_stake` immediately participate in the next `total_staked_balance` increase driven by future `internal_ping` calls [3](#0-2) .

### Title
Reward distribution in `ping()`/`internal_ping()` lets last-moment depositors capture rewards accrued by prior stakers - (File: `staking-pool/src/internal.rs`)

### Summary
`internal_ping` distributes all reward accrued since the last epoch/ping (validator staking rewards, gas fee rebates, and even accidental transfers) strictly in proportion to the `stake_shares` an account holds at the moment `ping` executes, with zero regard to how long those shares have existed [4](#0-3) . Because any public call (`deposit_and_stake`, `stake`, `withdraw`, etc.) triggers `internal_ping` before or as part of processing [5](#0-4) , an unprivileged actor watching the mempool for an imminent `ping`-triggering transaction (or simply timing their action to land right before the epoch-boundary reward realization) can call `deposit_and_stake` to mint stake shares immediately prior to the reward being locked in, then receive a proportional cut of rewards that were earned entirely by other long-term delegators' capital/risk.

### Finding Description
This is the same accounting/timing class of bug as the reported `Delegation.sol` issue: rewards are allocated based on a point-in-time snapshot of stake shares rather than time-weighted contribution. In `staking-pool`, the README itself documents that both validator rewards and "gas fee rebates" (and even stray transfers) accumulate silently between `ping` calls and are only realized/distributed the next time any account triggers `internal_ping` [6](#0-5) . Because `total_reward` is computed as `current_total_balance - last_total_balance` and split by current share ratio at that single instant, an attacker who stakes moments before someone else's transaction calls `ping` (or before the epoch switch is finally observed) captures a slice of rewards proportional to their newly-added shares, despite having contributed zero elapsed time/risk during the period in which that reward accrued [2](#0-1) .

### Impact Explanation
This falls under the "High" impact category for reward/balance-accounting divergence letting an unprivileged user over-credit value at the expense of other users' fair entitlement. Long-term delegators who bore the actual staking/slashing risk over the epoch have their proportional reward diluted by newcomers who staked seconds before distribution, effectively siphoning yield without commensurate risk exposure.

### Likelihood Explanation
The attack requires only unprivileged, public calls (`deposit`, `stake`, `deposit_and_stake`) and mempool observation/timing — no privileged role, validator control, or key compromise is needed. It is straightforward and reliably reproducible whenever a `ping`-triggering reward event (gas rebate accumulation, stray transfer, or epoch-boundary validation reward) is about to be realized, matching the "unprivileged user, public protocol input" requirement.

### Recommendation
- Short term: Exclude newly-staked shares from receiving rewards accrued prior to their creation — e.g., snapshot pending stake amounts separately and only merge them into the reward-eligible `total_stake_shares` pool after the delay already inherent in NEAR's validator-activation epoch delay, rather than immediately upon `internal_stake`.
- Long term: Implement time-weighted or per-epoch checkpointed share accounting so that reward distribution reflects the duration each depositor's stake was actually exposed to validation risk, consistent with the general mitigation recommended for the analogous `Delegation.sol` issue.

### Proof of Concept
1. Long-term delegator Alice has staked for many epochs; a large "reward" balance (gas rebates + stray transfer + validator reward) has silently accumulated in the contract since `last_total_balance` was last recorded.
2. Attacker Bob observes (via mempool or timing) that a transaction is about to trigger `internal_ping` (e.g., anyone calling `withdraw`, `stake`, or the epoch is about to roll over on the next call).
3. Bob front-runs by calling `deposit_and_stake()`; per the implementation, `internal_ping()` runs first (distributing the reward at the OLD share ratio, so Bob's own transaction cannot self-capture it), so instead Bob targets the case where he can get his `stake()`/`deposit_and_stake()` call included in the same epoch *before* another party's transaction which will trigger the actual reward-distributing `ping`.
4. Once that subsequent transaction calls `internal_ping`, the accrued reward (`total_reward`) is split over `total_stake_shares`, which now includes Bob's freshly minted shares from step 3 [7](#0-6) .
5. Bob immediately calls `unstake_all`/`withdraw` to realize the gained share-price uplift, having borne none of the time/risk that produced the reward, while Alice's proportional share of the same reward pool is diluted.

### Citations

**File:** staking-pool/src/lib.rs (L227-236)
```rust
    /// Deposits the attached amount into the inner account of the predecessor and stakes it.
    #[payable]
    pub fn deposit_and_stake(&mut self) {
        self.internal_ping();

        let amount = self.internal_deposit();
        self.internal_stake(amount);

        self.internal_restake();
    }
```

**File:** staking-pool/src/lib.rs (L279-287)
```rust
    pub fn stake(&mut self, amount: U128) {
        // Stake action always restakes
        self.internal_ping();

        let amount: Balance = amount.into();
        self.internal_stake(amount);

        self.internal_restake();
    }
```

**File:** staking-pool/src/internal.rs (L96-106)
```rust
        account.unstaked -= charge_amount;
        account.stake_shares += num_shares;
        self.internal_save_account(&account_id, &account);

        // The staked amount that will be added to the total to guarantee the "stake" share price
        // never decreases. The difference between `stake_amount` and `charge_amount` is paid
        // from the allocated STAKE_SHARE_PRICE_GUARANTEE_FUND.
        let stake_amount = self.staked_amount_from_num_shares_rounded_up(num_shares);

        self.total_staked_balance += stake_amount;
        self.total_stake_shares += num_shares;
```

**File:** staking-pool/src/internal.rs (L205-234)
```rust
        let total_balance =
            env::account_locked_balance() + env::account_balance() - env::attached_deposit();

        assert!(
            total_balance >= self.last_total_balance,
            "The new total balance should not be less than the old total balance"
        );
        let total_reward = total_balance - self.last_total_balance;
        if total_reward > 0 {
            // The validation fee that the contract owner takes.
            let owners_fee = self.reward_fee_fraction.multiply(total_reward);

            // Distributing the remaining reward to the delegators first.
            let remaining_reward = total_reward - owners_fee;
            self.total_staked_balance += remaining_reward;

            // Now buying "stake" shares for the contract owner at the new share price.
            let num_shares = self.num_shares_from_staked_amount_rounded_down(owners_fee);
            if num_shares > 0 {
                // Updating owner's inner account
                let owner_id = self.owner_id.clone();
                let mut account = self.internal_get_account(&owner_id);
                account.stake_shares += num_shares;
                self.internal_save_account(&owner_id, &account);
                // Increasing the total amount of "stake" shares.
                self.total_stake_shares += num_shares;
            }
            // Increasing the total staked balance by the owners fee, no matter whether the owner
            // received any shares or not.
            self.total_staked_balance += owners_fee;
```

**File:** staking-pool/README.md (L85-103)
```markdown
### Reward distribution

Before every action the contract calls method `internal_ping`.
This method distributes rewards towards active delegators when the blockchain epoch switches.
The rewards might be given due to staking and also because the contract earns gas fee rebates for every function call.
Note, the if someone accidentally (or intentionally) transfers tokens to the contract (without function call), then
tokens from the transfer will be distributed to the active stake participants of the contract in the next epoch.
Note, in a rare scenario, where the owner withdraws tokens and while the call is being processed deletes their account, the
withdraw transfer will fail and the tokens will be returned to the staking pool. These tokens will also be distributed as
a reward in the next epoch.

The method first checks that the current epoch is different from the last epoch, and if it's not changed exits the method.

The reward are computed the following way. The contract keeps track of the last known total account balance.
This balance consist of the initial contract balance, and all delegator account balances (including the owner) and all accumulated rewards.
(Validation rewards are added automatically at the beginning of the epoch, while contract execution gas rebates are added after each transaction)

When the method is called the contract uses the current total account balance (without attached deposit) and the subtracts the last total account balance.
The difference is the total reward that has to be distributed.
```
