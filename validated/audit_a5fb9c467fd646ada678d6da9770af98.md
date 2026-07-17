### Title
Broken Pigeonhole Invariant in `set_state_header` Allows Malicious Peer to Omit Incoming Receipts During State Sync — (`chain/chain/src/state_sync/adapter.rs`)

---

### Summary

The receipt-proof completeness check in `set_state_header` relies on a Pigeonhole argument that is logically unsound. The code enforces uniqueness of `from_shard_id` values across the supplied `receipt_proofs`, but it never verifies that each `RootProof.root` corresponds to the chunk identified by `from_shard_id`. A malicious peer can supply `chunks_included` proofs with distinct `from_shard_id` labels while reusing the `prev_outgoing_receipts_root` of a shard that has **no** receipts to the target shard for every entry. All cryptographic checks pass, the header is accepted and stored, and `set_state_finalize` subsequently applies the chunk with an empty (or incomplete) incoming-receipt list, producing a wrong state root.

---

### Finding Description

**Step 4c** (line 464–468) verifies:

```
receipt_proofs.len() == block_header.chunks_included()
```

**Step 4d** (lines 480–486) verifies that all `from_shard_id` values are distinct via `visited_shard_ids`.

The comment at lines 470–474 states:

> "According to Pigeonhole principle, it's enough to ensure all receipt_proofs are distinct to prove that all receipts were received and no receipts were hidden." [1](#0-0) 

This argument is **incorrect**. The Pigeonhole principle would hold only if each `RootProof(root, block_proof)` were cryptographically bound to the chunk at `from_shard_id`. The code performs no such binding. Steps 4e and 4f only verify:

- `verify_path(root, proof, receipts_hash)` — receipts hash into `root`
- `verify_path(block_receipts_root, block_proof, root)` — `root` is *some* leaf in the block's Merkle tree [2](#0-1) 

Neither check constrains which chunk's root is used, nor does any check prevent the same `root` from appearing in multiple proofs.

**Concrete attack (2-shard example):**

| | Shard A (index 0) | Shard B (index 1) |
|---|---|---|
| Receipts to target T | non-empty | empty |
| `prev_outgoing_receipts_root` | `root_A` | `root_B` |

The attacker constructs two proofs, both using `root_B` and its Merkle proof `block_proof_B`:

```
Proof 1: from_shard_id=A, receipts=[], proof=proof_empty_in_B,
         RootProof(root_B, block_proof_B)

Proof 2: from_shard_id=B, receipts=[], proof=proof_empty_in_B,
         RootProof(root_B, block_proof_B)
```

All checks pass:
- **4c**: `len == 2 == chunks_included` ✓
- **4d**: `{A, B}` are distinct ✓
- **4e** (both): `verify_path(root_B, proof_empty_in_B, hash(ReceiptList(T,[])))` ✓ (B genuinely has no receipts to T)
- **4f** (both): `verify_path(block_receipts_root, block_proof_B, root_B)` ✓

Shard A's receipts to T are entirely absent from the accepted header.

**Downstream impact in `set_state_finalize`:**

`set_state_finalize` directly uses `incoming_receipts_proofs` from the stored header to build the receipt list passed to `apply_chunk`:

```rust
let receipts = collect_receipts_from_response(&receipt_proof_responses);
// ...
apply_chunk(..., &receipts, ...)
``` [3](#0-2) 

`collect_receipts_from_response` simply flattens the `ReceiptProof` vectors from the header: [4](#0-3) 

With the crafted header, shard A's receipts are missing, so `apply_chunk` runs with an incomplete receipt set, producing a state root that diverges from the canonical chain.

---

### Impact Explanation

A syncing node that accepts the crafted `ShardStateSyncResponseHeader` will:
1. Store it in `DBCol::StateHeaders` (line 528).
2. Call `set_state_finalize`, which applies the chunk with missing incoming receipts.
3. Persist a wrong state root for the synced shard.

The node's shard state permanently diverges from the canonical chain. Any subsequent block production or validation on that shard will be incorrect. This is a concrete, irreversible wrong-state-transition impact scoped to the syncing node's shard state. [5](#0-4) 

---

### Likelihood Explanation

State sync data is served by arbitrary peers; no validator or privileged role is required. The attacker only needs to:
1. Be a peer of the syncing node.
2. Know the block structure (public information on-chain).
3. Compute valid Merkle proofs for a shard with empty receipts to the target — all inputs are public.

The crafted header is fully constructible from public chain data. No cryptographic forgery is required.

---

### Recommendation

The fix must bind each `RootProof.root` to the chunk identified by `from_shard_id`. Two equivalent approaches:

1. **Verify `root` corresponds to `from_shard_id`**: After step 4d, look up the chunk at `from_shard_id`'s index in the block and assert `root == block.chunks()[from_shard_index].prev_outgoing_receipts_root()`. This is exactly what `compute_state_response_header` does at line 204. [6](#0-5) 

2. **Also enforce uniqueness of `root` values**: Add a `visited_roots: HashSet<CryptoHash>` alongside `visited_shard_ids` and reject any proof that reuses a `root`.

Option 1 is strictly stronger and directly closes the gap between what the Pigeonhole argument assumes and what the code actually checks.

---

### Proof of Concept

```rust
// Pseudocode unit test sketch
// Setup: 2-shard network, block B has chunks_included=2
// Shard 0 sent receipts to target shard T; shard 1 sent none.

let root_1 = block.chunks()[1].prev_outgoing_receipts_root(); // shard 1, empty receipts to T
let (block_receipts_root, block_proofs) = merklize(
    block.chunks().iter().map(|c| *c.prev_outgoing_receipts_root()).collect()
);
let block_proof_1 = block_proofs[1].clone();

// Merkle proof that hash(ReceiptList(T, [])) is in root_1
let proof_empty_in_1 = /* computed from shard 1's outgoing receipt tree */;

let crafted_header = ShardStateSyncResponseHeaderV2 {
    incoming_receipts_proofs: vec![ReceiptProofResponse(block_hash, Arc::new(vec![
        ReceiptProof(vec![], ShardProof { from_shard_id: 0, to_shard_id: T, proof: proof_empty_in_1.clone() }),
        ReceiptProof(vec![], ShardProof { from_shard_id: 1, to_shard_id: T, proof: proof_empty_in_1.clone() }),
    ]))],
    root_proofs: vec![vec![
        RootProof(root_1, block_proof_1.clone()),
        RootProof(root_1, block_proof_1.clone()),
    ]],
    // ... other valid fields ...
};

// Assert: set_state_header accepts the crafted header (bug present)
assert!(adapter.set_state_header(T, sync_hash, crafted_header).is_ok());

// Assert: set_state_finalize applies chunk with 0 incoming receipts
// (shard 0's receipts are silently dropped)
```

### Citations

**File:** chain/chain/src/state_sync/adapter.rs (L202-206)
```rust
                let from_shard_index = prev_shard_layout.get_shard_index(*from_shard_id)?;

                let root_proof = *block.chunks()[from_shard_index].prev_outgoing_receipts_root();
                root_proofs_cur
                    .push(RootProof(root_proof, block_receipts_proofs[from_shard_index].clone()));
```

**File:** chain/chain/src/state_sync/adapter.rs (L470-486)
```rust
            // We know there were exactly `block_header.chunks_included` chunks included
            // on the height of block `block_hash`.
            // There were no other proofs except for included chunks.
            // According to Pigeonhole principle, it's enough to ensure all receipt_proofs are distinct
            // to prove that all receipts were received and no receipts were hidden.
            let mut visited_shard_ids = HashSet::<ShardId>::new();
            for (j, receipt_proof) in receipt_proofs.iter().enumerate() {
                let ReceiptProof(receipts, shard_proof) = receipt_proof;
                let ShardProof { from_shard_id, to_shard_id: _, proof } = shard_proof;
                // 4d. Checking uniqueness for set of `from_shard_id`
                match visited_shard_ids.get(from_shard_id) {
                    Some(_) => {
                        byzantine_assert!(false);
                        return Err(Error::Other("set_shard_state failed: invalid proofs".into()));
                    }
                    _ => visited_shard_ids.insert(*from_shard_id),
                };
```

**File:** chain/chain/src/state_sync/adapter.rs (L487-503)
```rust
                let RootProof(root, block_proof) = &shard_state_header.root_proofs()[i][j];
                let receipts_hash = CryptoHash::hash_borsh(ReceiptList(shard_id, receipts));
                // 4e. Proving the set of receipts is the subset of outgoing_receipts of shard `shard_id`
                if !verify_path(*root, proof, &receipts_hash) {
                    byzantine_assert!(false);
                    return Err(Error::Other("set_shard_state failed: invalid proofs".into()));
                }
                // 4f. Proving the outgoing_receipts_root matches that in the block
                if !verify_path(
                    *block_header.prev_chunk_outgoing_receipts_root(),
                    block_proof,
                    root,
                ) {
                    byzantine_assert!(false);
                    return Err(Error::Other("set_shard_state failed: invalid proofs".into()));
                }
            }
```

**File:** chain/chain/src/state_sync/adapter.rs (L525-529)
```rust
        // Saving the header data.
        let mut store_update = self.chain_store.store().store_update();
        let key = borsh::to_vec(&StateHeaderKey(shard_id, sync_hash)).unwrap();
        store_update.set_ser(DBCol::StateHeaders, &key, &shard_state_header);
        store_update.commit();
```

**File:** chain/chain/src/chain_update.rs (L487-542)
```rust
        let receipts = collect_receipts_from_response(&receipt_proof_responses);
        let is_genesis = block_header.height() == self.chain_store_update.get_genesis_height();
        let prev_block_header = (!is_genesis)
            .then(|| self.chain_store_update.get_block_header(block_header.prev_hash()))
            .transpose()?;

        // Prev block header should be present during state sync, since headers have been synced at
        // this point, except for genesis.
        let gas_price = if let Some(prev_block_header) = &prev_block_header {
            prev_block_header.next_gas_price()
        } else {
            block_header.next_gas_price()
        };

        let chunk_header = chunk.cloned_header();
        let gas_limit = chunk_header.gas_limit();
        let block = self.chain_store_update.get_block(block_header.hash())?;
        let transactions = chunk.to_transactions().to_vec();
        let transaction_validity = if let Some(prev_block_header) = prev_block_header {
            self.chain_store_update
                .chain_store()
                .compute_transaction_validity(&prev_block_header, &chunk)
        } else {
            vec![true; transactions.len()]
        };
        let transactions = SignedValidPeriodTransactions::new(transactions, transaction_validity);
        let shard_uid =
            shard_id_to_uid(self.epoch_manager.as_ref(), shard_id, block_header.epoch_id())?;
        let memtrie_pin = self
            .runtime_adapter
            .get_tries()
            .maybe_pin_memtrie_root(shard_uid, chunk_header.prev_state_root())?;
        let apply_result = self.runtime_adapter.apply_chunk(
            RuntimeStorageConfig::new(chunk_header.prev_state_root(), true),
            ApplyChunkReason::UpdateTrackedShard,
            ApplyChunkShardContext {
                shard_uid,
                gas_limit,
                last_validator_proposals: chunk_header.prev_validator_proposals(),
                is_new_chunk: true,
                on_post_state_ready: None,
                memtrie_pin,
            },
            ApplyChunkBlockContext {
                block_type: BlockType::Normal,
                height: chunk_header.height_included(),
                prev_block_hash: *chunk_header.prev_block_hash(),
                block_timestamp: block_header.raw_timestamp(),
                gas_price,
                random_seed: *block_header.random_value(),
                congestion_info: block.block_congestion_info(),
                bandwidth_requests: block.block_bandwidth_requests(),
            },
            &receipts,
            transactions,
        )?;
```

**File:** chain/chain/src/chain.rs (L4141-4147)
```rust
pub fn collect_receipts_from_response(
    receipt_proof_response: &[ReceiptProofResponse],
) -> Vec<Receipt> {
    collect_receipts(
        receipt_proof_response.iter().flat_map(|ReceiptProofResponse(_, proofs)| proofs.iter()),
    )
}
```
