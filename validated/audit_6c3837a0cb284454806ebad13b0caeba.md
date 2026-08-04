The referenced file `cumulus/primitives/core/src/scheduling.rs` contains only V3 candidate scheduling structures (`SchedulingInfoPayload`, `SignedSchedulingInfo`, `SchedulingProof`) for collator core-selection and has nothing to do with `pallet_proxy` or `create_pure`. The actual `pure_account` derivation lives in `substrate/frame/proxy/src/lib.rs`. Analysis is based on that real function.

### Title
No vulnerability — `pure_account` derivation is spawner-bound and front-running yields at most `Duplicate`, never fund misdirection ([File: substrate/frame/proxy/src/lib.rs])

### Summary
The `pure_account` hash includes the calling account `who` as part of its preimage, alongside `height`, `ext_index`, `proxy_type`, and `index`. Because `who` is bound to the caller's own signed origin, an attacker cannot produce a colliding derivation for a victim's distinct account, and at worst can only trigger `Error::Duplicate` for their own repeated/identical call, not the victim's.

### Finding Description
`Pallet::pure_account` computes the entropy as `(b"modlpy/proxy____", who, height, ext_index, proxy_type, index)` hashed with `blake2_256`, then decoded into an `AccountId` via `TrailingZeroInput` [1](#0-0) . In `create_pure`, `who` is derived from `ensure_signed(origin)`, i.e., it is always the caller's own account — it cannot be supplied or spoofed by an attacker [2](#0-1) .

For the attacker to make `Proxies::<T>::contains_key(&pure)` return true and block the victim, the attacker would need to compute the *same* `pure` account as the victim, which requires the same `(who, height, ext_index, proxy_type, index)` tuple. Since `who` differs (attacker's account vs. victim's account) and `blake2_256` is collision-resistant, the attacker cannot select `proxy_type`/`index` to force a hash collision against a *different* `who`. This is confirmed by the existing test `pure_works`, which shows that different spawners (`1` vs `2`) with identical `proxy_type`/`index`/block/ext-index produce distinct pure accounts (`anon` vs `anon2`) [3](#0-2) , and that `Duplicate` only occurs when the *same* signer repeats the exact same parameters at the same height/ext_index [4](#0-3) .

The scoped concern about "victim's deposit reserved against an account the attacker already controls as delegate" cannot occur either: the `ProxyDefinition` inserted into `Proxies::<T>` always sets `delegate: who.clone()` where `who` is the actual caller of `create_pure` [5](#0-4) . Since the derived pure account already encodes `who`, an attacker's `create_pure` call would only ever create/own an account keyed to their own `who`; it cannot silently attach itself as delegate to an account derived from the victim's `who`.

### Impact Explanation
None. No cross-account collision is possible because `who` is part of the hash preimage and is bound to `ensure_signed` of the actual caller. The only "collision" scenario is the same signer submitting identical `create_pure` parameters twice at the same block/extrinsic-index, which correctly returns `Error::<T>::Duplicate` and does not reserve any additional deposit or create incorrect delegate attribution.

### Likelihood Explanation
Not applicable — the described attack path is not reachable given the account-binding of the hash preimage.

### Recommendation
No fix required. If desired for defense-in-depth documentation, the doc comment on `pure_account`/`create_pure` could be extended to explicitly state that the derivation is spawner-bound and thus front-running across different spawners is infeasible, but this is not a functional change.

### Proof of Concept
Existing test `pure_works` in `substrate/frame/proxy/src/tests.rs` already demonstrates the relevant invariants: different spawners (`1`, `2`) with identical `proxy_type=Any`, `index=0` at the same block/ext_index produce distinct `pure` accounts (`anon` != `anon2`), and repeating identical parameters for the *same* spawner at the same block/ext_index correctly fails with `Error::<Test>::Duplicate` [6](#0-5) . An additional integration test could explicitly assert `Proxy::pure_account(&attacker, &pt, idx, Some((h, ei))) != Proxy::pure_account(&victim, &pt, idx, Some((h, ei)))` for all attacker-chosen `pt`/`idx` at a fixed `(h, ei)`, confirming no exploitable collision exists.

### Citations

**File:** substrate/frame/proxy/src/lib.rs (L340-349)
```rust
		pub fn create_pure(
			origin: OriginFor<T>,
			proxy_type: T::ProxyType,
			delay: BlockNumberFor<T>,
			index: u16,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;

			let pure = Self::pure_account(&who, &proxy_type, index, None);
			ensure!(!Proxies::<T>::contains_key(&pure), Error::<T>::Duplicate);
```

**File:** substrate/frame/proxy/src/lib.rs (L351-359)
```rust
			let proxy_def =
				ProxyDefinition { delegate: who.clone(), proxy_type: proxy_type.clone(), delay };
			let bounded_proxies: BoundedVec<_, T::MaxProxies> =
				vec![proxy_def].try_into().map_err(|_| Error::<T>::TooMany)?;

			let deposit = T::ProxyDepositBase::get() + T::ProxyDepositFactor::get();
			T::Currency::reserve(&who, deposit)?;

			Proxies::<T>::insert(&pure, (bounded_proxies, deposit));
```

**File:** substrate/frame/proxy/src/lib.rs (L826-843)
```rust
	pub fn pure_account(
		who: &T::AccountId,
		proxy_type: &T::ProxyType,
		index: u16,
		maybe_when: Option<(BlockNumberFor<T>, u32)>,
	) -> T::AccountId {
		let (height, ext_index) = maybe_when.unwrap_or_else(|| {
			(
				T::BlockNumberProvider::current_block_number(),
				frame_system::Pallet::<T>::extrinsic_index().unwrap_or_default(),
			)
		});

		let entropy = (b"modlpy/proxy____", who, height, ext_index, proxy_type, index)
			.using_encoded(blake2_256);
		Decode::decode(&mut TrailingZeroInput::new(entropy.as_ref()))
			.expect("infinite length input; no invalid inputs for type; qed")
	}
```

**File:** substrate/frame/proxy/src/tests.rs (L565-596)
```rust
#[test]
fn pure_works() {
	new_test_ext().execute_with(|| {
		Balances::make_free_balance_be(&1, 11); // An extra one for the ED.
		assert_ok!(Proxy::create_pure(RuntimeOrigin::signed(1), ProxyType::Any, 0, 0));
		let anon = Proxy::pure_account(&1, &ProxyType::Any, 0, None);
		System::assert_last_event(
			ProxyEvent::PureCreated {
				pure: anon,
				who: 1,
				proxy_type: ProxyType::Any,
				disambiguation_index: 0,
				at: <Test as Config>::BlockNumberProvider::current_block_number(),
				extrinsic_index: System::extrinsic_index().unwrap(),
			}
			.into(),
		);

		// other calls to pure allowed as long as they're not exactly the same.
		assert_ok!(Proxy::create_pure(RuntimeOrigin::signed(1), ProxyType::JustTransfer, 0, 0));
		assert_ok!(Proxy::create_pure(RuntimeOrigin::signed(1), ProxyType::Any, 0, 1));
		let anon2 = Proxy::pure_account(&2, &ProxyType::Any, 0, None);
		assert_ok!(Proxy::create_pure(RuntimeOrigin::signed(2), ProxyType::Any, 0, 0));
		assert_noop!(
			Proxy::create_pure(RuntimeOrigin::signed(1), ProxyType::Any, 0, 0),
			Error::<Test>::Duplicate
		);
		System::set_extrinsic_index(1);
		assert_ok!(Proxy::create_pure(RuntimeOrigin::signed(1), ProxyType::Any, 0, 0));
		System::set_extrinsic_index(0);
		System::set_block_number(2);
		assert_ok!(Proxy::create_pure(RuntimeOrigin::signed(1), ProxyType::Any, 0, 0));
```
