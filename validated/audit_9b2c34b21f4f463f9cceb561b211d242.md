### Title
Invalid Receipt Proofs in Chunk State Witnesses at Resharding Boundaries Cause Stateless Validation Failure - (File: `chain/chain/src/stateless_validation/state_witness.rs`)

### Summary
When a shard is split during resharding, `collect_source_receipt_proofs` generates Merkle receipt proofs that are structurally invalid for the child shards. The proofs were committed over the full set of receipts addressed to the parent shard, but the witness-building code filters those receipts to only the child shard's subset before embedding them. The resulting mismatch between the committed Merkle root and the filtered receipt list causes every chunk state witness produced for a child shard at the resharding epoch boundary to fail validation by chunk validators.

### Finding Description

The function `collect_source_receipt_proofs` in `chain/chain/src/stateless_validation/state_witness.rs` is responsible for collecting incoming receipt proofs that prove the execution of a chunk. It calls `get_incoming_receipts_for_shard` to retrieve stored receipt proofs for the target shard. [1](#0-0) 

At a resharding boundary, the parent shard (e.g., shard B) is split into two children (B_left, B_right). The outgoing receipts from source shards were committed to the block's Merkle tree with `to_shard_id = B`. The Merkle proof for each `ReceiptProof` covers `hash(ReceiptList(B, all_receipts_to_B))`.

When building the state witness for B_left, `get_incoming_receipts_for_shard` retrieves the stored incoming receipts for the parent shard B. These proofs have `to_shard_id = B` and their Merkle proofs cover the full receipt list going to B. The function then filters or the downstream `validate_source_receipt_proofs` filters these receipts to only those belonging to B_left: [2](#0-1) 

After filtering, the receipt list is a strict subset of what the Merkle proof covers. The proof verifies `hash(ReceiptList(B, all_receipts_to_B))`, but the witness now contains only `hash(ReceiptList(B_left, filtered_receipts))`. These hashes differ, so the proof is invalid.

The codebase explicitly acknowledges this as an unresolved bug: [3](#0-2) 

The `get_incoming_receipts_for_shard` function, when crossing the resharding epoch boundary, maps the child shard back to the parent shard ID and retrieves the parent's stored incoming receipts: [4](#0-3) 

The stored proofs are keyed to the parent shard and their Merkle proofs are computed over the parent's full receipt list. No mechanism exists to re-derive a valid sub-proof for only the child shard's receipts.

### Impact Explanation

Every chunk state witness produced for a child shard (B_left or B_right) at the first block of the resharding epoch will contain receipt proofs that fail Merkle verification. Chunk validators executing `validate_source_receipt_proofs` will reject these witnesses: [5](#0-4) 

The corrupted protocol value is the **validity decision** for chunk state witnesses at the resharding boundary. Rejected witnesses mean the chunk producer cannot collect sufficient endorsements, causing missing chunks for all child shards at the resharding epoch boundary. This is a liveness failure: the network cannot make progress on child shards until the epoch passes or the bug is worked around.

**Impact: High** — all child shards at every resharding boundary are affected simultaneously.

### Likelihood Explanation

Resharding is a scheduled, infrequent protocol event (static resharding via protocol upgrade, or dynamic resharding triggered by shard memory thresholds). However, cross-shard receipts are routine: any transaction that calls a contract on a different shard generates outgoing receipts. At any resharding boundary where cross-shard receipts exist (which is virtually guaranteed in a live network), the bug fires deterministically.

An unprivileged user can amplify the impact by sending cross-shard transactions in the epoch before resharding, ensuring receipts are present at the boundary. Even without deliberate action, staking rewards, protocol treasury transfers, and normal DeFi activity generate cross-shard receipts continuously.

**Likelihood: Low** — resharding events are rare, but the bug fires deterministically when they occur.

### Recommendation

Follow the approach described in the TODO: collect the original unfiltered `ReceiptProof` (covering the full parent shard receipt list) and validate the Merkle proof against the committed root before filtering. Only after successful proof verification should the receipts be filtered to the child shard's subset for state application. This preserves proof validity while correctly partitioning receipts between children.

Concretely, `collect_source_receipt_proofs` should embed the full parent-shard proof in the witness, and `validate_source_receipt_proofs` should verify the proof against the parent's committed root, then filter receipts for application — not filter before verification.

### Proof of Concept

1. In epoch N, shard B is scheduled to split into B_left and B_right at the start of epoch N+1.
2. An unprivileged user sends a cross-shard transaction from shard A to an account on shard B in epoch N. This generates an outgoing receipt from A to B, committed in A's chunk with `prev_outgoing_receipts_root` covering `hash(ReceiptList(B, [receipt_r]))`.
3. At the first block of epoch N+1, the chunk producer for B_left builds a chunk state witness. `collect_source_receipt_proofs` calls `get_incoming_receipts_for_shard` for B_left, crosses the epoch boundary, maps B_left → B, retrieves the stored `ReceiptProof(receipts=[receipt_r], ShardProof{to_shard_id=B, proof=π})`.
4. `validate_source_receipt_proofs` calls `validate_receipt_proof` with `current_target_shard_id = B_left`. The proof π was computed over `hash(ReceiptList(B, [receipt_r]))` but is now being verified for `to_shard_id = B_left`, causing a hash mismatch and returning `Error::InvalidChunkStateWitness`.
5. All chunk validators reject the witness. B_left produces no endorsed chunk. The block at that height contains a missing chunk for B_left (and similarly B_right). The network cannot finalize chunks for child shards at the resharding boundary. [3](#0-2) [6](#0-5) [7](#0-6)

### Citations

**File:** chain/chain/src/stateless_validation/state_witness.rs (L257-263)
```rust
    /// State witness proves the execution of receipts proposed by `prev_chunk`.
    /// This function collects all incoming receipts for `prev_chunk`, along with the proofs
    /// that those receipts really originate from the right chunks.
    /// TODO(resharding): `get_incoming_receipts_for_shard` generates invalid proofs on resharding
    /// boundaries, because it removes the receipts that target the other half of a split shard,
    /// which makes the proof invalid. We need to collect the original proof and later, after verification,
    /// filter it to remove the receipts that were meant for the other half of the split shard.
```

**File:** chain/chain/src/stateless_validation/chunk_validation.rs (L477-515)
```rust
    for block in receipt_source_blocks {
        // Collect all receipts coming from this block.
        let mut block_receipt_proofs = Vec::new();

        for chunk in block.chunks().iter_new() {
            // Collect receipts coming from this chunk and validate that they are correct.
            let Some(receipt_proof) = source_receipt_proofs.get(&chunk.chunk_hash()) else {
                return Err(Error::InvalidChunkStateWitness(format!(
                    "Missing source receipt proof for chunk {:?}",
                    chunk.chunk_hash()
                )));
            };

            validate_receipt_proof(
                receipt_proof,
                chunk,
                current_target_shard_id,
                *chunk.prev_outgoing_receipts_root(),
            )?;

            expected_proofs_len += 1;
            block_receipt_proofs.push(receipt_proof.clone());
        }

        block_receipt_proofs = filter_incoming_receipts_for_shard(
            &target_shard_layout,
            target_chunk_shard_id,
            Arc::new(block_receipt_proofs),
        )?;

        // Arrange the receipts in the order in which they should be applied.
        shuffle_receipt_proofs(&mut block_receipt_proofs, get_receipts_shuffle_salt(block));
        for proof in block_receipt_proofs {
            receipts_to_apply.extend(proof.0.iter().cloned());
        }

        current_target_shard_id = epoch_manager
            .get_prev_shard_id_from_prev_hash(block.header().prev_hash(), current_target_shard_id)?
            .1;
```

**File:** chain/chain/src/store/utils.rs (L186-272)
```rust
pub fn get_incoming_receipts_for_shard(
    chain_store: &ChainStoreAdapter,
    epoch_manager: &dyn EpochManagerAdapter,
    target_shard_id: ShardId,
    target_shard_layout: &ShardLayout,
    block_hash: CryptoHash,
    last_chunk_height_included: BlockHeight,
    receipts_filter: ReceiptFilter,
) -> Result<Vec<ReceiptProofResponse>, Error> {
    let _span =
            tracing::debug_span!(target: "chain", "get_incoming_receipts_for_shard", ?target_shard_id, ?block_hash, last_chunk_height_included).entered();

    let mut ret = vec![];

    let mut current_shard_id = target_shard_id;
    let mut current_block_hash = block_hash;
    let mut current_shard_layout = target_shard_layout.clone();

    loop {
        let header = chain_store.get_block_header(&current_block_hash)?;

        if header.height() < last_chunk_height_included {
            panic!("get_incoming_receipts_for_shard failed");
        }

        if header.height() == last_chunk_height_included {
            break;
        }

        let prev_hash = header.prev_hash();
        let prev_shard_layout = epoch_manager.get_shard_layout_from_prev_block(prev_hash)?;

        if prev_shard_layout != current_shard_layout {
            let parent_shard_id = current_shard_layout.get_parent_shard_id(current_shard_id)?;
            tracing::info!(
                target: "chain",
                version = current_shard_layout.version(),
                prev_version = prev_shard_layout.version(),
                ?current_shard_id,
                ?parent_shard_id,
                "crossing epoch boundary with shard layout change, updating shard id"
            );
            current_shard_id = parent_shard_id;
            current_shard_layout = prev_shard_layout;
        }

        let maybe_receipts_proofs =
            chain_store.get_incoming_receipts(&current_block_hash, current_shard_id);
        let receipts_proofs = match maybe_receipts_proofs {
            Ok(receipts_proofs) => {
                tracing::debug!(
                    target: "chain",
                    "found receipts from block with missing chunks",
                );
                receipts_proofs
            }
            Err(err) => {
                tracing::debug!(
                    target: "chain",
                    ?err,
                    "could not find receipts from block with missing chunks"
                );

                // This can happen when all chunks are missing in a block
                // and then we can safely assume that there aren't any
                // incoming receipts. It would be nicer to explicitly check
                // that condition rather than relying on errors when reading
                // from the db.
                Arc::new(vec![])
            }
        };

        let filtered_receipt_proofs = match receipts_filter {
            ReceiptFilter::All => receipts_proofs,
            ReceiptFilter::TargetShard => Arc::new(filter_incoming_receipts_for_shard(
                &target_shard_layout,
                target_shard_id,
                receipts_proofs,
            )?),
        };

        ret.push(ReceiptProofResponse(current_block_hash, filtered_receipt_proofs));
        current_block_hash = *prev_hash;
    }

    Ok(ret)
}
```
