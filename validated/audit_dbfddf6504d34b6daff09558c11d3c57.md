### Title
`FecSetRoot` merkle-proof leaf is not bound to its claimed index/count, allowing the same leaf to validate at multiple tree positions - ([File: core/src/repair/serve_repair.rs])

### Summary
`BlockIdRepairType::verify_response` uses `merkle_tree::verify_merkle_proof` (a `get_merkle_root`-style fold over a flattened proof) to validate double-Merkle repair responses against the peer-reported `block_id`. For the `ParentAndFecSetCount` variant, the leaf hash explicitly binds `fec_set_count` into the leaf (`hashv(&[parent_slot, parent_block_id, fec_set_count])`), and the repo's own regression test `test_verify_fec_set_count_non_malleable` [1](#0-0)  demonstrates why that binding is necessary: because `MerkleTree::try_new_with_len`/`make_merkle_proof` duplicate the last node when a tree level has an odd width [2](#0-1) [3](#0-2) , the same leaf value is provably valid at both index `N` and index `N+1` in the padded tree. For `FecSetRoot`, however, the leaf that is verified is simply `*fec_set_root` — the raw hash reported by the peer, with no binding of `fec_set_index`/`leaf_index` into the hash [4](#0-3) .

### Finding Description
`verify_merkle_proof`/`get_merkle_root` reconstruct the root purely from the supplied `index` parity bits and proof entries, and only ever check that `index` reduces to `0` after folding — they never independently confirm that `index` is less than the real number of leaves that existed when the tree was built [5](#0-4) . This matches the general bug class in the external report: nothing constrains `_index`/`leaf_index` relative to proof length beyond making the fold terminate at zero.

Because `MerkleTree::try_new_with_len` pads odd-width levels by duplicating the last node with itself (`other = &nodes[(index + 1).min(offset + size - 1)]`) rather than rejecting/requiring a strict power-of-two width [2](#0-1) , the last real leaf of the tree is provably identical whether you present index `N-1` or the synthetic padding index `N` — `join_nodes(node, other)` is commutative when `node == other`, so the swap in operand order caused by the differing index parity produces the same hash, and every higher level shares the same `>>=1` trajectory. This is exactly the “same leaf, multiple valid indices” bug class described in the report, just triggered by odd-leaf-count padding instead of proof-length/index mismatch.

For `BlockIdRepairType::FecSetRoot`, the verified leaf (`*fec_set_root`) carries no binding to `fec_set_index`/`leaf_index`, so if the FEC-set-root sub-tree ever contains such a duplicated boundary leaf, a peer can present a legitimate proof for one `fec_set_index` while claiming an adjacent (unbacked) `fec_set_index`, and `verify_merkle_proof` will accept it [6](#0-5) . Contrast this with `ParentAndFecSetCount`, where the developers explicitly hashed `fec_set_count` into the leaf specifically to close this hole [7](#0-6) , proving the team is aware of and treats this as a real vulnerability class for this exact code path, but the mitigation was only applied to one of the two verified variants.

### Impact Explanation
If exploitable, this lets a malicious/faulty repair peer answer a `FecSetRoot` repair request for `fec_set_index = X` with a merkle proof/root that is truly for a different `fec_set_index`, while still passing `verify_response`. The requester (`BlockIdRepairService::process_block_id_repair_response`) then trusts `fec_set_root` as the correct Merkle root for the requested FEC set and issues follow-on `ShredForBlockId` repair requests using that (wrong) root/index mapping [8](#0-7) , corrupting the shred-verification pivot for an entire FEC set and risking acceptance of shreds under a root that does not actually correspond to the on-chain committed slot content — an undeclared-state/validation-bypass condition in the block-repair pipeline that other validators do not necessarily share (cross-node divergence in what shreds each node considers validly signed for that FEC set).

### Likelihood Explanation
This requires the double-Merkle tree for a slot to actually exhibit the odd-width duplication (fec_set_count/leaf composition dependent), and requires a byzantine or bugged repair peer intentionally constructing/re-using a proof at a mismatched index — this is not something an ordinary unprivileged client triggers by accident and needs a specific tree shape plus an adversarial response. I could not fully confirm from the available index whether `fec_set_index` bounds are cross-checked elsewhere (e.g., against a previously verified/cached `fec_set_count` before this response is trusted), which would materially reduce/eliminate exploitability; this could not be fully traced within the provided context.

### Recommendation
Bind `fec_set_index`/`leaf_index` (and ideally `block_id`/slot context) into the `FecSetRoot` leaf hash the same way it was done for `ParentAndFecSetCount`, e.g. verify `hashv(&[fec_set_index.to_le_bytes(), fec_set_root.as_ref()])` against the proof instead of the bare `*fec_set_root`, and/or enforce `leaf_index < fec_set_count` (with a verified/agreed `fec_set_count`) before accepting the proof.

### Proof of Concept
Conceptually mirrors the existing repo test `test_verify_fec_set_count_non_malleable` [1](#0-0) : build a tree whose FEC-set-root leaf level has odd width so the last `fec_set_root` leaf is self-duplicated by `try_new_with_len`; obtain the honest proof for the real `fec_set_index`; call `BlockIdRepairType::FecSetRoot{ .. }.verify_response` with the *same* `fec_set_proof`/`fec_set_root` but an incremented `fec_set_index` that maps to the padding position — because the `FecSetRoot` leaf is not bound to `fec_set_index` (unlike `parent_info_leaf`), `verify_merkle_proof` returns `Ok(())` for both indices.

### Citations

**File:** core/src/repair/serve_repair.rs (L313-324)
```rust
                let parent_info_leaf = hashv(&[
                    &parent_slot.to_le_bytes(),
                    parent_block_id.as_ref(),
                    &fec_set_count.to_le_bytes(),
                ]);
                merkle_tree::verify_merkle_proof(
                    parent_info_leaf,
                    *fec_set_count as usize,
                    parent_proof,
                    *block_id,
                )
                .is_ok()
```

**File:** core/src/repair/serve_repair.rs (L327-353)
```rust
            (
                Self::FecSetRoot {
                    slot: _slot,
                    block_id,
                    fec_set_index,
                },
                Self::Response::FecSetRoot {
                    fec_set_root,
                    fec_set_proof,
                },
            ) => {
                // The double-Merkle tree contains at least one FEC-set root and
                // the parent-info leaf, so a valid proof cannot be empty.
                if fec_set_proof.is_empty() {
                    return false;
                }
                debug_assert_eq!(*fec_set_index as usize % DATA_SHREDS_PER_FEC_BLOCK, 0);
                // Convert from shred-space to leaf-index
                let leaf_index = *fec_set_index as usize / DATA_SHREDS_PER_FEC_BLOCK;
                merkle_tree::verify_merkle_proof(
                    *fec_set_root,
                    leaf_index,
                    fec_set_proof,
                    *block_id,
                )
                .is_ok()
            }
```

**File:** core/src/repair/serve_repair.rs (L3258-3304)
```rust
    #[test]
    fn test_verify_fec_set_count_non_malleable() {
        let parent_slot = 99u64;
        let parent_block_id = Hash::new_unique();
        let fec_set_count: u32 = 2; // even => total leaves = 3, last leaf duplicated
        let fec_set_roots: Vec<Hash> = (0..fec_set_count).map(|_| Hash::new_unique()).collect();
        let real_parent_leaf = hashv(&[
            &parent_slot.to_le_bytes(),
            parent_block_id.as_ref(),
            &fec_set_count.to_le_bytes(),
        ]);
        let mut leaves: Vec<Hash> = fec_set_roots;
        leaves.push(real_parent_leaf);
        let tree =
            merkle_tree::MerkleTree::try_new_with_len(leaves.iter().copied().map(Ok), leaves.len())
                .unwrap();
        let block_id = *tree.root();
        let real_parent_proof: Vec<u8> = tree
            .make_merkle_proof(fec_set_count as usize, leaves.len())
            .flat_map(|entry| entry.unwrap().iter().copied())
            .collect();

        let request = BlockIdRepairType::ParentAndFecSetCount {
            slot: 100,
            block_id,
        };

        // honest response verifies
        assert!(
            request.verify_response(&BlockIdRepairResponse::ParentFecSetCount {
                fec_set_count,
                parent_info: (parent_slot, parent_block_id),
                parent_proof: real_parent_proof.clone(),
            })
        );

        // Attack: claim N+1 and reuse the honest proof. The padded tree puts
        // `real_parent_leaf` at both positions N and N+1, so without binding
        // `fec_set_count` into the leaf this proof would verify.
        assert!(
            !request.verify_response(&BlockIdRepairResponse::ParentFecSetCount {
                fec_set_count: fec_set_count + 1,
                parent_info: (parent_slot, parent_block_id),
                parent_proof: real_parent_proof.clone(),
            })
        );
    }
```

**File:** ledger/src/shred/merkle_tree.rs (L56-65)
```rust
        let init = (len > 1).then_some(len);
        for size in successors(init, |&k| (k > 2).then_some((k + 1) >> 1)) {
            let offset = nodes.len() - size;
            for index in (offset..offset + size).step_by(2) {
                let node = &nodes[index];
                let other = &nodes[(index + 1).min(offset + size - 1)];
                let parent = join_nodes(node, other);
                nodes.push(parent);
            }
        }
```

**File:** ledger/src/shred/merkle_tree.rs (L82-90)
```rust
        if index >= size {
            // Force below iterator to return Error.
            (size, offset) = (0, self.nodes.len());
        }
        std::iter::from_fn(move || {
            if size > 1 {
                let Some(node) = self.nodes.get(offset + (index ^ 1).min(size - 1)) else {
                    return Some(Err(Error::InvalidMerkleProof));
                };
```

**File:** ledger/src/shred/merkle_tree.rs (L115-152)
```rust
pub fn get_merkle_root<'a, I>(index: usize, node: Hash, proof: I) -> Result<Hash, Error>
where
    I: IntoIterator<Item = &'a MerkleProofEntry>,
{
    let (index, root) = proof
        .into_iter()
        .fold((index, node), |(index, node), other| {
            let parent = if index % 2 == 0 {
                join_nodes(node, other)
            } else {
                join_nodes(other, node)
            };
            (index >> 1, parent)
        });
    (index == 0)
        .then_some(root)
        .ok_or(Error::InvalidMerkleProof)
}

/// Given a flattened merkle `proof` for `node` at `index`,
/// verify the proof against merkle root `root`
pub fn verify_merkle_proof(
    node: Hash,
    index: usize,
    proof: &[u8],
    expected_root: Hash,
) -> Result<(), Error> {
    let proof = proof
        .chunks(SIZE_OF_MERKLE_PROOF_ENTRY)
        .map(<&MerkleProofEntry>::try_from)
        .map(|entry| entry.map_err(|_| Error::InvalidMerkleProof))
        .collect::<Result<Vec<_>, Error>>()?;
    let merkle_root = get_merkle_root(index, node, proof)?;

    (merkle_root == expected_root)
        .then_some(())
        .ok_or(Error::InvalidMerkleProof)
}
```

**File:** core/src/repair/block_id_repair_service.rs (L1516-1541)
```rust
        // Verify: ShredForBlockId requests were added to pending (one for each shred in FEC set)
        assert_eq!(
            state.pending_repair_requests.len(),
            DATA_SHREDS_PER_FEC_BLOCK
        );

        // Verify the shred requests have correct parameters
        while let Some(req) = state.pending_repair_requests.pop() {
            match req {
                OutgoingMessage::Shred(ShredRepairType::ShredForBlockId {
                    slot: s,
                    index,
                    fec_set_merkle_root,
                    block_id: b,
                }) => {
                    assert_eq!(s, slot);
                    assert!(
                        index >= fec_set_index
                            && index < fec_set_index + DATA_SHREDS_PER_FEC_BLOCK as u32
                    );
                    assert_eq!(fec_set_merkle_root, fec_set_root);
                    assert_eq!(b, block_id);
                }
                _ => panic!("Expected ShredForBlockId request"),
            }
        }
```
