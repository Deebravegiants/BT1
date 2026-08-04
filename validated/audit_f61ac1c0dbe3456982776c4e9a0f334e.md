I've completed the requested analog scan across the FRAME pallets, parachain runtime, and related primitives for the "stale-index-after-swap-remove" vulnerability class described in the LRT DepositPool report. Here is my conclusion:

**No vulnerability found for this question.**

Rationale for this conclusion:

The LRTDepositPool bug hinges on a specific pattern: an external/internal actor retains a **persistent array index** as an identifier for an entity (an NDC) across *separate calls/transactions*, and a `swap-with-last` removal invalidates that stored index, causing a subsequent call to operate on the wrong entity.

Searching polkadot-sdk for `swap_remove`-based removal patterns turned up several superficially similar usages, but none share the root-cause structure:

- `substrate/frame/collective/src/lib.rs` `do_vote` uses `voting.ayes.swap_remove(pos)` / `voting.nays.swap_remove(pos)`, but the index is computed and consumed within the same atomic call, never persisted across transactions. [1](#0-0) 
- `substrate/frame/staking/src/pallet/mod.rs` `kick` uses `nom.targets.swap_remove(pos)`, again computed and consumed atomically inside the closure. [2](#0-1) 
- `polkadot/runtime/rococo/src/validator_manager.rs` `new_session` swap-removes validators from the session's validator vec, but this list is rebuilt fresh from `pallet_session` each session and is not indexed by any externally-held identifier. [3](#0-2) 
- `substrate/frame/session/src/lib.rs` `DisabledValidators` uses a sorted `Vec` with `binary_search_by_key`/`insert`/`remove` (not `swap_remove`), specifically avoiding index-shift ambiguity for validator indices that are referenced elsewhere (e.g., in disputes, backing checks). [4](#0-3) 
- `polkadot/runtime/parachains/src/inclusion/mod.rs` `PendingAvailability` — the analog closest to "NDC list with index/core reference" — deliberately uses an ordered `VecDeque` with `drain()` for eviction rather than swap-based removal, which avoids the shifting-index race entirely; candidates are processed/evicted in strict dependency order. [5](#0-4) 
- `polkadot/runtime/parachains/src/disputes.rs` `filter_statement_set` does use `swap_remove` on statement indices, but explicitly removes indices in **reverse sorted order within a single pass** to guarantee correctness, and the indices are locally derived, not held across calls. [6](#0-5) 
- `ValidatorIndex` in the disputes/inclusion machinery is a stable identifier tied to session-shuffled validator sets (`ActiveValidatorIndices`) rather than a raw array position that shifts on removal. [7](#0-6) 

None of these exhibit the two required conditions for the reported vulnerability class: (1) a stable index/identifier persisted and referenced by a *separate*, later transaction/call, and (2) an intervening swap-based removal by another actor that silently redirects that later operation to a different entity. Where polkadot-sdk pallets track cross-call entities by index (validator indices, core indices), they either use non-shifting identifiers (session-based `ValidatorIndex`, `CoreIndex` tied to a fixed core count) or ordered structures (`VecDeque` + `drain`) that avoid the shifting-index hazard by design.

### Citations

**File:** substrate/frame/collective/src/lib.rs (L1008-1019)
```rust
			if let Some(pos) = position_no {
				voting.nays.swap_remove(pos);
			}
		} else {
			if position_no.is_none() {
				voting.nays.push(who.clone());
			} else {
				return Err(Error::<T, I>::DuplicateVote.into());
			}
			if let Some(pos) = position_yes {
				voting.ayes.swap_remove(pos);
			}
```

**File:** substrate/frame/staking/src/pallet/mod.rs (L1857-1867)
```rust
				Nominators::<T>::mutate(&nom_stash, |maybe_nom| {
					if let Some(ref mut nom) = maybe_nom {
						if let Some(pos) = nom.targets.iter().position(|v| v == stash) {
							nom.targets.swap_remove(pos);
							Self::deposit_event(Event::<T>::Kicked {
								nominator: nom_stash.clone(),
								stash: stash.clone(),
							});
						}
					}
				});
```

**File:** polkadot/runtime/rococo/src/validator_manager.rs (L103-124)
```rust
impl<T: Config> pallet_session::SessionManager<T::ValidatorId> for Pallet<T> {
	fn new_session(new_index: SessionIndex) -> Option<Vec<T::ValidatorId>> {
		if new_index <= 1 {
			return None;
		}

		let mut validators = Session::<T>::validators();

		ValidatorsToRetire::<T>::take().iter().for_each(|v| {
			if let Some(pos) = validators.iter().position(|r| r == v) {
				validators.swap_remove(pos);
			}
		});

		ValidatorsToAdd::<T>::take().into_iter().for_each(|v| {
			if !validators.contains(&v) {
				validators.push(v);
			}
		});

		Some(validators)
	}
```

**File:** substrate/frame/session/src/lib.rs (L1055-1096)
```rust
	pub fn disable_index_with_severity(i: u32, severity: OffenceSeverity) -> bool {
		if i >= Validators::<T>::decode_len().defensive_unwrap_or(0) as u32 {
			return false;
		}

		DisabledValidators::<T>::mutate(|disabled| {
			match disabled.binary_search_by_key(&i, |(index, _)| *index) {
				// Validator is already disabled, update severity if the new one is higher
				Ok(index) => {
					let current_severity = &mut disabled[index].1;
					if severity > *current_severity {
						log!(
							trace,
							"updating disablement severity of validator {:?} from {:?} to {:?}",
							i,
							*current_severity,
							severity
						);
						*current_severity = severity;
					}
					true
				},
				// Validator is not disabled, add to `DisabledValidators` and disable it
				Err(index) => {
					log!(trace, "disabling validator {:?}", i);
					Self::deposit_event(Event::ValidatorDisabled {
						validator: Validators::<T>::get()[i as usize].clone(),
					});
					disabled.insert(index, (i, severity));
					T::SessionHandler::on_disabled(i);
					true
				},
			}
		})
	}

	/// Disable the validator of index `i` with a default severity (defaults to most severe),
	/// returns `false` if the validator is not found.
	pub fn disable_index(i: u32) -> bool {
		let default_severity = OffenceSeverity::default();
		Self::disable_index_with_severity(i, default_severity)
	}
```

**File:** polkadot/runtime/parachains/src/inclusion/mod.rs (L1064-1101)
```rust
	fn free_failed_cores<
		P: Fn(&CandidatePendingAvailability<T::Hash, BlockNumberFor<T>>) -> bool,
	>(
		pred: P,
		capacity_hint: Option<usize>,
	) -> impl Iterator<Item = CandidatePendingAvailability<T::Hash, BlockNumberFor<T>>> {
		let mut earliest_dropped_indices: BTreeMap<ParaId, usize> = BTreeMap::new();

		for (para_id, pending_candidates) in PendingAvailability::<T>::iter() {
			// We assume that pending candidates are stored in dependency order. So we need to store
			// the earliest dropped candidate. All others that follow will get freed as well.
			let mut earliest_dropped_idx = None;
			for (index, candidate) in pending_candidates.iter().enumerate() {
				if pred(candidate) {
					earliest_dropped_idx = Some(index);
					// Since we're looping the candidates in dependency order, we've found the
					// earliest failed index for this paraid.
					break;
				}
			}

			if let Some(earliest_dropped_idx) = earliest_dropped_idx {
				earliest_dropped_indices.insert(para_id, earliest_dropped_idx);
			}
		}

		let mut cleaned_up_cores =
			if let Some(capacity) = capacity_hint { Vec::with_capacity(capacity) } else { vec![] };

		for (para_id, earliest_dropped_idx) in earliest_dropped_indices {
			// Do cleanups and record the cleaned up cores
			PendingAvailability::<T>::mutate(&para_id, |record| {
				if let Some(record) = record {
					let cleaned_up = record.drain(earliest_dropped_idx..);
					cleaned_up_cores.extend(cleaned_up);
				}
			});
		}
```

**File:** polkadot/runtime/parachains/src/disputes.rs (L832-840)
```rust
			StatementSetFilter::RemoveIndices(mut indices) => {
				indices.sort();
				indices.dedup();

				// reverse order ensures correctness
				for index in indices.into_iter().rev() {
					// `swap_remove` guarantees linear complexity.
					statement_set.statements.swap_remove(index);
				}
```

**File:** polkadot/runtime/parachains/src/shared.rs (L263-280)
```rust
	/// Fetches disabled validators list from session pallet.
	/// CAVEAT: this might produce incorrect results on session boundaries
	pub fn disabled_validators() -> Vec<ValidatorIndex> {
		let shuffled_indices = ActiveValidatorIndices::<T>::get();
		// mapping from raw validator index to `ValidatorIndex`
		// this computation is the same within a session, but should be cheap
		let reverse_index = shuffled_indices
			.iter()
			.enumerate()
			.map(|(i, v)| (v.0, ValidatorIndex(i as u32)))
			.collect::<BTreeMap<u32, ValidatorIndex>>();

		// we might have disabled validators who are not parachain validators
		T::DisabledValidators::disabled_validators()
			.iter()
			.filter_map(|v| reverse_index.get(v).cloned())
			.collect()
	}
```
