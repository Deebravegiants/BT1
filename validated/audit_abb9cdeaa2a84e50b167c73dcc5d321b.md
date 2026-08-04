[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** cumulus/pallets/weight-reclaim/src/lib.rs (L219-262)
```rust
		if benchmarked_actual_proof_size < measured_proof_size {
			log::error!(
				target: LOG_TARGET,
				"Benchmarked storage weight smaller than consumed storage weight. \
				benchmarked: {benchmarked_actual_proof_size} consumed: {measured_proof_size}"
			);
		} else {
			log::trace!(
				target: LOG_TARGET,
				"Reclaiming storage weight. benchmarked: {benchmarked_actual_proof_size},
				consumed: {measured_proof_size}"
			);
		}

		let accurate_weight = benchmarked_actual_weight.set_proof_size(measured_proof_size);

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

**File:** cumulus/pallets/weight-reclaim/src/lib.rs (L264-271)
```rust
		// The saturation will happen if the pre-dispatch weight is underestimating the proof
		// size or if the node-side proof size is higher than expected.
		// In this case the extrinsic proof size weight reclaimed is 0 and not a negative reclaim.
		let accurate_unspent = info
			.total_weight()
			.saturating_sub(accurate_weight)
			.saturating_sub(Weight::from_parts(0, pov_size_missing_from_node));
		frame_system::ExtrinsicWeightReclaimed::<T>::put(accurate_unspent);
```
