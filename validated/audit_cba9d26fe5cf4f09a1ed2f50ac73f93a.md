### Title
`pallet-identity::set_subs` does not deduplicate sub-accounts, allowing an inflated `SubsOf` count and deposit-loss on removal - (File: `substrate/frame/identity/src/lib.rs`)

### Summary
`Pallet::set_subs` builds the caller's `SubsOf` bounded list by iterating over the caller-supplied `subs: Vec<(T::AccountId, Data)>` and pushing every entry into `ids` without checking whether the same sub-account is repeated within the input. This mirrors the reported `GlobalRegistryService::_updateInvestor` bug where the same wallet could be added multiple times to the same investor, inflating `walletCount`.

### Finding Description
In `set_subs` [1](#0-0) , the only anti-collision check performed is:
```rust
let not_other_sub =
    subs.iter().filter_map(|i| SuperOf::<T>::get(&i.0)).all(|i| i.0 == sender);
ensure!(not_other_sub, Error::<T>::AlreadyClaimed);
```
This only guards against claiming a sub-account that is already owned by *another* main account; it does not detect that `subs` itself contains the same `AccountId` more than once. The subsequent loop then unconditionally pushes every entry:
```rust
for (id, name) in subs {
    SuperOf::<T>::insert(&id, (sender.clone(), name));
    ids.try_push(id).expect("subs length is less than T::MaxSubAccounts; qed");
}
``` [2](#0-1) 
If the caller passes the same account twice (e.g. `[(A, data1), (A, data2)]`), `SuperOf` will simply be overwritten twice (harmless, single storage entry), but `ids` (the `SubsOf` bounded list) will contain `A` twice, and `new_subs = ids.len()` will count it as 2 sub-identities. The new deposit `Self::subs_deposit(subs.len())` is calculated from `subs.len()`, so the caller is charged for both duplicate slots even though only one unique `SuperOf` mapping exists.

This is the direct analog of the reported Solidity issue: an item that already logically belongs to the same owner is re-added instead of being treated as a no-op, inflating a bounded count (`walletCount` → `SubsOf` length) that is checked against a hard cap (`MAX_WALLETS_PER_INVESTOR` → `T::MaxSubAccounts`).

Downstream inconsistency in `remove_sub` compounds this: `sub_ids.retain(|x| x != &sub)` [3](#0-2)  removes **all** duplicate occurrences of `sub` from `sub_ids` in one call, but only a single `T::SubAccountDeposit::get()` amount is unreserved, regardless of how many duplicate slots were cleared — so deposit accounting no longer matches the true number of removed entries.

### Impact Explanation
- A user can artificially inflate their own `SubsOf` list toward `T::MaxSubAccounts`, consuming slots with duplicate entries and being prematurely blocked from registering additional (legitimate, distinct) sub-identities via `set_subs`/`add_sub` (`Error::TooManySubAccounts`).
- The deposit paid via `subs_deposit(subs.len())` no longer corresponds to the number of unique `SuperOf` records created, causing the caller to over-pay for phantom slots, and to lose part of that deposit permanently when `remove_sub`'s `retain` removes all duplicates but only refunds one `SubAccountDeposit`.
- Unlike the original Securitize report, this bug is **self-inflicted**: the caller can only corrupt their own `SubsOf`/deposit bookkeeping, not another account's state. There is no cross-account griefing path, no on-chain fund extraction from other users, and `clear_identity`/`kill_identity` still function correctly even with duplicate entries present (since they iterate and remove by key, tolerating repeats).

### Likelihood Explanation
High likelihood of reachability (any signed account with a registered identity can call `set_subs` with a crafted `Vec` containing repeated `AccountId`s), but the blast radius is confined to the caller's own account state and deposit — there is no unprivileged-attacker-vs-victim path, and no protocol-level accounting is broken (aggregate reserved balances still correspond to what was actually reserved). This significantly limits severity/likelihood relative to the original report, where wallet-count inflation could block administrative operations (including investor removal) performed by a service on behalf of end users.

### Recommendation
In `set_subs`, deduplicate the incoming `subs` vector (e.g., via a `BTreeSet`/`sort_unstable_by_key` + `dedup`) before computing `new_deposit` and populating `ids`, so that repeated entries for the same `AccountId` are collapsed into a single sub-identity, consistent with how `pallet-proxy::add_proxy_delegate` and `pallet-alliance::add_member` use `binary_search` + `Error::Duplicate`/`AlreadyMember` to reject (or ignore) redundant additions before mutating bounded storage [4](#0-3) .

### Proof of Concept
Conceptual PoC (analogous to the reported PoC against `updateInvestor`):
```rust
// caller `ten` has a registered identity, MaxSubAccounts >= 2
let subs = vec![
    (acct_a.clone(), Data::Raw(vec![1].try_into().unwrap())),
    (acct_a.clone(), Data::Raw(vec![2].try_into().unwrap())), // same account repeated
];
assert_ok!(Identity::set_subs(RuntimeOrigin::signed(ten.clone()), subs));

// SubsOf(ten) now reports 2 sub-accounts even though SuperOf(acct_a) is a single entry
let (deposit, ids) = SubsOf::<Test>::get(&ten);
assert_eq!(ids.len(), 2);                      // inflated count
assert_eq!(deposit, 2 * SubAccountDeposit);    // double-charged deposit for one unique sub
```
This can be validated against `substrate/frame/identity/src/lib.rs` lines 623-677 (`set_subs`) and lines 1088-1105 (`remove_sub`).

### Citations

**File:** substrate/frame/identity/src/lib.rs (L623-663)
```rust
		pub fn set_subs(
			origin: OriginFor<T>,
			subs: Vec<(T::AccountId, Data)>,
		) -> DispatchResultWithPostInfo {
			let sender = ensure_signed(origin)?;
			ensure!(IdentityOf::<T>::contains_key(&sender), Error::<T>::NotFound);
			ensure!(
				subs.len() <= T::MaxSubAccounts::get() as usize,
				Error::<T>::TooManySubAccounts
			);

			let (old_deposit, old_ids) = SubsOf::<T>::get(&sender);
			let new_deposit = Self::subs_deposit(subs.len() as u32);

			let not_other_sub =
				subs.iter().filter_map(|i| SuperOf::<T>::get(&i.0)).all(|i| i.0 == sender);
			ensure!(not_other_sub, Error::<T>::AlreadyClaimed);

			if old_deposit < new_deposit {
				T::Currency::reserve(&sender, new_deposit - old_deposit)?;
			} else if old_deposit > new_deposit {
				let err_amount = T::Currency::unreserve(&sender, old_deposit - new_deposit);
				debug_assert!(err_amount.is_zero());
			}
			// do nothing if they're equal.

			for s in old_ids.iter() {
				SuperOf::<T>::remove(s);
			}
			let mut ids = BoundedVec::<T::AccountId, T::MaxSubAccounts>::default();
			for (id, name) in subs {
				SuperOf::<T>::insert(&id, (sender.clone(), name));
				ids.try_push(id).expect("subs length is less than T::MaxSubAccounts; qed");
			}
			let new_subs = ids.len();

			if ids.is_empty() {
				SubsOf::<T>::remove(&sender);
			} else {
				SubsOf::<T>::insert(&sender, (new_deposit, ids));
			}
```

**File:** substrate/frame/identity/src/lib.rs (L1093-1103)
```rust
			let (sup, _) = SuperOf::<T>::get(&sub).ok_or(Error::<T>::NotSub)?;
			ensure!(sup == sender, Error::<T>::NotOwned);
			SuperOf::<T>::remove(&sub);
			SubsOf::<T>::mutate(&sup, |(ref mut subs_deposit, ref mut sub_ids)| {
				sub_ids.retain(|x| x != &sub);
				let deposit = T::SubAccountDeposit::get().min(*subs_deposit);
				*subs_deposit -= deposit;
				let err_amount = T::Currency::unreserve(&sender, deposit);
				debug_assert!(err_amount.is_zero());
				Self::deposit_event(Event::SubIdentityRemoved { sub, main: sender, deposit });
			});
```

**File:** substrate/frame/proxy/src/lib.rs (L860-867)
```rust
		Proxies::<T>::try_mutate(delegator, |(ref mut proxies, ref mut deposit)| {
			let proxy_def = ProxyDefinition {
				delegate: delegatee.clone(),
				proxy_type: proxy_type.clone(),
				delay,
			};
			let i = proxies.binary_search(&proxy_def).err().ok_or(Error::<T>::Duplicate)?;
			proxies.try_insert(i, proxy_def).map_err(|_| Error::<T>::TooMany)?;
```
