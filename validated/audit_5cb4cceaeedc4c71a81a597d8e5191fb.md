Now I have all the information needed for a complete analysis. Let me trace the full attack path.

**Key code facts:**

1. `set_state_header` (adapter.rs:463-503): The pigeonhole check only enforces `from_shard_id` uniqueness via a `HashSet`, not that each `from_shard_id` maps to the actual shard whose outgoing receipts root is used.

2. Check 4f (adapter.rs:495-502): `verify_path(*block_header.prev_chunk_outgoing_receipts_root(), block_proof, root)` — verifies `root` is *some* leaf in the block's Merkle tree, but does **not** verify which position (which shard) that leaf corresponds to.

3. `collect_receipts_from_response` (chain.rs:4141-4147): Flat-maps all receipts with no deduplication — `from_shard_id` is completely ignored.

4. `set_state_finalize` (chain_update.rs:487, 540): Passes the collected receipts directly to `apply_chunk` with no post-apply state root validation.

5. `apply_chunk_postprocessing` (chunk_application.rs:70, 83): Stores `apply_result.to_chunk_extra(gas_limit)` (containing the wrong new state root) into `DBCol::ChunkExtra` unconditionally.

**The attack:**

For a block with shards A and B (2 chunks included), attacker crafts:
- Entry 0: `from_shard_id=A`, `root=root_B`, `block_proof=proof_for_B_in_block`, `receipts=B_receipts`, `proof=proof_of_B_receipts_in_root_B`
- Entry 1: `from_shard_id=B`, `root=root_B`, `block_proof=proof_for_B_in_block`, `receipts=B_receipts`, `proof=proof_of_B_receipts_in_root_B`

All checks pass:
- Count: 2 == `chunks_included` ✓
- Uniqueness: A ≠ B ✓
- Check 4e: `verify_path(root_B, proof_of_B_receipts_in_root_B, hash(target_shard_id, B_receipts))` ✓
- Check 4f: `verify_path(block_outgoing_root, proof_for_B, root_B)` ✓

Shard A's receipts are omitted; shard B's receipts are applied twice. `collect_receipts_from_response` produces a wrong receipt list. `apply_chunk` produces a wrong `new_root`. This wrong root is committed to `DBCol::ChunkExtra` with no validation.

**Post-sync consequence:** When the node processes the next block, `validate_chunk_with_chunk_extra` compares the next chunk's `prev_state_root` (canonical) against the stored wrong `chunk_extra.state_root()` — mismatch causes the node to be permanently stuck.

---

### Title
Flawed Pigeonhole Receipt Proof Check in `set_state_header` Allows Malicious Peer to Inject Wrong Receipts, Producing Wrong State Root — (`chain/chain/src/state_sync/adapter.rs`)

### Summary
The pigeonhole completeness argument in `set_state_header` is unsound. It checks only that `from_shard_id` values are distinct, but never verifies that each `from_shard_id` corresponds to the shard whose outgoing receipts root (`root`) is actually used. A malicious peer can reuse one shard's outgoing receipts root for two entries under different `from_shard_id` labels, passing all Merkle proof checks while omitting one shard's receipts entirely. The wrong receipt set is then applied unconditionally in `set_state_finalize`, producing a wrong state root that is committed to the DB, permanently breaking the syncing node.

### Finding Description
In `set_state_header`, the receipt proof loop (adapter.rs:475–503) enforces:
- `from_shard_id` uniqueness via `HashSet<ShardId>` (lines 475–486)
- Count equality with `block_header.chunks_included()` (lines 464–465)
- Merkle proof 4e: receipts hash is in `root` (lines 490–492)
- Merkle proof 4f: `root` is a leaf in `block_header.prev_chunk_outgoing_receipts_root()` (lines 495–502)

The `root` and `block_proof` come from the attacker-controlled `shard_state_header.root_proofs()[i][j]` (line 487). Check 4f only verifies that `root` is *some* valid leaf in the block's Merkle tree — it does not verify which shard's position that leaf occupies. The `from_shard_id` field is never cross-checked against the actual shard index of `root` in the block's chunk list.

An attacker sets `root_proofs[i][0] = root_proofs[i][1] = RootProof(root_B, proof_for_B)` and provides two `ReceiptProof` entries with `from_shard_id=A` and `from_shard_id=B` respectively, both carrying shard B's receipts and shard B's Merkle proof. All four checks pass. Shard A's receipts are absent; shard B's receipts appear twice.

