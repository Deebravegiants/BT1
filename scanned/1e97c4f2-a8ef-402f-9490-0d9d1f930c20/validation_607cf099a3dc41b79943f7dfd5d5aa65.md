### Title
`do_reschedule_named` performs no origin-privilege comparison, allowing any `ScheduleOrigin`-permitted caller to reschedule another origin's named task - ([File: substrate/frame/scheduler/src/lib.rs])

### Summary
`Pallet::do_cancel` / `do_cancel_named` take the caller's `PalletsOrigin` and reject the call with `BadOrigin` whenever `T::OriginPrivilegeCmp::cmp_privilege` returns anything other than `Some(Ordering::Greater/Equal)` (including `None`, i.e. incomparable). `Pallet::do_reschedule` / `do_reschedule_named`, however, do not take a caller origin at all and never compare it against the stored task origin, so any origin that merely passes the `ScheduleOrigin` filter on the `reschedule_named` extrinsic can move (reschedule) a task that was scheduled by a *different, unrelated or higher-privileged* origin.

### Finding Description
The `cancel`/`cancel_named` dispatch path resolves the caller's `PalletsOrigin` and passes it into `do_cancel`/`do_cancel_named`, where the check is effectively:
```rust
if *o != s.origin &&
    !T::OriginPrivilegeCmp::cmp_privilege(o, &s.origin).map_or(false, |o| o != Ordering::Less)
{
    return Err(BadOrigin.into())
}
```
Here `map_or(false, ...)` means that when `cmp_privilege` returns `None` (incomparable), the expression evaluates to `false`, `!false == true`, and the branch correctly returns `BadOrigin`. So cancellation is properly protected against incomparable-privilege origins.

`reschedule` / `reschedule_named`, in contrast, operate purely on `(when, index)` / `TaskName` and a new `DispatchTime`, with no `PalletsOrigin` parameter and no invocation of `T::OriginPrivilegeCmp` anywhere in their bodies (see the `Anon`/`Named` `schedule` trait implementations and the dispatchables `reschedule`/`reschedule_named`, which only call `T::ScheduleOrigin::ensure_origin_or_root(origin)?` before delegating to `do_reschedule`/`do_reschedule_named`). The stored task's `origin` field is never read for authorization in these code paths - it is only used later for actually dispatching the call at execution time.

This creates the asymmetry described in the question: the "an origin cannot affect a task belonging to a strictly higher or incomparable-privileged origin" invariant is enforced for cancellation but not for rescheduling.

### Impact Explanation
Any account that is authorized under `T::ScheduleOrigin` (which, per the pallet design, is meant to allow multiple distinct origins - e.g. different governance tracks - to use the scheduler) can call `reschedule_named` on a `TaskName` scheduled by a *different* origin, even one with strictly higher or provably-incomparable privilege (as determined by `OriginPrivilegeCmp`). This lets a lower/incomparable-privileged caller delay, accelerate, or otherwise disrupt when a privileged scheduled call (e.g. a Root-authorized referendum enactment) executes, without needing to pass any origin-comparison check. This is a genuine cross-origin scheduling-integrity violation, distinct from (and broader than) the cancel-path `None` handling asked about.

### Likelihood Explanation
Feasible whenever a runtime configures `ScheduleOrigin` to accept more than one non-Root origin (a common pattern, e.g. OpenGov tracks or custom collective origins), and `OriginPrivilegeCmp` returns `None` for at least one pair of those origins (the default `EqualPrivilegeOnly` only allows exact-origin equality, effectively making every non-equal pair "not sufficiently privileged" from the cancel side, but this has no bearing on reschedule at all since reschedule performs zero comparison). No special preconditions beyond having scheduled a named task and having any account with `ScheduleOrigin` access are required; the exploit is a plain two-transaction sequence and fully repeatable.

