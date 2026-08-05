#No
Vulnerability found for this question.

The code in `cumulus/pallets/weight-reclaim/src/lib.rs` `StorageWeightReclaim::post_dispatch_details` (and the equivalent legacy implementation in `cumulus/primitives/storage-weight-reclaim/src/lib.rs`) already explicitly defends against the exact scenario described. After computing `accurate_weight` from the host-measured `measured_proof_size` (not the possibly-underestimated benchmark), the `frame_system::BlockWeight::<T>::mutate` closure additionally computes `node_side_pov_size` (the real node-measured proof size plus block size) and compares it against `current_weight.total().proof_size()`. If the runtime-side bookkeeping is still lower than the true node-side PoV (`pov_size_missing_from_node > 0`), it tops up `current_weight` with the difference via `current_weight.accrue(Weight::from_parts(0, pov_size_missing_from_node), info.class)`. [1](#0-0) 

This is precisely the invariant-enforcing mechanism the question asks about — it guarantees `current_weight.total().proof_size() >= node_side_pov_size` after `post_dispatch_details` runs, which is confirmed by the dedicated test `sets_to_node_storage_proof_if_higher` that asserts the block weight is corrected upward to match the node-side proof size when the benchmark underestimates it. [2](#0-1) 

Since accrual happens per extrinsic before the next extrinsic's `CheckWeight` pre-dispatch validation runs (and before the block author includes further extrinsics), any under-benchmarking discrepancy is folded into `BlockWeight` immediately, preventing an attacker from causing bookkeeping to permanently under-account real PoV within the block. There is no reachable path for a normal signed user to bypass this reconciliation step through ordinary extrinsic submission, since `post_dispatch_details` is unconditionally invoked by the transaction extension pipeline for every dispatched extrinsic using this extension. No missing check, bad accounting, or logic error was found that would violate the stated invariant.

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

**File:** cumulus/primitives/storage-weight-reclaim/src/tests.rs (L153-196)
```rust
#[test]
#[allow(deprecated)]
fn sets_to_node_storage_proof_if_higher() {
	// The storage proof reported by the proof recorder is higher than what is stored on
	// the runtime side.
	{
		let mut test_ext = setup_test_externalities(&[1000, 1005]);

		test_ext.execute_with(|| {
			// Stored in BlockWeight is 5
			set_current_storage_weight(5);

			// Benchmarked storage weight: 10
			let info =
				DispatchInfo { call_weight: Weight::from_parts(0, 10), ..Default::default() };
			let post_info = PostDispatchInfo::default();

			let (_, next_len) = CheckWeight::<Test>::do_validate(&info, LEN).unwrap();
			assert_ok!(CheckWeight::<Test>::do_prepare(&info, LEN, next_len));

			let (pre, _) = StorageWeightReclaim::<Test>(PhantomData)
				.validate_and_prepare(Some(ALICE.clone()).into(), CALL, &info, LEN, 0)
				.unwrap();
			assert_eq!(pre, Some(1000));

			assert_ok!(CheckWeight::<Test>::post_dispatch_details(
				(),
				&info,
				&post_info,
				0,
				&Ok(())
			));
			assert_ok!(StorageWeightReclaim::<Test>::post_dispatch_details(
				pre,
				&info,
				&post_info,
				LEN,
				&Ok(())
			));

			// We expect that the storage weight was set to the node-side proof size (1005) +
			// extrinsics length (150)
			assert_eq!(get_storage_weight().total().proof_size(), 1155);
		})
```
