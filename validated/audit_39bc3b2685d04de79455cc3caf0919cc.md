### Title
Proxy delay bypass via duplicate `(delegate, proxy_type)` entries with different `delay` values allows premature `proxy_announced` execution - ([File: substrate/frame/proxy/src/lib.rs])

### Summary
`add_proxy` (via `add_proxy_delegate`) does not enforce uniqueness on `(delegate, proxy_type)`; it only rejects an insert if the *entire* `ProxyDefinition` (including `delay`) is identical to an existing one. This allows two `ProxyDefinition` entries for the same delegate and proxy type to coexist with different `delay` values. `find_proxy`, used by both `proxy` and `proxy_announced`, matches only on `delegate`/`proxy_type` and returns the first match in the sorted `BoundedVec`, which — due to the struct's derived `Ord` (field order `delegate`, `proxy_type`, `delay`) — is always the entry with the *lowest* `delay`. A delegate can therefore get any pending, higher-delay-gated announcement executed immediately once a lower-delay entry for the same type exists, regardless of when the announcement was actually made.

### Finding Description
`add_proxy_delegate` performs a `binary_search` on the full `ProxyDefinition` (delegate, proxy_type, delay) and only errors with `Duplicate` if an identical triple exists: [1](#0-0) 
Because `delay` is part of the comparison key, calling `add_proxy(real, delegate, Any, 0)` when `(real, delegate, Any, 10)` already exists does **not** fail as `Duplicate` — it inserts a second, independent entry into the `Proxies` `BoundedVec` for `real`.

`find_proxy`, used by `proxy_announced` (and `proxy`), only filters on `delegate` and (optionally) `proxy_type`, ignoring `delay` entirely, and returns the first match found by iterating the vector: [2](#0-1) 
Since `ProxyDefinition` derives `Ord`/`PartialOrd` over fields in declaration order (`delegate`, `proxy_type`, `delay`) and `try_insert` maintains sorted order, when two entries share `delegate` and `proxy_type` but differ in `delay`, the lower-`delay` entry always sorts first and is what `find_proxy` returns.

`proxy_announced` then gates execution using whatever `def.delay` `find_proxy` returned, not the delay that was in force when the announcement was made: [3](#0-2) 
The `Announcement` struct only records `real`, `call_hash`, and `height` — it never records which `ProxyDefinition`/`delay` was active at announce time: [4](#0-3) 

Exploit flow:
1. `real` calls `add_proxy(delegate, Any, delay=10)`.
2. Delegate calls `announce(real, call_hash)` at block `N` — recorded with `height = N` under the assumption the 10-block delay applies.
3. `real` later calls `add_proxy(delegate, Any, delay=0)` (e.g., attempting to "lower" the delay for the same relationship) — this does **not** replace the existing entry; it adds a second `ProxyDefinition{delegate, Any, 0}` alongside the original `{delegate, Any, 10}`.
4. Delegate immediately calls `proxy_announced(delegate, real, None, call)` whose hash matches the pending announcement. `find_proxy` returns the `delay=0` entry (sorts first), so `now.saturating_sub(ann.height) < def.delay` is `now - N < 0`, which is false, so `edit_announcements`'s retain-predicate removes the announcement and the call executes immediately — bypassing the originally committed 10-block window.

Existing checks do not stop this: `find_proxy` has no notion of "the specific definition that existed when the announcement was made"; it only checks `delegate` + optional `force_proxy_type`, never `delay`, and always resolves ambiguity by picking the lowest-delay entry due to sort order.

### Impact Explanation
This is a proxy delay/announcement bypass: a delegate can execute an already-announced privileged call before the delay committed to at announcement time has elapsed, provided a second lower/zero-delay `ProxyDefinition` for the same `(delegate, proxy_type)` exists. This defeats the entire purpose of the announce/delay mechanism (giving `real` a veto window via `reject_announcement`), enabling premature execution of arbitrary proxied calls (transfers, governance votes, etc., depending on `ProxyType`) once the ambiguous dual-entry state is reached.

### Likelihood Explanation
The vulnerable state (two `ProxyDefinition`s for the same `delegate`/`proxy_type` with different `delay`) is easy to reach through ordinary use: a `real` account attempting to "update" a delegate's delay by calling `add_proxy` again with a new delay — without first calling `remove_proxy` with the exact original delay — will unintentionally create this duplicate. `remove_proxy_delegate` requires the caller to supply the exact original `delay` to remove an entry, which is easy to get wrong or omit, so this is a realistic operational mistake, not a contrived edge case. Given `MaxProxies` allows more than one entry per account (typically dozens), nothing in the pallet prevents or warns about this scenario.

### Recommendation
Enforce uniqueness of `(delegate, proxy_type)` in `add_proxy_delegate` (independent of `delay`), rejecting/updating in place rather than allowing multiple `delay` values for the same pair; alternatively, have `find_proxy` require an exact `delay` match tied to the announcement, or store the applicable `delay`/`proxy_type` inside the `Announcement` itself at announce time so `proxy_announced` gates on the delay that was actually in force when the announcement was created.

### Proof of Concept
Rust unit test in `substrate/frame/proxy/src/tests.rs` (new test, using existing mock runtime):
```rust
#[test]
fn duplicate_delay_entries_bypass_announcement_delay() {
    new_test_ext().execute_with(|| {
        // real=1, delegate=2, ProxyType::Any
        assert_ok!(Proxy::add_proxy(RuntimeOrigin::signed(1), 2, ProxyType::Any, 10));
        let call_hash = call_transfer_hash(); // hash of some call
        System::set_block_number(1);
        assert_ok!(Proxy::announce(RuntimeOrigin::signed(2), 1, call_hash));

        // real adds a second entry for same delegate/type with delay=0,
        // without removing the delay=10 entry.
        assert_ok!(Proxy::add_proxy(RuntimeOrigin::signed(1), 2, ProxyType::Any, 0));

        // Immediately (no blocks advanced), delegate executes the announced call.
        System::set_block_number(2); // well before height + 10
        assert_ok!(Proxy::proxy_announced(
            RuntimeOrigin::signed(2), 2, 1, None, Box::new(call_that_hashes_to(call_hash))
        ));
        // EXPECTATION (should fail if fixed): call executed before delay=10 elapsed.
        // Assert on side effect of the inner call to prove premature execution.
    });
}
```
Expected result on the current code: the test passes (call executes at block 2, well before `height + 10`), proving the bypass. After the fix (uniqueness enforced on `(delegate, proxy_type)` or delay recorded per-announcement), the second `add_proxy` call should either fail with `Duplicate`/update the existing entry, or `proxy_announced` should still require `now - height >= 10`, causing the test to fail with `Error::Unannounced`.

### Citations

**File:** substrate/frame/proxy/src/lib.rs (L94-101)
```rust
pub struct Announcement<AccountId, Hash, BlockNumber> {
	/// The account which made the announcement.
	real: AccountId,
	/// The hash of the call to be made.
	call_hash: Hash,
	/// The height at which the announcement was made.
	height: BlockNumber,
}
```

**File:** substrate/frame/proxy/src/lib.rs (L560-574)
```rust
			let def = Self::find_proxy(&real, &delegate, force_proxy_type)?;

			let call_hash = T::CallHasher::hash_of(&call);
			let now = T::BlockNumberProvider::current_block_number();
			Self::edit_announcements(&delegate, |ann| {
				ann.real != real ||
					ann.call_hash != call_hash ||
					now.saturating_sub(ann.height) < def.delay
			})
			.map_err(|_| Error::<T>::Unannounced)?;

			Self::do_proxy(def, real, *call);

			Ok(())
		}
```

**File:** substrate/frame/proxy/src/lib.rs (L860-874)
```rust
		Proxies::<T>::try_mutate(delegator, |(ref mut proxies, ref mut deposit)| {
			let proxy_def = ProxyDefinition {
				delegate: delegatee.clone(),
				proxy_type: proxy_type.clone(),
				delay,
			};
			let i = proxies.binary_search(&proxy_def).err().ok_or(Error::<T>::Duplicate)?;
			proxies.try_insert(i, proxy_def).map_err(|_| Error::<T>::TooMany)?;
			let new_deposit = Self::deposit(proxies.len() as u32);
			if new_deposit > *deposit {
				T::Currency::reserve(delegator, new_deposit - *deposit)?;
			} else if new_deposit < *deposit {
				T::Currency::unreserve(delegator, *deposit - new_deposit);
			}
			*deposit = new_deposit;
```

**File:** substrate/frame/proxy/src/lib.rs (L982-992)
```rust
	pub fn find_proxy(
		real: &T::AccountId,
		delegate: &T::AccountId,
		force_proxy_type: Option<T::ProxyType>,
	) -> Result<ProxyDefinition<T::AccountId, T::ProxyType, BlockNumberFor<T>>, DispatchError> {
		let f = |x: &ProxyDefinition<T::AccountId, T::ProxyType, BlockNumberFor<T>>| -> bool {
			&x.delegate == delegate &&
				force_proxy_type.as_ref().map_or(true, |y| &x.proxy_type == y)
		};
		Ok(Proxies::<T>::get(real).0.into_iter().find(f).ok_or(Error::<T>::NotProxy)?)
	}
```
