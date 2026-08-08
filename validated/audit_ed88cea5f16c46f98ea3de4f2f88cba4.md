### Title
Vote account `pending_delegator_rewards` reserve is never decremented on the vote account itself, permanently locking withdrawer funds — (File: programs/vote/src/vote_state/mod.rs)

### Summary
`withdraw()` in `programs/vote/src/vote_state/mod.rs` enforces that a vote account's balance can never drop below `rent_exempt_minimum + pending_delegator_rewards`, and blocks closing the account entirely while `pending_delegator_rewards > 0` [1](#0-0) . This mirrors the Biconomy `removeSupportedToken` bug class: once a "supported/reserved" flag/balance is set, a check elsewhere permanently refuses to let the owner withdraw funds tied to that flag, even after the underlying obligation should have been satisfied.

### Finding Description
`pending_delegator_rewards` is incremented via `deposit_delegator_rewards` → `add_pending_delegator_rewards`, which only ever adds to the field (`checked_add`), never subtracts [2](#0-1) [3](#0-2) .

Separately, `runtime/src/bank/partitioned_epoch_rewards/calculation.rs::calculate_block_reward` *reads* `vote_state.pending_delegator_rewards()` to compute per-delegator block rewards during epoch reward distribution [4](#0-3) , and the distribution path (`store_stake_accounts_in_partition` / `build_updated_stake_reward`) credits lamports to delegators' *stake accounts* [5](#0-4) . However, none of the searched call sites in `vote_state/handler.rs`, `vote_state/mod.rs`, or `vote_processor.rs` show the vote account's own `pending_delegator_rewards` field being decremented after this distribution occurs — the only mutator found is the additive one in `handler.rs`. If the vote account's stored `pending_delegator_rewards` is not reduced once the corresponding lamports have actually been paid out to delegators, the `withdraw()` check keeps reserving those lamports forever, i.e., the withdrawer's own already-deposited SOL becomes permanently unreclaimable even though the debt it was meant to cover has already been settled — directly analogous to Biconomy's `removeLiquidity` check on `isTokenSupported` blocking withdrawal of otherwise-legitimate funds indefinitely.

### Impact Explanation
If confirmed, this results in a real, permanent loss of access to funds for the vote account's `authorized_withdrawer` — an unprivileged actor from the SVM's perspective interacting only through the ordinary `Withdraw` vote instruction. Lamports deposited via `DepositDelegatorRewards` (SIMD-0123) to fund future delegator rewards would remain locked in the vote account forever after they have already been paid out to delegators, since `withdraw()`'s `min_balance = rent_exempt_minimum + pending_delegator_rewards` check in `programs/vote/src/vote_state/mod.rs:1113-1121` never relaxes.

### Likelihood Explanation
Uncertain / not fully verified. My tool-based search of `programs/vote/src/vote_state/handler.rs`, `programs/vote/src/vote_state/mod.rs`, and `programs/vote/src/vote_processor.rs` found only the additive mutator (`add_pending_delegator_rewards`) and no visible decrement call site reachable from the reward-distribution code path (`runtime/src/bank/partitioned_epoch_rewards/*`), but the index/search coverage may be incomplete — there could be a decrement performed elsewhere (e.g., inside `store_accounts`/`build_updated_stake_reward`'s handling of the vote account, or a separate function not surfaced by these searches) that I could not locate. Given that this is an actively evolving, not-yet-fully-activated feature (SIMD-0123, "Always zero until SIMD-0123 is activated" per the code comment at `programs/vote/src/vote_state/mod.rs:1084`), this should be treated as a hypothesis requiring direct code confirmation, not a proven vulnerability.

### Recommendation
Confirm whether/where the vote account's `pending_delegator_rewards` field is decremented in lockstep with `calculate_block_reward`'s distribution of those rewards to delegator stake accounts. If no such decrement exists, add logic to reduce `pending_delegator_rewards` on the vote account by the exact amount distributed during `store_stake_accounts_in_partition`/`distribute_epoch_rewards_in_partition`, ensuring the withdrawer's reserved balance is released once the corresponding obligation is settled.

### Proof of Concept
Not constructed — this requires confirming the absence of a decrement path across `runtime/src/bank/partitioned_epoch_rewards/distribution.rs` and the vote program, which I could not fully trace within the available search iterations. A PoC would: (1) deposit delegator rewards into a V4 vote account via `DepositDelegatorRewards`, (2) run epoch reward distribution so the block reward is paid out to delegators, (3) attempt to withdraw the vote account down below the (stale) `pending_delegator_rewards` reserve via `Withdraw`, and (4) observe whether the withdrawal is wrongly rejected by `InstructionError::InsufficientFunds` in `programs/vote/src/vote_state/mod.rs:1119-1121` despite the reward obligation already being paid.

### Citations

**File:** programs/vote/src/vote_state/mod.rs (L935-988)
```rust
/// Deposit delegator rewards into a vote account (SIMD-0123).
pub fn deposit_delegator_rewards<S: std::hash::BuildHasher>(
    invoke_context: &mut InvokeContext,
    vote_account_index: IndexOfAccount,
    sender_account_index: IndexOfAccount,
    deposit: u64,
    signers: &HashSet<Pubkey, S>,
) -> Result<(), InstructionError> {
    let transaction_context = &invoke_context.transaction_context;
    let instruction_context = transaction_context.get_current_instruction_context()?;

    let vote_address = *instruction_context.get_key_of_instruction_account(vote_account_index)?;
    let source_address =
        *instruction_context.get_key_of_instruction_account(sender_account_index)?;

    // Source account must sign the transfer.
    verify_authorized_signer(&source_address, signers)?;

    // SIMD-0123 states we must validate the vote account deserializes to a v4
    // *before* attempting CPI, then update the `pending_delegator_rewards`
    // field *last*.
    // We can deserialize it, and hold onto the deserialized payload in-memory.
    // This way, we can drop the account borrow but avoid re-deserializing
    // later, since we know only lamports will change.
    let mut vote_state = {
        let vote_account =
            instruction_context.try_borrow_instruction_account(vote_account_index)?;

        // Can't use `get_vote_state_handler_checked`, since it will convert
        // the underlying vote state to v4.
        // SIMD-0123 requires an *initialized v4*.
        let versioned = VoteStateVersions::deserialize(vote_account.get_data())?;
        if let VoteStateVersions::V4(vote_state_v4) = versioned {
            Ok(VoteStateHandler::new_v4(*vote_state_v4))
        } else {
            Err(InstructionError::InvalidAccountData)
        }
    }?;

    // CPI to System: Transfer from sender to vote account.
    invoke_context.native_invoke_signed(
        system_instruction::transfer(&source_address, &vote_address, deposit),
        &[],
    )?;

    // Update `pending_delegator_rewards`.
    let transaction_context = &invoke_context.transaction_context;
    let instruction_context = transaction_context.get_current_instruction_context()?;
    let mut vote_account =
        instruction_context.try_borrow_instruction_account(vote_account_index)?;

    vote_state.add_pending_delegator_rewards(deposit)?;
    vote_state.set_vote_account_state(&mut vote_account)
}
```

**File:** programs/vote/src/vote_state/mod.rs (L1084-1121)
```rust
    // Always zero until SIMD-0123 is activated.
    let pending_delegator_rewards = vote_state.pending_delegator_rewards();

    if remaining_balance == 0 {
        // SIMD-0123: vote account cannot be closed if
        // pending_delegator_rewards > 0.
        if pending_delegator_rewards > 0 {
            return Err(InstructionError::InsufficientFunds);
        }

        let reject_active_vote_account_close = vote_state
            .epoch_credits()
            .last()
            .map(|(last_epoch_with_credits, _, _)| {
                let current_epoch = clock.epoch;
                // if current_epoch - last_epoch_with_credits < 2 then the validator has received credits
                // either in the current epoch or the previous epoch. If it's >= 2 then it has been at least
                // one full epoch since the validator has received credits.
                current_epoch.saturating_sub(*last_epoch_with_credits) < 2
            })
            .unwrap_or(false);

        if reject_active_vote_account_close {
            return Err(VoteError::ActiveVoteAccountClose.into());
        } else {
            // Deinitialize upon zero-balance
            VoteStateHandler::deinitialize_vote_account_state(&mut vote_account, target_version)?;
        }
    } else {
        // SIMD-0123: withdrawable balance when pending_delegator_rewards > 0
        // is lamports - pending_delegator_rewards - rent_exempt_minimum.
        let min_rent_exempt_balance = rent_sysvar.minimum_balance(vote_account.get_data().len());
        let min_balance = min_rent_exempt_balance
            .checked_add(pending_delegator_rewards)
            .ok_or(InstructionError::ArithmeticOverflow)?;
        if remaining_balance < min_balance {
            return Err(InstructionError::InsufficientFunds);
        }
```

**File:** programs/vote/src/vote_state/handler.rs (L196-209)
```rust
    pub(crate) fn add_pending_delegator_rewards(
        &mut self,
        amount: u64,
    ) -> Result<(), InstructionError> {
        match &mut self.target_state {
            TargetVoteState::V4(v4) => {
                v4.pending_delegator_rewards = v4
                    .pending_delegator_rewards
                    .checked_add(amount)
                    .ok_or(InstructionError::ArithmeticOverflow)?;
                Ok(())
            }
        }
    }
```

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L173-231)
```rust
/// Calculates block reward for a stake account based on SIMD-0123
fn calculate_block_reward(
    rewarded_epoch: Epoch,
    delegation: &Delegation,
    stake_history: &StakeHistory,
    distribution_epoch_vote_accounts: &VoteAccounts,
    ag_epoch_type: &AlpenglowEpochType,
    new_warmup_cooldown_rate_epoch: Option<Epoch>,
    use_fixed_point_stake_math: bool,
) -> u64 {
    let vote_pubkey = delegation.voter_pubkey;
    let Some(vote_account) = distribution_epoch_vote_accounts.get(&vote_pubkey) else {
        debug!("could not find vote account {vote_pubkey} in cache");
        return 0;
    };
    let vote_state = vote_account.vote_state_view();
    let pending_delegator_rewards = vote_state.pending_delegator_rewards();
    // NOTE: during recalculation, `distribution_epoch_vote_accounts` already
    // includes updated stake activation values from after the new epoch
    // calculation, so we need to use `RewardEpochDelegatedStakes` for the exact
    // values at the end of the reward epoch.
    let (AlpenglowEpochType::Alpenglow {
        reward_epoch_delegated_stakes,
        ..
    }
    | AlpenglowEpochType::MigrationEpoch {
        reward_epoch_delegated_stakes,
        ..
    }) = ag_epoch_type
    else {
        debug!("Alpenglow must be enabled for block reward calculation");
        return 0;
    };
    let total_active_stake = reward_epoch_delegated_stakes
        .delegated_stakes
        .get(&vote_pubkey)
        .copied()
        .unwrap_or(0);
    if total_active_stake == 0 {
        0
    } else {
        let stake = delegation_effective_stake(
            delegation,
            rewarded_epoch,
            stake_history,
            new_warmup_cooldown_rate_epoch,
            use_fixed_point_stake_math,
        );
        // During recalculation, if stake account has already received rewards,
        // it's possible to have `stake > total_active_stake`. If
        // `pending_delegator_rewards` is a huge number, we could potentially
        // overflow a `u64`. We can also have individual rewards look greater
        // than the pending rewards. This is harmless in practice, but we
        // clamp it just to be safe
        (pending_delegator_rewards as u128 * stake as u128 / total_active_stake as u128)
            .try_into()
            .unwrap_or(u64::MAX)
            .min(pending_delegator_rewards)
    }
```

**File:** runtime/src/bank/partitioned_epoch_rewards/distribution.rs (L239-325)
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
        account
            .set_state(&StakeStateV2::Stake(meta, new_stake, flags))
            .map_err(|_| DistributionError::UnableToSetState)?;

        let stake_at_distribution_epoch = delegation_effective_stake(
            &new_stake.delegation,
            distribution_epoch,
            stake_history,
            new_warmup_cooldown_rate_epoch,
            use_fixed_point_stake_math,
        );
        let reward_type = if stake_at_distribution_epoch == 0 {
            RewardType::DeactivatedStake
        } else {
            RewardType::Staking
        };
        Ok(StakeReward {
            stake_pubkey: partitioned_stake_reward.stake_pubkey,
            stake_reward_info: StakeRewardInfo {
                reward_type,
                lamports: i64::try_from(
                    partitioned_stake_reward.inflation.stake_reward
                        + partitioned_stake_reward.block_reward,
                )
                .unwrap(),
                post_balance: account.lamports(),
                commission_bps: partitioned_stake_reward.inflation.commission_bps,
            },
            stake_account: account,
        })
    }
```
