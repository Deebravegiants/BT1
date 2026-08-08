## Title
Validator commission rewards can be silently burned instead of credited to a legitimately designated non-vote commission collector - ([File: runtime/src/bank/partitioned_epoch_rewards/calculation.rs])

### Summary
This is analogous to the reported Datatrust bug: a "successful" protocol action (here, epoch reward distribution) can permanently destroy value that rightfully belongs to an account owner, with no opportunity to withdraw or fix the situation beforehand. In agave, SIMD-0232 allows a vote account to designate a custom, non-vote-account "commission collector" that receives validator commission each epoch. If that collector account fails post-transfer validation (e.g., it isn't rent-exempt, or it is a reserved account), the commission lamports are not returned to the vote account or held in escrow — they are unconditionally burned.

### Finding Description
`load_and_reward_commission_accounts` loads each epoch's designated commission-collector account and credits it with `commission_lamports`. When `custom_commission_collector` is active, the collector can be an arbitrary system-owned account, not just the vote account itself [1](#0-0) .

After crediting, `collector_type_checked` is invoked to ensure the account is system-owned, not reserved, and rent-exempt after the deposit [2](#0-1) . If any of these checks fail, the code does **not** roll back to the vote account or hold the funds for a future retry — it adds the entire `commission_lamports` amount to `total_non_incinerator_burned_lamports`, and `return None` drops the account update entirely [3](#0-2) . These burned lamports are then subtracted from bank capitalization in `distribute_reward_commissions` [4](#0-3) .

This is structurally identical to the reported issue: an entity (the collector account owner, analogous to the Maker/Alice) has "accumulated" a reward (commission) that is forcibly destroyed by an automatic system action (epoch reward distribution, analogous to `resolveChallenge`/`removeListing`) without any chance to withdraw, top up, or otherwise remedy the account state beforehand. Unlike the intentional VAT/incinerator burns elsewhere in the bank (which are deliberate protocol-level slashing/burn mechanisms), this burn is a byproduct of an unrelated rent-exemption/account validation failure on the destination account, and it strikes the *validator's* earned reward, not a bad actor's.

### Impact Explanation
A vote account owner who designates a custom commission collector can lose their entire epoch commission if:
- The collector account's balance dips (from any other transaction, by the owner or a third party who happens to control instructions on that account) so that `commission_lamports` isn't enough to reach rent-exemption at distribution time, or
- The collector address becomes a "reserved" account between commission calculation and distribution.

Because commission accounts are loaded fresh at distribution time (explicitly to reflect "any intervening account mutations") [5](#0-4) , an adversary who can influence or drain the designated collector account in the window between reward calculation and the (multi-block) partitioned distribution can cause the legitimate commission to be irrecoverably burned instead of returned to the vote account or the validator. This is a genuine value-destruction bug reachable without any operator/validator privilege over the *victim's* funds — only control of (or influence on) the collector account is required, and the loss falls on the vote account owner who receives nothing instead.

### Likelihood Explanation
Medium-low. It requires SIMD-0232's `custom_commission_collector` feature to be active and the vote account owner to have configured a non-vote-account collector, plus a window where the collector account transitions out of "valid" state between calculation and store. Existing tests in the repo (`test_alpenglow_partitioned_rewards_use_epoch_start_budget_after_burn`, `store_commission_accounts_partitioned` tests) demonstrate this "burn" path is a known, exercised code path rather than a purely theoretical one [6](#0-5) .

### Recommendation
- Short term: When `collector_type_checked` fails for a custom commission collector, fall back to crediting the vote account itself (the entity that ultimately owns the commission) rather than burning the lamports, mirroring the report's recommendation to transfer to the rightful owner instead of destroying value.
- Long term: Add invariant tests/fuzzing (in the spirit of the report's Echidna/Manticore recommendation) asserting that `RewardCommissionLamportAmounts::burned_lamports` is always zero unless the account is provably unrecoverable (e.g., truly closed), and treat any non-zero burn as an alertable anomaly.

### Proof of Concept
Not independently executed; based on static analysis of `runtime/src/bank/partitioned_epoch_rewards/calculation.rs` and `runtime/src/bank/fee_distribution.rs`. Conceptual PoC:
1. Enable `custom_commission_collector`; vote account V sets its commission collector to account C (a plain system account funded to just above rent-exemption).
2. At epoch boundary, `calculate_stake_rewards_and_commissions` computes `commission_lamports` for C based on the vote account's earned commission.
3. Before `distribute_reward_commissions` runs (which can span multiple blocks/partitions), a transaction drains C's non-rent-exempt excess or an account-reservation update occurs.
4. At distribution, `load_and_reward_commission_accounts` reloads C, adds `commission_lamports`, then `collector_type_checked` fails the rent-exemption/reserved check.
5. The entire `commission_lamports` is added to `total_non_incinerator_burned_lamports` and lost — V's validator receives none of it, with no error surfaced to V and no ability to intervene beforehand.

Note: I was not able to fully trace how/whether the collector address can be changed mid-epoch versus only at vote-state update boundaries (this would need review of `programs/vote/src/vote_state/mod.rs`'s commission-collector-update instruction handling, which the index only partially surfaced). This affects the precise likelihood/exploitability assessment and should be verified in a full checkout before treating this as confirmed-exploitable rather than a design smell.

### Citations

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L384-408)
```rust
        let RewardCommissionLamportAmounts {
            distributed_lamports,
            distributed_to_incinerator_lamports,
            burned_lamports,
        } = reward_commission_accounts.amounts;
        self.store_commission_accounts_partitioned(&reward_commission_accounts, rewards_metrics);
        self.update_reward_commissions(&reward_commission_accounts);

        let StakeRewardCalculation {
            total_stake_rewards_lamports,
            ..
        } = stake_rewards;

        // verify that we didn't pay any more than we expected to
        assert!(
            point_value.rewards
                >= distributed_lamports
                    + distributed_to_incinerator_lamports
                    + burned_lamports
                    + total_stake_rewards_lamports,
            "point_value={point_value:?}, distributed_lamports={distributed_lamports}, \
             distributed_to_incinerator_lamports={distributed_to_incinerator_lamports} \
             burned_lamports={burned_lamports}, \
             total_stake_rewards_lamports={total_stake_rewards_lamports}"
        );
```

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L1097-1101)
```rust
    /// Load each planned commission account from the store and apply its
    /// reward. This is the single point where commission account data is
    /// fetched, ensuring we always see the latest balances — including any
    /// intervening account mutations (e.g. VAT burns in `update_epoch_stakes`)
    /// that happen between calculation and distribution.
```

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L1128-1149)
```rust
                        let maybe_commission_account =
                            self.get_account_with_fixed_root_no_cache(commission_pubkey);
                        let mut commission_account = if custom_commission_collector {
                            // If the account doesn't exist, the vote commission
                            // may be enough lamports to cover rent-exemption
                            // and properly create the commission account.
                            maybe_commission_account.unwrap_or_default()
                        } else {
                            // Before SIMD-0232, commission accounts were always
                            // vote accounts, which cannot be closed unless the
                            // account hasn't voted for at least a full epoch.
                            // This means that `maybe_commission_account` should
                            // always exist.
                            let Some(commission_account) = maybe_commission_account else {
                                debug!(
                                    "commission account {commission_pubkey} missing at \
                                     distribution time"
                                );
                                return None;
                            };
                            commission_account
                        };
```

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L1163-1186)
```rust
                        if !is_vote_account {
                            match Self::collector_type_checked(
                                commission_pubkey,
                                pre_lamports,
                                &commission_account,
                                reserved_account_keys,
                                rent,
                                relax_post_exec_min_balance_check,
                            ) {
                                Ok(ExternalCollectorType::SystemAccount) => {}
                                Ok(ExternalCollectorType::Incinerator) => {
                                    total_incinerator_lamports
                                        .fetch_add(*commission_lamports, Relaxed);
                                }
                                Err(err) => {
                                    debug!(
                                        "reward redemption failed for {commission_pubkey} due to \
                                         commission account error: {err:?}"
                                    );
                                    total_non_incinerator_burned_lamports
                                        .fetch_add(*commission_lamports, Relaxed);
                                    return None;
                                }
                            }
```

**File:** runtime/src/bank/partitioned_epoch_rewards/calculation.rs (L4185-4243)
```rust
        let unchanged_balance = bank.get_balance(&collector_into_vote_address);
        assert_eq!(unchanged_balance, pre_balance);

        // `collector_into_vote_address` receives its rewards, but `vote_address`
        // has its rewards burned
        let bank = apply_epoch_operations(
            bank,
            bank_forks.as_ref(),
            EpochOperations {
                epoch: 3,
                vote_operations: vec![
                    (
                        vote_address,
                        VoteOperations {
                            earned_credits: Some(1000),
                            expect_reward: true,
                            ..VoteOperations::default()
                        },
                    ),
                    (
                        collector_into_vote_address,
                        VoteOperations {
                            earned_credits: Some(1000),
                            expect_reward: true,
                            ..VoteOperations::default()
                        },
                    ),
                ],
            },
        );

        // Some rewards were distributed
        let post_balance = bank.get_balance(&collector_into_vote_address);
        assert!(post_balance > pre_balance);

        // They're reflected in the reported rewards
        let vote_reward = bank
            .rewards
            .read()
            .unwrap()
            .iter()
            .find(|(address, _reward)| *address == collector_into_vote_address)
            .map(|(_address, reward)| *reward)
            .unwrap();
        assert_eq!(vote_reward.lamports as u64, post_balance - pre_balance);

        // Some lamports were burned
        let reward_commissions = recalculate_reward_commissions_for_tests(&bank);
        let reward_commission = reward_commissions
            .get(&collector_into_vote_address)
            .unwrap();
        assert_ne!(reward_commission.burned_lamports, 0);

        // The burned lamports are included in the epoch rewards sysvar
        let epoch_rewards = bank.get_epoch_rewards_sysvar();
        assert_eq!(
            reward_commission.burned_lamports + reward_commission.commission_lamports,
            epoch_rewards.distributed_rewards
        );
```

**File:** runtime/src/bank/fee_distribution.rs (L235-270)
```rust
    /// Checks if a collector account adheres to the rules outlined in SIMD-0232:
    /// * system program owned account
    /// * rent-exempt after depositing inflation rewards commission
    /// * not a reserved account
    ///
    /// Returns the kind of collector
    pub(super) fn collector_type_checked(
        collector_id: &Pubkey,
        pre_lamports: u64,
        account: &AccountSharedData,
        reserved_account_keys: &ReservedAccountKeys,
        rent: &Rent,
        relax_post_execution_balance_checks: bool,
    ) -> Result<ExternalCollectorType, DepositFeeError> {
        if !system_program::check_id(account.owner()) {
            return Err(DepositFeeError::InvalidAccountOwner);
        }

        if reserved_account_keys.is_reserved(collector_id) {
            return Err(DepositFeeError::ReservedCollector);
        }

        // Don't perform rent check on the incinerator, so that the deposit
        // always works. The incinerator is run at the end of a block
        if *collector_id == incinerator::id() {
            Ok(ExternalCollectorType::Incinerator)
        } else {
            if !rent.is_exempt(account.lamports(), account.data().len())
                && (!relax_post_execution_balance_checks || pre_lamports == 0)
            {
                Err(DepositFeeError::InvalidRentPayingAccount)
            } else {
                Ok(ExternalCollectorType::SystemAccount)
            }
        }
    }
```
