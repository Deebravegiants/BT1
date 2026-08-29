# [M] Owner proxy except sudo_set_sn_owner_hotkey carve-out is bypassable via the duplicate alias sudo_set_subnet_owner_hotkey

## Summary
Severity: Medium
Chain: Bittensor
Component: opentensor/subtensor
CWE: Incorrect Authorization
Published: 2026-06-17
Source: https://github.com/RaoFoundation/subtensor/security/advisories/GHSA-xm63-2wwx-pm6w
Type: github-advisory

## Details
## Summary
The `Owner` proxy type allows `AdminUtils::*` but carves out a single exception, `AdminUtils::sudo_set_sn_owner_hotkey` (call_index 67), to prevent an Owner-scoped delegate from changing the subnet owner hotkey. However, `pallet-admin-utils` exposes a second, live, non-deprecated extrinsic — `sudo_set_subnet_owner_hotkey` (call_index 64) — that calls the exact same backend `pallet_subtensor::do_set_sn_owner_hotkey`. The proxy filter matches the exception by call variant name, so call 64 is covered by the `AdminUtils::*` allow wildcard, is not in the `except` set, and is therefore permitted. An Owner-proxy delegate can change `SubnetOwnerHotkey` through call 64, fully defeating the carve-out it was designed to enforce.

## Details
The runtime defines the `Owner` proxy rule in the `define_proxy_filters!` DSL:

`runtime/src/lib.rs:693-699`
```rust
Owner => allow {
    AdminUtils::*,
    SubtensorModule::set_subnet_identity,
    SubtensorModule::update_symbol,
} except {
    AdminUtils::sudo_set_sn_owner_hotkey,
}
```

The proc-macro (`support/macros/src/proxy_filter.rs:308-322`) lowers an `allow … except …` rule to:

```rust
ProxyType::Owner => {
    matches!(c, RuntimeCall::AdminUtils(..) | /* set_subnet_identity */ | /* update_symbol */)
    && !matches!(c, RuntimeCall::AdminUtils(pallet_admin_utils::Call::sudo_set_sn_owner_hotkey { .. }))
}
```

The exception is keyed on the concrete call variant `sudo_set_sn_owner_hotkey`. Any other `AdminUtils` variant still satisfies `RuntimeCall::AdminUtils(..)` and is **not** excluded.

`pallet-admin-utils` defines two distinct call variants that perform the identical mutation:

`pallets/admin-utils/src/lib.rs:1544-1553` (call_index 64)
```rust
#[pallet::call_index(64)]
pub fn sudo_set_subnet_owner_hotkey(
    origin: OriginFor<T>,
    netuid: NetUid,
    hotkey: <T as frame_system::Config>::AccountId,
) -> DispatchResult {
```

_Trimmed to 38 lines — full report: https://github.com/RaoFoundation/subtensor/security/advisories/GHSA-xm63-2wwx-pm6w_
