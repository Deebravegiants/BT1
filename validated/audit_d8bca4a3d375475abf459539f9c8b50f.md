### Title
`ExtrinsicWeightReclaimed` leaks across extrinsics, causing the previous extrinsic's reclaimed weight to be re-added into `BlockWeight` when processing the next extrinsic - (File: cumulus/pallets/weight-reclaim/src/lib.rs)

### Summary
`frame_system::ExtrinsicWeightReclaimed` is a single, non-keyed `StorageValue` that `StorageWeightReclaim::post_dispatch_details` writes at the end of every extrinsic and reads at the start of the *next* extrinsic's inner `CheckWeight` reclaim step. Because this value is never reset between extrinsics, the previous extrinsic's already-finalized "unspent"/reclaimed weight gets re-injected (`current_weight.accrue(already_reclaimed, ...)`) into `BlockWeight` while processing the following extrinsic, permanently inflating `BlockWeight` for the rest of the block.

### Finding Description
`StorageWeightReclaim::post_dispatch_details` [1](#0-0)  performs a telescoping correction pattern on `BlockWeight`:

```
already_reclaimed = ExtrinsicWeightReclaimed::get();
current_weight.accrue(already_reclaimed, info.class);
current_weight.reduce(info.total_weight(), info.class);
current_weight.accrue(accurate_weight, info.class);
...
ExtrinsicWeightReclaimed::put(accurate_unspent);
```

This is designed so the *outer* extension (`StorageWeightReclaim`) can

### Citations

**File:** cumulus/pallets/weight-reclaim/src/lib.rs (L235-262)
```rust
		let pov_size_missing_from_node = frame_system::BlockWeight::<T>::mutate(|current_weight| {
			let already_reclaimed = frame_system::ExtrinsicWeightReclaimed::<T>::get();
			current_weight.accrue(already_reclaimed, info.class);
			current_weight.reduce(info.total_weight(), info.class);
			current_weight.accrue(accurate_weight, info.class);

			// If we encounter a situation where the node-side proof size is already higher than
			// what we have in the runtime bookkeeping, we add the difference to the `BlockWeight`.
			// This prevents that the proof size grows faster than the runtime proof size.
			let block_size = frame_system::BlockSize::<T>::get().unwrap_or(0);
			let node_side_pov_size = proof_size_after_dispatch.saturating_add(block_size.into());
			let block_weight_proof_size = current_weight.total().proof_size();
			let pov_size_missing_from_node =
				node_side_pov_size.saturating_sub(block_weight_proof_size);
			if pov_size_missing_from_node > 0 {
				log::warn!(
					target: LOG_TARGET,
					"Node-side PoV size higher than runtime proof size weight. node-side: \
					{node_side_pov_size} block_size: {block_size} runtime: \
					{block_weight_proof_size}, missing: {pov_size_missing_from_node}. Setting to \
					node-side proof size."
				);
				current_weight
					.accrue(Weight::from_parts(0, pov_size_missing_from_node), info.class);
			}

			pov_size_missing_from_node
		});
```
