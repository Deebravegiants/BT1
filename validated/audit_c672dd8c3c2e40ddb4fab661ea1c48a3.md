No vulnerability found for this question.

**Analysis:**

The incarnation recheck at `scheduler_v2.rs` line 672 is specifically designed to close the exact race the question describes, not to leave it open. `start_commit` is only ever called while the caller holds `queueing_commits_lock` [1](#0-0) , and the code comment explicitly documents that cold-validation blocking/unblocking happens under this same lock, so any abort-driven incarnation bump that occurs between the `is_commit_blocked` check and the second incarnation read is caught by comparing the two incarnation snapshots [2](#0-1) . If a concurrent abort increments the incarnation (which `finish_abort`/`start_abort` always does when a re-execution is required, per the status lifecycle documented in `scheduler_status.rs`) [3](#0-2) , the second `self.txn_statuses.incarnation(next_to_commit_idx)` read will differ from the first, and `start_commit` returns `CommitResult::None` rather than committing [4](#0-3) . The transaction is only actually marked `Ready` for commit after this check passes, using the freshly re-read incarnation value again at the return statement [5](#0-4) .

Beyond the scheduler-level guard, the premise conflates scheduler commit-sequencing with the actual write-set target address of a store-creation transaction. The address that a token-object secondary-store-creation write targets is determined entirely by the Move-level execution logic of that specific incarnation (module/authenticator-level custody logic), not by the BlockSTMv2 scheduler's bookkeeping; the scheduler only decides *whether* an already-computed incarnation's output is allowed to be committed, and never mutates or misattributes the write set itself. Since the incarnation-mismatch check already prevents committing a stale incarnation's output, and the write-set contents are independent of scheduler races, there is no unprivileged-input path here that changes who owns or controls a secondary store's metadata.

This finding is about generic BlockSTMv2 engine concurrency-control soundness, not a custody-boundary violation reachable by unprivileged transaction input in the sense the review scope targets (deposit/withdraw/transfer/split/merge/burn authority checks). The described defense (the incarnation recheck) already closes the path, so per the Decision Standard this should be rejected.

### Citations

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L610-616)
```rust
    /// Attempts to get the next transaction index that is ready to be committed. This method
    /// MUST be called only while holding the `queueing_commits_lock` (acquired via
    /// [SchedulerV2::commit_hooks_try_lock]). The worker can then perform a critical section
    /// consisting of any logic for committing a txn that needs to occur sequentially.
    /// The completion of this sequential commit hook logic must be followed by a call to
    /// [SchedulerV2::end_commit].
    ///
```

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L659-674)
```rust
            if self
                .cold_validation_requirements
                .is_commit_blocked(next_to_commit_idx, incarnation)
            {
                // May not commit a txn with an unsatisfied validation requirement. This will be
                // more rare than !is_executed in the common case, hence the order of checks.
                return Ok(CommitResult::BlockedByValidation);
            }
            // The check might have passed after the validation requirement has been fulfilled.
            // Yet, if validation failed, the status would be aborted before removing the block,
            // which would increase the incarnation number. It is also important to note that
            // blocking happens during sequential commit hook, while holding the lock (which is
            // also held here), hence before the call of this method.
            if incarnation != self.txn_statuses.incarnation(next_to_commit_idx) {
                return Ok(CommitResult::None);
            }
```

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L701-704)
```rust
            return Ok(CommitResult::Ready(
                next_to_commit_idx,
                self.txn_statuses.incarnation(next_to_commit_idx),
            ));
```

**File:** aptos-move/block-executor/src/scheduler_status.rs (L29-52)
```rust
2. Abort Process:
   - A transaction incarnation may be aborted if it reads data that is later modified in a way
     that would cause the transaction to read different values if it executed again. This
     signals the need for re-execution with an incremented incarnation number.
   - In BlockSTMv2, a transaction can be aborted while executing or after execution finishes.
   - Abort happens in two distinct phases:

   a) Start Abort Phase:
      - [ExecutionStatuses::start_abort] is called with an incarnation number and succeeds if
        the incarnation has started executing and has not already been aborted.
      - This serves as an efficient test-and-set filter for multiple abort attempts (which
        can occur when a transaction makes multiple reads that may each be invalidated by
        different transactions).
      - Early detection allows the ongoing execution to stop immediately rather than continue
        work that will ultimately be discarded.

   b) Finish Abort Phase:
      - A successful [ExecutionStatuses::start_abort] must be followed by a
        [ExecutionStatuses::finish_abort] call on the status.
        • If the status was 'Executed', it transitions to 'PendingScheduling' for the
          next incarnation, unless start_next_incarnation is true. In this case, the status
          goes directly to 'Executing' without going through 'PendingScheduling'.
        • If the status was 'Executing', it transitions to 'Aborted'. In this case,
          start_next_incarnation must be false.
```
