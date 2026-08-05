The claim is confirmed by direct code inspection. The `pure_account` derivation at [1](#0-0)  includes `who` in the hash preimage, and `create_pure` derives `who` from `ensure_signed(origin)` — the caller's own account, unspoofable — before checking `Duplicate` and inserting `delegate: who.clone()` [2](#0-1) . Since `who` is bound to the caller and cannot be forged, no cross-account collision is derivable by an attacker against a distinct victim account, and `Duplicate` only triggers for identical repeated parameters from the same signer.

Audit Report

## Title
No vulnerability — `pure_account` derivation is spawner-bound and front-running yields at most `Duplicate`, never fund misdirection ([File: substrate/frame/proxy/src/lib.rs])

## Summary
The `pure_account` hash includes the calling account `who` as part of its preimage, alongside `height`, `ext_index`, `proxy_type`, and `index`. Because `who` is bound to the caller's own signed origin, an attacker cannot produce a colliding derivation for a victim's distinct account, and at worst can only trigger `Error::Duplicate` for their own repeated/identical call, not the victim's.

## Finding Description
`Pallet::pure_account` computes the entropy as `(b"modlpy/proxy____", who, height, ext_index, proxy_type, index)` hashed with `blake2_256`, then decoded into an `AccountId` via `TrailingZeroInput`. In `create_pure`, `who` is derived from `ensure_signed(origin)`, i.e., it is always the caller's own account — it cannot be supplied or spoofed by an attacker. For the attacker to make `Proxies::<T>::contains_key(&pure)` return true and block the victim, the attacker would need to compute the *same* `pure` account as the victim, which requires the same `(who, height, ext_index, proxy_type, index)` tuple. Since `who` differs (attacker's account vs. victim's account) and `blake2_256` is collision-resistant, the attacker cannot select `proxy_type`/`index` to force a hash collision against a different `who`.

## Impact Explanation
None. No cross-account collision is possible because `who` is part of the hash preimage and is bound to `ensure_signed` of the actual caller. The only "collision" scenario is the same signer submitting identical `create_pure` parameters twice at the same block/extrinsic-index, which correctly returns `Error::<T>::Duplicate` and does not reserve any additional deposit or create incorrect delegate attribution.

## Likelihood Explanation
Not applicable — the described attack path is not reachable given the account-binding of the hash preimage.

## Recommendation
No fix required.

## Proof of Concept
Existing test `pure_works` in [3](#0-2)  already demonstrates the relevant invariants: different spawners (`1`, `2`) with identical `proxy_type=Any`, `index=0` at the same block/ext_index produce distinct `pure` accounts, and repeating identical parameters for the same spawner at the same block/ext_index correctly fails with `Error::<Test>::Duplicate`.

### Citations

**File:** substrate/frame/proxy/src/lib.rs (L340-359)
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

			let proxy_def =
				ProxyDefinition { delegate: who.clone(), proxy_type: proxy_type.clone(), delay };
			let bounded_proxies: BoundedVec<_, T::MaxProxies> =
				vec![proxy_def].try_into().map_err(|_| Error::<T>::TooMany)?;

			let deposit = T::ProxyDepositBase::get() + T::ProxyDepositFactor::get();
			T::Currency::reserve(&who, deposit)?;

			Proxies::<T>::insert(&pure, (bounded_proxies, deposit));
```

**File:** substrate/frame/proxy/src/lib.rs (L826-841)
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
