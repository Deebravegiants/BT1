### Title
Proxy `InstanceFilter` check is bypassed for calls wrapped in `Multisig::as_multi_threshold_1` because the origin substitution the multisig pallet performs does not carry forward the filter `Proxy::do_proxy` attached to the original origin - (File: substrate/frame/proxy/src/lib.rs)

### Summary
`Proxy::do_proxy` enforces `InstanceFilter::filter` by attaching a filter closure to the `RawOrigin::Signed(real)` origin via `origin.add_filter(...)` and then calling `call.dispatch(origin)` [1](#0-0) . When the wrapped `call` is `Multisig::as_multi_threshold_1`, that pallet function derives a brand-new `RawOrigin::Signed(multi_account_id(&signatories, 1))` and dispatches the inner (nested) `call` on that fresh origin object, which never inherited the filter closure attached in `do_proxy`. As a result the inner call is not checked by `def.proxy_type.filter(c)` at all.

### Finding Description
`do_proxy` builds an origin `Signed(real)` and pushes a filter closure onto it that inspects only the *immediate* `Call` passed to `dispatch` (`_ => def.proxy_type.filter(c)`), matching solely on the outer `RuntimeCall` variant [2](#0-1) . If the delegate's `ProxyType` permits `RuntimeCall::Multisig(..)`, the outer call `Multisig::as_multi_threshold_1{ other_signatories: [], call: privileged_call }` passes this check unconditionally, because the closure never unwraps `privileged_call`.

Inside `pallet_multisig`, `as_multi_threshold_1` computes `who = ensure_signed(origin)?` (still `real`, since the filter only restricts *which* calls the origin may execute, not the account behind it), builds `signatories` including `who`, derives `id = Self::multi_account_id(&signatories, 1)`, and dispatches the wrapped call with a **freshly constructed** `RawOrigin::Signed(id).into()` origin object — not the filtered origin instance passed into the extrinsic. Because `OriginTrait::add_filter` closures live on the specific origin value (not derived deterministically from the account id), this brand-new origin carries no filter stack, so `privileged_call` executes without ever being evaluated against `def.proxy_type.filter(c)`.

This differs fundamentally from `pallet_utility::batch`, which reuses the *same* origin object for nested dispatches, so filters chain correctly there. `pallet_multisig`'s account-changing dispatch breaks that chain.

### Impact Explanation
The scoped impact is that the proxy `InstanceFilter` can be evaded for any call type by wrapping it in `Multisig::as_multi_threshold_1`, as long as the outer `Multisig` call variant itself is permitted by the delegate's `ProxyType` (e.g. `NonTransfer`-style filters that allow `RuntimeCall::Multisig(..)`). The `privileged_call` executes under `Signed(multi_account_id(&[real],1))`, a deterministic pseudonym account derived from `real`, rather than being rejected as the filter design intends.

Note that the effective blast radius of this specific dispatch is bounded by the fact that the resulting origin is not `real`'s primary account but a distinct, normally-unfunded pseudonym account tied to it; any asset-moving `privileged_call` acts on that pseudonym account's own state, not `real`'s balance directly. The concrete, guaranteed exploit is therefore a **filter-bypass / unauthorized-dispatch** issue (violating "unauthorized privileged state transitions must not be accepted" and "proxy approvals must not be effectively forgeable/circumventable"), rather than a guaranteed drain of `real`'s primary funds — unless that specific derived pseudonym account happens to hold assets/roles (e.g., from a prior legitimate `as_multi_threshold_1` call by `real`).

### Likelihood Explanation
This is deterministically reproducible with no special preconditions beyond: (1) `real` has added `delegate` as a proxy with a `ProxyType` that permits `RuntimeCall::Multisig(..)` (a common configuration, e.g. `NonTransfer`), and (2) `delegate` submits `Proxy::proxy(real, None, Multisig::as_multi_threshold_1{ other_signatories: [], call: privileged_call })`. No signatures, races, or governance actions are required — it is a single, always-available extrinsic sequence.

### Recommendation
Have `Proxy`'s filter (or `InstanceFilter::filter` implementations) recursively unwrap known origin-changing composite calls (`Multisig::as_multi`, `Multisig::as_multi_threshold_1`, and similarly any future pallet that redirects to a derived origin) and apply the filter to the inner call as well, or disallow `RuntimeCall::Multisig(..)` entirely for restrictive `ProxyType`s that are not `Any`. Alternatively/additionally, fix `pallet_multisig::as_multi_threshold_1` to dispatch the inner call while preserving/propagating the caller origin's filter chain rather than constructing a filter-free origin from scratch.

### Proof of Concept
Integration test in `substrate/frame/proxy/src/tests.rs` (or a combined proxy+multisig mock runtime):
1. Configure a mock `ProxyType::NonTransfer` whose `filter()` returns `false` for `RuntimeCall::SomePrivilegedPallet(..)` but `true` for `RuntimeCall::Multisig(..)`.
2. `Proxy::add_proxy(real, delegate, ProxyType::NonTransfer, 0)`.
3. Directly assert `ProxyType::NonTransfer.filter(&RuntimeCall::SomePrivilegedPallet(privileged_call.clone()))` returns `false` (baseline: direct call is blocked).
4. Call `Proxy::proxy(delegate_origin, real, None, Box::new(RuntimeCall::Multisig(pallet_multisig::Call::as_multi_threshold_1 { other_signatories: vec![], call: Box::new(privileged_call.clone()) })))`.
5. Assert that `privileged_call`'s state effect (e.g. a storage write, event, or balance change on `multi_account_id(&[real],1)`) **did occur**, proving the filter was bypassed, contrary to the expectation that `NonTransfer` should have blocked it.
6. Contrast with an equivalent direct `Proxy::proxy(delegate_origin, real, None, privileged_call)` call which correctly returns `Err`/filtered result, demonstrating the discrepancy is specific to the `Multisig::as_multi_threshold_1` wrapping.

### Citations

**File:** substrate/frame/proxy/src/lib.rs (L999-1024)
```rust
		use frame::traits::{InstanceFilter as _, OriginTrait as _};
		// This is a freshly authenticated new account, the origin restrictions doesn't apply.
		let mut origin: T::RuntimeOrigin = frame_system::RawOrigin::Signed(real).into();
		origin.add_filter(move |c: &<T as frame_system::Config>::RuntimeCall| {
			let c = <T as Config>::RuntimeCall::from_ref(c);
			// We make sure the proxy call does access this pallet to change modify proxies.
			match c.is_sub_type() {
				// Proxy call cannot add or remove a proxy with more permissions than it already
				// has.
				Some(Call::add_proxy { ref proxy_type, .. }) |
				Some(Call::remove_proxy { ref proxy_type, .. })
					if !def.proxy_type.is_superset(proxy_type) =>
				{
					false
				},
				// Proxy call cannot remove all proxies or kill pure proxies unless it has full
				// permissions.
				Some(Call::remove_proxies { .. }) | Some(Call::kill_pure { .. })
					if def.proxy_type != T::ProxyType::default() =>
				{
					false
				},
				_ => def.proxy_type.filter(c),
			}
		});
		let e = call.dispatch(origin);
```
