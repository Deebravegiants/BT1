### Title
Per-receipt storage proof hard limit is only enforced in-VM for `FunctionCall` actions, allowing non-`FunctionCall` action receipts (AddKey/DeleteKey/Stake/DeployContract) to bypass incremental metering - ([File: runtime/near-vm-runner/src/logic/recorded_storage_counter.rs])

### Summary
`RecordedStorageCounter::observe_size` is only invoked from inside `VMLogic`/`Ctx` host functions (`storage_read`, `storage_write`, `storage_remove`, `storage_has_key`, etc.), i.e. only during `FunctionCall` execution. Non-`FunctionCall` action handlers such as `action_add_key`/`action_delete_key` in `runtime/runtime/src/access_keys.rs` never call into `RecordedStorageCounter`, so a receipt built entirely from these actions has no incremental (per-trie-operation) enforcement of `per_receipt_storage_proof_size_limit` while it executes.

### Finding Description
`RecordedStorageCounter::new` is constructed with `per_receipt_storage_proof_size_limit` and wired into `VMLogic`/`Ctx` exclusively: [1](#0-0) [2](#0-1) 

Every storage host call checks it after the trie operation completes: [3](#0-2) 

This means the hard, receipt-scoped `per_receipt_storage_proof_size_limit` is only actively enforced while a `FunctionCall` action's WASM guest code is running. Action handlers for `AddKey`/`DeleteKey` (`action_add_key`, `action_delete_key` in `runtime/runtime/src/access_keys.rs`), `Stake`, and `DeployContract` perform their own trie reads/writes but never touch `recorded_storage_counter` at all — there is no equivalent call anywhere in `access_keys.rs`. A receipt composed only of these actions (e.g., a long list of `AddKey`/`DeleteKey` actions) can therefore accumulate trie proof size without any in-loop check comparable to `RecordedStorageCounter::observe_size`.

The only remaining backstop is the coarser trie-level accounting in `TrieRecorder` (`check_proof_size_limit_exceed`, `core/store/src/trie/trie_recording.rs`), which tracks an `upper_bound_size`/`size` counter across all recorded nodes regardless of action type: [4](#0-3) 
This mechanism is consumed by chunk-level accounting (`main_storage_proof_size_soft_limit`, referenced in `runtime/runtime/src/congestion_control.rs` and `runtime/runtime/src/lib.rs`), which is documented as operating post-hoc and only at receipt granularity for deferring *subsequent* receipts to the delayed queue — not for aborting an in-flight receipt mid-execution: [5](#0-4) 

Because the soft/coarse check operates at receipt boundaries (after a receipt's actions have already fully executed and their trie nodes already recorded), any trie growth caused by an all-non-`FunctionCall`-actions receipt is only visible to the system *after* it has already been fully recorded into the witness — the proof bytes are already paid for/materialized before any rejection decision can be made, unlike the `FunctionCall` path where `RecordedStorageCounter` aborts execution mid-flight as soon as the hard limit is observed.

### Impact Explanation
An attacker who can force many trie touches per non-`FunctionCall` action (e.g., many `AddKey`/`DeleteKey` actions in one receipt, walking distinct parts of the account's access-key subtree, or repeated `DeployContract` actions that touch large existing-code nodes) can grow the recorded storage proof for a single receipt without the in-VM hard-limit check ever firing, because that check is wired only into `VMLogic`/`Ctx` host functions used by `FunctionCall`. The result matches the class "storage/gas metering bypass" and "chunk validation stall" impact: an oversized `ChunkStateWitness` for that receipt could reach chunk validators, and because the per-receipt hard limit meant to catch this ahead of time is absent for these action types, detection is deferred to post-execution/soft accounting that does not undo or bound the already-recorded proof of the exceeding receipt itself.

### Likelihood Explanation
Feasibility requires only an unprivileged account able to submit a receipt/transaction with many `AddKey`/`DeleteKey` actions (bounded by `max_actions_per_receipt` and gas limits, but each individual action's trie proof contribution is not counted against `per_receipt_storage_proof_size_limit` outside of `FunctionCall`). No special privileges, validator access, or node compromise is required — this is reachable directly by ordinary transaction senders via RPC. The main practical constraint (not fully verified in this review) is whether `max_actions_per_receipt` and gas costs per `AddKey`/`DeleteKey` are low enough that a single receipt can accumulate enough trie touches to approach the 4MB `per_receipt_storage_proof_size_limit`; this would need to be validated with an integration test.

### Recommendation
Move the `RecordedStorageCounter` (or an equivalent per-receipt proof-size check) out of `VMLogic`/`Ctx` and into the shared receipt-action execution loop in `runtime/runtime/src/lib.rs`, so it is invoked after every trie-touching operation for *all* action types (`AddKey`, `DeleteKey`, `Stake`, `DeployContract`, `DeleteAccount`, etc.), not just `FunctionCall`. Alternatively, call `TrieRecorder::check_proof_size_limit_exceed` (or a per-receipt-scoped variant) immediately after each non-`FunctionCall` action inside the action-application loop in `runtime/runtime/src/lib.rs`, comparing against `per_receipt_storage_proof_size_limit`, and abort/return `ActionErrorKind`-style failure before continuing to the next action.

### Proof of Concept
Add an integration test analogous to `integration-tests/src/tests/features/storage_proof_size_limit.rs::test_storage_proof_size_limit`, but building a receipt consisting solely of many `Action::AddKey`/`Action::DeleteKey` actions on an account with a large number of existing access keys (to maximize per-action trie proof), with no `FunctionCall` action present:
1. Set `per_receipt_storage_proof_size_limit` to a small test value (e.g., a few hundred KB).
2. Construct one receipt with N `AddKey`/`DeleteKey` actions such that the sum of individual trie proof deltas would exceed the limit if accounted incrementally.
3. Apply the receipt via `runtime.apply(...)`.
4. Assert whether the receipt is rejected with a size-exceeded error (expected under correct metering) versus succeeding with `apply_result.proof` exceeding `per_receipt_storage_proof_size_limit` in total size (demonstrating the bypass), similar to the assertion pattern in `test_storage_proof_size_limit` at `integration-tests/src/tests/features/storage_proof_size_limit.rs:123-126`.

### Citations

**File:** runtime/near-vm-runner/src/logic/logic.rs (L256-259)
```rust
        let recorded_storage_counter = RecordedStorageCounter::new(
            ext.get_recorded_storage_size(),
            config.limit_config.per_receipt_storage_proof_size_limit,
        );
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L347-350)
```rust
        let recorded_storage_counter = RecordedStorageCounter::new(
            ext.get_recorded_storage_size(),
            result_state.config.limit_config.per_receipt_storage_proof_size_limit,
        );
```

**File:** runtime/near-vm-runner/src/logic/recorded_storage_counter.rs (L17-33)
```rust
    /// Update the latest observed storage proof size and check if it exceeds the limit.
    /// Should be called after every trie operation.
    pub fn observe_size(&mut self, latest_storage_proof_size: usize) -> Result<(), VMLogicError> {
        self.last_observed_storage_size = latest_storage_proof_size;

        let current_size = self.get_storage_size()?;
        if current_size > self.size_limit {
            let limit_u64 = self.size_limit.try_into().map_err(|_| {
                VMLogicError::InconsistentStateError(InconsistentStateError::IntegerOverflow)
            })?;
            return Err(VMLogicError::HostError(HostError::RecordedStorageExceeded {
                limit: ByteSize::b(limit_u64),
            }));
        }

        Ok(())
    }
```

**File:** core/store/src/trie/trie_recording.rs (L161-163)
```rust
    pub fn check_proof_size_limit_exceed(&self) -> bool {
        self.upper_bound_size.load(Ordering::Acquire) as u64 > self.proof_size_limit
    }
```

**File:** docs/misc/state_witness_size_limits.md (L25-28)
```markdown
* `main_storage_proof_size_soft_limit - 4 MB`
  * This is a limit on the total size of storage proof generated by receipts in one chunk. Once receipts generate more storage proof than this limit, the chunk producer stops processing receipts and moves the rest to the delayed queue.
  * It's a soft limit, which means that the total size of storage proof could reach 8 MB (3.99MB + one receipt which generates 4MB of storage proof)
  * Due to implementation details it's hard to find the exact amount of storage proof generated by a receipt, so an upper bound estimation is used instead. This upper bound assumes that every removal generates additional 2000 bytes of storage proof, so receipts which perform a lot of trie removals might be limited more than theoretically applicable.
```
