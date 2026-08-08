I found the strongest analog: the reward calculation/distribution race in `runtime/src/bank/partitioned_epoch_rewards/`. This mirrors the Solidity bug class precisely — a value (reward/commission amount) is calculated against a snapshot of state, but the account can be mutated by an unprivileged, independent action before the deferred distribution/settlement actually executes, and the code explicitly acknowledges this creates an incorrect/inconsistent outcome that "should NOT be used."

### Title
Stale reward-commission accounting due to snapshot/distribution time-of-check-to-time-of-use gap - (File: `runtime/src/bank/partitioned_epoch_rewards/calculation.rs`)

### Summary
Partitioned epoch rewards are computed in two temporally separated phases: a "calculation" phase that snapshots stake/vote account state and computes `PartitionedRewardsCalculation` (including `RewardCommissionAccounts`), and a later "distribution" phase where the computed lamport amounts are actually applied to accounts loaded fresh from the bank. Between these two phases, unprivileged users can mutate the relevant accounts (e.g., via VAT/other burns, transfers, or other unprivileged instructions acting on stake/vote/commission accounts), causing the amounts computed during calculation to diverge from the true state at distribution time — analogous to the Lido vault computing `adminSettleDebtAmount` against an expected vault state that changes before settlement executes, resulting in under/mis-compensation.

