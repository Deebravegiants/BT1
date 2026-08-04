I'll investigate whether an analogous pattern exists in the Polkadot SDK — specifically any place where a permission/filter check validates only a call's selector/discriminant (like a function signature) and then permits arbitrary/extensible sub-logic (like the 0x transformer nonces) without further validation.## Analysis Result

The report's vulnerability class — **a permission gate that filters one specific "bad" invocation at a single choke point, while any other path that ends up dispatching the same underlying logic under the same privileged origin is left completely unguarded** — has a plausible analog in this repo's **custom `pallet-recovery`** implementation.

### Root cause

`Pallet::control_inherited_account` in `substrate/frame/recovery/src/lib.rs` lets the `inheritor` of a recovered account dispatch **any** call as the `recovered` account, explicitly *except* calls belonging to the Recovery pallet itself: [1](#0-0) 

The "reentrancy guard" is implemented as a **locally-scoped** filter attached to a freshly-constructed `RawOrigin::Signed(recovered)` origin object: [2](#0-1) 

This filter only exists for the duration of this one `call.dispatch(origin)` invocation — it is not persisted anywhere, and it only excludes calls whose `is_sub_type()` resolves to the Recovery pallet's own `Call` enum (`c.is_sub_type().is_none()`). Any other pallet's call — e.g. `pallet_proxy::add_proxy` — is **not** filtered, exactly like the 0x controller in the external report only validating `sig == 0x415565b0` and then allowing everything downstream unconditionally.

The included regression tests in `substrate/frame/recovery/src/tests.rs` (`inheritor_can_slash_higher_priority_attempts_and_remove_friend_groups`, `inheritor_cannot_bypass_filter_via_utility_batch`) confirm the pallet authors were specifically worried about the inheritor circumventing this restriction, and that direct recursive dispatch (`Utility::batch` wrapping) is blocked because `Utility::batch` re-enters the same filtered `RuntimeCall::dispatch` path with the same origin object: [3](#0-2) 

However, `pallet-proxy` establishes delegated dispatch via a **brand-new** signed origin for the `real` account (this is the pallet's documented purpose — "allowing accounts to give permission to other accounts to dispatch types of calls from their signed origin"): [4](#0-3) 

Because `control_inherited_account` itself permits arbitrary non-Recovery calls, the inheritor can use it to call `Proxy::add_proxy(delegate = <inheritor or any account>, proxy_type = Any, delay = 0)` **as the `recovered` account**. This creates a standing Proxy relationship completely outside of Recovery's local filter scope. On a subsequent, independent extrinsic, the delegate can call `Proxy::proxy(real = recovered, call = Recovery::slash_attempt{...} or Recovery::set_friend_groups{...})`. This dispatch path builds its own fresh `Signed(recovered)` origin inside `pallet-proxy` and never touches the one-shot filter that `control_inherited_account` created — so the Recovery pallet's own protection (its stated purpose is exactly to stop the inheritor from "messing with the recovery configuration and possibly cancel[ing] or slash[ing] attempts from higher-priority friend groups") is bypassed.

**Important caveat:** I could not fully re-verify the body of `pallet_proxy::proxy()` in this pass (ran out of tool iterations after confirming only the module doc comment and general Substrate proxy semantics, which construct a fresh `Signed` origin from the `real` account and check permissions via `Config::ProxyType`, not via any caller-supplied filter). This is consistent with upstream Substrate's well-known `pallet-proxy` design, but I recommend explicitly re-reading `substrate/frame/proxy/src/lib.rs`'s `proxy` and `proxy_announced` dispatchables to confirm the origin construction before finalizing any report, since this repo's pallets have been non-trivially modified from upstream (e.g. `pallet-recovery`'s "friend groups"/"inheritance priority" model does not exist upstream).

### Title
Recovery pallet's `control_inherited_account` reentrancy filter is a one-shot, path-specific gate bypassable via `pallet-proxy` delegation — (File: `substrate/frame/recovery/src/lib.rs`)

### Summary
`control_inherited_account` blocks the inheritor from directly dispatching Recovery-pallet calls as the `recovered` account, but does not prevent the inheritor from first granting itself (or a third party) an "Any" `pallet-proxy` delegation over `recovered`, then using that proxy relationship — a completely separate dispatch path that builds its own unfiltered origin — to call the very same Recovery extrinsics (`slash_attempt`, `set_friend_groups`) that the guard was designed to block.

### Finding Description
The guard in `control_inherited_account` (lines 580–589) is attached to a locally created `RuntimeOrigin` object and is checked only for the single `call.dispatch(origin)` performed inside that function body. It filters solely by `is_sub_type()` against the Recovery pallet's `Call` enum, not by any broader notion of "calls that could indirectly re-enter Recovery's privileged state." Since arbitrary non-Recovery calls (such as `pallet_proxy::add_proxy`) are permitted through this same gate, the inheritor can escalate privilege by installing a persistent Proxy relationship on `recovered`, then invoke Recovery calls through `pallet_proxy::proxy` in a later, independent extrinsic where Recovery's filter is never constructed or consulted at all.

### Impact Explanation
An inheritor of a lower-priority friend group (or any account they collude with/authorize via proxy) can slash a higher-priority group's in-flight recovery attempt (`slash_attempt`) or wipe/change `FriendGroups` (`set_friend_groups`) for the `recovered` account — exactly the abuse scenario the pallet's own documentation says it is designed to prevent. This directly undermines the priority/conflict-resolution guarantees central to the pallet's design (see the pallet's `## Scenario: Multiple friend groups...` doc), potentially letting a malicious or compromised low-priority inheritor permanently lock out a legitimate higher-priority recovery.

### Likelihood Explanation
High, if `pallet-proxy` is included alongside this custom `pallet-recovery` in a runtime (as is typical, e.g. it's already used together in the same "system chain" pattern in this repo). No privileged role is required: any account that becomes an `inheritor` (a normal, permissionless outcome of the recovery mechanism itself) can execute this two-step bypass using entirely public extrinsics.

### Recommendation
Do not rely on a one-shot origin filter scoped only to a single dispatch call. Instead:
- Track "recovered" accounts persistently (e.g. a storage flag) and enforce the Recovery-call restriction at `BaseCallFilter` or via a `SignedExtension`/`CallFilter` that inspects the *resolved* dispatch origin for every extrinsic (including those coming via `pallet-proxy`, `pallet-multisig`, `pallet-utility::as_derivative`, etc.), not just calls originating from within `control_inherited_account`.
- Alternatively, explicitly disallow proxy/multisig/derivative delegation from being set up for accounts currently under active `Inheritor` control, or filter `pallet_proxy::add_proxy` (and similar delegation-creating calls) inside `control_inherited_account`'s scope in addition to Recovery's own calls.

### Proof of Concept
1. Alice's account is recovered; `Inheritor::<T>::get(alice) = (priority=1, inheritor=FERDIE, ..)` (a lower-priority group already finished recovery).
2. A higher-priority "Family" group (priority 0) calls `initiate_attempt` against Alice's account — `substrate/frame/recovery/src/lib.rs:687-746`.
3. FERDIE calls `Recovery::control_inherited_account(origin=FERDIE, recovered=Alice, call=Proxy::add_proxy{ delegate: FERDIE, proxy_type: Any, delay: 0 })`. This call is *not* a Recovery-pallet call, so it passes the local filter at `lib.rs:583-586` and is dispatched as `Signed(Alice)` — granting FERDIE an unrestricted proxy over Alice.
4. In a separate, later extrinsic, FERDIE calls `Proxy::proxy(real=Alice, call=Recovery::slash_attempt{friend_group_index: 0})`. This path never constructs Recovery's reentrancy filter, so the Family group's higher-priority attempt is slashed, and its security deposit is burned — the exact "VULNERABILITY" scenario the pallet's own tests were written to prevent (`substrate/frame/recovery/src/tests.rs:1353-1421`), but through an unguarded side-channel.

### Citations

**File:** substrate/frame/recovery/src/lib.rs (L567-601)
```rust
		pub fn control_inherited_account(
			origin: OriginFor<T>,
			recovered: AccountIdLookupOf<T>,
			call: Box<<T as Config>::RuntimeCall>,
		) -> DispatchResult {
			let maybe_inheritor = ensure_signed(origin)?;
			let recovered = T::Lookup::lookup(recovered)?;

			let inheritor = Inheritor::<T>::get(&recovered)
				.map(|(_, inheritor, _ticket)| inheritor)
				.ok_or(Error::<T>::NoInheritor)?;
			ensure!(maybe_inheritor == inheritor, Error::<T>::NotInheritor);

			let mut origin: T::RuntimeOrigin =
				frame_system::RawOrigin::Signed(recovered.clone()).into();
			// Reentrancy guard
			origin.add_filter(|c: &<T as frame_system::Config>::RuntimeCall| {
				let c = <T as Config>::RuntimeCall::from_ref(c);
				c.is_sub_type().is_none()
			});

			let call_hash = call.using_encoded(&T::Hashing::hash);
			let call_result = call.dispatch(origin).map(|_| ()).map_err(|r| r.error);

			Self::deposit_event(Event::<T>::RecoveredAccountControlled {
				recovered,
				inheritor,
				call_hash,
				call_result,
			});

			// NOTE: We ALWAYS return okay if the caller had the permission to control the lost
			// account regardless of the inner call result.
			Ok(())
		}
```

**File:** substrate/frame/recovery/src/tests.rs (L1423-1477)
```rust
/// Verify that wrapping a recovery call inside Utility::batch does not bypass the filter.
#[test]
fn inheritor_cannot_bypass_filter_via_utility_batch() {
	new_test_ext().execute_with(|| {
		let family = FriendGroupOf::<T> {
			friends: friends([BOB, CHARLIE]),
			friends_needed: 1,
			inheritor: DAVE,
			inheritance_delay: 10,
			inheritance_priority: 0,
			cancel_delay: 5,
		};
		let friends_group = FriendGroupOf::<T> {
			friends: friends([CHARLIE, EVE]),
			friends_needed: 1,
			inheritor: FERDIE,
			inheritance_delay: 1,
			inheritance_priority: 1,
			cancel_delay: 5,
		};
		assert_ok!(Recovery::set_friend_groups(signed(ALICE), vec![family, friends_group]));

		// Friends group recovers first (CHARLIE's auto-approval reaches the threshold).
		assert_ok!(Recovery::initiate_attempt(signed(CHARLIE), ALICE, 1));
		inc_block_number(2);
		assert_ok!(Recovery::finish_attempt(signed(EVE), ALICE, 1));
		assert_eq!(Recovery::inheritor(ALICE), Some(FERDIE));

		// Family initiates higher-priority attempt
		assert_ok!(Recovery::initiate_attempt(signed(BOB), ALICE, 0));
		let bob_balance_before = <Test as Config>::Currency::total_balance(&BOB);

		// FERDIE wraps the slash inside a utility::batch call to try to bypass the filter
		let slash_call: RuntimeCall = RecoveryCall::slash_attempt { friend_group_index: 0 }.into();
		let batch_call: RuntimeCall =
			pallet_utility::Call::batch { calls: vec![slash_call] }.into();
		assert_ok!(Recovery::control_inherited_account(
			signed(FERDIE),
			ALICE,
			Box::new(batch_call),
		));

		// The batch dispatched as ALICE, but the inner slash should have still executed
		// since our filter only checks the outer call. Check if BOB was slashed:
		let bob_balance_after = <Test as Config>::Currency::total_balance(&BOB);
		let was_slashed = bob_balance_after < bob_balance_before;

		if was_slashed {
			panic!(
				"BYPASS: recovery call filter was circumvented via utility::batch! \
				 BOB lost {} from security deposit slash.",
				bob_balance_before - bob_balance_after
			);
		}
	});
```

**File:** substrate/frame/proxy/src/lib.rs (L18-24)
```rust
//! # Proxy Pallet
//! A pallet allowing accounts to give permission to other accounts to dispatch types of calls from
//! their signed origin.
//!
//! The accounts to which permission is delegated may be required to announce the action that they
//! wish to execute some duration prior to execution happens. In this case, the target account may
//! reject the announcement and in doing so, veto the execution.
```
