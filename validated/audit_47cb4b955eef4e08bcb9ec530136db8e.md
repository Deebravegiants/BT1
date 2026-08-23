### Title
Unbounded recursive child-unref in `MemTrieNodeId::remove_ref` can stack-overflow a validator on deep trie deletions - (File: core/store/src/trie/mem/node/encoding.rs)

### Finding Description
`MemTrieNodeId::remove_ref` decrements a node's refcount and, when it hits zero, deallocates the node and then recurses into every child via a plain (non-tail, non-iterative) call `MemTrieNodeId { pos: *child }.remove_ref(arena)` for each entry in `children_to_unref`. [1](#0-0) 
There is no explicit worklist/stack-based traversal and no depth limiting; the call depth of this recursion tracks the depth of the in-memory trie path being torn down. This function is reached from ordinary chunk application whenever the last reference to a chain of memtrie nodes is dropped, e.g. via `MemTries::delete_root` -> `MemTrieNodeId::remove_ref`, which is exercised on every committed trie update as old roots expire. [2](#0-1) 

An attacker who is only an ordinary account holder can submit `storage_write`/`storage_remove` calls whose key length is bounded only by the protocol's `max_length_storage_key` parameter (2048 bytes in current mainnet/testnet configs, larger in historical configs), enforced in `VMLogic::storage_write`. [3](#0-2) 
By writing a "comb"-shaped set of keys that diverge one nibble at a time (each new key sharing an ever-longer common prefix with the previous keys before diverging), the attacker can force the trie to materialize a long alternating chain of `Branch`/`Extension` nodes whose depth approaches the nibble-length of the key (up to ~4096 nibbles at the current 2048-byte key limit, or far more under legacy 4MB key-length configurations). Deleting these keys in one or a few receipts causes a single `remove_ref` call on the terminal node to cascade recursively through the entire chain as refcounts drop to zero at each level, since nothing else references the intermediate nodes.

Existing protections (max key length, gas metering, storage costs) bound the *size* and *cost* of the attack but do not bound the *recursion depth* of `remove_ref` itself — none of them impose a check that limits trie depth or converts this deallocation walk to an iterative one. This differs from typical disk-backed trie deletion code paths in the same crate, and stands out as the one recursive unref path without an explicit stack/worklist.

### Impact Explanation
If the resulting recursion depth exceeds the runtime thread's stack size, this crashes the validating/chunk-applying thread with a stack overflow, which is an unrecoverable process abort in Rust (no way to catch it), potentially taking down a validator/RPC node applying the chunk. Because chunk application must be deterministic and reproducible across nodes, if the attack is embedded in a chunk, every honest node processing that chunk (validators, RPC nodes with memtries enabled) would independently crash on the same operation, which maps to a chain-halt / denial-of-service class impact (`DETERMINISM_AND_LIVENESS`).

### Likelihood Explanation
- Preconditions are attacker-controllable: ordinary account keys, `storage_write` and `storage_remove` are public host functions with no special privilege needed.
- Feasibility is constrained by protocol limits: current `max_length_storage_key = 2048` bytes limits nibble depth per key to 4096, and building a full binary comb of that depth requires on the order of thousands of separate keys/writes, each costing gas for `storage_write_key_byte`/`storage_write_base`, spread across many receipts/blocks due to per-receipt gas limits (`max_total_prepaid_gas`, `max_gas_burnt`). [4](#0-3) 
- Whether ~4096 recursive stack frames of `remove_ref` (each holding a `SmallVec<[ArenaPos; NUM_CHILDREN]>`, decoded header structs, and pointer bookkeeping) is sufficient to overflow the actual runtime thread's stack could not be conclusively determined from static review alone — this depends on frame size (a few hundred bytes to low KB, from inspection) and the specific thread's configured stack size in the chunk-application call path, which I was unable to fully verify within available search results (no explicit `stack_size`/`thread::Builder` configuration was found near memtrie/runtime apply code in this pass). This is a real gap in verification that would need a constrained-stack unit test to confirm the concrete overflow threshold, as the audit prompt itself proposes.

### Recommendation
Convert `MemTrieNodeId::remove_ref`'s child-unref cascade from recursive calls to an explicit iterative worklist (e.g., a `Vec`/`VecDeque` of pending `ArenaPos` to unref, processed in a loop) so that recursion depth is O(1) regardless of trie depth. This mirrors safe patterns already used elsewhere for potentially deep trie traversals and removes any dependency on host thread stack size.

### Proof of Concept
1. Add a unit/integration test in `core/store/src/trie/mem/` that:
   - Builds a `MemTries` structure via repeated `storage_write`-equivalent insertions of a "comb" key set: keys `k_0..k_N` where `k_i` shares the first `i` nibbles with `k_{i-1}` then diverges, using key lengths at or near `max_length_storage_key` nibble-depth (up to ~4096 nibbles).
   - Commits these as one trie root, then deletes all of them in a single update (`delete_root`/equivalent full removal so all intermediate refcounts drop to 0).
2. Run this test on a thread spawned with a deliberately constrained stack size (e.g., `std::thread::Builder::new().stack_size(1_MiB)`), matching or below realistic node thread stack sizes, and assert the thread does not crash/abort.
3. Fuzz over comb depth (number of diverging keys) and key length to empirically find the depth at which `remove_ref`'s recursion overflows the stack, and confirm whether that depth is reachable within `max_length_storage_key`/`max_gas_burnt` constraints — establishing whether the theoretical bug is practically triggerable by an attacker under production thread configurations.

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

**File:** core/store/src/trie/mem/memtries.rs (L200-212)
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

**File:** core/parameters/res/runtime_configs/parameters.yaml (L271-283)
```yaml
max_total_log_length: 16_384
max_total_prepaid_gas: 300_000_000_000_000
max_actions_per_receipt: 100
max_deploy_actions_per_receipt: 100
max_number_bytes_method_names: 2_000
max_length_method_name: 256
max_arguments_length: 4_194_304
max_length_returned_data: 4_194_304
max_contract_size: 4_194_304
max_transaction_size: 4_194_304
max_receipt_size: 4_294_967_295
max_length_storage_key: 4_194_304
max_length_storage_value: 4_194_304
```
