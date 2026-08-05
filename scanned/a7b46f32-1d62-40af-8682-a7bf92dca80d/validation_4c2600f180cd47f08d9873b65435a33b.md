Based on my analysis, the key finding involves the `cached_info` lookup at `substrate/frame/revive/src/exec.rs:2201-2211`, which finds the **first** ancestor frame matching `dest` account_id, applies its pending diff, and hands that preview-applied clone to the new child frame. Symmetrically, `pop_frame`'s `bank_pending_changes_and_invalidate` search at `exec.rs:1667` (`self.frames_mut().find(|f| f.account_id == *account_id)`) also finds only the **first** (nearest) matching ancestor to bank into.

In a 3+-level self-reentry chain `X→X2→X3` (all same contract, `X2` writes `K2` then reenters into `X3`), when `X3` pops:
1. `X3`'s finalized `ContractInfo` (containing `K1+K2+K3`, since `K2` was already preview-applied by `push_frame`/`cached_info` into what `X3` saw) is persisted via `insert_contract`.
2. The ancestor search finds `X2` (nearest match) and calls `bank_pending_changes_and_invalidate(X2)`.
3. This reloads `X2`'s `contract_info` from storage (now `K1+K2+K3`) and applies `X2.frame_meter`'s still-`Alive` `own_contribution` (`K2`) on top — re-adding `K2` a second time.

This traces the same root-cause class described in PR #12267 (`prdoc/pr_12267.prdoc`) — preview-apply making a pending diff visible to a descendant without the ancestor's own_contribution being consumed — but for a **three-frame** self-reentry chain rather than the two-frame case the fix's tests (`same_contract_reentry_does_not_double_count_storage`, `transitive_reentry_does_not_double_count_storage`) exercise. Both existing regression tests use only a single intervening no-op/proxy frame between two writes on the same contract (`ReentryStorage.writeReenterWrite`/`writeReenterWriteVia`), i.e. exactly one ancestor with a pending diff at bank time. Neither test covers a scenario where **two** stacked ancestors of the same contract both hold live `own_contribution` diffs when a descendant pops.

I was not able to fully verify this hypothesis by tracing execution end-to-end (in particular, I could not confirm within the remaining budget whether `absorb_all_meters`/`FrameMeter::finalize` semantics for the *middle* frame `X2` cause its `own_contribution` to be reset to `Checked` before `X3`'s pop reaches it, which would neutralize the double-count I described — this reset only happens when `X2` itself pops, per the prdoc's own account of ordering). Given the specificity of the described mechanism, the multi-level scenario is plausible but unconfirmed without either running the described 3-level test or tracing `FrameMeter::absorb_all_meters` and `RawMeter::nested`/`Contribution` state transitions precisely across all three frames.

### Title
Potential storage-deposit double-count in 3+-level self-reentry chains not covered by PR #12267's fix - (File: substrate/frame/revive/src/exec.rs)

### Summary
PR #12267 fixed same-contract reentry double-counting for the two-level case (`X→X` and `X→Y→X` with a single pending-diff ancestor at bank time), but the ancestor-matching logic in both `push_frame`'s `cached_info` lookup (`exec.rs:2201-2211`) and `pop_frame`'s `bank_pending_changes_and_invalidate` search (`exec.rs:1667`) only ever act on the *nearest* matching ancestor frame. A three-level self-reentry chain (`X→X2→X3`, same contract at all three levels) may leave an intermediate ancestor's `own_contribution` diff applied twice: once via preview-apply into the descendant's persisted `ContractInfo`, and once when that ancestor is later banked against freshly-reloaded storage that already contains it.

### Finding Description
`push_frame`/the precompile `call` cached_info lookup (`exec.rs:2201-2211`) clones the *first* matching ancestor's cached `ContractInfo`, preview-applies that ancestor's still-pending diff via `apply_pending_storage_changes`, and hands the clone to the new frame — without consuming the ancestor's `own_contribution`. When a further-nested frame of the same contract (`X3`) later completes and its final `ContractInfo` is persisted, `pop_frame` (`exec.rs:1667`) searches `self.frames_mut()` for the first remaining frame with the matching `account_id` and calls `bank_pending_changes_and_invalidate` (`exec.rs:1613-1626`) on it. `bank_pending_changes` (`metering/storage.rs:514-528`) reloads the ancestor's info from storage and applies its `Alive` `own_contribution` on top. If that intermediate ancestor (`X2`) is not the *closest* one to `X3`, or if two ancestors both hold live diffs from writes made before spawning nested self-reentrant frames, the diff that was already preview-applied into storage by an inner frame's `insert_contract` can be re-applied by an outer ancestor's later bank — reproducing the double-count class the PR aimed to eliminate, but at one additional nesting depth.

