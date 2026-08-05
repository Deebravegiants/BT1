### Title
Unbounded `parachains` vector in `submit_parachain_heads_ex` lets weight scale beyond the tiny benchmarked range - (File: bridges/modules/parachains/src/lib.rs)

### Summary
`submit_parachain_heads_ex` accepts an un-bounded `Vec<(ParaId, ParaHash)>` and charges pre-dispatch weight using a linear model (`submit_parachain_heads_with_n_parachains(p)`), but the benchmark that produces this linear coefficient only exercises `p` in the range `[1, 2]` (matching the tiny, fixed set of parachains configured for the actual bridge instance). There is no runtime check that rejects a `parachains` vector whose length exceeds the benchmarked/realistic range, so a caller can submit a call with a much larger `parachains.len()` than was ever benchmarked, extrapolating the charged weight from a two-point sample.

### Finding Description
The dispatchable is: [1](#0-0) 

and the weight formula: [2](#0-1) 

`submit_parachain_heads_with_n_parachains(p)` is benchmarked only for `p in 1..(T::parachains().len() + 1)`: [3](#0-2) 

and, as the generated weight files confirm, the actually-measured range on production runtimes is `[1, 2]`: [4](#0-3) [5](#0-4) 

The dispatch body itself loops over the caller-supplied `parachains` vector with no upper bound check on its length before doing any work: [6](#0-5) 

Each loop iteration performs a proof lookup (`storage.read_parachain_head`), a hash comparison, and (for entries whose head is present but stale/duplicate/untracked) a `ParasInfo::try_mutate` read-modify-write. None of these operations require the storage proof itself to grow (a caller can repeat the same `ParaId` many times, referencing the same already-proven leaf, without adding new trie nodes) — the `ensure_no_unused_keys()` check only forbids *unused* trie nodes, not duplicate/repeated use of an already-decoded key: [7](#0-6) 

Because `parachains: Vec<(ParaId, ParaHash)>` is a plain (unbounded) `Vec` rather than a `BoundedVec` capped at some `MaxParachains`, and the only real limit on its length is the runtime's maximum extrinsic/block length, an attacker can submit a call with a length far beyond `p=2` (the only values ever measured). The charged weight for such a call is a linear extrapolation from a 2-point benchmark, so there is no empirical basis for the correctness of the per-item weight coefficient at the input sizes actually reachable by an unprivileged submitter.

### Impact Explanation
If the per-entry weight coefficient learned from `p ∈ {1,2}` underestimates real per-entry cost at large `p` (e.g. due to storage-map access patterns, trie decoding overhead, or event-deposit costs not amortized the same way at scale), a submitter can craft a single valid, signed `submit_parachain_heads_ex` transaction whose *charged* weight fits comfortably within block limits while its *actual* execution time is substantially higher, risking block-production time overruns. This is the scoped "chain halt" class of impact (block time overrun / validator resource exhaustion via a publicly reachable, correctly-signed extrinsic), not an asset-theft or replay bug — no signature/origin/nonce checks are bypassed, and `ensure_signed` plus `ensure_not_halted` are correctly enforced.

### Likelihood Explanation
Preconditions are minimal: the attacker only needs a valid signed account, one legitimately generated/known `ParaHeadsProof` for at least one tracked parachain head at an already-imported relay block, and the ability to repeat that `(ParaId, ParaHash)` pair (or use nonexistent para IDs, which hit the cheap `MissingParachainHead` branch) many times in the `parachains` vector, up to the extrinsic/block length limit. This does not require any privileged role, relayer status, or malicious peer/node assumption — it is a normal, syntactically valid extrinsic. However, the actual severity depends on how far the true per-entry cost diverges from the benchmarked linear coefficient, which cannot be confirmed from static code reading alone; it requires empirical measurement (the "fast validation" step called for in the prompt).

### Recommendation
- Bound `parachains` with a `BoundedVec<(ParaId, ParaHash), T::MaxParachains>` (or an explicit `ensure!(parachains.len() <= T::MaxParachains::get())`) so the dispatch rejects vectors longer than what is actually benchmarked/supported.
- Extend the `submit_parachain_heads_with_n_parachains` benchmark to cover the full valid range up to the new `MaxParachains` bound (including duplicate-ParaId and untracked-ParaId degenerate shapes), not just `[1, T::parachains().len()]`, so the linear/extrapolated weight model has empirical support across the whole accepted range.

### Proof of Concept
Rust integration test plan (in `bridges/modules/parachains/src/lib.rs` test module or a dedicated benchmarking-diff test):
1. Build a `ParaHeadsProof` for a single tracked parachain `P` at relay block `RB` (as done in `prepare_parachain_heads_proof`).
2. Construct `parachains = vec![(P, head_hash); N]` for a large `N` (e.g., `N = 50_000`, within block length limits), all referencing the same already-included proof leaf.
3. Call `Pallet::submit_parachain_heads_ex(..., parachains, parachain_heads_proof, false)` and measure wall-clock execution time (or extension-level weight consumption via `frame_benchmarking`'s manual instrumentation) versus the weight returned by `submit_parachain_heads_weight(..., N)`.
4. Assert that measured execution time diverges from the linearly-extrapolated charged weight by more than an acceptable margin (e.g., >20%), demonstrating that the benchmarked `p ∈ {1,2}` sample does not generalize to realistic `N`.
5. Repeat with `parachains` containing `N` distinct but untracked `ParaId`s (hitting `UntrackedParachainRejected`) and again with `N` stale duplicates (hitting the `ParasInfo::try_mutate` failure path with refund) to confirm cost drift across the different degenerate branches identified in the loop body.

### Citations

**File:** bridges/modules/parachains/src/lib.rs (L410-422)
```rust
		#[pallet::call_index(3)]
		#[pallet::weight(WeightInfoOf::<T, I>::submit_parachain_heads_weight(
			T::DbWeight::get(),
			parachain_heads_proof,
			parachains.len() as _,
		))]
		pub fn submit_parachain_heads_ex(
			origin: OriginFor<T>,
			at_relay_block: (RelayBlockNumber, RelayBlockHash),
			parachains: Vec<(ParaId, ParaHash)>,
			parachain_heads_proof: ParaHeadsProof,
			_is_free_execution_expected: bool,
		) -> DispatchResultWithPostInfo {
```

**File:** bridges/modules/parachains/src/lib.rs (L426-461)
```rust
			let total_parachains = parachains.len();
			let free_headers_interval =
				T::FreeHeadersInterval::get().unwrap_or(RelayBlockNumber::MAX);
			// the pallet allows two kind of free submissions
			// 1) if distance between all parachain heads is gte than the [`T::FreeHeadersInterval`]
			// 2) if all heads are the first heads of their parachains
			let mut free_parachain_heads = 0;

			// we'll need relay chain header to verify that parachains heads are always increasing.
			let (relay_block_number, relay_block_hash) = at_relay_block;
			let relay_block = pallet_bridge_grandpa::ImportedHeaders::<
				T,
				T::BridgesGrandpaPalletInstance,
			>::get(relay_block_hash)
			.ok_or(Error::<T, I>::UnknownRelayChainBlock)?;
			ensure!(
				relay_block.number == relay_block_number,
				Error::<T, I>::InvalidRelayChainBlockNumber,
			);

			// now parse storage proof and read parachain heads
			let mut actual_weight = WeightInfoOf::<T, I>::submit_parachain_heads_weight(
				T::DbWeight::get(),
				&parachain_heads_proof,
				parachains.len() as _,
			);

			let mut storage: ParachainsStorageProofAdapter<T, I> =
				ParachainsStorageProofAdapter::try_new_with_verified_storage_proof(
					relay_block_hash,
					parachain_heads_proof.storage_proof,
				)
				.map_err(Error::<T, I>::HeaderChainStorageProof)?;

			for (parachain, parachain_head_hash) in parachains {
				let parachain_head = match storage.read_parachain_head(parachain) {
```

**File:** bridges/modules/parachains/src/lib.rs (L573-580)
```rust
			// even though we may have accepted some parachain heads, we can't allow relayers to
			// submit proof with unused trie nodes
			// => treat this as an error
			//
			// (we can throw error here, because now all our calls are transactional)
			storage.ensure_no_unused_keys().map_err(|e| {
				Error::<T, I>::HeaderChainStorageProof(HeaderChainError::StorageProof(e))
			})?;
```

**File:** bridges/modules/parachains/src/weights_ext.rs (L59-86)
```rust
	/// Weight of the parachain heads delivery extrinsic.
	fn submit_parachain_heads_weight(
		db_weight: RuntimeDbWeight,
		proof: &impl Size,
		parachains_count: u32,
	) -> Weight {
		// weight of the `submit_parachain_heads` with exactly `parachains_count` parachain
		// heads of the default size (`DEFAULT_PARACHAIN_HEAD_SIZE`)
		let base_weight = Self::submit_parachain_heads_with_n_parachains(parachains_count);

		// overhead because of extra storage proof bytes
		let expected_proof_size = parachains_count
			.saturating_mul(DEFAULT_PARACHAIN_HEAD_SIZE)
			.saturating_add(Self::expected_extra_storage_proof_size());
		let actual_proof_size = proof.size();
		let proof_size_overhead = Self::storage_proof_size_overhead(
			actual_proof_size.saturating_sub(expected_proof_size),
		);

		// potential pruning weight (refunded if hasn't happened)
		let pruning_weight =
			Self::parachain_head_pruning_weight(db_weight).saturating_mul(parachains_count as u64);

		base_weight
			.saturating_add(proof_size_overhead)
			.saturating_add(pruning_weight)
			.saturating_add(Self::submit_parachain_heads_overhead_from_runtime())
	}
```

**File:** bridges/modules/parachains/src/benchmarking.rs (L56-79)
```rust
	// Benchmark `submit_parachain_heads` extrinsic with different number of parachains.
	submit_parachain_heads_with_n_parachains {
		let p in 1..(T::parachains().len() + 1) as u32;

		let sender = account("sender", 0, 0);
		let mut parachains = T::parachains();
		let _ = if p <= parachains.len() as u32 {
			parachains.split_off(p as usize)
		} else {
			Default::default()
		};
		tracing::trace!(target: crate::LOG_TARGET, "=== {:?}", parachains.len());
		let (relay_block_number, relay_block_hash, parachain_heads_proof, parachains_heads) = T::prepare_parachain_heads_proof(
			&parachains,
			DEFAULT_PARACHAIN_HEAD_SIZE,
			UnverifiedStorageProofParams::default(),
		);
		let at_relay_block = (relay_block_number, relay_block_hash);
	}: submit_parachain_heads(RawOrigin::Signed(sender), at_relay_block, parachains_heads, parachain_heads_proof)
	verify {
		for parachain in parachains {
			assert!(crate::Pallet::<T, I>::best_parachain_head(parachain).is_some());
		}
	}
```

**File:** cumulus/parachains/runtimes/bridge-hubs/bridge-hub-rococo/src/weights/pallet_bridge_parachains.rs (L63-73)
```rust
	/// The range of component `p` is `[1, 2]`.
	fn submit_parachain_heads_with_n_parachains(_p: u32, ) -> Weight {
		// Proof Size summary in bytes:
		//  Measured:  `156`
		//  Estimated: `2543`
		// Minimum execution time: 36_844_000 picoseconds.
		Weight::from_parts(38_748_161, 0)
			.saturating_add(Weight::from_parts(0, 2543))
			.saturating_add(T::DbWeight::get().reads(4))
			.saturating_add(T::DbWeight::get().writes(3))
	}
```

**File:** cumulus/parachains/runtimes/bridge-hubs/bridge-hub-westend/src/weights/pallet_bridge_parachains.rs (L63-75)
```rust
	/// The range of component `p` is `[1, 2]`.
	fn submit_parachain_heads_with_n_parachains(p: u32, ) -> Weight {
		// Proof Size summary in bytes:
		//  Measured:  `83`
		//  Estimated: `2543`
		// Minimum execution time: 35_560_000 picoseconds.
		Weight::from_parts(37_182_961, 0)
			.saturating_add(Weight::from_parts(0, 2543))
			// Standard Error: 100_736
			.saturating_add(Weight::from_parts(42_669, 0).saturating_mul(p.into()))
			.saturating_add(T::DbWeight::get().reads(4))
			.saturating_add(T::DbWeight::get().writes(3))
	}
```
