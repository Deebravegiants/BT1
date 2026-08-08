### Title
Permissionless `DepositDelegatorRewards` griefing lets any unprivileged user perpetually block a vote account from being closed/fully withdrawn - (File: `programs/vote/src/vote_state/mod.rs`)

### Summary
The vote program's SIMD-0123 `DepositDelegatorRewards` instruction lets *any* signer transfer an arbitrary (even 1-lamport) amount of SOL into a vote account, unconditionally incrementing the account's `pending_delegator_rewards` counter. The `withdraw` instruction refuses to fully close a vote account (or withdraw below `rent_exempt + pending_delegator_rewards`) whenever `pending_delegator_rewards > 0`. Because deposits are permissionless and cheap while the counter is only reduced by the periodic, validator-driven partitioned epoch-rewards distribution, an attacker can re-arm the block with a trivial transaction each time it is cleared, indefinitely preventing the legitimate `authorized_withdrawer` from closing the account or recovering its full balance - the same "tiny unprivileged transfer forces the target into a long, protocol-enforced hold state" pattern described in the Lido `LidoVault` report.

### Finding Description
`deposit_delegator_rewards` only requires the *source* account to sign; it does not require any authority over the vote account itself: [1](#0-0) 

It then CPIs a system transfer from the (attacker-controlled) source into the vote account and unconditionally increases `pending_delegator_rewards`: [2](#0-1) 

The increment itself has no minimum, and `checked_add` simply grows the counter with each call: [3](#0-2) 

`withdraw` then enforces that reserve against the account owner (the withdrawer), regardless of who created the reserve: [4](#0-3) 

Specifically:
- If the withdraw would zero the account, and `pending_delegator_rewards > 0`, the withdraw is rejected outright (`InsufficientFunds`), so the account can never be closed.
- If the withdraw would leave a nonzero balance, the withdrawer may only take funds down to `rent_exempt_minimum + pending_delegator_rewards`.

`pending_delegator_rewards` is only decremented as part of the bank's partitioned epoch-rewards distribution (once per epoch, at commission collection time) - a process outside the withdrawer's control and outside the attacker's control as well, but crucially also outside the attacker's need to control: the attacker only needs to re-deposit a dust amount right after each distribution clears the counter to re-establish the block, at the cost of one lamport and one transaction fee per epoch.

### Impact Explanation
This mirrors the Lido bug class precisely: a completely unprivileged actor spends a negligible amount (1 lamport + fee) to force a state machine (here, the vote account's withdrawal gate) into a long-held blocking condition that harms an unrelated party (the vote account's authorized withdrawer / node operator), and can repeat the trigger every epoch to make the block effectively indefinite. The impact is a denial of the withdrawer's ability to fully close the account or reclaim its complete balance - a concrete loss of access to funds/value for the legitimate owner, imposed unilaterally by any third party at trivial cost. It also creates cross-actor asymmetry: the attacker's cost (lamports + fee) is far below the value locked/blocked in the vote account.

### Likelihood Explanation
The attack requires no special permissions - only a funded keypair capable of signing a system transfer and calling `DepositDelegatorRewards`, which by design accepts any signer as the source. It is reachable as long as the gating feature set (`commission_rate_in_basis_points`, `custom_commission_collector`, `block_revenue_sharing`) is active, and the cost to sustain the grief is one dust deposit per epoch. This is a realistic, cheaply repeatable unprivileged-user action, not a validator/operator-only or purely theoretical scenario.

### Recommendation
- Require the deposit amount to be validated against a meaningful floor/ceiling, or rate-limit/aggregate dust deposits so a 1-lamport transfer cannot re-arm the withdrawal block.
- Decouple the "cannot close while `pending_delegator_rewards > 0`" invariant from third-party-controlled deposits, e.g., by tracking a separate authorized-only "owed rewards" ledger that only the protocol's commission-distribution logic can increase, while permissionless deposits go through a distinct, withdrawer-sweepable balance that never blocks account closure.
- Alternatively, allow the authorized withdrawer to force-clear/reject arbitrary un-consumed `pending_delegator_rewards` deposits (e.g., a "reject deposit" or "sweep to collector" path) so a malicious depositor cannot indefinitely hold the account hostage.

### Proof of Concept
1. Withdrawer wants to fully withdraw/close their vote account (balance == `rent_exempt_minimum`, `pending_delegator_rewards == 0`).
2. Attacker (any funded keypair, no relationship to the vote account) submits `VoteInstruction::DepositDelegatorRewards { deposit: 1 }` with themselves as source signer, per `deposit_delegator_rewards` at [5](#0-4) . This succeeds and sets `pending_delegator_rewards = 1`.
3. Withdrawer calls `Withdraw(full_balance)`; per the check at [6](#0-5) , the instruction returns `InstructionError::InsufficientFunds` and the account cannot be closed.
4. When the epoch's partitioned-rewards distribution eventually pays out and clears `pending_delegator_rewards` to 0, the attacker repeats step 2 with another 1-lamport deposit before/soon-after the withdrawer's next withdraw attempt, re-establishing the block for another epoch cycle - repeatable indefinitely at negligible cost.

### Citations

**File:** programs/vote/src/vote_state/mod.rs (L936-988)
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