### Impact Explanation
Matches the scoped impact: inflated `storage_items`/`storage_bytes`/`storage_*_deposit` fields corrupt the persisted `ContractInfo`, which (per the prdoc's own analysis) causes subsequent `clear_storage` refunds to be pro-rated against an inflated denominator, under-refunding the depositor. Repeated/compounding double-counts across deeper reentry chains could plausibly inflate the phantom counters further than the single-level case, though the `.min(FixedU128::from_u32(1))` clamp described in the prdoc bounds any single refund event from over-refunding.

### Likelihood Explanation
Fully reachable by an unprivileged caller: `ReentrancyProtection::AllowReentry` (EVM default for non-zero-value/no-stipend calls) or `CallFlags::ALLOW_REENTRY` (PVM opt-in) are both user-controlled, requiring only a self-authored contract with a 3-level self-reentrant write pattern — no special privileges needed. However, this specific 3-level scenario is a hypothesis extrapolated from the documented 2-level mechanism; I could not confirm via full state-machine tracing (particularly the exact point at which an intermediate ancestor's `own_contribution` is reset to `Checked`) whether the double-count actually manifests at 3 levels or whether some other invariant (e.g., the ancestor search always terminating the chain correctly frame-by-frame as the prdoc's comment "each will invalidate the next cache when it is popped" implies) prevents it.

### Recommendation
Extend the existing differential test suite (`same_contract_reentry_does_not_double_count_storage`, `transitive_reentry_does_not_double_count_storage` in `substrate/frame/revive/src/metering/tests.rs`) with a 3+-level self-reentrant fixture (`X→X2→X3`, each level writing before reentering) and compare final `ContractInfo` accounting against an equivalent flat/direct baseline, as done for the existing 2-level cases.

### Proof of Concept
Add a Rust integration test in `substrate/frame/revive/src/metering/tests.rs` modeled on `transitive_reentry_does_not_double_count_storage`, but using a 3-level self-reentrant Solidity fixture (extend `ReentryStorage.sol` with a function like `writeReenterTwiceWrite` that writes `K1`, calls `this.writeReenterWrite()` — itself performing a write+reenter+write — then writes a final key), and assert:
- `reentrant_info.storage_items == baseline_info.storage_items`
- `reentrant_info.storage_bytes == baseline_info.storage_bytes`
- `reentrant_info.storage_item_deposit == baseline_info.storage_item_deposit`
- `reentrant_info.storage_byte_deposit == baseline_info.storage_byte_deposit`
- `reentrant.storage_deposit == baseline.storage_deposit`

against a non-reentrant baseline performing the equivalent three writes directly in one frame. A failure (inflated fields) would confirm the 3-level regression; a pass would disprove this specific hypothesis. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** substrate/frame/revive/src/exec.rs (L1606-1671)
```rust
	fn pop_frame(&mut self, persist: bool) {
		/// Bank the pending storage diff into the cached `ContractInfo`, then invalidate.
		///
		/// The `load` covers the case where an earlier same-contract reentry already
		/// invalidated this frame; without it a removal-bearing diff would be banked with
		/// no info and silently drop the refund pro-rata. A `None` after `load` means the
		/// frame is a precompile with no contract info, which has nothing to bank.
		fn bank_pending_changes_and_invalidate<T: Config>(f: &mut Frame<T>) {
			let contract = f.account_id.clone();
			f.contract_info.load(&f.account_id);
			if let Some(info) = f.contract_info.as_contract() {
				f.frame_meter.bank_pending_storage_changes(contract, info);
			}
			// `invalidate` drops the in-memory update `bank` made to `info`; that is safe
			// because storage already reflects it. Additions and `set_storage` removals leave
			// the frame `Cached` (write reloads the cache), so `push_frame` preview-persists
			// them before we get here. The only diff not yet in storage would be a removal on
			// an already-invalidated frame — reachable solely via `charge_storage`, which has
			// no contract-level caller. If that changes, persist here instead of invalidating.
			f.contract_info.invalidate();
		}

		// Pop the current frame from the stack and return it in case it needs to interact
		// with duplicates that might exist on the stack.
		// A `None` means that we are returning from the `first_frame`.
		let frame = self.frames.pop();

		// Both branches do essentially the same with the exception. The difference is that
		// the else branch does consume the hardcoded `first_frame`.
		if let Some(mut frame) = frame {
			let account_id = &frame.account_id;
			let prev = top_frame_mut!(self);

			// Only weight counter changes are persisted in case of a failure.
			if !persist {
				prev.frame_meter.absorb_weight_meter_only(frame.frame_meter);
				return;
			}

			// Record the storage meter changes of the nested call into the parent meter.
			// If the dropped frame's contract has a contract info we update the deposit
			// counter in its contract info. The load is necessary to pull it from storage in case
			// it was invalidated.
			frame.contract_info.load(account_id);
			let mut contract = frame.contract_info.into_contract();
			prev.frame_meter
				.absorb_all_meters(frame.frame_meter, account_id, contract.as_mut());

			// only on success inherit the created and to be destroyed contracts
			prev.contracts_created.extend(frame.contracts_created);
			prev.contracts_to_be_destroyed.extend(frame.contracts_to_be_destroyed);

			if let Some(contract) = contract {
				// Persist the info and invalidate the first stale cache we find.
				// This triggers a reload from storage on next use. Only the first
				// cache needs to be invalidated because that one will invalidate the next cache
				// when it is popped from the stack.
				AccountInfo::<T>::insert_contract(
					&T::AddressMapper::to_address(account_id),
					contract,
				);
				if let Some(f) = self.frames_mut().find(|f| f.account_id == *account_id) {
					// Bank before invalidating so finalize doesn't apply the diff a second time.
					bank_pending_changes_and_invalidate(f);
				}
			}
```

**File:** substrate/frame/revive/src/exec.rs (L2201-2211)
```rust
			let cached_info = self
				.frames()
				.find(|f| f.entry_point == ExportedFunction::Call && f.account_id == dest)
				.and_then(|f| match &f.contract_info {
					CachedContract::Cached(contract) => {
						let mut contract_with_pending = contract.clone();
						f.frame_meter.apply_pending_storage_changes(&mut contract_with_pending);
						Some(contract_with_pending)
					},
					_ => None,
				});
```

**File:** substrate/frame/revive/src/metering/storage.rs (L512-528)
```rust
	/// Apply the pending diff to `info` and push its deposit as a final charge, then reset
	/// `own_contribution` so finalize does not apply it a second time.
	pub fn bank_pending_changes(&mut self, contract: T::AccountId, info: &mut ContractInfo<T>) {
		if let Contribution::Alive(_) = &self.own_contribution {
			let deposit = self.own_contribution.update_contract(Some(info));
			self.own_contribution = Contribution::Alive(Default::default());
			if !deposit.is_zero() {
				self.charge_deposit(contract, deposit);
			}
		} else {
			debug_assert!(
				false,
				"on-stack ancestor frames have not finalized yet, so own_contribution \
				 should be Alive when banked; qed",
			);
		}
	}
```

**File:** substrate/frame/revive/src/metering/tests.rs (L226-295)
```rust
/// Transitive same-contract reentry (X -> Y -> X): the invalidation matcher keys on
/// `account_id`, so an ancestor reentered through an intermediary is affected too. Full
/// solc/resolc matrix over (`ReentryStorage`, `ReentryProxy`) -> 4 cases. As above, the
/// reentrant run must match a non-reentrant baseline exactly.
#[test_case(FixtureType::Solc  , FixtureType::Solc   ; "solc storage, solc proxy")]
#[test_case(FixtureType::Solc  , FixtureType::Resolc ; "solc storage, resolc proxy")]
#[test_case(FixtureType::Resolc, FixtureType::Solc   ; "resolc storage, solc proxy")]
#[test_case(FixtureType::Resolc, FixtureType::Resolc ; "resolc storage, resolc proxy")]
fn transitive_reentry_does_not_double_count_storage(
	storage_type: FixtureType,
	proxy_type: FixtureType,
) {
	let (storage_code, _) = compile_module_with_type("ReentryStorage", storage_type).unwrap();
	let (proxy_code, _) = compile_module_with_type("ReentryProxy", proxy_type).unwrap();

	ExtBuilder::default().build().execute_with(|| {
		let _ = <Test as Config>::Currency::set_balance(&ALICE, 100_000_000_000);

		let Contract { addr: proxy_addr, .. } = builder::bare_instantiate(Code::Upload(proxy_code))
			.salt(Some([3; 32]))
			.build_and_unwrap_contract();

		// Baseline: two writes, no reentry.
		let Contract { addr: baseline_addr, .. } =
			builder::bare_instantiate(Code::Upload(storage_code.clone()))
				.salt(Some([1; 32]))
				.build_and_unwrap_contract();
		let baseline = builder::bare_call(baseline_addr)
			.data(ReentryStorage::writeTwiceCall {}.abi_encode())
			.build();
		let baseline_info = AccountInfo::<Test>::load_contract(&baseline_addr).unwrap();

		// Reentrant: write, reenter self via the proxy (X -> Y -> X), write.
		let Contract { addr: reentrant_addr, .. } =
			builder::bare_instantiate(Code::Upload(storage_code))
				.salt(Some([2; 32]))
				.build_and_unwrap_contract();
		let reentrant = builder::bare_call(reentrant_addr)
			.data(
				ReentryStorage::writeReenterWriteViaCall { proxy: proxy_addr.0.into() }
					.abi_encode(),
			)
			.build();
		let reentrant_info = AccountInfo::<Test>::load_contract(&reentrant_addr).unwrap();

		assert!(baseline.result.is_ok(), "baseline call failed: {:?}", baseline.result);
		assert!(reentrant.result.is_ok(), "reentrant call failed: {:?}", reentrant.result);

		assert_eq!(
			reentrant_info.storage_items, baseline_info.storage_items,
			"storage_items inflated by double-applied diff under transitive reentry",
		);
		assert_eq!(
			reentrant_info.storage_bytes, baseline_info.storage_bytes,
			"storage_bytes inflated under transitive reentry",
		);
		assert_eq!(
			reentrant_info.storage_item_deposit, baseline_info.storage_item_deposit,
			"storage_item_deposit inflated under transitive reentry",
		);
		assert_eq!(
			reentrant_info.storage_byte_deposit, baseline_info.storage_byte_deposit,
			"storage_byte_deposit inflated under transitive reentry",
		);
		assert_eq!(
			reentrant.storage_deposit, baseline.storage_deposit,
			"net storage deposit charged to origin inflated under transitive reentry",
		);
	});
}
```

**File:** prdoc/pr_12267.prdoc (L9-17)
```text
    ## What goes wrong

    For `X` writes `K1` → calls itself → writes `K2`:

    1. `push_frame` (`exec.rs:1212-1223`) and the same-contract `cached_info` shortcut (`exec.rs:2150-2160`) clone the parent's `ContractInfo`, preview-apply the parent's pending diff to the clone, and use it as the child's view. The child persists that clone via `insert_contract` on success.
    2. The cache-invalidation matcher (`exec.rs:1616`) then marks the parent's cache `Invalidated`. The parent's next write reloads from storage, which already contains the preview-applied `K1`.
    3. The parent's `finalize()` (`exec.rs:1474-1478`) re-applies its still-pending `own_contribution` (which still contains `K1`) on top of the reloaded info → `K1` counted twice.

    This is a regression from [#10920](https://github.com/paritytech/polkadot-sdk/pull/10920) (commit `1b9ea1c3656`, merged 2026-02-10), which introduced the preview-apply step to make pending writes visible to nested frames for refund pro-rating, but did not consume the parent's `own_contribution`. The existing #10920 regression test (`metering::tests::nested_call_storage_refund` with the `setAndCallClear` fixture) does not catch the case because the parent performs no write after the nested call returns — its cache stays `Invalidated`, the outer pop's `as_contract()` returns `None`, and the diff is never re-applied.
```
