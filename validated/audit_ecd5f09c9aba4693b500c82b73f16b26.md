Based on my research, I found a valid analog in agave's partitioned epoch-rewards distribution logic. The core parallel to the Sherlock bug (auto-vote state read live at tally time instead of from an epoch-end snapshot) is that agave's stake-reward *distribution* phase reads the **live, current `stakes_cache`** for account lamports/state when crediting rewards across multiple blocks, rather than a frozen snapshot taken at calculation time — and there is no code-level mechanism preventing legitimate account-state mutation (e.g. lamport transfers) between calculation and the specific block a given stake account is processed.

### Title
Partitioned epoch-reward distribution reads live stake-account state instead of a calculation-time snapshot, relying on an undocumented/unenforced no-mutation assumption - (File: runtime/src/bank/partitioned_epoch_rewards/distribution.rs)

### Summary
`calculate_rewards_for_partitioning`/`calculate_stake_rewards_and_commissions` compute each account's reward once, at the epoch boundary, and cache the result (`PartitionedStakeReward`, containing a *pre-computed* `new_stake.delegation.stake`) for later, batched crediting across up to 10% of an epoch's slots [1](#0-0) . When each partition/block is actually processed — one to many slots later — `store_stake_accounts_in_partition`/`build_updated_stake_reward` re-fetch the account from the **current** `self.stakes_cache.stakes()` (i.e., live state at the block being processed, not a snapshot from calculation time) and apply the previously computed reward on top of it [2](#0-1) [3](#0-2) .

### Finding Description
The code explicitly documents the exact assumption that this bug class exploits and asserts it is safe purely on the basis of "stake-program restrictions": [4](#0-3) 

This is the direct analog of the reported vulnerability: the vulnerable Voter contract assumed `autoOption`/balance couldn't meaningfully change between epoch end and tally, and only guarded against *disabling* auto-vote, not other mutations. Here, agave's distribution code assumes stake accounts cannot be mutated between the calculation snapshot and the (much later) distribution block, but the enforcement of that assumption is not visible in this code path — it depends entirely on separate, unverified logic in the stake program.

Critically, the codebase's own test suite demonstrates that lamport-level mutation between calculation and distribution *is* possible and is *not* rejected: [5](#0-4) 

In `test_delegation_adjustment_at_distribution`, extra lamports are added to the stake account **after** the reward snapshot was taken (`partitioned_rewards`) and **before** `distribute_epoch_rewards_in_partition` runs, and the code proceeds without any check that the account's balance/state still matches what was true at calculation time [6](#0-5) .

Additionally, `recalculate_stake_rewards` (invoked after snapshot restore, mid-distribution) documents a related caveat: reward-commission accounts loaded from the *current* bank do not reflect the start-of-epoch state, because there is no snapshot of all commission accounts, explicitly warning "the `RewardCommissionAccounts`... should NOT be used ever" from that recalculation path [7](#0-6) . This is the same "window between snapshot-time state and later-used state" class of bug flagged in the report.

I was **not able to locate**, within the indexed portion of the codebase, the specific stake-program-side check (if any) that is supposed to block delegation/merge/split/withdraw instructions on a stake account while `EpochRewardStatus::Active` — the comment in `distribution.rs` asserts such a restriction exists ("further state mutation prevents by stake-program restrictions") but I could not confirm its implementation or completeness via search. Given index size limits, some stake-program instruction-processing files may not be fully indexed; a full audit of `programs/stake-related` instruction handlers would be needed to verify whether this restriction is complete (e.g. covers `Merge`, `Split`, `Withdraw`, `Deactivate`, and plain SOL transfers into the stake account) for every window between per-account calculation and that account's specific distribution block.

### Impact Explanation
If the stake-program restriction referenced in the comment is incomplete (e.g., it doesn't block a plain `system_instruction::transfer` of lamports into the stake account, which the test explicitly performs), a user's stake account's on-chain lamports/state can diverge from what was assumed during the epoch-boundary calculation before that specific account is credited in its distribution partition/block. Because up to 10% of an epoch's slots elapse between calculation and last-processed partition, this is a materially long window. Any divergence directly affects `stake_reward_lamports_minted`, `capitalization`, and the stored `StakeStateV2` delegation amount, i.e., concrete on-chain value accounting — the same "manipulated distribution of value" impact class as the original report.

### Likelihood Explanation
Likelihood depends entirely on whether the stake program (or other bank logic) truly and completely rejects all mutation vectors while `EpochRewardStatus::Active`/`RewardInterval::InsideInterval`. I could not confirm this enforcement in the indexed code, so likelihood is uncertain rather than proven. The comment in `distribution.rs` explicitly signals that this is a load-bearing but externally-enforced invariant rather than something checked locally.

### Recommendation
Recommend an agave engineer verify, end-to-end, that no unprivileged account mutation vector (including plain lamport transfers into a stake account, and any stake-program instruction) can succeed on any stake account for the entire duration that account is `Active` (calculation through that account's specific distribution partition), and add a local/defensive check (e.g., re-deriving `new_stake.delegation.stake` from the live account rather than blindly trusting the cached calculation-time value, or asserting equality with a hard failure rather than silent overwrite) in `build_updated_stake_reward`.

### Proof of Concept
Not independently reproducible from this review; cited test `test_delegation_adjustment_at_distribution` in `runtime/src/bank/partitioned_epoch_rewards/distribution.rs` demonstrates the mutation-after-calculation window exists at the lamports level, but does not by itself prove an exploitable value-loss/gain since delegation stake there stays consistent by test construction. Confirming exploitability requires checking the stake program's instruction-level restrictions (not found in this search) for the same window.

### Citations

**File:** runtime/src/bank/partitioned_epoch_rewards/mod.rs (L408-428)
```rust
    /// Calculate the number of blocks required to distribute rewards to all stake accounts.
    pub(super) fn get_reward_distribution_num_blocks(
        &self,
        rewards: &PartitionedStakeRewards,
    ) -> u64 {
        let total_stake_accounts = rewards.num_rewards();
        if self.epoch_schedule.warmup && self.epoch < self.first_normal_epoch() {
            1
        } else {
            const MAX_FACTOR_OF_REWARD_BLOCKS_IN_EPOCH: u64 = 10;
            let num_chunks = total_stake_accounts
                .div_ceil(self.partitioned_rewards_stake_account_stores_per_block() as usize)
                as u64;

            // Limit the reward credit interval to 10% of the total number of slots in a epoch
            num_chunks.clamp(
                1,
                (self.epoch_schedule.slots_per_epoch / MAX_FACTOR_OF_REWARD_BLOCKS_IN_EPOCH).max(1),
            )
        }
    }
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L249-297)
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
        account
            .set_state(&StakeStateV2::Stake(meta, new_stake, flags))
            .map_err(|_| DistributionError::UnableToSetState)?;
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L327-335)
```rust
    /// Store stake rewards in partition
    /// Returns DistributionResults containing the sum of all the rewards
    /// stored, the sum of all rewards burned, and the updated StakeRewards.
    /// Because stake accounts are checked in calculation, and further state
    /// mutation prevents by stake-program restrictions, there should never be
    /// rewards burned.
    ///
    /// Note: even if staker's reward is 0, the stake account still needs to be
    /// stored because credits observed has changed
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L336-365)
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
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L1256-1292)
```rust

        let partitioned_rewards = StartBlockHeightAndPartitionedRewards {
            distribution_starting_block_height: bank.block_height() + REWARD_CALCULATION_NUM_BLOCKS,
            all_stake_rewards: Arc::new(stake_rewards.into_iter().collect()),
            partition_indices: vec![(0..expected_num).collect::<Vec<_>>()],
        };

        // But we transfer in more lamports before distribution time
        stake_account.checked_add_lamports(1_000_000_000).unwrap();
        bank.store_account(&stake_pubkey, &stake_account);

        // Distribute rewards
        let pre_cap = bank.capitalization();
        bank.distribute_epoch_rewards_in_partition(&partitioned_rewards, 0);
        let post_cap = bank.capitalization();
        let post_epoch_rewards_account = bank.get_account(&sysvar::epoch_rewards::id()).unwrap();

        // Assert that epoch rewards sysvar lamports balance does not change
        assert_eq!(post_epoch_rewards_account.lamports(), expected_balance);

        let epoch_rewards: sysvar::epoch_rewards::EpochRewards =
            from_account(&post_epoch_rewards_account).unwrap();
        assert_eq!(epoch_rewards.total_rewards, total_rewards);
        assert_eq!(epoch_rewards.distributed_rewards, rewards_to_distribute,);

        // Assert that the bank total capital changed by the amount of rewards
        // distributed
        assert_eq!(pre_cap + rewards_to_distribute, post_cap);

        // Check that delegation just gets rewards
        let post_account = bank.get_account(&stake_pubkey).unwrap();
        let post_stake_state: StakeStateV2 = post_account.state().unwrap();
        let pre_stake_state: StakeStateV2 = stake_account.state().unwrap();
        assert_eq!(
            post_stake_state.delegation().unwrap().stake,
            pre_stake_state.delegation().unwrap().stake + reward_lamports
        );
```

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L1069-1075)
```rust
        // NOTE: the `RewardCommissionAccounts` will NOT have a correct
        // post_lamport amount if the commission account is NOT the vote account,
        // because the commission account is loaded from the current bank, and
        // not the start of the epoch. We don't have a snapshot of all commission
        // accounts from the start of the epoch. For this reason, the
        // `RewardCommissionAccounts` calculated in this function call should
        // NOT be used ever.
```
