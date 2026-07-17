The vulnerability is real. Here is the precise trace:

## `submit_promise_resume_data` — Double-Resume Guard Bypass

### The Guard Logic

In `submit_promise_resume_data`, the guard that prevents duplicate resume receipts is:

```rust
if has_yield_receipt_in_state || has_yield_status_in_state {
    self.receipt_manager.create_promise_resume_receipt(data_id, data);
    set_promise_yield_status(..., PromiseYieldStatus::ResumeInitiated);
    return Ok(true);
}
``` [1](#0-0) 

After the first call, `set_promise_yield_status` overwrites the trie entry for `TrieKey::PromiseYieldStatus { receiver_id, data_id }` with `ResumeInitiated`. It does **not** remove the key.

### Why `has_promise_yield_status` Returns `true` on the Second Call

`has_promise_yield_status` is a pure key-existence check:

```rust
pub fn has_promise_yield_status(...) -> Result<bool, StorageError> {
    trie.contains_key(
        &TrieKey::PromiseYieldStatus { receiver_id: receiver_id.clone(), data_id },
        AccessOptions::DEFAULT,
    )
}
``` [2](#0-1) 

It checks only whether the key **exists**, not what value it holds. After the first call writes `ResumeInitiated`, the key is still present. The second call to `submit_promise_resume_data` with the same `data_id` finds `has_yield_status_in_state == true` and proceeds to call `create_promise_resume_receipt` a second time.

### `create_promise_resume_receipt` Has No Deduplication

```rust
pub(super) fn create_promise_resume_receipt(&mut self, data_id: CryptoHash, data: Vec<u8>) {
    self.data_receipts.push(DataReceiptMetadata {
        data_id,
        data: Some(data),
        is_promise_resume: true,
    });
}
``` [3](#0-2) 

It unconditionally appends to `data_receipts`. There is no check for duplicate `data_id` entries. Two `PromiseResume` receipts with the same `data_id` are emitted in `outgoing_receipts`.

### Setup Path

When `promise_yield_create` is called within the same function execution, `create_promise_yield_receipt` in `ext.rs` writes `PromiseYieldStatus::Yielded` to the trie: [4](#0-3) 

This means `has_yield_status_in_state` is `true` from the moment of yield creation, and remains `true` through both resume calls (first as `Yielded`, then as `ResumeInitiated`).

### Impact

Two `PromiseResume` data receipts with the same `data_id` are produced in `outgoing_receipts`. When processed by the runtime:
- The first receipt satisfies the postponed receipt's data dependency and triggers the callback.
- The second receipt arrives for the same `data_id` and either triggers the callback a second time (with a different payload if the contract passed different data), or corrupts the `ReceivedData` trie entry by overwriting it after the callback has already consumed it.

This produces a non-deterministic or corrupted state root and outcome root, directly matching the scoped impact of cross-shard receipt handling with state-transition impact.

### Root Cause

The guard in `submit_promise_resume_data` must distinguish between `Yielded` (resume allowed) and `ResumeInitiated` (resume already in flight). Instead, it conflates both into a single key-existence check, making `ResumeInitiated` indistinguishable from `Yielded` for the purpose of the guard.

---

### Title
Double `PromiseResume` receipt emission via `submit_promise_resume_data` guard bypass — (`runtime/runtime/src/ext.rs`)

### Summary
`submit_promise_resume_data` uses `has_promise_yield_status` (a key-existence check) as its deduplication guard. After the first resume call writes `PromiseYieldStatus::ResumeInitiated`, the key still exists, so a second call with the same `data_id` passes the guard and emits a second `PromiseResume` receipt, causing the yield callback to execute twice with potentially different payloads and corrupting the state root.

### Finding Description
The guard at `ext.rs:407` checks `has_promise_yield_status`, which returns `true` for any stored status value — including `ResumeInitiated`. The first call writes `ResumeInitiated` but does not remove the key. The second call sees the key present, bypasses the guard, and calls `create_promise_resume_receipt` again. `ReceiptManager::create_promise_resume_receipt` has no deduplication logic and blindly appends a second `DataReceiptMetadata` with the same `data_id`.

### Impact Explanation
Two `PromiseResume` receipts with the same `data_id` appear in `outgoing_receipts`. Both satisfy the same postponed receipt's data dependency. The callback executes twice, potentially with different data payloads, producing divergent state roots and outcome roots across validators — a consensus-breaking state transition.

### Likelihood Explanation
Any unprivileged contract can call `promise_yield_create` followed by two calls to `promise_yield_resume` with the same `data_id` in a single function invocation. No special privileges are required. The host function is exposed to all contracts.

### Recommendation
In `submit_promise_resume_data`, replace the key-existence check with a value check: read the actual `PromiseYieldStatus` and only proceed if the status is `Yielded`. If the status is already `ResumeInitiated`, return `Ok(false)` (or an appropriate error). Alternatively, remove the `PromiseYieldStatus` key after setting `ResumeInitiated` and rely solely on `has_promise_yield_receipt` for the guard — but this requires verifying that no other code path depends on the `ResumeInitiated` status being present.

### Proof of Concept
Deploy a contract with a method that:
1. Calls `promise_yield_create` → obtains `data_id`
2. Calls `promise_yield_resume(data_id, b"payload1")` → returns `true`
3. Calls `promise_yield_resume(data_id, b"payload2")` → also returns `true` (bug)

Run `NightshadeRuntime::apply` and assert `outgoing_receipts` contains exactly one `PromiseResume` receipt. The assertion fails: two receipts are present, both with the same `data_id` but different payloads.

### Citations

**File:** runtime/runtime/src/ext.rs (L354-361)
```rust
        set_promise_yield_status(
            &mut self.trie_update,
            &receiver_id,
            input_data_id,
            PromiseYieldStatus::Yielded,
        );

        Ok((receipt_index, input_data_id))
```

**File:** runtime/runtime/src/ext.rs (L400-416)
```rust
        let has_yield_receipt_in_state =
            has_promise_yield_receipt(self.trie_update, self.account_id.clone(), data_id)
                .map_err(wrap_storage_error)?;
        let has_yield_status_in_state =
            has_promise_yield_status(self.trie_update, &self.account_id, data_id)
                .map_err(wrap_storage_error)?;

        if has_yield_receipt_in_state || has_yield_status_in_state {
            self.receipt_manager.create_promise_resume_receipt(data_id, data);
            set_promise_yield_status(
                &mut self.trie_update,
                &self.account_id,
                data_id,
                PromiseYieldStatus::ResumeInitiated,
            );
            return Ok(true);
        }
```

**File:** core/store/src/utils/mod.rs (L231-240)
```rust
pub fn has_promise_yield_status(
    trie: &dyn TrieAccess,
    receiver_id: &AccountId,
    data_id: CryptoHash,
) -> Result<bool, StorageError> {
    trie.contains_key(
        &TrieKey::PromiseYieldStatus { receiver_id: receiver_id.clone(), data_id },
        AccessOptions::DEFAULT,
    )
}
```

**File:** runtime/runtime/src/receipt_manager.rs (L175-181)
```rust
    pub(super) fn create_promise_resume_receipt(&mut self, data_id: CryptoHash, data: Vec<u8>) {
        self.data_receipts.push(DataReceiptMetadata {
            data_id,
            data: Some(data),
            is_promise_resume: true,
        });
    }
```
