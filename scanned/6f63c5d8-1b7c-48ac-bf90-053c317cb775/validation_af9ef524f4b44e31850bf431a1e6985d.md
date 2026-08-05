### Title
Shared preimage reference count not incremented on repeated `bound()`/`note()` calls, causing premature preimage deletion when one of multiple referencing scheduled tasks is canceled - (File: substrate/frame/preimage/src/lib.rs)

### Summary
`Pallet::note_bytes`, which backs `StorePreimage::note` and is called by every `T::Preimages::bound(call)` invocation (e.g. from `pallet_scheduler::schedule`), does **not** increment the `RequestStatus::Requested.count` field when a hash is already present with status `Requested`. As a result, two independent scheduled tasks that happen to reference an identical call (same encoded bytes/hash) end up sharing a `count` of `1` instead of `2`, so canceling either task via `T::Preimages::drop` → `do_unrequest_preimage` deletes the preimage data that the other, still-pending task requires.

### Finding Description
`bound()` in `substrate/frame/support/src/traits/preimages.rs` calls `Self::note(unbounded.into())` for any call too large to inline: [1](#0-0) . `note` maps to `Pallet::note_bytes(bytes, None)`: [2](#0-1) .

Inside `note_bytes`, when the hash already has an existing `RequestStatus::Requested` entry (i.e., a prior `bound()`/`note()` call for the identical encoded bytes already ran), the matching arm reuses the existing `count` verbatim instead of incrementing it: [3](#0-2) 

So if task X (attacker) and task Y (victim) are both scheduled with identical call bytes `C`, the first `bound()` sets `count = 1`; the second `bound()` for the same hash matches the `Some(RequestStatus::Requested { .. })` branch and leaves `count` at `1` — it never becomes `2`, even though two independent scheduled tasks now hold logical references to the same preimage data.

When the attacker cancels task X, the scheduler's cancel path invokes `T::Preimages::drop(&s.call)` → `QueryPreimage::unrequest` → `Pallet::do_unrequest_preimage`: [4](#0-3) . Because `count == 1` (never correctly reflecting 2 real references), the function enters the destructive `count == 1` branch (line 446 onward), calls `Self::remove(hash, len)` and clears `RequestStatusFor`, permanently deleting the preimage bytes from `PreimageFor`.

The victim's task Y still references the same hash for lookup. Any later attempt to `peek`/`realize`/`fetch` this hash fails: `fetch` returns `DispatchError::Unavailable` once the entry and bytes are gone: [5](#0-4) . In the scheduler, this failure to resolve the bounded call during `service_agenda`/`service_task` surfaces as an "Unavailable" servicing error for the victim's task, stalling or dropping it from the agenda.

No authorization/ownership check exists to prevent this because `do_unrequest_preimage`/`drop` operate purely on the shared `hash`, with no concept of "this specific `Bounded` instance created by this specific caller." The reference-counting mechanism that is supposed to protect shared preimages from premature deletion is broken specifically for the `note()`/`bound()` codepath (as opposed to `request()`/`do_request_preimage`, which correctly does `count.saturating_inc()`): [6](#0-5) .

### Impact Explanation
An unprivileged user who can schedule at least one task (subject to the runtime's `ScheduleOrigin`) and craft a call whose encoded bytes exactly match another user's already-scheduled (or about-to-be-scheduled) call can cause the shared preimage's `count` bookkeeping to under-represent real references. Canceling their own task destroys preimage data still required by the other, unrelated task, causing that victim task to fail with `Unavailable` during scheduler servicing — a queue-availability break triggered purely by an unprivileged user's normal `cancel` extrinsic. This matches the scoped impact: user-triggered halt/skip of another user's scheduled call.

### Likelihood Explanation
The bug is deterministic and does not require a "last reference wins a race" — because `note_bytes` never increments `count` past `1` for repeated `note()`/`bound()` calls on the same hash, the shared count is *always* wrong (staying at 1) as soon as a second task references the same call bytes, regardless of ordering. The only real precondition is: (1) the attacker must be able to reach `pallet_scheduler`'s scheduling call with a `ScheduleOrigin` that a normal/unprivileged account can satisfy (this varies per runtime — on chains where `ScheduleOrigin` is restricted to governance/root this path is not reachable by ordinary users, so the practical exploitability is runtime-configuration-dependent), and (2) the attacker must be able to produce a call whose SCALE encoding collides byte-for-byte with the victim's call (trivial if both reference a commonly-used call/preimage, or if the attacker can observe/predict the victim's pending call).

### Recommendation
Fix `Pallet::note_bytes` so that noting an already-`Requested` hash increments `count` (mirroring `do_request_preimage`'s `count.saturating_inc()`), or require every "reference-creating" `bound()`/`note()` call to be paired explicitly with a `request()` to properly account for multiplicity. At minimum, ensure `StorePreimage::bound` calls both `note()` and, when the hash is being freshly associated with a distinct logical owner, `request()`/increments the count so `drop()` calls made by one owner cannot deallocate a preimage still counted-for by another.

### Proof of Concept
Rust unit test in `substrate/frame/preimage/src/tests.rs`:
1. Call `Pallet::note_bytes(bytes_c.clone(), None)` twice in succession (simulating two independent `bound()` calls from two scheduler tasks referencing identical call bytes `C`), for hash `h`.
2. Assert `RequestStatusFor::<Test>::get(h)` is `RequestStatus::Requested { count: 2, .. }` — this assertion will FAIL, showing `count` remains `1`.
3. Call `Pallet::do_unrequest_preimage(&h)` once (simulating attacker canceling task X).
4. Assert `PreimageFor::<Test>::get((h, len))` is `None` (data deleted) while logically a second reference (task Y) still needs it.
5. Extended integration test in `pallet-scheduler`: schedule two named tasks bound to identical call bytes, `cancel` one, advance blocks, and assert the second task's `service_agenda` returns `Unavailable`/is skipped instead of executing successfully.

### Citations

**File:** substrate/frame/support/src/traits/preimages.rs (L255-262)
```rust
	fn bound<T: Encode>(t: T) -> Result<Bounded<T, Self::H>, DispatchError> {
		let data = t.encode();
		let len = data.len() as u32;
		Ok(match BoundedInline::try_from(data) {
			Ok(bounded) => Bounded::Inline(bounded),
			Err(unbounded) => Bounded::Lookup { hash: Self::note(unbounded.into())?, len },
		})
	}
```

**File:** substrate/frame/preimage/src/lib.rs (L343-357)
```rust
		let status = match (RequestStatusFor::<T>::get(hash), maybe_depositor) {
			(Some(RequestStatus::Requested { maybe_ticket, count, .. }), _) => {
				RequestStatus::Requested { maybe_ticket, count, maybe_len: Some(len) }
			},
			(Some(RequestStatus::Unrequested { .. }), Some(_)) => {
				return Err(Error::<T>::AlreadyNoted.into())
			},
			(Some(RequestStatus::Unrequested { ticket, len }), None) => RequestStatus::Requested {
				maybe_ticket: Some(ticket),
				count: 1,
				maybe_len: Some(len),
			},
			(None, None) => {
				RequestStatus::Requested { maybe_ticket: None, count: 1, maybe_len: Some(len) }
			},
```

**File:** substrate/frame/preimage/src/lib.rs (L379-396)
```rust
	fn do_request_preimage(hash: &T::Hash) {
		Self::do_ensure_updated(&hash);
		let (count, maybe_len, maybe_ticket) =
			RequestStatusFor::<T>::get(hash).map_or((1, None, None), |x| match x {
				RequestStatus::Requested { maybe_ticket, mut count, maybe_len } => {
					count.saturating_inc();
					(count, maybe_len, maybe_ticket)
				},
				RequestStatus::Unrequested { ticket, len } => (1, Some(len), Some(ticket)),
			});
		RequestStatusFor::<T>::insert(
			hash,
			RequestStatus::Requested { maybe_ticket, count, maybe_len },
		);
		if count == 1 {
			Self::deposit_event(Event::Requested { hash: *hash });
		}
	}
```

**File:** substrate/frame/preimage/src/lib.rs (L436-469)
```rust
	fn do_unrequest_preimage(hash: &T::Hash) -> DispatchResult {
		Self::do_ensure_updated(&hash);
		match RequestStatusFor::<T>::get(hash).ok_or(Error::<T>::NotRequested)? {
			RequestStatus::Requested { mut count, maybe_len, maybe_ticket } if count > 1 => {
				count.saturating_dec();
				RequestStatusFor::<T>::insert(
					hash,
					RequestStatus::Requested { maybe_ticket, count, maybe_len },
				);
			},
			RequestStatus::Requested { count, maybe_len, maybe_ticket } => {
				debug_assert!(count == 1, "preimage request counter at zero?");
				match (maybe_len, maybe_ticket) {
					// Preimage was never noted.
					(None, _) => RequestStatusFor::<T>::remove(hash),
					// Preimage was noted without owner - just remove it.
					(Some(len), None) => {
						Self::remove(hash, len);
						RequestStatusFor::<T>::remove(hash);
						Self::deposit_event(Event::Cleared { hash: *hash });
					},
					// Preimage was noted with owner - move to unrequested so they can get refund.
					(Some(len), Some(ticket)) => {
						RequestStatusFor::<T>::insert(
							hash,
							RequestStatus::Unrequested { ticket, len },
						);
					},
				}
			},
			RequestStatus::Unrequested { .. } => return Err(Error::<T>::NotRequested.into()),
		}
		Ok(())
	}
```

**File:** substrate/frame/preimage/src/lib.rs (L496-502)
```rust
	fn fetch(hash: &T::Hash, len: Option<u32>) -> FetchResult {
		let len = len.or_else(|| Self::len(hash)).ok_or(DispatchError::Unavailable)?;
		PreimageFor::<T>::get((hash, len))
			.map(|p| p.into_inner())
			.map(Into::into)
			.ok_or(DispatchError::Unavailable)
	}
```

**File:** substrate/frame/preimage/src/lib.rs (L574-584)
```rust
	fn note(bytes: Cow<[u8]>) -> Result<T::Hash, DispatchError> {
		// We don't really care if this fails, since that's only the case if someone else has
		// already noted it.
		let maybe_hash = Self::note_bytes(bytes, None).map(|(_, h)| h);
		// Map to the correct trait error.
		if maybe_hash == Err(DispatchError::from(Error::<T>::TooBig)) {
			Err(DispatchError::Exhausted)
		} else {
			maybe_hash
		}
	}
```
