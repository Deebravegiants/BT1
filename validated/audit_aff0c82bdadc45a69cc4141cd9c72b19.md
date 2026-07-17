Now I have all the information needed for a thorough analysis. Let me trace the full attack path.

**Key facts established:**

1. `verify_path` in `core/primitives/src/merkle.rs` only checks that a leaf hashes to the given root via the path — it does **not** verify which index/slot the leaf occupies.
2. `set_state_header` in `chain/chain/src/state_sync/adapter.rs` never compares `chunk.shard_id()` to the requested `shard_id`.
3. `validate_state_part_impl` in `chain/chain/src/runtime/mod.rs` ignores `shard_id` entirely for actual validation — it only uses `state_root` and `part_id`.

---

### Title
Missing `chunk.shard_id()` vs. requested `shard_id` check in `set_state_header` allows wrong-shard state to be applied under target shard identity — (`chain/chain/src/state_sync/adapter.rs`)

### Summary

`set_state_header` accepts a `ShardStateSyncResponseHeader` from a peer without ever asserting that `chunk.shard_id()` equals the requested `shard_id`. The `verify_path` Merkle check only proves the chunk is *somewhere* in the block's chunk-headers Merkle tree; it does not bind the proof to the correct shard slot. A malicious peer can supply shard 1's chunk (with its valid position-1 Merkle proof) in response to a shard 0 state-sync request, pass all validation, and have the header stored under `StateHeaderKey(shard_id=0, sync_hash)`. Because `validate_state_part` is also shard-agnostic (uses only `state_root`), the peer can then supply shard 1's state parts, which validate against shard 1's state root and are applied into shard 0's trie storage.

### Finding Description

