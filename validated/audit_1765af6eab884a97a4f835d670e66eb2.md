### Title
`do_proxy` gates `remove_proxies`/`kill_pure` on `ProxyType::default()` equality rather than an enforced "full permission" marker - (File: substrate/frame/proxy/src/lib.rs)

### Summary
`do_proxy` blocks `remove_proxies`/`kill_pure` calls unless the acting proxy's `proxy_type` equals `T::ProxyType::default()`. The pallet never verifies that `default()` actually represents the maximally-permissive variant; it merely assumes runtime authors configure it that way. If a runtime's `ProxyType::default()` is not the full-permission ("Any"-equivalent) variant, any proxy holding that nominal default type can call `remove_proxies`/`kill_pure`, including on a `create_pure`-spawned account, even though it was never intended to hold full control.

### Finding Description
In `do_proxy` [1](#0-0) , the filter closure blocks `remove_proxies`/`kill_pure` only when `def.proxy_type != T::ProxyType::default()`. Equivalently, it *permits* these dangerous calls whenever `def.proxy_type == T::ProxyType::default()`, per the comment "unless it has full permissions" — a comment that is only true if `default()` is defined by the runtime to correspond to the maximal-privilege variant (e.g. `Any`). Nothing in `pallet-proxy`'s `Config` trait or in `do_proxy` itself validates or constrains what `T::ProxyType::default()` must semantically represent; it is purely a runtime integrator convention (commonly achieved by placing the `Any` variant first in the enum so `#[derive(Default)]` selects it).

Given the described call sequence:
1. `create_pure(proxy_type = default, ...)` establishes a pure proxy account whose owner proxy relationship uses `ProxyType::default()`.
2. A second party is granted `add_proxy` with the same `default` type on the pure account (permitted trivially, since `is_superset` of a type against itself is true, and the pure account owner is authorized to add proxies of any type it already effectively controls).
3. That second party calls `proxy(pure, None, Proxy::remove_proxies{})`. Because their `def.proxy_type == T::ProxyType::default()`, the guard at line 1017 does **not** block the call, so it proceeds to `_ => def.proxy_type.filter(c)`, and if the runtime's `InstanceFilter` implementation for the default type also permits proxy-management calls, `remove_proxies` executes and wipes the pure account's proxy list.

The vulnerability's precondition is entirely a runtime-configuration hazard: if `ProxyType::default()` is defined as anything less than the full-permission type, this security-critical invariant ("only full-permission proxies may nuke a proxy list / kill a pure proxy") silently degrades to "only proxies of the nominal default type may do so," regardless of that type's actual privilege level. The pallet provides no compile-time or runtime assertion tying `Default` to "maximal privilege," so the invariant is implicit and unenforced in code.

### Impact Explanation
If exploited under the stated precondition, a lower-privileged delegate can irreversibly strip all proxies from (or fully kill, in the `kill_pure` case) a `create_pure` account, without ever having been granted `Any`-level trust. Since pure proxy accounts are frequently used as multi-party controlled vaults/treasuries, this can permanently sever legitimate stakeholders' proxy-based access to funds held by the pure account, matching the scoped impact of irreversible proxy-control loss / fund lock.

### Likelihood Explanation
This is entirely conditional on a runtime misconfiguration: `T::ProxyType::default()` must resolve to something other than the fully-permissive variant. In all first-party runtimes in this repo (Polkadot, Kusama-style, Westend, Rococo, Asset Hub, Collectives, Coretime, People, node-template) the convention of placing `Any` first (thus making it `Default`) is followed, so this exact attack is not reachable there today. However, the pallet does not enforce this anywhere, so any custom/third-party runtime that defines `ProxyType` with a non-`Any` first variant (or manually implements `Default` incorrectly) silently inherits this bypass with no compiler or runtime error to flag the misconfiguration. This makes the flaw latent and dependent solely on integrator diligence rather than any pallet-level protection.

### Recommendation
Do not overload `Default` as a stand-in for "full permission" in `do_proxy`. Instead:
- Add an explicit trait method/associated constant to the `InstanceFilter`-implementing `ProxyType` (or extend `InstanceFilter`) such as `fn is_full_permission(&self) -> bool` or a dedicated `T::ProxyType::FULL` associated constant, and use it in place of `T::ProxyType::default()` in the guard at `substrate/frame/proxy/src/lib.rs:1017`.
- Alternatively, require and enforce (e.g., via a runtime benchmark/test helper or a `#[cfg(debug_assertions)]` runtime-genesis check) that `T::ProxyType::default()` is the unique maximal element under `is_superset` for all other variants, failing pallet construction/tests otherwise.

### Proof of Concept
Rust unit test in `substrate/frame/proxy/src/tests.rs` style, using a custom mock `ProxyType` enum where the `Default` variant is deliberately restrictive (e.g., `ProxyType::JustTransfer` as variant 0/default, `ProxyType::Any` as a separate non-default variant):
```rust
// mock ProxyType: JustTransfer (index 0, Default) < Any
// is_superset: Any.is_superset(anything) = true; JustTransfer.is_superset(JustTransfer) = true; else false

#[test]
fn lower_priv_default_type_can_remove_proxies_on_pure() {
    new_test_ext().execute_with(|| {
        // owner creates pure account with proxy_type = default (JustTransfer)
        assert_ok!(Proxy::create_pure(RuntimeOrigin::signed(1), ProxyType::JustTransfer, 0, 0));
        let pure = pure_account(&1, &ProxyType::JustTransfer, 0, None);

        // owner grants account 2 a JustTransfer proxy (== default) on the pure account
        assert_ok!(Proxy::add_proxy(RuntimeOrigin::signed(pure), 2, ProxyType::JustTransfer, 0));

        // account 2 (not Any-privileged) calls remove_proxies via the pure account
        let call = Box::new(RuntimeCall::Proxy(ProxyCall::remove_proxies {}));
        assert_ok!(Proxy::proxy(RuntimeOrigin::signed(2), pure, None, call));

        // Assert: pure account's proxy list is now empty, despite account 2 never holding Any
        assert_eq!(Proxy::proxies(pure).0.len(), 0);
    });
}
```
Expected assertion: `remove_proxies` dispatch succeeds and empties `Proxies::<T>::get(pure)`, demonstrating that a non-`Any` proxy whose type merely matches a misconfigured `ProxyType::default()` can destroy the pure account's entire proxy list.

### Citations

**File:** substrate/frame/proxy/src/lib.rs (L1014-1020)
```rust
				// Proxy call cannot remove all proxies or kill pure proxies unless it has full
				// permissions.
				Some(Call::remove_proxies { .. }) | Some(Call::kill_pure { .. })
					if def.proxy_type != T::ProxyType::default() =>
				{
					false
				},
```
