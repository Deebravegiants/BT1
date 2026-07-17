Looking at the core of this claim, I need to verify whether `from_shard_id` is actually bound to the Merkle tree position in steps 4c/4d/4e/4f of `set_state_header`.

### Title
Unbound `from_shard_id` in State-Sync Receipt Proof Allows Receipt Omission via Pigeonhole Bypass — (`chain/chain/src/state_sync/adapter.rs`)

---

### Summary

The Pigeonhole-principle check in `set_state_header` (steps 4c/4d) is logically unsound. `chunks_included` counts every shard that produced a new chunk, but the `from_shard_id` field inside each `ShardProof` is **never verified against the Merkle-tree leaf position**. An attacker serving state-sync data can reuse the `(root, proof, block_proof)` triple of a shard that sent zero receipts to the target shard, attach it to a different `from_shard_id` (one that did send receipts), and thereby hide those receipts while passing every check. The syncing node stores the forged header and later applies an incomplete receipt set in `set_state_finalize`, producing a wrong state root.

---

### Finding Description

**Step 4c** (line 464–465) checks:

```rust
receipt_proofs.len() != block_header.chunks_included() as usize
```

`chunks_included()` is the count of `true` entries in `chunk_mask` — i.e., every shard that produced a new chunk, regardless of whether it sent any receipts to the target shard. [1](#0-0) 

**Step 4d** (line 480–486) only checks that `from_shard_id` values are pairwise distinct. [2](#0-1) 

**Steps 4e and 4f** (lines 487–502) verify:

- 4e: `verify_path(*root, proof, &receipts_hash)` — the receipt list hashes against `root`
- 4f: `verify_path(*block_header.prev_chunk_outgoing_receipts_root(), block_proof, root)` — `root` is a valid leaf in the block's outgoing-receipts Merkle tree [3](#0-2) 

`verify_path` is implemented as `compute_root_from_path(path, hash(item)) == root`. It does **not** check which leaf index the item occupies — only that the hash chain reaches the root. [4](#0-3) 

The block-level Merkle tree is built from **all** chunks' `prev_outgoing_receipts_root` values in order: [5](#0-4) 

**Attack construction** (concrete, 4-shard example):

| Shard | New chunk? | Receipts to target | Legitimate proof |
|-------|-----------|-------------------|-----------------|
| 0 | yes | non-empty | proof_0 |
| 1 | yes | **non-empty** | proof_1 ← attacker omits this |
| 2 | yes | **empty** | proof_2 |
| 3 | yes | non-empty | proof_3 |

Attacker submits 4 proofs (`chunks_included = 4`):

```
proof_0: from_shard_id=0, receipts=[...], root=root_0, block_proof=block_proof_0  ← legitimate
proof_1: from_shard_id=1, receipts=[],   root=root_2, block_proof=block_proof_2  ← FORGED
proof_2: from_shard_id=2, receipts=[],   root=root_2, block_proof=block_proof_2  ← legitimate
proof_3: from_shard_id=3, receipts=[...], root=root_3, block_proof=block_proof_3  ← legitimate
```

- **4c**: 4 == 4 ✓
- **4d**: {0,1,2,3} all distinct ✓
- **4e** for forged proof: `verify_path(root_2, proof_2_for_target, hash(ReceiptList(target, [])))` → shard 2 genuinely sent 0 receipts to target, so this path is valid ✓
- **4f** for forged proof: `verify_path(block_receipts_root, block_proof_2, root_2)` → `root_2` is a real leaf in the Merkle tree, path is valid ✓

All checks pass. Shard 1's receipts are silently dropped.

---

### Impact Explanation

`set_state_finalize` calls `collect_receipts_from_response` which simply flattens all `Vec<Receipt>` from the stored `incoming_receipts_proofs`: [6](#0-5) 

It then passes the flattened list directly to `apply_chunk`: [7](#0-6) 

With shard 1's receipts absent, `apply_chunk` produces a different post-state root than the canonical chain. The syncing node's `ChunkExtra` records this wrong state root, which will be used as `prev_state_root` for subsequent chunks. The node diverges from the canonical chain state and cannot participate in consensus correctly.

---

### Likelihood Explanation

State sync is triggered whenever a node needs to catch up (epoch boundary shard rotation, fresh node startup, or a node that fell behind). The syncing node requests `ShardStateSyncResponseHeader` from peers over the p2p network. Any peer — including an unprivileged attacker node — can respond. The attack requires only public on-chain data (the block's outgoing-receipts Merkle tree and the per-shard receipt proofs) to construct the forged header. No validator or admin privileges are needed.

---

### Recommendation

Replace the Pigeonhole check with an explicit enumeration of all new-chunk shards. For each shard that produced a new chunk (i.e., each `true` entry in `chunk_mask`), require exactly one `ReceiptProof` whose `from_shard_id` matches that shard's ID **and** whose `block_proof` verifies against that shard's position in the Merkle tree (using `verify_path_with_index` or by looking up the shard index and comparing `root` against `block.chunks()[shard_index].prev_outgoing_receipts_root()`). This ties `from_shard_id` to the Merkle leaf position and closes the substitution gap.

---

### Proof of Concept

1. Identify a block B where shard Y produced a new chunk but sent 0 receipts to target shard T, and shard X produced a new chunk with non-empty receipts to T.
2. Obtain the legitimate `ShardStateSyncResponseHeader` for shard T.
3. Replace the `ReceiptProof` entry for shard X with a copy of shard Y's entry, changing only `from_shard_id` to X.
4. Serve this crafted header to a syncing node requesting state for shard T at the corresponding `sync_hash`.
5. Observe that `set_state_header` accepts the header (all four checks pass).
6. After state parts are downloaded and `set_state_finalize` runs, the node's computed state root for shard T will differ from the canonical value because shard X's receipts were never applied. [8](#0-7)

### Citations

**File:** core/primitives/src/block_header.rs (L1340-1351)
```rust
    pub fn chunks_included(&self) -> u64 {
        let mask = match self {
            BlockHeader::BlockHeaderV1(header) => return header.inner_rest.chunks_included,
            BlockHeader::BlockHeaderV2(header) => &header.inner_rest.chunk_mask,
            BlockHeader::BlockHeaderV3(header) => &header.inner_rest.chunk_mask,
            BlockHeader::BlockHeaderV4(header) => &header.inner_rest.chunk_mask,
            BlockHeader::BlockHeaderV5(header) => &header.inner_rest.chunk_mask,
            BlockHeader::BlockHeaderV6(header) => &header.inner_rest.chunk_mask,
            BlockHeader::BlockHeaderV7(header) => &header.inner_rest.chunk_mask,
        };
        mask.iter().map(|&x| u64::from(x)).sum::<u64>()
    }
```

**File:** chain/chain/src/state_sync/adapter.rs (L183-189)
```rust
            let (block_receipts_root, block_receipts_proofs) = merklize(
                &block
                    .chunks()
                    .iter()
                    .map(|chunk| *chunk.prev_outgoing_receipts_root())
                    .collect::<Vec<CryptoHash>>(),
            );
```

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

**File:** core/primitives/src/merkle.rs (L112-119)
```rust
/// Verify merkle path for given item and corresponding path.
pub fn verify_path<T: BorshSerialize>(root: MerkleHash, path: &MerklePath, item: T) -> bool {
    verify_hash(root, path, CryptoHash::hash_borsh(item))
}

pub fn verify_hash(root: MerkleHash, path: &MerklePath, item_hash: MerkleHash) -> bool {
    compute_root_from_path(path, item_hash) == root
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
