## Analog Vulnerability Found

### Title
Reward fee share minting occurs after `total_staked_balance` is inflated, causing the owner to be under-minted stake shares and delegators to over-accrue value - (File: `staking-pool/src/internal.rs`)

### Summary
In `StakingContract::internal_ping()`, the delegators' portion of newly earned rewards (`remaining_reward`) is added to `self.total_staked_balance` **before** the owner's "stake" shares for the protocol fee (`owners_fee`) are computed via `num_shares_from_staked_amount_rounded_down`. This is the exact analog of the reported StWSX bug: shares for the fee recipient are calculated using a share price that has already been inflated by the reward being distributed, instead of computing shares first (as the deposit/stake flow correctly does) and only then updating the total balance.

### Finding Description
The correct pattern, used in `internal_stake` at [1](#0-0) , computes `num_shares` from the *pre-update* `total_staked_balance`/`total_stake_shares` ratio, and only afterwards increments `self.total_staked_balance` and `self.total_stake_shares`.

`internal_ping()` violates this ordering for the owner's fee: [2](#0-1) 

Specifically:
1. `self.total_staked_balance += remaining_reward;` executes first (line 219), inflating the balance used as the denominator for the share-price calculation.
2. Only then is `num_shares_from_staked_amount_rounded_down(owners_fee)` called (line 222), which computes `num_shares = total_stake_shares * owners_fee / total_staked_balance` — but `total_staked_balance` here already includes `remaining_reward`, making the effective share price higher than it should be at the moment the fee is "purchased."
3. `self.total_staked_balance += owners_fee;` is applied afterward (line 234).

Because the share price denominator (`total_staked_balance`) is artificially inflated by `remaining_reward` prior to computing the owner's shares, `num_shares_from_staked_amount_rounded_down` yields a smaller `num_shares` than it would if computed against the pre-reward-distribution balance/shares ratio (as the deposit/stake flow does). This causes the owner (DAO/validator fee recipient) to be systematically under-minted shares for their protocol fee, with the value instead diffusing to existing stakers' share price. `internal_ping()` is invoked automatically on essentially every public entrypoint (`deposit`, `stake`, `unstake`, `ping`, etc.), so this ordering bug fires on every reward-bearing epoch transition triggered by any unprivileged user's ordinary contract interaction.

### Impact Explanation
This is a share/reward accounting divergence: the owner's protocol fee shares are minted at a mispriced share value due to incorrect operation ordering, causing systematic loss of fee value to the pool owner and a corresponding (small but compounding) over-credit to delegators' share price relative to fair entitlement. This matches the in-scope High-severity class of "Share, reward ... accounting divergence that lets ... over-credit value ... bypass fees." The magnitude is bounded by rounding (a few wei per epoch per the original report), but compounds over the contract's lifetime across many epochs and reward distributions.

### Likelihood Explanation
Likelihood is high in terms of reachability: `internal_ping()` runs on nearly every call, and any unprivileged staker's ordinary interactions (deposit/stake/unstake) after reward accrual will trigger the mispriced computation, with no special privilege required to trigger it. It requires no attacker action, only the natural progression of epochs and rewards — this is a systemic accounting bug rather than an exploit path controlled to disproportionately benefit a specific attacker, but it deterministically and repeatedly erodes owner fee accuracy in favor of the collective staked pool.

### Recommendation
Reorder the operations in `internal_ping()` to mirror `internal_stake`'s pattern: compute `num_shares` from `owners_fee` using the total_staked_balance/total_stake_shares state *before* `remaining_reward` is added, mint owner shares, and only then apply both `remaining_reward` and `owners_fee` to `self.total_staked_balance`. Concretely:
- Compute `num_shares = self.num_shares_from_staked_amount_rounded_down(owners_fee)` using the pre-update `total_staked_balance`.
- Update `account.stake_shares` and `self.total_stake_shares`.
- Only afterward apply `self.total_staked_balance += remaining_reward + owners_fee`.

### Proof of Concept
Given `total_staked_balance = T`, `total_stake_shares = S`, and a reward `total_reward = R` split into `remaining_reward = R_d` (delegators) and `owners_fee = R_o` (owner):

- Current (buggy) order: `T' = T + R_d`, then `num_shares = S * R_o / T'` = `S * R_o / (T + R_d)`.
- Correct order (deposit-flow-consistent): `num_shares = S * R_o / T` (computed before `T` is bumped by `R_d`).

Since `T + R_d > T`, the buggy computation always yields `num_shares` ≤ the correct value, under-minting the owner's fee shares — reproducible deterministically on any epoch with `total_reward > 0`, by simply calling `deposit`/`stake`/`unstake`/`ping` as any account after a new epoch with accrued staking rewards, referencing [2](#0-1) .

### Citations

**File:** staking-pool/src/internal.rs (L76-106)
```rust
        // Calculate the number of "stake" shares that the account will receive for staking the
        // given amount.
        let num_shares = self.num_shares_from_staked_amount_rounded_down(amount);
        assert!(
            num_shares > 0,
            "The calculated number of \"stake\" shares received for staking should be positive"
        );
        // The amount of tokens the account will be charged from the unstaked balance.
        // Rounded down to avoid overcharging the account to guarantee that the account can always
        // unstake at least the same amount as staked.
        let charge_amount = self.staked_amount_from_num_shares_rounded_down(num_shares);
        assert!(
            charge_amount > 0,
            "Invariant violation. Calculated staked amount must be positive, because \"stake\" share price should be at least 1"
        );

        assert!(
            account.unstaked >= charge_amount,
            "Not enough unstaked balance to stake"
        );
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

**File:** staking-pool/src/internal.rs (L213-234)
```rust
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