`collect_receipts_from_response` (chain.rs:4141–4147) flat-maps all receipts without deduplication or `from_shard_id` inspection. The wrong receipt list is passed to `apply_chunk` (chain_update.rs:540). `apply_chunk_postprocessing` (chunk_application.rs:83) writes the resulting wrong `ChunkExtra` (containing the wrong state root) to `DBCol::ChunkExtra` with no post-apply state root validation.

### Impact Explanation
The syncing node stores a wrong state root in `ChunkExtra`. On the next block, `validate_chunk_with_chunk_extra` detects a mismatch between the canonical chunk's `prev_state_root` and the stored wrong root, causing the node to permanently fail block processing. The node is stuck and cannot participate in the network until it re-syncs from scratch. Any peer can trigger this against any node currently performing state sync.

### Likelihood Explanation
State sync is a standard production code path triggered whenever a node is far behind. Any peer the syncing node contacts can serve a crafted header. The block structure (shard outgoing receipts roots, Merkle paths) is publicly derivable from on-chain data. No validator or admin privileges are required. The crafted header requires only arithmetic over public block data.

### Recommendation
In the receipt proof loop, after check 4f, verify that `root` equals the outgoing receipts root of the shard identified by `from_shard_id` — i.e., look up `block.chunks()[shard_layout.get_shard_index(from_shard_id)?].prev_outgoing_receipts_root()` and assert it equals `root`. This closes the gap between the `from_shard_id` label and the actual shard root being proven. Alternatively, replace the `HashSet<ShardId>` uniqueness check with a `HashSet<CryptoHash>` over `root` values, ensuring each shard's outgoing receipts root is used at most once.

### Proof of Concept
```
// Block has shards A (index 0) and B (index 1), both with new chunks.
// root_A = block.chunks()[0].prev_outgoing_receipts_root()
// root_B = block.chunks()[1].prev_outgoing_receipts_root()
// proof_for_B = block_receipts_proofs[1]  (Merkle path for root_B in block tree)
// B_receipts = receipts shard B sent to target shard
// proof_of_B_in_root_B = Merkle path proving B_receipts ∈ root_B

crafted_header.incoming_receipts_proofs[block_i] = ReceiptProofResponse(block_hash, [
    ReceiptProof(B_receipts, ShardProof { from_shard_id: A, to_shard_id: target, proof: proof_of_B_in_root_B }),
    ReceiptProof(B_receipts, ShardProof { from_shard_id: B, to_shard_id: target, proof: proof_of_B_in_root_B }),
]);
crafted_header.root_proofs[block_i] = [
    RootProof(root_B, proof_for_B),   // entry for "A" — actually B's root
    RootProof(root_B, proof_for_B),   // entry for B
];

// Call set_state_header with crafted_header:
// - count check: 2 == chunks_included(2) ✓
// - uniqueness: {A, B} no duplicates ✓
// - 4e for entry 0: verify_path(root_B, proof_of_B_in_root_B, hash(target, B_receipts)) ✓
// - 4f for entry 0: verify_path(block_outgoing_root, proof_for_B, root_B) ✓
// - same for entry 1 ✓
// Header accepted and stored.

// set_state_finalize applies B_receipts twice, A_receipts never.
// Wrong state root committed to ChunkExtra.
// Node stuck on next block: prev_state_root mismatch.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** chain/chain/src/state_sync/adapter.rs (L463-503)
```rust
            // 4c. Checking len of receipt_proofs for current block
            if receipt_proofs.len() != shard_state_header.root_proofs()[i].len()
                || receipt_proofs.len() != block_header.chunks_included() as usize
            {
                byzantine_assert!(false);
                return Err(Error::Other("set_shard_state failed: invalid proofs".into()));
            }
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

**File:** chain/chain/src/spice/chunk_application.rs (L70-83)
```rust
    let chunk_extra = apply_result.to_chunk_extra(gas_limit);

    let ApplyChunkResult {
        mut trie_changes,
        outcomes,
        outgoing_receipts,
        processed_receipts,
        receipt_to_tx,
        stats,
        ..
    } = apply_result;

    // `ChunkExtra` marks this shard's apply as done; must share `store_update` with the refcounted writes below.
    store_update.chunk_store_update().set_chunk_extra(block_hash, &shard_uid, &chunk_extra);
```