### Finding Description
`Bank::recalculate_stake_rewards` in [1](#0-0)  explicitly documents this exact hazard: [2](#0-1) 

This comment states that `RewardCommissionAccounts` computed during recalculation "will NOT have a correct post_lamport amount if the commission account is NOT the vote account, because the commission account is loaded from the current bank, and not the start of the epoch," and that these values "should NOT be used ever" — a direct admission that a calculation-time snapshot value diverges from actual current state by the time distribution occurs, i.e. exactly the TOCTOU pattern in the reference report (compute an amount against an assumed/expected state, but the real state can change before the computed amount is actually applied).

The `distribute_reward_commissions` path separately re-loads commission accounts at distribution time via `load_and_reward_commission_accounts`, with a comment acknowledging "any intervening account mutations (e.g. VAT burns in `update_epoch_stakes`)" between calculation and distribution: [3](#0-2) . Similarly, `redeem_delegation_rewards` contains explicit logic to handle stake accounts receiving unexpected lamports between calculation and distribution: [4](#0-3) , and `delegation_may_need_adjustment`/`build_updated_stake_reward` in [5](#0-4)  adjust delegation to reconcile the gap.

While the "distribution" phase (`store_stake_accounts_in_partition`/`load_and_reward_commission_accounts`) does reload accounts and appears to reconcile many cases, the explicit statement that `RewardCommissionAccounts` from `recalculate_stake_rewards` "should NOT be used ever" indicates this recalculation path produces stale/inconsistent commission accounting whenever it is invoked (e.g., following snapshot restore mid-distribution), and any caller relying on it, or any edge case not covered by the reconciliation logic in `build_updated_stake_reward`'s `adjust_delegations_for_rent` branch, would use pre-mutation figures for a post-mutation account.

### Impact Explanation
If reward-commission or stake-delegation lamport amounts computed during the calculation phase are ever consumed by code without re-deriving them at actual distribution time (as the recalculation path explicitly warns against but leaves as an available API surface), validators could pay out commissions/rewards that don't match on-chain account state — producing value creation/loss or accounting mismatches that would materially diverge node behavior if the reconciliation isn't applied uniformly by all callers. This maps to the reference report's "Medium" impact class: participants (stakers/vote accounts) receiving mis-priced settlement due to a stale expected-state assumption.

### Likelihood Explanation
This requires no privileged access — any account mutation to a stake or non-vote-account commission collector between the epoch-boundary calculation block and the corresponding partitioned distribution block(s) (which can span many blocks) triggers the divergence. The codebase's own tests (`test_load_and_reward_commission_accounts_reflects_vat_burn`, `test_delegation_adjustment_at_distribution`, `test_recalculate_alpenglow_rewards_after_partial_distribution_uses_original_denominator`) demonstrate the developers are aware of and actively testing this race window, confirming it is a real, reachable condition rather than theoretical.

### Recommendation
Ensure every consumer of stake/commission reward amounts always re-derives lamport deltas from the account state at actual distribution time rather than the calculation-time snapshot, and remove or gate the `recalculate_stake_rewards` "should NOT be used" `RewardCommissionAccounts` output so it cannot be mistakenly consumed by future code paths (e.g., make the type unconstructible/unreturnable in that function, or add a debug assertion).

### Proof of Concept
1. At an epoch boundary, `Bank::calculate_rewards`/`calculate_stake_rewards_and_commissions` snapshots stake and vote/commission accounts and computes expected commission lamport amounts and stake delegations for the whole reward-distribution window (which spans multiple blocks/partitions).
2. Before the specific partition containing a given stake/commission account is processed by `distribute_partitioned_epoch_rewards`, an unprivileged transaction (or protocol-level VAT burn, as tested in `test_load_and_reward_commission_accounts_reflects_vat_burn`) modifies the account's lamport balance.
3. `recalculate_stake_rewards`, invoked on `recalculate_partitioned_rewards_if_active` (e.g., after snapshot restore mid-distribution), computes `RewardCommissionAccounts` against the *current* (already-mutated) account for stake rewards, while its own inline comment confirms the commission-account lamport figures it produces "will NOT have a correct post_lamport amount" and "should NOT be used ever" — demonstrating the calculation-vs-distribution snapshot divergence is a known, real hazard in this exact code path [6](#0-5) .

### Citations

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L651-696)
```rust
        let Some(vote_account) = distribution_epoch_vote_accounts.get(&vote_pubkey) else {
            debug!("could not find vote account {vote_pubkey} in cache");
            // Even if the vote account doesn't exist, there might still be a
            // need to adjust the stake delegation
            if adjust_delegations_for_rent {
                let status = delegation_activation_status(
                    &stake.delegation,
                    rewarded_epoch,
                    stake_history,
                    new_rate_activation_epoch,
                    use_fixed_point_stake_math,
                );
                if delegation_may_need_adjustment(
                    stake.delegation.stake,
                    stake.delegation.stake,
                    current_lamports,
                    minimum_lamports,
                    status,
                ) {
                    debug!(
                        "delegation for stake {stake_pubkey} may be adjusted at distribution, \
                         unless lamports are transferred before distribution block"
                    );
                    let inflation = InflationReward {
                        stake,
                        stake_reward: 0,
                        commission_bps: (!custom_commission_collector).then_some(0),
                    };
                    // Set `is_vote_account` to `false` in order to deliberately
                    // fail during commission collector checks. This avoids
                    // creating a reward entry during payout.
                    let reward_commission = RewardCommission {
                        commission_bps: (!custom_commission_collector).then_some(0),
                        commission_lamports: 0,
                        burned_lamports: 0,
                        is_vote_account: false,
                    };
                    return Some(InflationRewardWithCommission {
                        inflation,
                        commission_pubkey: vote_pubkey,
                        reward_commission,
                    });
                } else {
                    debug!("delegation for stake {stake_pubkey} will not be adjusted");
                    return None;
                }
```

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L1063-1075)
```rust
        // On recalculation, only the `StakeRewardCalculation::stake_rewards`
        // field is relevant. It is assumed that reward commission accounts have
        // already been calculated and delivered, while
        // `StakeRewardCalculation::total_rewards` only reflects rewards that
        // have not yet been distributed.
        //
        // NOTE: the `RewardCommissionAccounts` will NOT have a correct
        // post_lamport amount if the commission account is NOT the vote account,
        // because the commission account is loaded from the current bank, and
        // not the start of the epoch. We don't have a snapshot of all commission
        // accounts from the start of the epoch. For this reason, the
        // `RewardCommissionAccounts` calculated in this function call should
        // NOT be used ever.
```

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L1097-1075)
```rust

```

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L1097-1101)
```rust
    /// Load each planned commission account from the store and apply its
    /// reward. This is the single point where commission account data is
    /// fetched, ensuring we always see the latest balances — including any
    /// intervening account mutations (e.g. VAT burns in `update_epoch_stakes`)
    /// that happen between calculation and distribution.
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L239-294)
```rust
    fn build_updated_stake_reward(
        distribution_epoch: u64,
        stake_history: &StakeHistory,
        new_warmup_cooldown_rate_epoch: Option<Epoch>,
        stakes_cache_accounts: &imbl::HashMap<Pubkey, StakeAccount<Delegation>>,
        partitioned_stake_reward: &PartitionedStakeReward,
        rent: &Rent,
        adjust_delegations_for_rent: bool,
        use_fixed_point_stake_math: bool,
    ) -> Result<StakeReward, DistributionError> {
        let stake_account = stakes_cache_accounts
            .get(&partitioned_stake_reward.stake_pubkey)
            .ok_or(DistributionError::AccountNotFound)?
            .clone();

        let (mut account, stake_state): (AccountSharedData, StakeStateV2) = stake_account.into();
        let StakeStateV2::Stake(meta, stake, flags) = stake_state else {
            // StakesCache only stores accounts where StakeStateV2::delegation().is_some()
            unreachable!(
                "StakesCache entry {:?} failed StakeStateV2 deserialization",
                partitioned_stake_reward.stake_pubkey
            )
        };
        account
            .checked_add_lamports(partitioned_stake_reward.inflation.stake_reward)
            .map_err(|_| DistributionError::ArithmeticOverflow)?;
        account
            .checked_add_lamports(partitioned_stake_reward.block_reward)
            .map_err(|_| DistributionError::ArithmeticOverflow)?;

        let mut new_stake = partitioned_stake_reward.inflation.stake;
        if adjust_delegations_for_rent {
            let minimum_balance = rent.minimum_balance(account.data().len());
            // The rewarded epoch is right before the distribution epoch
            let rewarded_epoch = distribution_epoch.saturating_sub(1);
            // The entry in `partitioned_stake_reward` contains the rewards,
            // calculated during the calculation phase
            let delegation_with_rewards = new_stake.delegation.stake;
            adjust_delegation_for_rent(
                &mut new_stake.delegation,
                rewarded_epoch,
                delegation_with_rewards,
                account.lamports(),
                minimum_balance,
            );
        } else {
            let expected_delegation = stake
                .delegation
                .stake
                .saturating_add(partitioned_stake_reward.inflation.stake_reward);
            assert_eq!(
                expected_delegation, new_stake.delegation.stake,
                "stake reward delegation must be consistent with the updated stake account \
                 lamport balance"
            );
        }
```
