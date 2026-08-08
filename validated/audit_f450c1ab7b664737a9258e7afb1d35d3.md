### Title
Stake reward/delegation adjustment computed from instantaneous account balance rather than tracked delegation, allowing lamport-transfer manipulation - (File: runtime/src/inflation_rewards/mod.rs; runtime/src/bank/partitioned_epoch_rewards/calculation.rs; runtime/src/bank/partitioned_epoch_rewards/distribution.rs)

### Summary
The rent-adjustment logic added for SIMD-0392 (`adjust_delegations_for_rent`) computes a stake account's new delegation amount from the *current point-in-time lamport balance* of the stake account (`stake_account.lamports()` / `current_lamports`) rather than from a value that is fixed/tracked independently of external lamport transfers. Because a stake account's lamport balance can be increased between reward-calculation time and reward-distribution time by anyone transferring lamports directly into it (the same class of issue as the external report: relying on a "balance at a specific moment" instead of a tracked cumulative/authoritative amount), the computed `delegation.stake` can be inflated beyond what the staker actually delegated/earned via the normal delegate/rewards path.

### Finding Description
In `redeem_stake_rewards` (`runtime/src/inflation_rewards/mod.rs`), when `adjust_delegations_for_rent` is active, the new delegation is derived from `current_lamports` (the stake account's live lamport balance) plus staker rewards: [1](#0-0) 

`current_lamports` is passed in from `redeem_delegation_rewards` in `runtime/src/bank/partitioned_epoch_rewards/calculation.rs`, and it is read directly off the stake account object at reward-calculation time via `stake_account.lamports()`: [2](#0-1) 

Separately, `delegation_may_need_adjustment` (`runtime/src/inflation_rewards/mod.rs`, re-exported logic) and `adjust_delegation_for_rent` in `runtime/src/bank/partitioned_epoch_rewards/distribution.rs` again clamp/compute `new_delegation` using `lamports_with_rewards` — i.e., the balance read at distribution time, not a value protected from external mutation: [3](#0-2) 

The bank's own test suite explicitly documents that lamports can be transferred into the stake account *between calculation and distribution*, changing the outcome — the debug log even warns "delegation for stake {stake_pubkey} may be adjusted at distribution, unless lamports are transferred before distribution block": [4](#0-3) 

And the regression test `test_delegation_adjustment_at_distribution` demonstrates the exact mechanic: after reward calculation, the test transfers extra lamports into the stake account before the distribution block runs, and the final delegation/stake amount changes as a direct consequence of that late balance change: [5](#0-4) 

This mirrors the external report's root cause precisely: a limit/derived-value calculation (there: max mintable amount; here: delegation/stake amount) is computed from a mutable point-in-time balance (`daoBalance` there; `stake_account.lamports()` / `current_lamports` here) instead of from a value tracked independently of unrelated external transfers into the account.

### Impact Explanation
If the derived `delegation.stake` can be pushed upward by transferring extra lamports into a stake account after reward calculation but before distribution (a normal, permissionless system-program transfer to any stake account, since stake accounts are simply lamport-holding accounts), a staker's effective/active stake used for future epoch reward-point calculations, warm-up/cool-down stake activation, and capitalization accounting can be inflated relative to what was legitimately delegated. Since this feeds into stake-weighted reward distribution and (transitively) leader/voting stake weight calculations, it represents undeclared/incorrect state mutation of consensus-relevant stake amounts driven by an account-balance side channel rather than the delegate/deactivate instruction path. This is a Medium-impact class of bug consistent with the original report (imprecise validation/derivation of amounts from balance snapshots rather than tracked state).

### Likelihood Explanation
Likelihood is constrained by the fact that this code path is gated by the `relax_post_exec_min_balance_check` / `adjust_delegations_for_rent` feature flag and only actually changes behavior in narrow SIMD-0392 rent-increase adjustment scenarios (i.e., it is a deliberate mechanism to "absorb" externally-added lamports into stake, and the code/tests appear aware of and intentionally tolerate the timing window). It requires the attacker to send a plain system transfer to a target stake account within the calculation→distribution window of an epoch boundary, which is easily performable by any unprivileged user, but the actual value uplift achievable is bounded by the rent-related adjustment logic's clamps (`min(new_delegation_with_rewards, lamports_with_rewards - minimum_lamports)`), not unbounded free minting.

### Recommendation
Do not derive `delegation.stake` from the stake account's live lamport balance at calculation/distribution time. Instead, track the delegation amount and any legitimately expected reward/rent adjustments as an independent value computed once (e.g., snapshotted at reward-calculation time) and carried through distribution without re-reading `stake_account.lamports()`, or explicitly bound the adjustment to only the amount attributable to the rent-parameter change and rewards, never to arbitrary externally-added lamports. If the SIMD-0392 design intentionally allows folding in externally-added lamports as a mitigation for rent increases, this should be re-documented and explicitly reviewed to confirm it cannot be leveraged to manipulate active-stake accounting beyond the intended rent-shortfall-absorption use case.

### Proof of Concept
The existing test `test_delegation_adjustment_at_distribution` in `runtime/src/bank/partitioned_epoch_rewards/distribution.rs` is itself a working PoC of the mechanism: it creates a stake account destined to be destaked/reduced by the rent adjustment logic, then calls `stake_account.checked_add_lamports(1_000_000_000)` (a plain lamport credit, equivalent to any external transfer) and stores it back to the bank *before* `distribute_epoch_rewards_in_partition` executes: [6](#0-5) 
The test then asserts the resulting delegation differs from what it would have been without the injected transfer, confirming that an externally-injected balance change between calculation and distribution alters the computed delegation/stake value — the same "balance at a specific moment doesn't reflect the true tracked amount" flaw described in the source report, applied to Agave's stake delegation accounting instead of a DAO's deposit-cap accounting.

### Citations

**File:** runtime/src/inflation_rewards/mod.rs (L146-169)
```rust
    let staker_rewards = maybe_rewards.map(|x| x.0).unwrap_or(0);
    if adjust_delegations_for_rent {
        let new_delegation_with_rewards = stake.delegation.stake.saturating_add(staker_rewards);
        let needs_adjustment = delegation_may_need_adjustment(
            stake.delegation.stake,
            new_delegation_with_rewards,
            current_lamports.saturating_add(staker_rewards),
            minimum_lamports,
            status,
        );
        // If `maybe_rewards.is_some()`, need to drive forward credits, even
        // if rewards are zero
        if needs_adjustment || maybe_rewards.is_some() {
            stake.delegation.stake = new_delegation_with_rewards;
            let voter_rewards = maybe_rewards.map(|x| x.1).unwrap_or(0);
            Some((staker_rewards, voter_rewards))
        } else {
            None
        }
    } else {
        stake.delegation.stake += staker_rewards;
        maybe_rewards
    }
}
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

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L663-696)
```rust
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

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L49-76)
```rust
/// Adjusts stake delegation based on Rent sysvar parameters.
///
/// As part of SIMD-0392, if Rent is ever increased, we need to make sure that
/// lamports are not double-counted for the rent-exempt minimum and the stake
/// delegation. This function adjusts the delegation in a Stake if needed, right
/// at distribution time.
fn adjust_delegation_for_rent(
    delegation: &mut Delegation,
    rewarded_epoch: Epoch,
    new_delegation_with_rewards: u64,
    lamports_with_rewards: u64,
    minimum_lamports: u64,
) {
    let new_delegation = std::cmp::min(
        new_delegation_with_rewards,
        lamports_with_rewards.saturating_sub(minimum_lamports),
    );

    if new_delegation != delegation.stake {
        delegation.stake = new_delegation;
        // Deactivate stake if needed. This deactivation is immediate,
        // unlike a requested deactivation which happens at the next epoch
        // boundary
        if new_delegation == 0 {
            delegation.deactivation_epoch = rewarded_epoch;
        }
    }
}
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L1244-1292)
```rust
        lower_rent.lamports_per_byte /= 10;

        // Below new minimum, small reward, should normally be destaked
        let reward_lamports = 1;
        let reward = PartitionedStakeReward::new_with_lamport_amounts(reward_lamports, 0, 1);
        let rewards_to_distribute = reward.inflation.stake_reward;
        let stake_pubkey = reward.stake_pubkey;
        let stake_rewards = [reward];
        populate_starting_stake_accounts_from_stake_rewards(&bank, &lower_rent, &stake_rewards);
        let mut stake_account = bank.get_account(&stake_pubkey).unwrap();

        let expected_num = 1;

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
