Based on the code, this exact check already exists and directly prevents the described attack.

## Analysis

`verify_blocks_form_chain` in `cumulus/pallets/parachain-system/src/validate_block/implementation.rs` is called **before** any block execution occurs, at line 172 of `validate_block`, using the fixed `num_blocks = blocks.len()` computed from the actual bundle. [1](#0-0) 

Inside the `fold` loop over all blocks, for every block that has a `BlockBundleInfo` digest, the code explicitly asserts:

- If `block_index + 1 < num_blocks` (i.e., **not** the last block), it panics if `is_last_block_in_core` is `true`. [2](#0-1) 
- If `block_index + 1 == num_blocks` (the actual last block), it panics if `is_last_block_in_core` is **not** set (unless bundle info is absent). [3](#0-2) 

Applying this directly to the scenario in the question — a 3-block bundle where block at index 0 carries `is_last_block_in_core = true` while blocks 1 and 2 follow — `block_index = 0`, `num_blocks = 3`, so `block_index + 1 < num_blocks` (`1 < 3`) is true, and the assertion at line 465-469 fires and panics, rejecting the entire block bundle before any execution/weight accounting happens. There is no race in the ordering: `num_blocks` is fixed once from `blocks.len()` at line 409, and the `fold` iterates deterministically in order, so this invariant is enforced identically and consistently for every block in the bundle, not dependent on any interleaving. [4](#0-3) 

Furthermore, block-weight accounting (`MaxParachainBlockWeight`/`FULL_CORE_WEIGHT`) is applied per-block during runtime execution using each block's own header digest (`CoreInfo`, `BlockBundleInfo`), and this execution only happens in the loop starting at line 229 — strictly *after* `verify_blocks_form_chain` has already validated bundle consistency. So a malformed bundle that violates the digest invariant never reaches the weight-accounting/execution stage at all. [5](#0-4) [6](#0-5) 

This is also covered by existing tests validating bundle-info/full-core interactions in `cumulus/pallets/parachain-system/src/validate_block/tests.rs`. [7](#0-6) 

#No vulnerability found for this question.

### Citations

**File:** cumulus/pallets/parachain-system/src/validate_block/implementation.rs (L170-181)
```rust
	let (blocks, proof) = block_data.into_inner();

	verify_blocks_form_chain::<B>(&blocks, &parent_header);

	let mut processed_downward_messages = 0;
	let mut upward_messages = BoundedVec::default();
	let mut upward_message_signals = Vec::<Vec<_>>::new();
	let mut horizontal_messages = BoundedVec::default();
	let mut hrmp_watermark = Default::default();
	let mut head_data = None;
	let mut new_validation_code = None;
	let num_blocks = blocks.len();
```

**File:** cumulus/pallets/parachain-system/src/validate_block/implementation.rs (L229-284)
```rust
	for (block_index, mut block) in blocks.into_iter().enumerate() {
		// We use the storage root of the `parent_head` to ensure that it is the correct root.
		// This is already being done above while creating the in-memory db, but let's be paranoid!!
		let backend = sp_state_machine::TrieBackendBuilder::new_with_cache(
			&db,
			*parent_header.state_root(),
			&cache_provider,
		)
		.build();

		// Each node only contributes once to the total size of the storage proof. So, we keep track
		// of them inside `seen_nodes` to always return the correct proof size.
		let mut execute_recorder = SizeOnlyRecorderProvider::with_seen_nodes(seen_nodes.clone());
		// `backend` with the `execute_recorder`. As the `execute_recorder`, this should only be
		// used for `execute_block`.
		let execute_backend = sp_state_machine::TrieBackendBuilder::wrap(&backend)
			.with_recorder(execute_recorder.clone())
			.build();

		let mut overlay = OverlayedChanges::default();

		parent_header = block.header().clone();

		run_with_externalities_and_recorder::<B, _, _>(
			&backend,
			&mut Default::default(),
			&mut Default::default(),
			|| {
				E::verify_and_remove_seal(&mut block);
			},
		);

		run_with_externalities_and_recorder::<B, _, _>(
			&execute_backend,
			// Here is the only place where we want to use the recorder.
			// We want to ensure that we not accidentally read something from the proof, that
			// was not yet read and thus, alter the proof size. Otherwise, we end up with
			// mismatches in later blocks.
			&mut execute_recorder,
			&mut overlay,
			|| {
				E::execute_verified_block(block);
			},
		);

		let code_upgrade_detected =
			if <PSC as frame_system::Config>::Version::get().system_version >= 3 {
				overlay.storage(well_known_keys::PENDING_CODE).is_some()
			} else {
				overlay.storage(well_known_keys::CODE).is_some()
			};
		if code_upgrade_detected && num_blocks > 1 {
			panic!(
				"When applying a runtime upgrade, only one block per PoV is allowed. Received {num_blocks}."
			)
		}
```

**File:** cumulus/pallets/parachain-system/src/validate_block/implementation.rs (L408-482)
```rust
fn verify_blocks_form_chain<B: BlockT>(blocks: &[B::LazyBlock], parent_header: &B::Header) {
	let num_blocks = blocks.len();

	// Check first block's parent matches the given parent_header
	assert_eq!(
		*blocks
			.first()
			.expect("BlockData should have at least one block")
			.header()
			.parent_hash(),
		parent_header.hash(),
		"Parachain head needs to be the parent of the first block"
	);

	let mut first_block_has_bundle_info: Option<bool> = None;

	blocks.iter().enumerate().fold(
		parent_header.hash(),
		|expected_parent, (block_index, block)| {
			// Check chain validity
			assert_eq!(
				expected_parent,
				*block.header().parent_hash(),
				"Not a valid chain of blocks :(; {:?} not a parent of {:?}?",
				array_bytes::bytes2hex("0x", expected_parent.as_ref()),
				array_bytes::bytes2hex("0x", block.header().parent_hash().as_ref()),
			);

			let encoded_header_size = block.header().encoded_size();
			assert!(
				encoded_header_size <= MAX_HEAD_DATA_SIZE as usize,
				"Header size {encoded_header_size} exceeds MAX_HEAD_DATA_SIZE {MAX_HEAD_DATA_SIZE}",
			);

			// Validate BlockBundleInfo consistency
			let bundle_info = CumulusDigestItem::find_block_bundle_info(block.header().digest());
			match (first_block_has_bundle_info, &bundle_info) {
				(None, info) => {
					first_block_has_bundle_info = Some(info.is_some());
				},
				(Some(true), None) => {
					panic!("All blocks in a bundled PoV must include `BlockBundleInfo`");
				},
				(Some(false), _) => {
					panic!("A PoV without `BlockBundleInfo` may only contain a single block");
				},
				_ => {},
			}

			if let Some(ref info) = bundle_info {
				assert_eq!(
					info.index as usize, block_index,
					"BlockBundleInfo index mismatch: expected {block_index}, got {}",
					info.index
				);

				if block_index + 1 < num_blocks {
					assert!(
						!CumulusDigestItem::is_last_block_in_core(block.header().digest()).unwrap_or(false),
						"Intermediate block at index {block_index} is marked as last block in core, \
						but more blocks follow in the PoV",
					);
				} else if !CumulusDigestItem::is_last_block_in_core(block.header().digest())
					.unwrap_or(true)
				{
					panic!(
						"Last block in PoV must include the digest that marks it as the last block in the core"
					);
				}
			}

			block.header().hash()
		},
	);
}
```

**File:** cumulus/pallets/parachain-system/src/block_weight/mod.rs (L294-316)
```rust
/// Is this the first block in a core?
fn is_first_block_in_core<T: Config>() -> Option<bool> {
	let digest = frame_system::Pallet::<T>::digest();
	is_first_block_in_core_with_digest(&digest)
}

/// Is this the first block in a core? (takes digest as parameter)
///
/// Returns `None` if the [`CumulusDigestItem::BlockBundleInfo`] digest is not set.
fn is_first_block_in_core_with_digest(digest: &Digest) -> Option<bool> {
	CumulusDigestItem::find_block_bundle_info(digest).map(|bi| bi.index == 0)
}

/// Is the `BlockWeight` already above the target block weight?
///
/// Returns `None` if the [`CumulusDigestItem::BlockBundleInfo`] digest is not set.
fn block_weight_over_target_block_weight<T: Config, TargetBlockRate: Get<u32>>() -> bool {
	let target_block_weight = MaxParachainBlockWeight::<T, TargetBlockRate>::target_block_weight();

	frame_system::Pallet::<T>::remaining_block_weight()
		.consumed()
		.any_gt(target_block_weight)
}
```

**File:** cumulus/pallets/parachain-system/src/validate_block/tests.rs (L944-969)
```rust
#[test]
fn validate_block_accepts_single_block_with_use_full_core() {
	sp_tracing::try_init_simple();

	let (client, parent_head) = create_elastic_scaling_test_client();

	// Build a single block with BlockBundleInfo (is_last=false) and UseFullCore set via
	// extrinsic UseFullCore should make validation succeed even without is_last=true
	let TestBlockData { block, validation_data } = build_block_with_witness(
		&client,
		vec![generate_extrinsic(&client, Alice, TestPalletCall::set_use_full_core {})],
		parent_head.clone(),
		Default::default(),
		vec![BlockBundleInfo { index: 0, is_last: false }.to_digest_item()],
	);

	// Validation should succeed because UseFullCore marks it as last block
	let header = block.blocks()[0].header().clone();
	let res_header = call_validate_block_elastic_scaling(
		parent_head,
		block,
		validation_data.relay_parent_storage_root,
	)
	.expect("Calls `validate_block`");
	assert_eq!(header, res_header);
}
```
