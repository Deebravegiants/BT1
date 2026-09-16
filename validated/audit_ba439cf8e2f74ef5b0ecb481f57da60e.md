### Title
Non-atomic MMR leaf ingestion in `pallet-mmr::finalize` can persist a partially-updated MMR when a mid-batch leaf lookup fails - (File: modules/pallets/mmr/src/lib.rs)

### Summary
The Xen advisory describes P2M hypercalls that split a ranged operation into smaller chunks, where a failure partway through the chunked operation was not properly accounted for, leaving the memory-mapping state partially and inconsistently updated. The closest reachable analog in Hyperbridge is `Pallet::<T, I>::finalize()` in `modules/pallets/mmr/src/lib.rs`, which iterates over a *range* of buffered leaves and pushes each one individually into the on-chain MMR, persisting storage writes (`Nodes`, `NumberOfLeaves`) as it goes via the underlying `MMRStore::append` implementation, rather than atomically.

### Finding Description
`finalize()` computes `buffer_len` and iterates `0u64..buffer_len`, calling `mmr.push(leaf)` for each buffered leaf: [1](#0-0) 

Each `push` call inside the loop invokes the underlying `merkle_mountain_range::MMR::push`, which is backed by `Storage<RuntimeStorage, ...>::append` — this writes new peak hashes directly into the `Nodes` map and updates `NumberOfLeaves` immediately for every appended element, not only when the whole batch succeeds: [2](#0-1) 

If a later iteration in the loop fails — e.g. `IntermediateLeaves::<T, I>::get(index).ok_or(Error::Push)?` cannot find an expected buffered leaf at some index greater than 0 — the function returns `Err(Error::Push)` via `?` immediately: [3](#0-2) 

However, the storage writes already made by prior successful iterations of the same loop (calls to `Nodes::<T, I>::insert` and `NumberOfLeaves::<T, I>::put` performed inside `append` for the leaves processed *before* the failing index) are **not rolled back**. This mirrors the Xen bug class exactly: a ranged/chunked mutating operation is partially applied, and the error path does not account for or undo the partial progress that already landed in the durable store.

This function is not wrapped in `#[frame_support::transactional]`, and it runs from the block-finalization hook path (used by `pallet-ismp` to accumulate MMR leaves for request/response commitments), which is not itself an extrinsic-scoped transactional context that would auto-revert storage on error.

### Impact Explanation
If the MMR ever gets into a state where `IntermediateLeaves` and the expected `buffer_len` become desynchronized mid-loop (e.g. via a runtime upgrade race, a re-entrant/duplicate `push` call, or any code path that clears/mutates `IntermediateLeaves` between `push()` calls and `finalize()`), the on-chain `Nodes`/`NumberOfLeaves` storage would advance for the leaves before the failure point while `RootHash` is never updated (since the `mmr.finalize()`/root computation is not reached). This desynchronizes `NumberOfLeaves` (and the persisted peak nodes) from the actual committed root, corrupting the MMR's internal accounting. Because MMR proofs (`mmr_queryProof` and the `ProofKeys`-based membership checks used by relayers and `pallet-ismp` handlers) rely on `NumberOfLeaves`/`Nodes` being consistent with `RootHash`, this could make legitimate request/response commitment proofs unverifiable or, in a worse case, allow future leaf insertions to silently collide with/overwrite improperly-accounted positions — undermining the state-membership guarantees the whole ISMP message-delivery pipeline depends on.

### Likelihood Explanation
I was unable to fully verify within the available tool budget whether `IntermediateLeaves::get(index)` can actually miss an entry in normal execution given `push()` and `finalize()` semantics as implemented (the `push()`/`finalize()` calling pattern appears to keep `IntermediateLeaves` and `buffer_len` in sync in the code paths I inspected). The comment "MMR push should never fail" in the source itself and the defensive `Err(Error::Push)?` suggest the pallet authors also expected this to be effectively unreachable under normal operation. Without confirming a concrete trigger (e.g., a runtime upgrade, chain-fork replay, or bug in `IntermediateLeaves` population elsewhere) that could desynchronize the two, I cannot confirm this is currently exploitable from a single unprivileged transaction — it depends on an as-yet-unidentified precondition to actually decouple `buffer_len` from `IntermediateLeaves` contents.

### Recommendation
Given the uncertainty above, I recommend a Devin session investigate:
1. Whether `IntermediateLeaves::<T, I>::count()` and the `0..buffer_len` range can ever diverge from the actual keys present (e.g., due to non-contiguous keys, concurrent clearing, or upgrade migrations).
2. If any divergence is possible, wrap `finalize()`'s leaf-ingestion loop in a transactional storage layer (`with_transaction`/`#[frame_support::transactional]`) so that a mid-loop error rolls back all `Nodes`/`NumberOfLeaves` writes made in that call, restoring atomicity analogous to what should have applied to Xen's chunked P2M operations.

### Proof of Concept
I could not construct a concrete, reachable trigger for the `Err(Error::Push)` branch given the code paths inspected (this requires `IntermediateLeaves::get(index)` to return `None` for some `index < buffer_len`, which the normal `push`/`finalize` flow does not appear to allow). Confirming exploitability requires deeper analysis of all callers/mutators of `IntermediateLeaves` across pallet-ismp and any migrations, which was not completed within this investigation.

### Citations

**File:** modules/pallets/mmr/src/lib.rs (L239-254)
```rust
		// append new leaves to MMR
		let range = 0u64..buffer_len;
		for index in range {
			let leaf = IntermediateLeaves::<T, I>::get(index).ok_or(Error::Push)?;
			// Mmr push should never fail
			match mmr.push(leaf) {
				None => {
					log::error!(target: "pallet-mmr", "MMR push failed ");
					// MMR push never fails, but better safe than sorry.
					Err(Error::Push)?
				},
				Some(position) => {
					log::trace!(target: "pallet-mmr", "MMR push {position}");
				},
			}
		}
```

**File:** modules/pallets/mmr/src/mmr/storage.rs (L109-164)
```rust
	fn append(
		&mut self,
		pos: NodeIndex,
		elems: Vec<NodeOf<T, I, L>>,
	) -> merkle_mountain_range::Result<()> {
		if elems.is_empty() {
			return Ok(());
		}

		trace!(
			target: "pallet-mmr", "elems: {:?}",
			elems.iter().map(|elem| elem.hash()).collect::<Vec<_>>()
		);

		let leaves = NumberOfLeaves::<T, I>::get();
		let size = NodesUtils::new(leaves).size();

		if pos != size {
			return Err(merkle_mountain_range::Error::InconsistentStore);
		}

		let new_size = size + elems.len() as NodeIndex;

		// A sorted (ascending) iterator over peak indices to prune and persist.
		let (peaks_to_prune, mut peaks_to_store) = peaks_to_prune_and_store(size, new_size);

		// Now we are going to iterate over elements to insert
		// and keep track of the current `node_index` and `leaf_index`.
		let mut leaf_index = leaves;
		let mut node_index = size;

		// Use a uniquely generated hash for every block as an extra identifier
		// in offchain DB to avoid DB collisions and overwrites in case of forks.
		let fork_identifier = <T::ForkIdentifierProvider as ForkIdentifier<T>>::identifier();
		for elem in elems {
			// On-chain we are going to only store new peaks.
			if peaks_to_store.next_if_eq(&node_index).is_some() {
				Nodes::<T, I>::insert(node_index, elem.hash());
			}
			// We are storing full node off-chain (using indexing API).
			Self::store_to_offchain(node_index, fork_identifier, &elem);

			// Increase the indices.
			if let Node::Data(..) = elem {
				leaf_index += 1;
			}
			node_index += 1;
		}

		// Update current number of leaves.
		NumberOfLeaves::<T, I>::put(leaf_index);

		// And remove all remaining items from `peaks_before` collection.
		for pos in peaks_to_prune {
			Nodes::<T, I>::remove(pos);
		}
```
