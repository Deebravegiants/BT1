### Title
Unauthenticated `DepositDelegatorRewards` allows griefing that permanently blocks vote account withdrawal/closure - (File: `programs/vote/src/vote_state/mod.rs`)

### Summary
The vote program's `DepositDelegatorRewards` instruction (SIMD-0123) lets **any signer** deposit lamports into a vote account and increment its `pending_delegator_rewards` counter, without verifying that the depositor is a legitimate rewards-distribution mechanism (e.g., the runtime's epoch-reward distribution) or is otherwise privileged. Because `withdraw()` refuses to fully close a vote account (or to bring its balance below `rent_exempt_minimum + pending_delegator_rewards`) whenever `pending_delegator_rewards > 0`, an unprivileged attacker can grief any vote account's authorized withdrawer by repeatedly (or even once, with a minimal amount) calling `DepositDelegatorRewards`, permanently preventing that withdrawer from closing the account — directly analogous to the Audius H02 pattern where unprivileged delegators can block a service provider's ability to deregister/withdraw.

### Finding Description
`deposit_delegator_rewards` only checks that the *source* account signed the transfer; it performs no check on who the source is: [1](#0-0) 

It then unconditionally increments the vote account's `pending_delegator_rewards`: [2](#0-1) [3](#0-2) 

`withdraw()` — which is gated on the *authorized withdrawer's* signature, the analog of the "service provider" role in the Audius report — is then blocked from ever bringing the account to zero (closing it) as long as `pending_delegator_rewards > 0`, and is capped on partial withdrawals to preserve that reserve: [4](#0-3) 

This mirrors the Audius bug class precisely: an unprivileged party (any depositor, standing in for a "delegator") can unilaterally create on-chain state (`pending_delegator_rewards > 0`) that blocks a privileged party (the vote account's authorized withdrawer, standing in for the "service provider") from performing a legitimate lifecycle operation (fully withdrawing/closing the account), with no consent or intervening action required from the withdrawer. Within the files reachable from the index, no code path was found that ever decrements `pending_delegator_rewards` back toward zero outside of the epoch-rewards distribution machinery in `runtime/src/bank/partitioned_epoch_rewards/calculation.rs`, which only *reads* the field to compute `calculate_block_reward` — it was not possible to confirm from the indexed code whether/where the field is actually reset to reflect paid-out rewards, so it is uncertain whether legitimate protocol flow ever clears attacker-inflated deposits.

### Impact Explanation
An attacker with a trivial amount of SOL (even 1 lamport) can call `DepositDelegatorRewards` against a target vote account they do not control, setting `pending_delegator_rewards` to a nonzero value. From that point on, the vote account's authorized withdrawer is unable to fully close the account (`InstructionError::InsufficientFunds` on `withdraw`), permanently locking the account's rent-exempt reserve and rewards from ever being fully reclaimed via `Withdraw`, regardless of the withdrawer's intent. This is a concrete denial-of-service / fund-lock against any vote account once SIMD-0123 (`commission_rate_in_basis_points`, `custom_commission_collector`, `block_revenue_sharing`) is activated, and requires no privileged role, mirroring the "unprivileged" scope of the target bug class.

### Likelihood Explanation
Once the three gating features are active on a cluster, exploitation requires only: (1) any keypair holding a small SOL balance, and (2) a single `DepositDelegatorRewards` transaction naming an arbitrary victim vote account. No special permissions, races, or validator/operator role are needed — this is fully reachable by any unprivileged wallet.

### Recommendation
Restrict `DepositDelegatorRewards` so that the increment to `pending_delegator_rewards` can only originate from the legitimate rewards-distribution pathway (e.g., require the source/caller to be a specific system-derived account controlled by the runtime, or gate the instruction so it can only be invoked via the reward-distribution CPI path), and/or ensure there is a well-defined, reachable mechanism to decrement `pending_delegator_rewards` as rewards are actually paid out to delegator stake accounts, so that an attacker-inflated balance cannot permanently block `withdraw()`.

### Proof of Concept
1. Enable/assume features `commission_rate_in_basis_points`, `custom_commission_collector`, and `block_revenue_sharing` are active (required by `VoteInstruction::DepositDelegatorRewards` per `programs/vote/src/vote_processor.rs:409-421`).
2. Attacker, holding an unrelated funded keypair, submits `VoteInstruction::DepositDelegatorRewards { deposit: 1 }` naming any victim vote account and themself as the signing source account — no relationship to the vote account or its stakers is required (`deposit_delegator_rewards`, `programs/vote/src/vote_state/mod.rs:936-988`).
3. The victim vote account's `pending_delegator_rewards` becomes `1` (`add_pending_delegator_rewards`, `programs/vote/src/vote_state/handler.rs:196-209`).
4. The victim's authorized withdrawer subsequently attempts `VoteInstruction::Withdraw(full_balance)` to close the account; the call fails with `InstructionError::InsufficientFunds` because `pending_delegator_rewards > 0` (`withdraw`, `programs/vote/src/vote_state/mod.rs:1087-1092`), as also demonstrated by the existing test `test_withdraw_pending_delegator_rewards` (`programs/vote/src/vote_processor.rs:5219-5314`), which shows the same InsufficientFunds rejection when pending rewards are nonzero.

### Citations

**File:** programs/vote/src/vote_state/mod.rs (L936-951)
```rust
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
```

**File:** programs/vote/src/vote_state/mod.rs (L974-988)
```rust
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

**File:** programs/vote/src/vote_state/mod.rs (L1084-1122)
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
