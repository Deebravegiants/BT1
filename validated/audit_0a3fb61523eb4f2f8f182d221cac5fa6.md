Based on the code investigation, this claim does not describe a real vulnerability. The premise — that the SVM "only compares aggregate sums" and could therefore be bypassed by compensating errors across accounts — is factually incorrect given the actual layered protections in the codebase.

### Analysis

There are **two independent, complementary invariant checks**, not just one aggregate check:

1. **Per-instruction (and per-CPI-frame) balance check**: `TransactionContext::pop()` verifies `self.accounts.get_lamports_delta() != 0` on *every* instruction pop — including every nested CPI return, not just at the end of the whole transaction. Any lamport imbalance introduced inside a single instruction (or CPI call), even if later "compensated" by another instruction, would be caught the moment that instruction context is popped, immediately returning `InstructionError::UnbalancedInstruction`. [1](#0-0) 

2. **Whole-transaction aggregate check**: after execution, `transaction_accounts_lamports_sum` sums all account lamports using `u128` with `checked_add`, avoiding overflow/rounding tricks, and compares pre- vs post-execution sums exactly, failing with `TransactionError::UnbalancedTransaction` on any mismatch. [2](#0-1) [3](#0-2) 

3. **Per-account authorization guard on lamport mutation**: `BorrowedInstructionAccount::set_lamports` disallows *any* program from decreasing the lamports of an account it does not own (`ExternalAccountLamportSpend`) and disallows any lamport change on read-only accounts (`ReadonlyLamportChange`). Every lamport mutation also updates a running `add_lamports_delta` tracked by the transaction context, which is exactly what the per-instruction pop check inspects. [4](#0-3) 

Because the per-instruction check fires on every CPI/instruction boundary (not merely once at the end of the whole transaction), a "compensating error" pattern spread across multiple instructions/accounts within a single transaction cannot slip through: each instruction (including the top-level ones invoking `CreateAccount` or any transfer) must independently net to zero lamport delta, and any nonzero delta at pop time is a hard error before the transaction can even reach the final aggregate check. The `svm/doc/spec.md` reference (step 3.1 / 3.11) describes only the whole-transaction check documented at a high level; it does not describe the full set of guards actually implemented, and the actual code has finer-grained enforcement than the spec doc summary implies. [5](#0-4) [6](#0-5) 

Given these layered, per-instruction and per-account guards in addition to the aggregate sum check, the described attack (crafting a multi-instruction transaction where per-account rounding/reentrant errors compensate in the aggregate sum but not per-instruction) has no code path to exploit — the per-instruction pop check would reject any imbalance immediately, well before the final aggregate sum comparison is reached.

#No vulnerability found for this question.

### Citations

**File:** transaction-context/src/transaction.rs (L465-492)
```rust
        // Verify (before we pop) that the total sum of all lamports in this instruction did not change
        let detected_an_unbalanced_instruction =
            self.get_current_instruction_context()
                .and_then(|instruction_context| {
                    // Verify all executable accounts have no outstanding refs
                    self.accounts
                        .try_borrow_mut(
                            instruction_context.get_index_of_program_account_in_transaction()?,
                        )
                        .map_err(|err| {
                            if err == InstructionError::AccountBorrowFailed {
                                InstructionError::AccountBorrowOutstanding
                            } else {
                                err
                            }
                        })?;
                    Ok(self.accounts.get_lamports_delta() != 0)
                });
        // Always pop, even if we `detected_an_unbalanced_instruction`
        self.instruction_stack.pop();
        if let Some(instr_idx) = self.instruction_stack.last() {
            self.transaction_frame.current_executing_instruction = *instr_idx as u16;
        }
        if detected_an_unbalanced_instruction? {
            Err(InstructionError::UnbalancedInstruction)
        } else {
            Ok(())
        }
```

**File:** svm/src/transaction_processor.rs (L1052-1061)
```rust
        fn transaction_accounts_lamports_sum(
            accounts: &[(Pubkey, AccountSharedData)],
        ) -> Option<u128> {
            accounts.iter().try_fold(0u128, |sum, (_, account)| {
                sum.checked_add(u128::from(account.lamports()))
            })
        }

        let lamports_before_tx =
            transaction_accounts_lamports_sum(&transaction_accounts).unwrap_or(0);
```

**File:** svm/src/transaction_processor.rs (L1183-1189)
```rust
        if post_account_state_info_result.is_ok()
            && transaction_accounts_lamports_sum(&accounts)
                .filter(|lamports_after_tx| lamports_before_tx == *lamports_after_tx)
                .is_none()
        {
            post_account_state_info_result = Err(TransactionError::UnbalancedTransaction);
        }
```

**File:** transaction-context/src/instruction_accounts.rs (L119-143)
```rust
    /// Overwrites the number of lamports of this account (transaction wide)
    pub fn set_lamports(&mut self, lamports: u64) -> Result<(), InstructionError> {
        // An account not owned by the program cannot have its balance decrease
        if !self.is_owned_by_current_program() && lamports < self.get_lamports() {
            return Err(InstructionError::ExternalAccountLamportSpend);
        }
        // The balance of read-only may not change
        if !self.is_writable() {
            return Err(InstructionError::ReadonlyLamportChange);
        }
        // don't touch the account if the lamports do not change
        let old_lamports = self.get_lamports();
        if old_lamports == lamports {
            return Ok(());
        }

        let lamports_balance = (lamports as i128).saturating_sub(old_lamports as i128);
        self.transaction_context
            .accounts
            .add_lamports_delta(lamports_balance)?;

        self.touch()?;
        self.account.set_lamports(lamports);
        Ok(())
    }
```

**File:** svm/doc/spec.md (L255-258)
```markdown
3. Execute each loaded transactions
   1. Compute the sum of transaction accounts' balances. This sum is
      invariant in the transaction execution.
   2. Obtain rent state of each account before the transaction
```

**File:** svm/doc/spec.md (L291-293)
```markdown
   10. Extract `ExecutionRecord` components from transaction context.
   11. Check balances of accounts to match the sum of balances before
       transaction execution.
```
