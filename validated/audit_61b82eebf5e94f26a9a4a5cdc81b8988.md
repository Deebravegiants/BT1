### Title
Unbounded recursive deallocation in `MemTrieNodeId::remove_ref` can cause stack overflow on deletion of a deep attacker-built trie subtree - (File: core/store/src/trie/mem/node/encoding.rs)

### Summary
`MemTrieNodeId::remove_ref` (core/store/src/trie/mem/node/encoding.rs:240-265) recursively calls itself on every child node once a node's refcount hits zero, with no iteration/worklist bound and no recursion-depth guard. An unprivileged attacker can grow a long single-child extension/branch chain in the in-memory trie via ordinary `storage_write` calls sharing a common key prefix, then trigger deallocation of that whole chain by removing the keys (e.g. via `storage_remove` or `DeleteAccount`), producing recursion depth proportional to the crafted chain length.

### Finding Description
`remove_ref` decrements a node's refcount and, on reaching zero, collects the node's children into a `SmallVec`, deallocates the node itself, and then calls `remove_ref` again on each child [1](#0-0) . This is a plain self-recursive function with no explicit iterative worklist, so the call stack depth is bounded only by the depth of the trie subtree being torn down.

An attacker fully controls the shape of the subtree under their own account/storage keys: repeated `storage_write` calls with keys sharing a long common prefix but differing in trailing nibbles force the compressed patricia trie to materialize a branch/extension node at (up to) every differing nibble position, producing trie depth on the order of the key length in nibbles, bounded only by `max_length_storage_key` (a configured, but not tiny, protocol constant) [2](#0-1) . Deleting all such keys in one receipt (`storage_remove` per key, or `DeleteAccount`/`remove_account` which iterates and removes account/contract-data/access-key trie entries) causes the corresponding memtrie node chain's refcount to drop to zero and unwinds via the same recursive `remove_ref` path [3](#0-2) .

Critically, this deallocation does not happen synchronously inside the metered `FunctionCall`/action execution: root refcounts are only actually decremented to zero when `MemTries::delete_root`/`delete_until_height` runs (block-height-based GC of old state roots, or `MemTrieRootPin::drop`) [4](#0-3) [5](#0-4) . This means the recursive deallocation cost/depth is not accounted for by any gas or compute metering applied to the triggering receipt, and it can execute at a point disconnected from the transaction that logically caused it.

No existing check in `remove_ref`, `MemTries`, or the calling sites converts this recursion into an iterative loop or bounds its depth. The only bound on depth is the protocol's key-length limit, which is large enough that recursion depth could reach into the thousands of stack frames.

### Impact Explanation
If the recursion depth times the per-frame stack usage (each frame holds a `SmallVec<[ArenaPos; NUM_CHILDREN]>`, a decoded node view, and iterator state) exceeds the thread's stack size, this crashes the validator/node process with a stack overflow — a liveness/availability violation (node panic / process crash), matching the "node crash / unbounded resource use" bounty impact class. Because deallocation is decoupled from receipt-level gas metering (it runs during height-based GC or pin-drop, not during the metered action execution), there is no gas cost that scales with or limits this recursive unwind.

### Likelihood Explanation
Feasibility depends on whether an attacker can practically build a subtree deep enough, within existing key-length limits (`max_length_storage_key`) and account-id length limits, to overflow a realistic thread stack. This is plausible but not conclusively confirmed here: I was able to confirm the recursive, unbounded structure of `remove_ref` and the existence of a configurable `max_length_storage_key` limit enforced in `storage_write`/`storage_remove`, but I could not verify the exact configured numeric value of that limit or benchmark actual per-frame stack usage in this environment, so I cannot state with certainty that the reachable maximum depth exceeds a typical 8MB thread stack. The exploit is otherwise fully reachable by an ordinary account holder using only `storage_write`/`storage_remove`/`DeleteAccount`, requiring no special privilege, and is repeatable.

### Recommendation
Rewrite `MemTrieNodeId::remove_ref` to use an explicit iterative worklist (e.g., a `Vec`/`VecDeque` stack of nodes to unref) instead of self-recursion, so deallocation of arbitrarily deep trie subtrees runs in bounded stack space regardless of trie depth. This mirrors defensive patterns already used elsewhere in the codebase for iterating over children via `SmallVec` collection, but currently that collection is only used per-level rather than as a global explicit-stack across levels.

### Proof of Concept
Unit test plan (to be run/validated by an engineer with access to build/execute the code, since exact numeric limits and stack behavior could not be confirmed via static reading alone):
1. In `core/store/src/trie/mem/node/encoding.rs` or `memtries.rs` tests, construct a chain of N nested `InputMemTrieNode::Extension` (or alternating Branch) nodes via `MemTrieNodeId::new`, each wrapping the next, terminating in a `Leaf`, for N at or near the maximum trie depth reachable under `max_length_storage_key`/account-id length limits (compute this bound explicitly from the config constants first).
2. Insert this chain as a memtrie root via `MemTries::insert_root`/`apply_memtrie_changes`.
3. Call `MemTries::delete_root` (which calls `remove_ref`) on the root, run under a constrained-stack test thread (e.g., `std::thread::Builder::new().stack_size(...)` set to the default validator thread stack size) and assert the process does not crash/overflow (or, before the fix, observe the crash to confirm the vulnerability).
4. After converting `remove_ref` to an iterative implementation, re-run the same test and assert successful completion plus `tries.arena.num_active_allocs() == 0`, matching the existing invariant checked in `test_refcount` [6](#0-5) .

### Citations

**File:** core/store/src/trie/mem/node/encoding.rs (L252-263)
```rust
        if new_refcount == 0 {
            let mut children_to_unref: SmallVec<[ArenaPos; NUM_CHILDREN]> = SmallVec::new();
            let node_ptr = self.as_ptr(arena.memory());
            for child in node_ptr.view().iter_children() {
                children_to_unref.push(child.id().pos);
            }
            let alloc_size = node_ptr.size_of_allocation();
            arena.dealloc(self.pos, alloc_size);
            for child in &children_to_unref {
                MemTrieNodeId { pos: *child }.remove_ref(arena);
            }
        }
```

**File:** runtime/near-vm-runner/src/logic/logic.rs (L4318-4325)
```rust
        let key = get_memory_or_register!(self, key_ptr, key_len)?;
        if key.len() as u64 > self.config.limit_config.max_length_storage_key {
            return Err(HostError::KeyLengthExceeded {
                length: key.len() as u64,
                limit: self.config.limit_config.max_length_storage_key,
            }
            .into());
        }
```

**File:** core/store/src/utils/mod.rs (L504-574)
```rust
/// Removes account, code and all access keys and gas keys associated to it.
pub fn remove_account(
    state_update: &mut TrieUpdate,
    account_id: &AccountId,
) -> Result<RemoveAccountResult, StorageError> {
    state_update.remove(TrieKey::Account { account_id: account_id.clone() });
    state_update.remove(TrieKey::ContractCode { account_id: account_id.clone() });

    let mut gas_key_nonce_count: usize = 0;
    let mut gas_key_nonce_total_key_bytes: usize = 0;

    // Removing access keys and gas key nonces
    let lock = state_update.trie().lock_for_iter();
    let mut keys_to_remove: Vec<TrieKey> = Vec::new();
    for raw_key in state_update
        .locked_iter(&trie_key_parsers::get_raw_prefix_for_access_keys(account_id), &lock)?
    {
        let raw_key = raw_key?;
        let key_handle = trie_key_parsers::parse_key_handle_from_access_key_key(
            &raw_key, account_id,
        )
        .map_err(|_e| {
            StorageError::StorageInconsistentState(
                "Can't parse key handle from raw key for AccessKey".to_string(),
            )
        })?;
        let nonce_index =
            trie_key_parsers::parse_nonce_index_from_gas_key_key(&raw_key, account_id, &key_handle)
                .map_err(|_e| {
                    StorageError::StorageInconsistentState(
                        "Can't parse nonce index from raw key for AccessKey".to_string(),
                    )
                })?;
        if let Some(index) = nonce_index {
            gas_key_nonce_count += 1;
            gas_key_nonce_total_key_bytes += raw_key.len();
            keys_to_remove.push(TrieKey::gas_key_nonce(
                account_id.clone(),
                key_handle.clone(),
                index,
            ));
        } else {
            keys_to_remove.push(TrieKey::access_key(account_id.clone(), key_handle.clone()));
        }
    }
    drop(lock);

    for trie_key in keys_to_remove {
        state_update.remove(trie_key);
    }

    // Removing contract data
    let lock = state_update.trie().lock_for_iter();
    let data_keys = state_update
        .locked_iter(&trie_key_parsers::get_raw_prefix_for_contract_data(account_id, &[]), &lock)?
        .map(|raw_key| {
            trie_key_parsers::parse_data_key_from_contract_data_key(&raw_key?, account_id)
                .map_err(|_e| {
                    StorageError::StorageInconsistentState(
                        "Can't parse data key from raw key for ContractData".to_string(),
                    )
                })
                .map(Vec::from)
        })
        .collect::<Result<Vec<_>, _>>()?;
    drop(lock);

    for key in data_keys {
        state_update.remove(TrieKey::ContractData { account_id: account_id.clone(), key });
    }
    Ok(RemoveAccountResult { gas_key_nonce_count, gas_key_nonce_total_key_bytes })
```

**File:** core/store/src/trie/mem/memtries.rs (L200-216)
```rust
    pub fn delete_root(&mut self, state_root: &CryptoHash) {
        if let Some(ids) = self.roots.get_mut(state_root) {
            let last_id = ids.last().unwrap();
            let new_ref = last_id.remove_ref(&mut self.arena);
            if new_ref == 0 {
                ids.pop();
                if ids.is_empty() {
                    self.roots.remove(state_root);
                }
            }
        } else {
            debug_assert!(false, "Deleting non-existent root: {}", state_root);
        }
        MEMTRIE_NUM_ROOTS
            .with_label_values(&[&self.shard_uid.to_string()])
            .set(self.roots.len() as i64);
    }
```

**File:** core/store/src/trie/mem/memtries.rs (L333-337)
```rust
impl Drop for MemTrieRootPin {
    fn drop(&mut self) {
        self.memtries.write().delete_root(&self.state_root);
    }
}
```

**File:** core/store/src/trie/mem/memtries.rs (L401-404)
```rust
        // Expire all roots, and now the number of allocs should be zero.
        tries.delete_until_height(201);
        assert_eq!(tries.arena.num_active_allocs(), 0);
        assert_eq!(tries.num_roots(), 0);
```
