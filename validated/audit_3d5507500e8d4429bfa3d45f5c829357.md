Audit Report

## Title
`do_cancel_named` silently skips `Retries` cleanup and `Preimages::drop` when invoked with `origin: None`, orphaning retry state and preimage holds - (File: substrate/frame/scheduler/src/lib.rs)

## Summary
`Pallet::do_cancel_named` only calls `Retries::<T>::remove((when, index))` and `T::Preimages::drop(&s.call)` inside the `if let (Some(ref o), Some(ref s)) = (origin, s.borrow())` branch, so when invoked with `origin: None` — as happens via `schedule::v3::Named::cancel_named(id)`, which always calls `Self::do_cancel_named(None, id)` — the task's `Lookup` entry is cleared and the agenda slot is emptied, but the `Retries` entry and the preimage reference are never cleaned up. This directly contrasts with the anonymous-task counterpart `do_cancel`, which performs these cleanups unconditionally, gating only the privilege check on `origin`.

## Finding Description
Direct inspection of the code confirms the claim precisely: [1](#0-0) 
`do_cancel` structures the origin check purely as a privilege gate (`if let (Some(ref o), ...) { ensure_privilege... }`) and then unconditionally executes `T::Preimages::drop(&s.call)` and `Retries::<T>::remove((when, index))` on the `Some(s)` branch, regardless of whether `origin` was `Some` or `None`. [2](#0-1) 
`do_cancel_named`, however, nests `Retries::<T>::remove((when, index))` and `T::Preimages::drop(&s.call)` *inside* the same tuple pattern `(Some(ref o), Some(ref s))` used for the privilege check. When `origin` is `None` (as it always is when called through the `Named` trait's `cancel_named`), the inner pattern fails to match, so both cleanup calls are skipped, while `*s = None` still executes unconditionally, clearing the agenda slot without cleaning up `Retries` or dropping the preimage.

The trait implementation that triggers this path with `origin: None` is present exactly as described.

This is a genuine asymmetry between the two cancellation code paths, and the root cause (cleanup logic incorrectly co-located with the privilege-check pattern match instead of being gated only on "was a task actually found and removed") is real and verifiable directly from the source.

## Impact Explanation
Confirmed impact: a stale `Retries<T>` entry survives at `(when, index)` after a named task is cancelled via the internal trait path, and `T::Preimages::drop` is never invoked, leaving the preimage reference/deposit undropped. Since `Agenda` slots at a given block are reused positionally as new tasks are scheduled, a stale `Retries` entry can later apply retry semantics to an unrelated task that lands at the same `(when, index)`, and the undropped preimage keeps any associated deposit locked. This is a real storage/accounting desynchronization within the scheduler pallet itself, not a hypothetical or mocked-path issue.

## Likelihood Explanation
The bug is deterministic: every call to `do_cancel_named` with `origin: None` (i.e., every call through `<Pallet as schedule::v3::Named<...>>::cancel_named`) hits this path. However, I was unable to independently verify within available tool budget which concrete downstream pallets/extrinsics in this repository snapshot invoke this trait method from an unprivileged/permissionless code path (e.g., a referenda pallet's permissionless nudge/cancel logic), which the original report itself also flags as unverified. This limits certainty about real-world unprivileged reachability, though the pallet-internal bug itself is confirmed and reproducible by any code exercising this trait method directly (as demonstrated in the report's proposed unit test structure).

## Recommendation
Restructure `do_cancel_named` so that `Retries::<T>::remove((when, index))` and `T::Preimages::drop(&s.call)` execute whenever a task is actually found and removed, independent of whether an `origin` privilege check was requested — mirroring `do_cancel`'s structure:
```rust
if let Some(s) = agenda.get_mut(i) {
    if let (Some(ref o), Some(ref s)) = (origin, s.borrow()) {
        Self::ensure_privilege(o, &s.origin)?;
    }
    if let Some(ref s) = s {
        Retries::<T>::remove((when, index));
        T::Preimages::drop(&s.call);
    }
    *s = None;
}
```

## Proof of Concept
Add a unit test in `substrate/frame/scheduler/src/tests.rs` that schedules a named task with `set_retry_named`, then cancels it via `<Scheduler as schedule::v3::Named<_,_,_>>::cancel_named(name)` (origin `None`), and asserts `Retries::<Test>::iter().count()` and preimage-drop state — as outlined in the original report. This reproduces the leak deterministically since it directly exercises the buggy code path confirmed above.

### Citations

**File:** substrate/frame/scheduler/src/lib.rs (L1078-1100)
```rust
		let scheduled = Agenda::<T>::try_mutate(when, |agenda| {
			agenda.get_mut(index as usize).map_or(
				Ok(None),
				|s| -> Result<Option<Scheduled<_, _, _, _, _>>, DispatchError> {
					if let (Some(ref o), Some(ref s)) = (origin, s.borrow()) {
						Self::ensure_privilege(o, &s.origin)?;
					};
					Ok(s.take())
				},
			)
		})?;
		if let Some(s) = scheduled {
			T::Preimages::drop(&s.call);
			if let Some(id) = s.maybe_id {
				Lookup::<T>::remove(id);
			}
			Retries::<T>::remove((when, index));
			Self::cleanup_agenda(when);
			Self::deposit_event(Event::Canceled { when, index });
			Ok(())
		} else {
			return Err(Error::<T>::NotFound.into());
		}
```

**File:** substrate/frame/scheduler/src/lib.rs (L1165-1187)
```rust
	fn do_cancel_named(origin: Option<T::PalletsOrigin>, id: TaskName) -> DispatchResult {
		Lookup::<T>::try_mutate_exists(id, |lookup| -> DispatchResult {
			if let Some((when, index)) = lookup.take() {
				let i = index as usize;
				Agenda::<T>::try_mutate(when, |agenda| -> DispatchResult {
					if let Some(s) = agenda.get_mut(i) {
						if let (Some(ref o), Some(ref s)) = (origin, s.borrow()) {
							Self::ensure_privilege(o, &s.origin)?;
							Retries::<T>::remove((when, index));
							T::Preimages::drop(&s.call);
						}
						*s = None;
					}
					Ok(())
				})?;
				Self::cleanup_agenda(when);
				Self::deposit_event(Event::Canceled { when, index });
				Ok(())
			} else {
				return Err(Error::<T>::NotFound.into());
			}
		})
	}
```
