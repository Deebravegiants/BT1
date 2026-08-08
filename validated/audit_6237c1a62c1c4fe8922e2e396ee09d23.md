### Title
Dust-lamport front-run can block vote account closure via `Withdraw` — (File: `programs/vote/src/vote_state/mod.rs`)

### Summary
The vote program's `withdraw` function determines whether a `Withdraw` instruction should close (deinitialize) a vote account by checking if the *exact* remaining balance after the withdrawal equals zero. Because any unprivileged account can send lamports to a vote account via a plain system transfer (destination ownership is not restricted), an attacker can front-run a withdrawer's "withdraw all / close account" transaction with a dust transfer to the vote account. This changes the computed `remaining_balance` from `0` to a small positive value that is still below the rent-exempt minimum, causing the withdraw instruction to fail with `InsufficientFunds` instead of succeeding, mirroring the reported bug class where dust transfers defeat an exact-balance completion check.

### Finding Description
`withdraw()` computes the expected post-withdrawal balance purely from the vote account's current on-chain lamports minus the requested withdrawal amount: [1](#0-0) 

If that computed `remaining_balance` is exactly `0`, the code treats it as a full closure and deinitializes the vote account (subject to `pending_delegator_rewards` and recent-vote-credit checks): [2](#0-1) 

Otherwise, it requires `remaining_balance >= min_rent_exempt_balance + pending_delegator_rewards`, or fails with `InstructionError::InsufficientFunds`: [3](#0-2) 

A withdrawer who wants to fully close/withdraw their vote account submits a `Withdraw(amount)` instruction where `amount` equals the balance they last observed on-chain, expecting `remaining_balance == 0`. Because the vote account is a normal account, anyone can add lamports to it with an ordinary `system_instruction::transfer` (the System program's transfer only requires the *source* to be system-owned and signed; it places no restriction on the destination's owner). An attacker who front-runs the withdrawer's transaction with a 1-lamport (or any small) transfer to the vote account changes `vote_account.get_lamports()` at execution time, so `remaining_balance` becomes a small positive number instead of `0`. Since that residual is far below the rent-exempt minimum for a vote account, the `else` branch's `remaining_balance < min_balance` check triggers and the whole withdraw transaction fails with `InsufficientFunds` — even though the withdrawer intended (and was otherwise entitled) to fully withdraw and close the account.

This is the same class of bug as the reported Maple Finance issue: a state-completion path relies on an *exact* balance comparison (`== 0`) of a value any unprivileged party can perturb by sending funds, letting an attacker griefer indefinitely block the legitimate completion/closure action by re-front-running with fresh dust each time the victim retries.

### Impact Explanation
This allows any unprivileged actor to repeatedly block a validator's withdrawer authority from fully withdrawing/closing a vote account by continuously front-running with dust transfers. This is a griefing/DoS on a legitimate state transition (closing/deinitializing a vote account), not merely a cosmetic issue — it can indefinitely delay legitimate fund withdrawal and account teardown for a targeted vote account, forcing the withdrawer into a race with the attacker or requiring them to under-withdraw and leave the account "stuck" open. It does not cause direct loss of funds (the extra dust simply stays owned by the account and gets withdrawn along with everything else on a successful attempt) or cross-node divergence, but it is a concrete denial-of-completion on a state transition triggered purely by unprivileged token transfers.

### Likelihood Explanation
The attack requires only a plain system transfer of a minimal amount of lamports and precise transaction ordering (front-running), which is readily achievable on Solana via standard priority-fee/ordering games or simply monitoring the mempool/recent transactions for `Withdraw` instructions targeting a known vote account with an amount matching its current balance. No special privilege is needed.

### Recommendation
Do not rely on an exact recomputed `remaining_balance == 0` derived from the account's live lamport balance to decide whether to deinitialize/close the account. Instead, have the instruction accept and validate an explicit "close account" intent (e.g., a dedicated withdraw-all/close code path that reads and withdraws the full current balance atomically, rather than a client-supplied exact amount), or treat any `remaining_balance` below the rent-exempt minimum (not just exactly zero, provided `pending_delegator_rewards == 0`) as eligible for closure, sweeping the residual dust to the recipient as well.

### Proof of Concept
1. Vote account `V` has withdrawer authority `W`; current balance is `B` lamports, `pending_delegator_rewards == 0`.
2. `W` builds and submits `Withdraw(B)` intending to empty and deinitialize `V`.
3. Attacker `E` observes this and submits `system_instruction::transfer(E, V, 1)` with higher priority so it lands first, raising `V`'s balance to `B + 1`.
4. `W`'s `Withdraw(B)` executes: `remaining_balance = (B + 1) - B = 1`, which is `!= 0`, so the code checks `1 >= min_rent_exempt_balance`; since the rent-exempt minimum for a vote account is orders of magnitude larger than `1`, this fails and the instruction returns `InstructionError::InsufficientFunds` — see the check at [4](#0-3) .
5. `W`'s transaction fails; `E` can repeat this on every retry, indefinitely preventing `W` from fully withdrawing/closing `V`.

### Citations

**File:** programs/vote/src/vote_state/mod.rs (L1079-1082)
```rust
    let remaining_balance = vote_account
        .get_lamports()
        .checked_sub(lamports)
        .ok_or(InstructionError::InsufficientFunds)?;
```

**File:** programs/vote/src/vote_state/mod.rs (L1087-1111)
```rust
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
```

**File:** programs/vote/src/vote_state/mod.rs (L1112-1122)
```rust
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
