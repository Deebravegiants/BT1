### Title
Stale reward-calculation snapshot vs. live stake state causes a deterministic `assert_eq!` panic during epoch reward distribution - (File: runtime/src/bank/partitioned_epoch_rewards/distribution.rs)

### Summary
The Notional bug arises because `_executeRebalance()` compares a "before" value computed one way and an "after" value computed another way, and the two are implicitly assumed to be consistent; when they diverge, an unconditional `require()` reverts. Agave has a structurally identical pattern in the partitioned epoch-reward pipeline: `TreasuryAction`'s two independent value computations map to `calculate_stake_rewards_and_commissions()` (a stake-delegation snapshot taken once at epoch-start, cached) versus the live `stakes_cache` read at distribution time several blocks later in `build_updated_stake_reward()`. Instead of a `require()`/revert, Agave uses an `assert_eq!` that panics the validator process when the two disagree.

### Finding Description
Reward calculation for an epoch is performed once, based on a snapshot of `stake_delegations` taken at the epoch boundary, and the result (`PartitionedStakeReward`, containing the pre-computed `new_stake.delegation.stake`) is cached and reused across multiple future blocks for the actual distribution [1](#0-0) . Distribution begins `REWARD_CALCULATION_NUM_BLOCKS` after calculation and proceeds over `num_partitions` further blocks [2](#0-1) . This is a multi-block window during which ordinary, permissionless stake-program instructions (Split, Merge, Withdraw, Deactivate, Redelegate) on the very same stake account can legitimately change its `delegation.stake` field, live in `stakes_cache`.

At distribution time, `store_stake_accounts_in_partition` reads the **current, live** stake account from `stakes_cache_accounts` (reflecting any such intervening mutation) and passes it to `build_updated_stake_reward` [3](#0-2) . Inside `build_updated_stake_reward`, when `adjust_delegations_for_rent` is `false` (i.e., the `relax_post_exec_min_balance_check` feature is not active), the code asserts that the live delegation plus the pre-computed reward equals the delegation value that was already baked into the cached calculation:

```
let expected_delegation = stake.delegation.stake
    .saturating_add(partitioned_stake_reward.inflation.stake_reward);
assert_eq!(
    expected_delegation, new_stake.delegation.stake,
    "stake reward delegation must be consistent with the updated stake account \
     lamport balance"
);
``` [4](#0-3) 

`stake.delegation.stake` here comes from the live account fetched from `stakes_cache_accounts` at distribution time [5](#0-4) , while `new_stake.delegation.stake` (`partitioned_stake_reward.inflation.stake`) was computed earlier from the epoch-start snapshot in `calculate_stake_rewards_and_commissions`/`redeem_delegation_rewards` [6](#0-5) . Just like Notional's `getExchangeRateView()` returning two different values depending on whether the interest-rate model changed, Agave here has two independently-derived values for the "same" delegation state that are only guaranteed consistent absent any intervening stake mutation. When they diverge — which is entirely plausible given the multi-block distribution window and permissionless stake operations — the `assert_eq!` fires.

### Impact Explanation
Unlike Notional's `require()`, which only reverts a single manager-triggered rebalance transaction, Agave's `assert_eq!` is a Rust panic executed deep inside deterministic block processing (`distribute_partitioned_epoch_rewards`, invoked every slot while rewards are active). Since all correctly-configured validators replay the same block deterministically, every validator that has not activated `relax_post_exec_min_balance_check` would hit this panic at the same point, crashing the validator process. This is a cluster-wide liveness halt triggered by an ordinary, unprivileged user action (splitting, merging, deactivating, or withdrawing from their own stake account) landing in the reward-calculation/distribution window — a categorically worse outcome than the referenced medium-severity Notional bug (a revert), since it is a hard crash/consensus halt rather than merely a failed transaction.

### Likelihood Explanation
Likelihood depends on:
- The `relax_post_exec_min_balance_check` feature gate: if it is active, the code path takes `adjust_delegation_for_rent` instead (no assert), so the bug is currently dormant on clusters where this feature has already been activated (this repo shows it is a fairly broadly-referenced, seemingly mature feature flag, and it is plausible it is enabled on mainnet-beta; this could not be fully confirmed from the index alone).
- On any cluster/testnet/devnet/private cluster where the feature has not yet been activated, or during any period between genesis and its activation, the scenario is reachable by any staker performing a normal stake operation during the distribution window, which spans multiple blocks per epoch by design.
- This matches the Sherlock panel's own reasoning for the Notional issue ("viable, though unlikely" scenario, still Medium) — here the analog is arguably *more* likely to occur naturally, since legitimate stake account mutations (Split/Merge/Deactivate/Withdraw) are common actions and the distribution window is guaranteed to span several blocks every epoch on every cluster still running with the flag off.

### Recommendation
Do not use a hard `assert_eq!`/panic when the calculation-time and distribution-time delegation values diverge. Instead, always apply the `adjust_delegation_for_rent`-style reconciliation logic (clamping/adjusting to the live account state) regardless of the `relax_post_exec_min_balance_check` feature flag, or gracefully recompute/skip the reward for that account rather than crashing the bank. At minimum, gate rollout of the fix so that the assert-based branch is fully retired on all clusters before any code path can still exercise it.

### Proof of Concept
1. On a cluster where `relax_post_exec_min_balance_check` is inactive, wait for an epoch boundary; reward calculation snapshots `stake_delegations` and computes `PartitionedStakeReward` entries, cached for the epoch [7](#0-6) .
2. During the window between `distribution_starting_block_height` (a few blocks after calculation) and completion of all `num_partitions` distribution blocks, submit a normal `Split`, `Merge`, `Deactivate`, or `Withdraw` instruction on a stake account whose reward has not yet been distributed, changing its live `delegation.stake`.
3. When the bank reaches the block/partition containing that stake account, `store_stake_accounts_in_partition` reads the now-mutated live account [3](#0-2)  and calls `build_updated_stake_reward`, where `expected_delegation` (live value + cached reward) no longer equals `new_stake.delegation.stake` (the calculation-time value), triggering the `assert_eq!` panic [8](#0-7) , crashing every validator that deterministically replays this block with the feature inactive.

### Citations

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L299-345)
```rust
    pub(in crate::bank) fn calculate_rewards(
        &self,
        stake_history: &StakeHistory,
        stake_delegations: Vec<(&Pubkey, &StakeAccount<Delegation>)>,
        cached_vote_accounts: CachedVoteAccounts<'_>,
        rewarded_epoch: Epoch,
        reward_epoch_delegated_stakes: RewardEpochDelegatedStakes,
        reward_calc_tracer: Option<impl Fn(&RewardCalculationEvent) + Send + Sync>,
        thread_pool: &ThreadPool,
        metrics: &mut RewardsMetrics,
    ) -> Arc<PartitionedRewardsCalculation> {
        // We hold the lock here for the epoch rewards calculation cache to prevent
        // rewards computation across multiple forks simultaneously. This aligns with
        // how banks are currently created- all banks are created sequentially.
        // As such, this lock does not actually introduce contention because bank
        // creation (and therefore reward calculation) is always done sequentially.
        //
        // However, if we plan to support creating banks in parallel in the future, this logic
        // would need to change to allow rewards computation on multiple forks concurrently.
        // That said, there's still a compelling reason to keep this lock even in a parallel
        // bank creation model: we want to avoid calculating rewards multiple times for the same
        // parent bank hash. This lock ensures that.
        //
        // Creating bank for multiple forks in parallel would also introduce contention for compute resources,
        // potentially slowing down the performance of both forks. This, in turn, could delay
        // vote propagation and consensus for the leading fork—the one most likely to become rooted.
        //
        // Therefore, it seems beneficial to continue processing forks sequentially at epoch
        // boundaries: acquire the lock for the first fork, compute rewards, and let other forks
        // wait until the computation is complete.
        let mut epoch_rewards_calculation_cache =
            self.epoch_rewards_calculation_cache.lock().unwrap();
        let rewards_calculation = epoch_rewards_calculation_cache
            .entry(self.parent_hash)
            .or_insert_with(|| {
                Arc::new(self.calculate_rewards_for_partitioning(
                    stake_history,
                    stake_delegations,
                    cached_vote_accounts,
                    rewarded_epoch,
                    reward_epoch_delegated_stakes,
                    reward_calc_tracer,
                    thread_pool,
                    metrics,
                ))
            })
            .clone();
```

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L642-649)
```rust
        let vote_pubkey = stake_account.delegation().voter_pubkey;

        let current_lamports = stake_account.lamports();
        let minimum_lamports = self
            .rent_collector
            .rent
            .minimum_balance(stake_account.data_len());
        let stake = *stake_account.stake();
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L80-149)
```rust
    pub(in crate::bank) fn distribute_partitioned_epoch_rewards(&mut self) {
        let EpochRewardStatus::Active(status) = &self.epoch_reward_status else {
            return;
        };

        let distribution_starting_block_height = match &status {
            EpochRewardPhase::Calculation(status) => status.distribution_starting_block_height,
            EpochRewardPhase::Distribution(status) => status.distribution_starting_block_height,
        };

        let height = self.block_height();
        if height < distribution_starting_block_height {
            return;
        }

        if let EpochRewardPhase::Calculation(status) = &status {
            // epoch rewards have not been partitioned yet, so partition them now
            // This should happen only once immediately on the first rewards distribution block, after reward calculation block.
            let epoch_rewards_sysvar = self.get_epoch_rewards_sysvar();
            let (partition_indices, partition_us) = measure_us!({
                epoch_rewards_hasher::hash_rewards_into_partitions(
                    &status.all_stake_rewards,
                    &epoch_rewards_sysvar.parent_blockhash,
                    epoch_rewards_sysvar.num_partitions as usize,
                )
            });

            // update epoch reward status to distribution phase
            self.set_epoch_reward_status_distribution(
                distribution_starting_block_height,
                Arc::clone(&status.all_stake_rewards),
                partition_indices,
            );

            datapoint_info!(
                "epoch-rewards-status-update",
                ("slot", self.slot(), i64),
                ("block_height", height, i64),
                ("partition_us", partition_us, i64),
                (
                    "distribution_starting_block_height",
                    distribution_starting_block_height,
                    i64
                ),
            );
        }

        let EpochRewardStatus::Active(EpochRewardPhase::Distribution(partition_rewards)) =
            &self.epoch_reward_status
        else {
            // We should never get here.
            unreachable!(
                "epoch rewards status is not in distribution phase, but we are trying to \
                 distribute rewards"
            );
        };

        let distribution_end_exclusive =
            distribution_starting_block_height + partition_rewards.partition_indices.len() as u64;

        assert!(
            self.epoch_schedule.get_slots_in_epoch(self.epoch)
                > partition_rewards.partition_indices.len() as u64
        );

        if height >= distribution_starting_block_height && height < distribution_end_exclusive {
            let partition_index = height - distribution_starting_block_height;

            self.distribute_epoch_rewards_in_partition(partition_rewards, partition_index);
        }
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L249-261)
```rust
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
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L269-293)
```rust
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
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L336-393)
```rust
    fn store_stake_accounts_in_partition(
        &self,
        partition_rewards: &StartBlockHeightAndPartitionedRewards,
        partition_index: u64,
    ) -> DistributionResults {
        let feature_snapshot = self.feature_set.snapshot();
        // Name intentionally doesn't match -- "adjust delegations for rent" is
        // part of relaxing post-exec min balance checks.
        let adjust_delegations_for_rent = feature_snapshot.relax_post_exec_min_balance_check;
        let use_fixed_point_stake_math = feature_snapshot.upgrade_bpf_stake_program_to_v5_1;

        let mut stake_reward_lamports_minted = 0;
        let mut stake_reward_lamports_burned = 0;
        let mut block_reward_lamports_distributed = 0;
        let mut block_reward_lamports_burned = 0;
        let indices = partition_rewards
            .partition_indices
            .get(partition_index as usize)
            .unwrap_or_else(|| {
                panic!(
                    "partition index out of bound: {partition_index} >= {}",
                    partition_rewards.partition_indices.len()
                )
            });
        let mut updated_stake_rewards = Vec::with_capacity(indices.len());
        let stakes_cache = self.stakes_cache.stakes();
        let stakes_cache_accounts = stakes_cache.stake_delegations();
        let stake_history = stakes_cache.history();
        let new_warmup_cooldown_rate_epoch = self.new_warmup_cooldown_rate_epoch();
        let rent = &self.rent_collector.rent;
        for index in indices {
            let partitioned_stake_reward = partition_rewards
                .all_stake_rewards
                .get(*index)
                .unwrap_or_else(|| {
                    panic!(
                        "partition reward out of bound: {index} >= {}",
                        partition_rewards.all_stake_rewards.total_len()
                    )
                })
                .as_ref()
                .unwrap_or_else(|| {
                    panic!("partition reward {index} is empty");
                });
            let stake_pubkey = partitioned_stake_reward.stake_pubkey;
            let stake_reward_amount = partitioned_stake_reward.inflation.stake_reward;
            let block_reward_amount = partitioned_stake_reward.block_reward;

            match Self::build_updated_stake_reward(
                self.epoch,
                stake_history,
                new_warmup_cooldown_rate_epoch,
                stakes_cache_accounts,
                partitioned_stake_reward,
                rent,
                adjust_delegations_for_rent,
                use_fixed_point_stake_math,
            ) {
```
