### Title
Duplicate `input_data_ids` in an `ActionReceipt` cause `PendingDataCount` to desync from the number of distinct `PostponedReceiptId` links, permanently stranding the receipt - (File: runtime/runtime/src/lib.rs)

### Summary
`validate_action_receipt` in `runtime/runtime/src/verifier.rs` only checks that `receipt.input_data_ids().len()` does not exceed `max_number_input_data_dependencies`; it does not check for duplicate ids in the list. When such a receipt with duplicate `input_data_ids` reaches `process_action_receipt` in `runtime/runtime/src/lib.rs`, the pending-data bookkeeping (`PendingDataCount` vs. `PostponedReceiptId`) desyncs because the counter is incremented once per (duplicated) id while the postponed-link index is keyed by `(account_id, data_id)` and therefore collapses duplicates into a single entry.

### Finding Description
`validate_action_receipt` performs only a cardinality check against `max_number_input_data_dependencies`; it does not deduplicate or reject an `input_data_ids` list containing the same `CryptoHash` more than once [1](#0-0) .

On receipt arrival, `process_action_receipt` iterates `action_receipt.input_data_ids()` and, for every id not yet received, both increments `pending_data_count` and writes a `TrieKey::PostponedReceiptId { receiver_id, data_id }` entry: [2](#0-1) 
If the same `data_id` appears twice in `input_data_ids`, `pending_data_count` is incremented twice, but the `PostponedReceiptId` write uses the same key both times, so only a single index entry exists for that `data_id`. The result is `PendingDataCount = 2` while there is only one path by which a matching `DataReceipt` can ever decrement it.

When the corresponding (unique) `DataReceipt` for that `data_id` is delivered, `process_receipt` looks up the single `PostponedReceiptId` entry, decrements `pending_data_count` by 1 (from 2 to 1), and removes the `PostponedReceiptId` link: [3](#0-2) 
Since a `data_id` is produced by exactly one promise result / `DataReceipt` in normal execution, no second `DataReceipt` will ever arrive to decrement the counter the rest of the way to 0. The postponed `ActionReceipt` and its `PendingDataCount` entry remain in the trie indefinitely — the `TrieKey::PostponedReceipt` is never removed and `apply_action_receipt` is never called for it, per the "Processing DataReceipt" invariant documented in `docs/RuntimeSpec/Receipts.md` (decrement to 0 triggers execution/removal) [4](#0-3) .

This matches the described exploit shape (`promise_and`/`promise_batch_then` combining a promise with itself, or otherwise causing the same data dependency id to be listed twice for one `ActionReceipt`): the receiving shard's postponed-receipt/pending-data-count accounting diverges from the actual number of distinct `DataReceipt`s that will ever be delivered.

### Impact Explanation
This is a receipt/congestion accounting failure: a postponed `ActionReceipt`, along with any prepaid gas/deposit balance attached to it, becomes permanently unresolvable and stuck in state (`PostponedReceipt`/`PendingDataCount` trie entries never cleared, action never executed, any promised callback/refund never fires). This is a state-bloat / stranded-funds condition rather than an immediate double-spend, but it violates the "no permanently stranded receipts" invariant and can be triggered repeatedly to leave garbage entries in the receiving shard's state permanently.

### Likelihood Explanation
The trigger only requires an ordinary account to submit a contract call whose logic constructs an `ActionReceipt` with a duplicated data dependency id (e.g., joining the same promise with itself via `promise_and`, or otherwise producing a callback receipt with a repeated input data id) — no elevated privileges are needed. However, I could not fully confirm within the available search budget whether the current `promise_and`/`promise_batch_then` implementation actually permits constructing a genuinely duplicated `data_id` in a single receipt's `input_data_ids` list (I only located the function names in `runtime/near-vm-runner/src/logic/logic.rs` but did not get to inspect their bodies before running out of tool iterations). This is the one precondition that remains unverified; the downstream accounting bug in `process_action_receipt`/`process_receipt` itself is confirmed directly from code.

### Recommendation
- In `validate_action_receipt` (`runtime/runtime/src/verifier.rs`), reject `ActionReceipt`s whose `input_data_ids` contain duplicate entries (e.g., via a `HashSet` uniqueness check), independent of the existing length-vs-`max_number_input_data_dependencies` check.
- Defensively, in `process_action_receipt` (`runtime/runtime/src/lib.rs`), deduplicate `input_data_ids` before computing `pending_data_count`, so the counter always matches the number of distinct `PostponedReceiptId` index entries created.

### Proof of Concept
Integration test plan (runtime crate):
1. Construct an `ActionReceipt` directly (bypassing the wasm promise API, to isolate the runtime-layer bug) with `input_data_ids = [data_id_x, data_id_x]` (same hash twice), targeting some receiver account, with a trivial action (e.g., a transfer).
2. Feed this receipt into `process_action_receipt`/`process_receipt` (or via full `apply` of a chunk containing it), and assert:
   - `PendingDataCount { receiver_id, receipt_id }` is set to `2`.
   - Only one `PostponedReceiptId { receiver_id, data_id: data_id_x }` entry exists.
3. Deliver a single `DataReceipt { receiver_id, data_id: data_id_x, data: Some(...) }` for that shard/account.
4. Assert that after processing, the postponed receipt is **not** removed (`get_postponed_receipt` still returns `Some`), `PendingDataCount` is now `1`, and no further `DataReceipt` for `data_id_x` will ever be produced by the protocol — demonstrating the receipt is permanently stranded and never executes, contradicting the "eventually resolves" invariant described in `docs/RuntimeSpec/Receipts.md`.

### Citations

**File:** runtime/runtime/src/verifier.rs (L1-1)
```rust
use crate::action_validation::{validate_actions, validate_actions_with_mode};
```

**File:** runtime/runtime/src/lib.rs (L1396-1472)
```rust
                // given data_id.
                // If we don't have a postponed receipt yet, we don't need to do anything for now.
                if let Some(receipt_id) = get(
                    state_update,
                    &TrieKey::PostponedReceiptId {
                        receiver_id: account_id.clone(),
                        data_id: data_receipt.data_id,
                    },
                )? {
                    // There is already a receipt that is awaiting for the just received data.
                    // Removing this pending data_id for the receipt from the state.
                    state_update.remove(TrieKey::PostponedReceiptId {
                        receiver_id: account_id.clone(),
                        data_id: data_receipt.data_id,
                    });
                    // Checking how many input data items is pending for the receipt.
                    let pending_data_count: u32 = get(
                        state_update,
                        &TrieKey::PendingDataCount { receiver_id: account_id.clone(), receipt_id },
                    )?
                    .ok_or_else(|| {
                        StorageError::StorageInconsistentState(
                            "pending data count should be in the state".to_string(),
                        )
                    })?;
                    if pending_data_count == 1 {
                        // It was the last input data pending for this receipt. We'll cleanup
                        // some receipt related fields from the state and execute the receipt.

                        // Removing pending data count from the state.
                        state_update.remove(TrieKey::PendingDataCount {
                            receiver_id: account_id.clone(),
                            receipt_id,
                        });
                        // Fetching the receipt itself.
                        let ready_receipt =
                            get_postponed_receipt(state_update, account_id, receipt_id)?
                                .ok_or_else(|| {
                                    StorageError::StorageInconsistentState(
                                        "pending receipt should be in the state".to_string(),
                                    )
                                })?;
                        // Removing the receipt from the state.
                        remove_postponed_receipt(state_update, account_id, receipt_id);
                        // Executing the receipt. It will read all the input data and clean it up
                        // from the state.
                        return self
                            .apply_action_receipt(
                                state_update,
                                apply_state,
                                pipeline_manager,
                                &ready_receipt,
                                receipt_sink,
                                instant_receipts,
                                validator_proposals,
                                stats,
                                epoch_info_provider,
                                receipt_to_tx,
                            )
                            .map(Some);
                    } else {
                        // There is still some pending data for the receipt, so we update the
                        // pending data count in the state.
                        set(
                            state_update,
                            TrieKey::PendingDataCount {
                                receiver_id: account_id.clone(),
                                receipt_id,
                            },
                            &(pending_data_count.checked_sub(1).ok_or_else(|| {
                                StorageError::StorageInconsistentState(
                                    "pending data count is 0, but there is a new DataReceipt"
                                        .to_string(),
                                )
                            })?),
                        );
                    }
```

**File:** runtime/runtime/src/lib.rs (L1608-1623)
```rust
        let mut pending_data_count: u32 = 0;
        for data_id in action_receipt.input_data_ids() {
            if !has_received_data(state_update, account_id, *data_id)? {
                pending_data_count += 1;
                // The data for a given data_id is not available, so we save a link to this
                // receipt_id for the pending data_id into the state.
                set(
                    state_update,
                    TrieKey::PostponedReceiptId {
                        receiver_id: account_id.clone(),
                        data_id: *data_id,
                    },
                    receipt.receipt_id(),
                )
            }
        }
```

**File:** docs/RuntimeSpec/Receipts.md (L159-164)
```markdown
Next, runtime checks if there are any [`Postponed ActionReceipt`](#postponed-actionreceipt) waiting for this `DataReceipt` by querying [`Pending DataReceipt` to the Postponed Receipt](#pending-datareceipt-for-postponed-actionreceipt). If there is no postponed `receipt_id` yet, we do nothing else. If there is a postponed `receipt_id`, we do the following:

- decrement [`Pending Data Count`](#pending-datareceipt-count) for the postponed `receipt_id`
- remove found [`Pending DataReceipt` to the `Postponed ActionReceipt`](#pending-datareceipt-for-postponed-actionreceipt)

If [`Pending DataReceipt Count`](#pending-datareceipt-count) is now 0 that means all the [`Receipt.input_data_ids`](#input_data_ids) are in storage and runtime can safely apply the [Postponed Receipt](#postponed-actionreceipt) and remove it from the store.
```