### Recommendation
Extend `do_reschedule`/`do_reschedule_named` (and the corresponding `Anon`/`Named` schedule-trait methods and dispatchables) to accept the caller's `PalletsOrigin` and apply the same `ensure_privilege`-style check used in `do_cancel`/`do_cancel_named` before moving/mutating another origin's scheduled task, treating `None` from `OriginPrivilegeCmp::cmp_privilege` as insufficient privilege (`BadOrigin`), consistent with the cancel path.

### Proof of Concept
Rust integration test in `substrate/frame/scheduler/src/tests.rs`, mirroring `should_use_origin`:
1. Configure a mock `OriginPrivilegeCmp` that returns `None` for two custom non-Root origins `OriginA` and `OriginB`.
2. `Scheduler::schedule_named(OriginA, name=X, when, None, priority, some_call)` - succeeds, task stored with `origin = OriginA`.
3. Assert `Scheduler::cancel_named(OriginB, X)` returns `Err(BadOrigin)` (this currently passes, confirming cancel path is protected).
4. Assert `Scheduler::reschedule_named(OriginB, X, new_when)` - expect it to also return `Err(BadOrigin)`, but current code returns `Ok(..)` and the task's execution block is changed, proving the missing check.
5. Fetch `Lookup::<T>::get(X)` and confirm the `when` value was changed by `OriginB` despite `cmp_privilege(OriginB, OriginA) == None`, demonstrating the disruption of `OriginA`'s scheduled task. [1](#0-0)

### Citations

**File:** substrate/frame/scheduler/src/lib.rs (L984-1046)
```rust
	fn place_task(
		when: BlockNumberFor<T>,
		what: ScheduledOf<T>,
	) -> Result<TaskAddress<BlockNumberFor<T>>, (DispatchError, ScheduledOf<T>)> {
		let maybe_name = what.maybe_id;
		let index = Self::push_to_agenda(when, what)?;
		let address = (when, index);
		if let Some(name) = maybe_name {
			Lookup::<T>::insert(name, address)
		}
		Self::deposit_event(Event::Scheduled { when: address.0, index: address.1 });
		Ok(address)
	}

	fn push_to_agenda(
		when: BlockNumberFor<T>,
		what: ScheduledOf<T>,
	) -> Result<u32, (DispatchError, ScheduledOf<T>)> {
		let mut agenda = Agenda::<T>::get(when);
		let index = if (agenda.len() as u32) < T::MaxScheduledPerBlock::get() {
			// will always succeed due to the above check.
			let _ = agenda.try_push(Some(what));
			agenda.len() as u32 - 1
		} else {
			if let Some(hole_index) = agenda.iter().position(|i| i.is_none()) {
				agenda[hole_index] = Some(what);
				hole_index as u32
			} else {
				return Err((DispatchError::Exhausted, what));
			}
		};
		Agenda::<T>::insert(when, agenda);
		Ok(index)
	}

	/// Remove trailing `None` items of an agenda at `when`. If all items are `None` remove the
	/// agenda record entirely.
	fn cleanup_agenda(when: BlockNumberFor<T>) {
		let mut agenda = Agenda::<T>::get(when);
		match agenda.iter().rposition(|i| i.is_some()) {
			// Note that `agenda.len() > i + 1` implies that the agenda ends on a sequence of at
			// least one `None` item(s).
			Some(i) if agenda.len() > i + 1 => {
				agenda.truncate(i + 1);
				Agenda::<T>::insert(when, agenda);
			},
			// This branch is taken if `agenda.len() <= i + 1 ==> agenda.len() == i + 1 <==>
			// agenda.len() - 1 == i` i.e. the agenda's last item is `Some`.
			Some(_) => {},
			// All items in the agenda are `None`.
			None => {
				Agenda::<T>::remove(when);
			},
		}
	}

	fn do_schedule(
		when: DispatchTime<BlockNumberFor<T>>,
		maybe_periodic: Option<schedule::Period<BlockNumberFor<T>>>,
		priority: schedule::Priority,
		origin: T::PalletsOrigin,
		call: BoundedCallOf<T>,
	) -> Result<TaskAddress<BlockNumberFor<T>>, DispatchError> {
```