In `set_state_header`: [1](#0-0) 

The function extracts `chunk` from the peer-supplied header and runs two checks:

1. **`validate_chunk_proofs`** — verifies the chunk's internal hash, tx root, and receipts root. It never inspects `chunk.shard_id()`. [2](#0-1) 

2. **`verify_path`** — verifies that `ChunkHashHeight(chunk.chunk_hash(), chunk.height_included())` is a leaf in the block's `chunk_headers_root` Merkle tree. The implementation simply recomputes the root from the path and compares; it does not check which index (shard slot) the leaf occupies. [3](#0-2) 

There is no guard of the form `chunk.shard_id() != shard_id` anywhere in `set_state_header`. [4](#0-3) 

After the header is stored, `set_state_part` retrieves the stored header, reads `state_root` from the chunk (now shard 1's state root), and calls `validate_state_part(shard_id=0, state_root=<shard1_root>, ...)`. The implementation of `validate_state_part_impl` ignores `shard_id` entirely and only validates against `state_root`: [5](#0-4) 

So shard 1's state parts pass validation and are then applied via `apply_state_part` into shard 0's `shard_uid` trie storage: [6](#0-5) 

### Impact Explanation

A node completing state sync for shard 0 ends up with shard 1's trie written into shard 0's storage. The node's shard 0 state root diverges from the canonical chain. The node cannot produce or validate shard 0 chunks correctly, causing it to be permanently out of consensus for that shard. This is a **Critical** sync-correctness / consensus-divergence impact.

### Likelihood Explanation

Any peer on the network can respond to state sync requests. The attacker only needs:
- A real shard 1 chunk and its position-1 Merkle proof (available from any full node).
- Valid receipt proofs for shard 0 for the height range implied by shard 1's `height_included` (also publicly available).
- Shard 1's state parts (publicly available).

No validator or admin privileges are required. The attack is fully constructible from public chain data.

### Recommendation

Add an explicit shard-id equality check immediately after extracting the chunk in `set_state_header`:

```rust
let chunk = shard_state_header.cloned_chunk();
if chunk.shard_id() != shard_id {
    return Err(Error::Other(
        "set_shard_state failed: chunk shard_id does not match requested shard_id".into(),
    ));
}
```

Similarly add the same guard for `prev_chunk_header.shard_id()`.

### Proof of Concept

1. Node A requests state sync for `shard_id = 0`, `sync_hash = H`.
2. Malicious peer B holds the real shard 1 chunk `C1` included in block `B_prev = prev(H)` at shard-index 1, along with its Merkle proof `proof1` against `B_prev.chunk_headers_root`.
3. B constructs a `ShardStateSyncResponseHeaderV2` with `chunk = C1`, `chunk_proof = proof1`, valid `prev_chunk_header`/`prev_chunk_proof` for shard 1, and valid receipt proofs for shard 0 covering the height range `[C1.height_included, H]`.
4. B sends this header to A in response to A's state-sync header request.
5. A calls `set_state_header(shard_id=0, sync_hash=H, header)`:
   - `validate_chunk_proofs(C1)` → passes (C1 is internally valid).
   - `verify_path(B_prev.chunk_headers_root, proof1, ChunkHashHeight(C1.hash, C1.height_included))` → passes (proof1 is the correct Merkle proof for C1 at slot 1).
   - Receipt proof checks → pass (B supplied real shard-0 receipts).
   - Header stored under `StateHeaderKey(shard_id=0, H)`.
6. B supplies shard 1's state parts. `set_state_part(shard_id=0, ...)` reads `state_root = C1.prev_state_root` (shard 1's root). `validate_state_part(shard_id=0, state_root=<shard1_root>, part)` → passes (validation is root-only).
7. `apply_state_part(shard_id=0, state_root=<shard1_root>, ...)` writes shard 1's trie into shard 0's `shard_uid` storage.
8. Node A now has shard 1's state under shard 0's identity — consensus divergence confirmed.

### Citations

**File:** chain/chain/src/state_sync/adapter.rs (L368-532)
```rust
    pub fn set_state_header(
        &self,
        shard_id: ShardId,
        sync_hash: CryptoHash,
        shard_state_header: ShardStateSyncResponseHeader,
    ) -> Result<(), Error> {
        let sync_block_header = self.chain_store.get_block_header(&sync_hash)?;

        let chunk = shard_state_header.cloned_chunk();
        let prev_chunk_header = shard_state_header.cloned_prev_chunk_header();

        // 1-2. Checking chunk validity
        if !validate_chunk_proofs(&chunk, self.epoch_manager.as_ref())? {
            byzantine_assert!(false);
            return Err(Error::Other(
                "set_shard_state failed: chunk header proofs are invalid".into(),
            ));
        }

        // Consider chunk itself is valid.

        // 3. Checking that chunks `chunk` and `prev_chunk` are included in appropriate blocks
        // 3a. Checking that chunk `chunk` is included into block at last height before sync_hash
        // 3aa. Also checking chunk.height_included
        let sync_prev_block_header =
            self.chain_store.get_block_header(sync_block_header.prev_hash())?;
        if !verify_path(
            *sync_prev_block_header.chunk_headers_root(),
            shard_state_header.chunk_proof(),
            &ChunkHashHeight(chunk.chunk_hash().clone(), chunk.height_included()),
        ) {
            byzantine_assert!(false);
            return Err(Error::Other(
                "set_shard_state failed: chunk isn't included into block".into(),
            ));
        }

        let block_header = get_block_header_on_chain_by_height(
            &self.chain_store,
            &sync_hash,
            chunk.height_included(),
        )?;
        // 3b. Checking that chunk `prev_chunk` is included into block at height before chunk.height_included
        // 3ba. Also checking prev_chunk.height_included - it's important for getting correct incoming receipts
        match (&prev_chunk_header, shard_state_header.prev_chunk_proof()) {
            (Some(prev_chunk_header), Some(prev_chunk_proof)) => {
                let prev_block_header =
                    self.chain_store.get_block_header(block_header.prev_hash())?;
                if !verify_path(
                    *prev_block_header.chunk_headers_root(),
                    prev_chunk_proof,
                    &ChunkHashHeight(prev_chunk_header.chunk_hash().clone(), prev_chunk_header.height_included()),
                ) {
                    byzantine_assert!(false);
                    return Err(Error::Other(
                        "set_shard_state failed: prev_chunk isn't included into block".into(),
                    ));
                }
            }
            (None, None) => {
                if chunk.height_included() != 0 {
                    return Err(Error::Other(
                    "set_shard_state failed: received empty state response for a chunk that is not at height 0".into()
                ));
                }
            }
            _ =>
                return Err(Error::Other("set_shard_state failed: `prev_chunk_header` and `prev_chunk_proof` must either both be present or both absent".into()))
        };

        // 4. Proving incoming receipts validity
        // 4a. Checking len of proofs
        if shard_state_header.root_proofs().len()
            != shard_state_header.incoming_receipts_proofs().len()
        {
            byzantine_assert!(false);
            return Err(Error::Other("set_shard_state failed: invalid proofs".into()));
        }
        let mut hash_to_compare = sync_hash;
        for (i, receipt_response) in
            shard_state_header.incoming_receipts_proofs().iter().enumerate()
        {
            let ReceiptProofResponse(block_hash, receipt_proofs) = receipt_response;

            // 4b. Checking that there is a valid sequence of continuous blocks
            if *block_hash != hash_to_compare {
                byzantine_assert!(false);
                return Err(Error::Other(
                    "set_shard_state failed: invalid incoming receipts".into(),
                ));
            }
            let header = self.chain_store.get_block_header(&hash_to_compare)?;
            hash_to_compare = *header.prev_hash();

            let block_header = self.chain_store.get_block_header(block_hash)?;
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
        }
        // 4g. Checking that there are no more heights to get incoming_receipts
        let header = self.chain_store.get_block_header(&hash_to_compare)?;
        if header.height() != prev_chunk_header.map_or(0, |h| h.height_included()) {
            byzantine_assert!(false);
            return Err(Error::Other("set_shard_state failed: invalid incoming receipts".into()));
        }

        // 5. Checking that state_root_node is valid
        let chunk_inner = chunk.take_header().take_inner();
        if matches!(
            self.runtime_adapter.validate_state_root_node(
                shard_state_header.state_root_node(),
                chunk_inner.prev_state_root(),
            ),
            StateRootNodeValidationResult::Invalid
        ) {
            byzantine_assert!(false);
            return Err(Error::Other("set_shard_state failed: state_root_node is invalid".into()));
        }

        // Saving the header data.
        let mut store_update = self.chain_store.store().store_update();
        let key = borsh::to_vec(&StateHeaderKey(shard_id, sync_hash)).unwrap();
        store_update.set_ser(DBCol::StateHeaders, &key, &shard_state_header);
        store_update.commit();

        Ok(())
    }
```

**File:** chain/chain/src/validate.rs (L22-66)
```rust
pub fn validate_chunk_proofs(
    chunk: &ShardChunk,
    epoch_manager: &dyn EpochManagerAdapter,
) -> Result<bool, Error> {
    let correct_chunk_hash = chunk.compute_header_hash();

    // 1. Checking chunk.header.hash
    let header_hash = chunk.header_hash();
    if header_hash != &correct_chunk_hash {
        byzantine_assert!(false);
        return Ok(false);
    }

    // 2. Checking that chunk body is valid
    // 2a. Checking chunk hash
    if chunk.chunk_hash() != &correct_chunk_hash {
        byzantine_assert!(false);
        return Ok(false);
    }
    let height_created = chunk.height_created();
    let outgoing_receipts_root = chunk.prev_outgoing_receipts_root();
    let (transactions, receipts) = (chunk.to_transactions(), chunk.prev_outgoing_receipts());

    // 2b. Checking that chunk transactions are valid
    let (tx_root, _) = merklize(transactions);
    if &tx_root != chunk.tx_root() {
        byzantine_assert!(false);
        return Ok(false);
    }
    // 2c. Checking that chunk receipts are valid
    if height_created == 0 {
        return Ok(receipts.is_empty() && outgoing_receipts_root == &CryptoHash::default());
    } else {
        let shard_layout = {
            let prev_block_hash = chunk.prev_block_hash();
            epoch_manager.get_shard_layout_from_prev_block(&prev_block_hash)?
        };
        let outgoing_receipts_hashes = Chain::build_receipts_hashes(receipts, &shard_layout)?;
        let (receipts_root, _) = merklize(&outgoing_receipts_hashes);
        if &receipts_root != outgoing_receipts_root {
            byzantine_assert!(false);
            return Ok(false);
        }
    }
    Ok(true)
```

**File:** core/primitives/src/merkle.rs (L113-119)
```rust
pub fn verify_path<T: BorshSerialize>(root: MerkleHash, path: &MerklePath, item: T) -> bool {
    verify_hash(root, path, CryptoHash::hash_borsh(item))
}

pub fn verify_hash(root: MerkleHash, path: &MerklePath, item_hash: MerkleHash) -> bool {
    compute_root_from_path(path, item_hash) == root
}
```

**File:** chain/chain/src/runtime/mod.rs (L531-551)
```rust
    fn validate_state_part_impl(
        &self,
        state_root: &StateRoot,
        part_id: PartId,
        part: &StatePart,
    ) -> StatePartValidationResult {
        let partial_state = part.to_partial_state();
        let Ok(partial_state) = part.to_partial_state() else {
            // Deserialization error means we've got the data from malicious peer
            tracing::error!(target: "state-parts", ?partial_state, "state part deserialization error");
            return StatePartValidationResult::Invalid;
        };
        match Trie::validate_state_part(state_root, part_id, partial_state) {
            Ok(_) => StatePartValidationResult::Valid,
            // Storage error should not happen
            Err(err) => {
                tracing::error!(target: "state-parts", ?err, "state part storage error");
                StatePartValidationResult::Invalid
            }
        }
    }
```

**File:** chain/chain/src/runtime/mod.rs (L1501-1527)
```rust
    fn apply_state_part(
        &self,
        shard_id: ShardId,
        state_root: &StateRoot,
        part_id: PartId,
        part: &StatePart,
        epoch_id: &EpochId,
    ) -> Result<(), Error> {
        let _timer = metrics::STATE_SYNC_APPLY_PART_DELAY
            .with_label_values(&[&shard_id.to_string()])
            .start_timer();

        let part = part
            .to_partial_state()
            .expect("Part was already validated earlier, so could never fail here");
        let ApplyStatePartResult { trie_changes, flat_state_delta, contract_codes } =
            Trie::apply_state_part(state_root, part_id, part);
        let tries = self.get_tries();
        let shard_uid = self.get_shard_uid_from_epoch_id(shard_id, epoch_id)?;
        let mut store_update = tries.store_update();
        tries.apply_all(&trie_changes, shard_uid, &mut store_update);
        tracing::debug!(target: "chain", %shard_id, values_count = %flat_state_delta.len(), "inserting values to flat storage");
        // TODO: `apply_to_flat_state` inserts values with random writes, which can be time consuming.
        //       Optimize taking into account that flat state values always correspond to a consecutive range of keys.
        flat_state_delta.apply_to_flat_state(&mut store_update.flat_store_update(), shard_uid);
        self.precompile_contracts(epoch_id, contract_codes)?;
        store_update.commit();
```
