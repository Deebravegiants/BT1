### Title
Unbounded native recursion in `post_order_traverse_updated_nodes` allows attacker-controlled trie depth to crash validators - ([File: core/store/src/trie/mem/memtrie_update.rs])

### Finding Description
`MemTrieUpdate::post_order_traverse_updated_nodes` performs a plain, unbounded Rust-level recursive descent over the tree of `updated_nodes`, recursing once per `Branch` child and once per `Extension` child [1](#0-0) . It is invoked from `to_memtrie_changes_internal`, which runs once per chunk application to materialize the final `MemTrieChanges` for the whole set of updates accumulated in that chunk [2](#0-1) .

The recursion depth equals the number of `Branch`/`Extension` nodes on the deepest path of *updated* nodes, not merely the byte length of any single key. Deep Extension nodes (long common prefixes) collapse into single nodes, but a chain of nested `Branch` nodes — created whenever one committed key is a strict prefix of another key that also has data further down — cannot be collapsed, since each such branch holds a value. An attacker fully controls this by writing many storage keys under their own contract account where key `i+1` extends key `i` by a small increment (e.g. one byte), each carrying a value. Because `max_length_storage_key` is `4,194,304` bytes (4 MiB) [3](#0-2) , the attacker can in principle build a nested-branch chain many times deeper than the OS thread stack can tolerate for native (non-tail-call) recursion, purely through `storage_write` host calls that are individually validated only for key/value length, not chain depth [4](#0-3) .

Crucially, this recursion happens in the validator's native Rust call stack while applying the chunk, completely outside of the WASM `max_stack_height`/finite-wasm metering, which only limits the *guest* WASM operand stack [5](#0-4) . No gas/limit check gates the depth of the trie subtree touched by a chunk's aggregate updates.

Notably, the codebase already recognizes this exact risk class elsewhere and has deliberately converted similar trie traversals to explicit-stack, non-recursive algorithms: `TrieStorageUpdate::flatten_nodes` uses an explicit `stack: Vec<(usize, FlattenNodesCrumb)>` instead of recursion [6](#0-5) , and `TrieRecorder::get_subtree_size` is explicitly commented "Non recursive approach to avoid any potential stack overflows" [7](#0-6) . `post_order_traverse_updated_nodes` was not given the same treatment, leaving it as an outlier with genuine unbounded native recursion.

### Impact Explanation
If the recursion depth exceeds available native stack space during chunk application, the validator process (and every other validator that must apply the same chunk) crashes with a stack overflow, which is a chain-halting liveness failure reachable purely from an ordinary account's contract storage writes — matching NEAR's "node panic / chain halt from attacker-controlled input" bounty impact class.

### Likelihood Explanation
Exploitability depends on economic feasibility: each nested key requires a separate `storage_write` (base cost ~64 Ggas plus per-byte cost) and pays NEAR storage staking cost per byte stored, so building a chain deep enough to overflow a typical thread stack (tens of thousands to hundreds of thousands of nested branch nodes, depending on frame size) requires many transactions/receipts within one chunk and a nontrivial amount of locked NEAR balance for storage. This is costly but not gated by any hard protocol limit on trie-update recursion depth — only by gas and storage-stake budgets, which an attacker willing to spend can accumulate over multiple transactions batched into a single chunk. This makes the bug reachable but with real economic cost, unlike the network-layer/free-to-repeat bugs that would be immediately practical.

### Recommendation
Rewrite `post_order_traverse_updated_nodes` to use an explicit work-stack (the same "Entering/Exiting" crumb pattern already used in `TrieStorageUpdate::flatten_nodes`) instead of native recursion, eliminating dependence on OS stack depth regardless of trie shape.

### Proof of Concept
Integration test plan:
1. Deploy a test contract and, from a single account, issue a bulk sequence of `storage_write` calls (spread across the max allowed actions/receipts per chunk permitted by gas limits) creating keys `k`, `k+1 byte`, `k+2 bytes`, ... each holding a small value, so that each successive key is a strict extension of the previous one and each intermediate key also stores a value (forcing a `Branch` node with a value at every level, preventing extension-node compression).
2. Apply the resulting chunk through the runtime and call `MemTrieUpdate::to_memtrie_changes_only`/`to_trie_changes`, which triggers `post_order_traverse_updated_nodes`.
3. Run under a stack-depth-instrumented build (or with a reduced test thread stack size) and assert that the call either completes successfully without crashing, or fails gracefully instead of overflowing the native stack — demonstrating the current implementation's vulnerability by observing a stack overflow/abort at a depth well below the protocol's nominal key-length-derived worst case.

### Citations

**File:** core/store/src/trie/mem/memtrie_update.rs (L292-326)
```rust
    fn post_order_traverse_updated_nodes(
        node_id: UpdatedNodeId,
        updated_nodes: &Vec<Option<UpdatedMemTrieNodeWithSize>>,
        ordered_nodes: &mut Vec<UpdatedNodeId>,
    ) {
        let node = updated_nodes[node_id].as_ref().unwrap();
        match &node.node {
            UpdatedMemTrieNode::Empty => {
                assert_eq!(node_id, 0); // only root can be empty
                return;
            }
            UpdatedMemTrieNode::Branch { children, .. } => {
                for child in children.iter() {
                    if let Some(OldOrUpdatedNodeId::Updated(child_node_id)) = child {
                        Self::post_order_traverse_updated_nodes(
                            *child_node_id,
                            updated_nodes,
                            ordered_nodes,
                        );
                    }
                }
            }
            UpdatedMemTrieNode::Extension { child, .. } => {
                if let OldOrUpdatedNodeId::Updated(child_node_id) = child {
                    Self::post_order_traverse_updated_nodes(
                        *child_node_id,
                        updated_nodes,
                        ordered_nodes,
                    );
                }
            }
            _ => {}
        }
        ordered_nodes.push(node_id);
    }
```

**File:** core/store/src/trie/mem/memtrie_update.rs (L404-409)
```rust
    fn to_memtrie_changes_internal(self) -> (MemTrieChanges, Vec<(CryptoHash, Vec<u8>)>) {
        MEMTRIE_NUM_NODES_CREATED_FROM_UPDATES
            .with_label_values(&[&self.shard_uid])
            .inc_by(self.updated_nodes.len() as u64);
        let mut ordered_nodes = Vec::new();
        Self::post_order_traverse_updated_nodes(0, &self.updated_nodes, &mut ordered_nodes);
```

**File:** core/parameters/src/snapshots/near_parameters__config_store__tests__42.json.snap (L236-236)
```text
      "max_length_storage_key": 4194304,
```

**File:** runtime/near-vm-runner/src/logic/logic.rs (L4303-4335)
```rust
    pub fn storage_write(
        &mut self,
        key_len: u64,
        key_ptr: u64,
        value_len: u64,
        value_ptr: u64,
        register_id: u64,
    ) -> Result<u64> {
        self.result_state.gas_counter.pay_base(base)?;
        if self.context.is_view() {
            return Err(
                HostError::ProhibitedInView { method_name: "storage_write".to_string() }.into()
            );
        }
        self.result_state.gas_counter.pay_base(storage_write_base)?;
        let key = get_memory_or_register!(self, key_ptr, key_len)?;
        if key.len() as u64 > self.config.limit_config.max_length_storage_key {
            return Err(HostError::KeyLengthExceeded {
                length: key.len() as u64,
                limit: self.config.limit_config.max_length_storage_key,
            }
            .into());
        }
        let value = get_memory_or_register!(self, value_ptr, value_len)?;
        if value.len() as u64 > self.config.limit_config.max_length_storage_value {
            return Err(HostError::ValueLengthExceeded {
                length: value.len() as u64,
                limit: self.config.limit_config.max_length_storage_value,
            }
            .into());
        }
        self.result_state.gas_counter.pay_per(storage_write_key_byte, key.len() as u64)?;
        self.result_state.gas_counter.pay_per(storage_write_value_byte, value.len() as u64)?;
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/logic.rs (L254-268)
```rust
pub fn finite_wasm_stack(
    ctx: &mut Ctx,
    _memory: &mut [u8],
    operand_size: u64,
    frame_size: u64,
) -> Result<()> {
    ctx.remaining_stack =
        match ctx.remaining_stack.checked_sub(operand_size.saturating_add(frame_size)) {
            Some(s) => s,
            None => return Err(VMLogicError::HostError(HostError::MemoryAccessViolation)),
        };
    let gas = ((frame_size + 7) / 8) * u64::from(ctx.config.regular_op_cost);
    consume_gas(&mut ctx.result_state.gas_counter, gas)?;
    Ok(())
}
```

**File:** core/store/src/trie/trie_storage_update.rs (L163-170)
```rust
    #[tracing::instrument(level = "debug", target = "store::trie", "Trie::flatten_nodes", skip_all)]
    pub(crate) fn flatten_nodes(
        mut self,
        old_root: &CryptoHash,
        node: usize,
    ) -> Result<TrieChanges, StorageError> {
        let mut stack: Vec<(usize, FlattenNodesCrumb)> = Vec::new();
        stack.push((node, FlattenNodesCrumb::Entering));
```

**File:** core/store/src/trie/trie_recording.rs (L298-306)
```rust
    fn get_subtree_size(&self, subtree_root: &CryptoHash) -> SubtreeSize {
        let mut nodes_size: usize = 0;
        let mut values_size: usize = 0;

        // Non recursive approach to avoid any potential stack overflows.
        let mut queue: VecDeque<CryptoHash> = VecDeque::new();
        queue.push_back(*subtree_root);

        let mut seen_items: HashSet<CryptoHash> = HashSet::new();
```
