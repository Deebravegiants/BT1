### Title
Uncapped `number_of_assets` in `pallet_xcm::claim_assets` combined with non-transactional XCM execution permits weight-underestimation DoS and partial state mutation (asset loss) - (File: `polkadot/xcm/pallet-xcm/src/lib.rs`)

### Summary
`claim_assets` derives `number_of_assets` directly from the caller-supplied `VersionedAssets` with no explicit upper bound before building `ClaimAsset`/`DepositAsset{AllCounted(number_of_assets)}` and calling `T::Weigher::weight`, and the extrinsic is not wrapped in a transactional guard. This allows an attacker who has trapped many distinct low/no-value assets under one hash to submit a single `claim_assets` call whose actual execution cost (iterating/matching potentially many distinct `AssetId`s in `ClaimAsset` and in `DepositAsset`'s wildcard filter against the holding register, bounded by `MaxAssetsIntoHolding`) can diverge from the benchmarked, fixed per-instruction weight used to charge the dispatch, and whose partial failure (`Outcome::Incomplete`) can leave prior storage mutations (e.g., trap accounting) committed while the deposit does not complete.

### Finding Description
`claim_assets` computes `number_of_assets` from the decoded `Assets` with only `assets.len() as u32`, with no cap comparable to `MAX_ASSETS_FOR_TRANSFER` used elsewhere in the same file (`transfer_assets` explicitly enforces `ensure!(assets.len() <= MAX_ASSETS_FOR_TRANSFER, ...)` at [1](#0-0) , but `claim_assets` has no equivalent check) [2](#0-1) .

The message `[ClaimAsset{assets, ticket}, DepositAsset{assets: AllCounted(number_of_assets), beneficiary}]` is then weighed with `T::Weigher::weight(&mut message, Weight::MAX)` [3](#0-2) . The production weigher (`WeightInfoBounds`) computes per-instruction cost via `instruction.weight()`, which dispatches to a fixed, benchmarked constant for each instruction variant (`instr_weight_with_limit` simply adds `instruction.weight()`, i.e., a single benchmarked value per instruction occurrence, not a value parameterized by the length of the embedded `Assets`/wildcard filter) [4](#0-3) . Benchmarks for `ClaimAsset` and `DepositAsset` are produced for a bounded/worst-case number of assets; the extrinsic path does not verify that the attacker-chosen `number_of_assets` stays within that benchmarked bound, so the actual execution work of matching/moving up to `number_of_assets` distinct assets between the trap, holding register (bounded by `MaxAssetsIntoHolding`), and beneficiary account can exceed what was charged.

Separately, `claim_assets` has no `#[transactional]` attribute, and XCM instruction execution performs real storage mutations instruction-by-instruction rather than as an atomic unit for the whole dispatchable; `outcome.ensure_complete()` is only checked after `prepare_and_execute` returns [5](#0-4) . If `ClaimAsset` (which removes assets from the trap store, mirrored by the `ClaimAssets`/`DropAssets` trait pair) succeeds but the subsequent `DepositAsset{AllCounted(N)}` fails partway (e.g., exceeding `MaxAssetsIntoHolding` while re-subsuming N distinct assets into the holding register, or a subsequent deposit failure), the trap-removal side effect is not automatically rolled back merely because the dispatchable maps the outcome to `Error::LocalExecutionIncompleteWithError`. This is exactly the invariant violation described: trap accounting decremented while assets are not fully delivered.

### Impact Explanation
Concretely: (1) unbounded `number_of_assets` lets an attacker submit a `claim_assets` call whose real CPU/proof-size cost of iterating/moving many distinct assets is not proportionally reflected in the extrinsic's charged weight, enabling cheap execution-time amplification versus the fee paid; (2) because the dispatchable is not transactional, an `Outcome::Incomplete` result from the constructed `ClaimAsset`+`DepositAsset` program can leave the trapped-asset record consumed without the assets landing at `beneficiary`, resulting in asset loss for the claiming account (and, if attacker-controlled trapped assets, funds that become unrecoverable once the trap entry is gone).

### Likelihood Explanation
Preconditions require the attacker to have trapped a large but bounded number of distinct near-worthless `AssetId`s under a single trap hash beforehand (achievable cheaply via repeated small `WithdrawAsset`+`Trap` XCM programs from an unprivileged signed origin using `execute`/`send`), then call `claim_assets` once with all N assets. This is fully reachable via ordinary signed extrinsics with no special privilege, and is repeatable at will since trapping cheap/worthless assets costs little.

### Recommendation
- Add an explicit upper bound check on `number_of_assets` (mirroring `MAX_ASSETS_FOR_TRANSFER` used in `transfer_assets`) before constructing the `ClaimAsset`/`DepositAsset` message and before calling `T::Weigher::weight`, rejecting claims with `Error::TooManyAssets` if the size exceeds what's safely benchmarked.
- Ensure XCM-instruction weight functions used for `ClaimAsset`/`DepositAsset(AllCounted(n))` are parameterized by the actual number of assets involved (or explicitly capped to the benchmarked worst case) so the pre-execution weight bound is a true upper bound on execution cost.
- Wrap `claim_assets` in a transactional context (e.g., `#[frame_support::transactional]` or explicit `with_storage_layer`) so that a partial/incomplete outcome fully rolls back trap-store mutations, preserving the invariant that `AssetTraps` accounting and actual asset delivery change atomically together.

### Proof of Concept
Integration/fuzz test plan (pallet-xcm mock runtime):
1. From a signed origin, execute N `WithdrawAsset`+`Trap` XCM programs, each trapping one distinct low-value `AssetId`, all under the same origin (same trap hash), for varying N (e.g., 10, 100, 1000, near `MaxAssetsIntoHolding`).
2. Call `claim_assets` with a `VersionedAssets` containing all N trapped assets and a valid beneficiary.
3. Assert: either (a) the call fully succeeds, `AssetTraps` entry for that hash is fully removed, and `beneficiary`'s balance reflects all N assets deposited; or (b) the call fails/rolls back entirely, with `AssetTraps` entry unchanged and no partial deposit to `beneficiary`.
4. Fuzz N up to/exceeding `MaxAssetsIntoHolding` and assert the invariant never observes a state where `AssetTraps` is decremented/removed but `beneficiary`'s deposited asset count is less than N (partial mutation), and separately benchmark the actual weight consumed by `prepare_and_execute` against the value returned by `T::Weigher::weight` to detect underestimation as N grows.

### Citations

**File:** polkadot/xcm/pallet-xcm/src/lib.rs (L1491-1491)
```rust
			ensure!(assets.len() <= MAX_ASSETS_FOR_TRANSFER, Error::<T>::TooManyAssets);
```

**File:** polkadot/xcm/pallet-xcm/src/lib.rs (L1543-1559)
```rust
			let number_of_assets = assets.len() as u32;
			let beneficiary: Location = (*beneficiary).try_into().map_err(|()| {
				tracing::debug!(
					target: "xcm::pallet_xcm::claim_assets",
					"Failed to convert beneficiary VersionedLocation",
				);
				Error::<T>::BadVersion
			})?;
			let ticket: Location = GeneralIndex(assets_version as u128).into();
			let mut message = Xcm(vec![
				ClaimAsset { assets, ticket },
				DepositAsset { assets: AllCounted(number_of_assets).into(), beneficiary },
			]);
			let weight = T::Weigher::weight(&mut message, Weight::MAX).map_err(|error| {
				tracing::debug!(target: "xcm::pallet_xcm::claim_assets", ?error, "Failed to calculate weight");
				Error::<T>::UnweighableMessage
			})?;
```

**File:** polkadot/xcm/pallet-xcm/src/lib.rs (L1561-1573)
```rust
			let outcome = T::XcmExecutor::prepare_and_execute(
				origin_location,
				message,
				&mut hash,
				weight,
				weight,
			);
			outcome.ensure_complete().map_err(|error| {
				tracing::error!(target: "xcm::pallet_xcm::claim_assets", ?error, "XCM execution failed with error");
				Error::<T>::LocalExecutionIncompleteWithError { index: error.index, error: error.error.into()}
			})?;
			Ok(())
		}
```

**File:** polkadot/xcm/xcm-builder/src/weight.rs (L200-223)
```rust
	fn instr_weight_with_limit(
		instruction: &mut Instruction<C>,
		instructions_left: &mut u32,
		weight_limit: Weight,
	) -> Result<Weight, XcmError> {
		let instruction_weight = match instruction {
			Transact { ref mut call, .. } => {
				call.ensure_decoded()
					.map_err(|_| XcmError::FailedToDecode)?
					.get_dispatch_info()
					.call_weight
			},
			SetErrorHandler(xcm) | SetAppendix(xcm) => {
				Self::weight_with_limit(xcm, instructions_left, weight_limit)
					.map_err(|outcome_error| outcome_error.error)?
			},
			_ => Weight::zero(),
		};
		let total_weight = instruction
			.weight()
			.checked_add(&instruction_weight)
			.ok_or(XcmError::Overflow)?;
		Ok(total_weight)
	}
```
