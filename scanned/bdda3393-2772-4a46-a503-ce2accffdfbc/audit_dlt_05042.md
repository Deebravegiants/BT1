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
    pallet_subtensor::Pallet::<T>::do_set_sn_owner_hotkey(origin, netuid, &hotkey)
}
```

`pallets/admin-utils/src/lib.rs:1731-1739` (call_index 67)
```rust
#[pallet::call_index(67)]
pub fn sudo_set_sn_owner_hotkey(
    origin: OriginFor<T>,
    netuid: NetUid,
    hotkey: <T as frame_system::Config>::AccountId,
) -> DispatchResult {
    pallet_subtensor::Pallet::<T>::do_set_sn_owner_hotkey(origin, netuid, &hotkey)
}
```

Both delegate to `do_set_sn_owner_hotkey` (`pallets/subtensor/src/subnets/subnet.rs:426-459`). Its only access gate is:

`pallets/subtensor/src/subnets/subnet.rs:432`
```rust
Self::ensure_subnet_owner_or_root(origin, netuid)?;
```

`ensure_subnet_owner_or_root` (`pallets/subtensor/src/utils/misc.rs:12-23`) accepts a signed origin equal to `SubnetOwner::<T>::get(netuid)`. Under a `Proxy::proxy` dispatch the origin is the **real** account (the subnet owner coldkey), so the check passes. The backend then writes `SubnetOwnerHotkey::<T>::insert(netuid, hotkey)` via `set_subnet_owner_hotkey` (`pallets/subtensor/src/utils/misc.rs:846-856`); the only validation there is that the hotkey is not a pallet sub-account (`CannotUseSystemAccount`). The call is rate-limited to once per `DefaultSetSNOwnerHotkeyRateLimit` = 50400 blocks (~1 week) per subnet (`pallets/subtensor/src/lib.rs:1062-1064`, `pallets/subtensor/src/subnets/subnet.rs:438-444`).

Net effect: the precise action the `Owner` carve-out is meant to forbid (changing `SubnetOwnerHotkey`) is reachable by an Owner-proxy delegate through the un-excepted alias call_index 64.

## Proof of Concept / Attack Scenario
Preconditions:
- A subnet exists with `SubnetOwner[netuid] = owner_coldkey`.
- `owner_coldkey` has granted an `Owner` proxy to `delegate` (e.g. an operator hired to tune hyperparameters, or a lease-management arrangement), relying on the `except sudo_set_sn_owner_hotkey` carve-out to retain exclusive control of the owner hotkey.
- The per-subnet `SetSNOwnerHotkey` rate limit window is open (no owner-hotkey change in the last ~50400 blocks).

Steps:
1. `delegate` submits:
   ```
   Proxy::proxy(
       real  = owner_coldkey,
       force_proxy_type = Some(ProxyType::Owner),
       call  = AdminUtils::sudo_set_subnet_owner_hotkey { netuid, hotkey: attacker_hotkey }   // call_index 64
   )
   ```
2. `proxy_type_filter(Owner, call)` returns `true`: the call matches `RuntimeCall::AdminUtils(..)` and is **not** the excepted `sudo_set_sn_owner_hotkey` variant.
3. The proxy re-dispatches with origin = `owner_coldkey`. `do_set_sn_owner_hotkey` → `ensure_subnet_owner_or_root` passes (origin == `SubnetOwner[netuid]`), the rate limit passes, and `SubnetOwnerHotkey[netuid]` is set to `attacker_hotkey`.

What the attacker gains / victim loses:
- The owner-hotkey identity for the subnet is now an account the delegate controls. Each epoch the subnet owner cut is staked to `(SubnetOwnerHotkey, SubnetOwner)` (`pallets/subtensor/src/coinbase/run_coinbase.rs:588-600`); the validator-take portion accrued by the owner hotkey now flows through a hotkey the attacker controls, and the owner hotkey receives deregistration immunity / priority placement in the owner-hotkey set (`run_coinbase.rs:570-574`, `:618`).
- The legitimate owner loses use of their intended owner hotkey until they reverse the change, which is itself gated by the same ~1-week rate limit — so the malicious state persists for at least one rate-limit window per correction attempt.

## Impact
- **Who:** Any subnet owner who delegates an `Owner` proxy under the (documented, intended) assumption that the delegate cannot change the owner hotkey. The carve-out at `runtime/src/lib.rs:697-699` is the explicit security boundary that this bug breaches.
- **Worst case:** Integrity violation of the subnet owner role — the delegate seizes the owner-hotkey identity (validator take, dereg immunity, owner-cut staking target) without the owner's consent, contradicting the proxy scope the owner granted. This is an availability/integrity impact on the subnet owner position, not a direct drain of the owner coldkey's balance: the owner cut is still staked under `SubnetOwner` (the real owner's coldkey), so the staked principal's withdrawal authority remains with the coldkey owner. The attacker captures the hotkey-level privileges and dividends-take routed through the owner hotkey.
- **Mitigating factors:** (1) Requires an existing `Owner` proxy delegation — not a permissionless attack against arbitrary subnets. (2) Rate-limited to once per ~50400 blocks (~1 week) per subnet. (3) The owner can revoke the proxy and re-set the owner hotkey (subject to the same rate limit). (4) `SubnetOwner` (coldkey ownership) is unchanged, so the owner retains ultimate control of the subnet and can recover.

Severity is assessed as **Medium**, consistent with the seed. The privilege requirement (a pre-granted Owner proxy) and the recoverable, non-coldkey-draining nature of the impact keep this below High; but it is a real and exploitable authorization-boundary bypass that fully defeats an intended security control, so it is above Low.

## Affected Code
- `runtime/src/lib.rs:693-699` — `Owner` proxy rule: `allow { AdminUtils::*, … } except { AdminUtils::sudo_set_sn_owner_hotkey }` (exception lists only call 67).
- `support/macros/src/proxy_filter.rs:308-322` — codegen lowering `allow … except …` to `matches!(allow) && !matches!(except)`, matching by call variant name.
- `pallets/admin-utils/src/lib.rs:1544-1553` — `sudo_set_subnet_owner_hotkey` (call_index 64) → `do_set_sn_owner_hotkey` (the un-excepted alias).
- `pallets/admin-utils/src/lib.rs:1731-1739` — `sudo_set_sn_owner_hotkey` (call_index 67) → `do_set_sn_owner_hotkey` (the excepted call).
- `pallets/subtensor/src/subnets/subnet.rs:426-459` — `do_set_sn_owner_hotkey`; gate at `:432` (`ensure_subnet_owner_or_root`).
- `pallets/subtensor/src/utils/misc.rs:12-23` — `ensure_subnet_owner_or_root` (passes for the proxy `real` owner coldkey).
- `pallets/subtensor/src/utils/misc.rs:846-856` — `set_subnet_owner_hotkey` (writes `SubnetOwnerHotkey`).
- `pallets/subtensor/src/coinbase/run_coinbase.rs:570-574`, `:588-600`, `:618` — owner hotkey controls owner-cut staking target, dereg immunity / priority placement.
- `pallets/subtensor/src/lib.rs:1062-1064` — `DefaultSetSNOwnerHotkeyRateLimit = 50400` (~1 week).

## Remediation
Primary fix — add the duplicate alias to the `Owner` proxy `except` block:

```diff
 Owner => allow {
     AdminUtils::*,
     SubtensorModule::set_subnet_identity,
     SubtensorModule::update_symbol,
 } except {
     AdminUtils::sudo_set_sn_owner_hotkey,
+    AdminUtils::sudo_set_subnet_owner_hotkey,
 }
```

Stronger fix (recommended) — eliminate the duplicate-alias class of bug entirely by deduplicating the two extrinsics. `sudo_set_subnet_owner_hotkey` (call 64) and `sudo_set_sn_owner_hotkey` (call 67) are byte-for-byte equivalent backends. Deprecate/remove one (keeping its call_index reserved for ABI stability) so the filter has a single call to gate. After consolidation, the `except` only ever needs to name one variant and cannot be silently bypassed by an alias.

Defense-in-depth — audit every proxy `except` / `deny` clause for other extrinsics that share a backend but are listed by only one variant name (e.g. any `*_limit` / aliased pairs). The matcher is name-based, so any unlisted alias of an excepted call is a bypass.

Regression test — extend `runtime/tests/pallet_proxy.rs` so that for `ProxyType::Owner`, BOTH `AdminUtils::sudo_set_sn_owner_hotkey` (call_index 67) and `AdminUtils::sudo_set_subnet_owner_hotkey` (call_index 64) are asserted denied, and assert no other `AdminUtils` variant aliases `do_set_sn_owner_hotkey`. The existing test (`runtime/tests/pallet_proxy.rs:595-603`) only constructs the call-67 variant, which is why the gap was not caught.

## Verification
I independently re-verified every claim against source at main @ 49164bd6:
- Confirmed the `Owner` rule and its single-entry `except` block at `runtime/src/lib.rs:693-699`.
- Confirmed via `support/macros/src/proxy_filter.rs:308-322` that `except` lowers to `matches!(allow) && !matches!(except)` and that the exception is matched on the concrete call variant name only — so the `AdminUtils::*` wildcard admits all other variants, including call 64.
- Confirmed both `sudo_set_subnet_owner_hotkey` (call_index 64, `pallets/admin-utils/src/lib.rs:1544-1553`) and `sudo_set_sn_owner_hotkey` (call_index 67, `:1731-1739`) call the identical backend `pallet_subtensor::Pallet::<T>::do_set_sn_owner_hotkey` (lines 1552 and 1738). Confirmed call 64 is live and non-deprecated (no `#[deprecated]`, no disable list; `ProxyType::is_deprecated` at `common/src/lib.rs:224-229` is unrelated and does not gate extrinsics).
- Confirmed the backend gate `ensure_subnet_owner_or_root` (`pallets/subtensor/src/utils/misc.rs:12-23`) accepts a signed origin equal to `SubnetOwner[netuid]`, which under `Proxy::proxy` is the real owner coldkey — so the proxy path passes.
- Confirmed the mutation target and its consequences: `SubnetOwnerHotkey` is written by `set_subnet_owner_hotkey` (`misc.rs:846-856`) and consumed for owner-cut staking and dereg immunity in `run_coinbase.rs:570-600,618`.
- Confirmed the rate limit (50400 blocks, `lib.rs:1062-1064`).
- Confirmed the existing proxy test only exercises the call-67 variant (`runtime/tests/pallet_proxy.rs:595-603`), explaining why the bypass is untested.

Scope adjustment vs. seed: the seed's harm list ("seizing the subnet validator identity / children-setting authority / dereg immunity") is largely accurate, but I narrowed two points for precision: (1) the owner cut is staked under the unchanged `SubnetOwner` coldkey, so this is a hotkey-identity/integrity seizure rather than a theft of the owner's staked principal; (2) I did not find code where `SubnetOwnerHotkey` by itself confers childkey-setting authority (childkey calls are gated on hotkey ownership via the coldkey, not on `SubnetOwnerHotkey`), so I dropped the "children-setting authority" claim from the confirmed impact. Severity remains Medium as proposed.

## Reproduction

**Status: REPRODUCED — passing compiled test.**

- Test: `ghsa_2026_003_owner_proxy_set_owner_hotkey_alias_bypass`
- File: `runtime/tests/ghsa_repro.rs`
- Run: `cargo test -p node-subtensor-runtime --test ghsa_repro`

The test asserts the buggy behavior (and a contrast assertion of the safe/expected behavior); it **passes** against `main` @ `49164bd6` (spec_version 417), demonstrating the vulnerability is live.

<details>
<summary>Reproduction test source (the actual passing test)</summary>

```rust
// runtime/tests/ghsa_repro.rs
/// GHSA-2026-003 — the Owner proxy excepts sudo_set_sn_owner_hotkey (call 67) but the
/// duplicate alias sudo_set_subnet_owner_hotkey (call 64) is allowed by the AdminUtils::*
/// wildcard, bypassing the carve-out.
#[test]
fn ghsa_2026_003_owner_proxy_set_owner_hotkey_alias_bypass() {
    assert!(
        !ProxyType::Owner.filter(&set_sn_owner_hotkey_c67()),
        "precondition: Owner correctly excepts sudo_set_sn_owner_hotkey (call 67)"
    );
    assert!(
        ProxyType::Owner.filter(&set_subnet_owner_hotkey_c64()),
        "VULN reproduced: Owner ALLOWS the alias sudo_set_subnet_owner_hotkey (call 64), \
         which calls the same do_set_sn_owner_hotkey backend — bypassing the except"
    );
}
```

</details>


## References
- Source: subtensor main @ 49164bd6, spec_version 417
- Merges confirmed entries `owner-proxy-set-sn-owner-hotkey-except-bypass` and `proxy-owner-set-owner-hotkey-except-bypass` (`.agents/confirmed_findings.json:187-245`) — same root cause.



---

## Patch

Fixed in [`opentensor/subtensor@5902428c50d4`](https://github.com/opentensor/subtensor/commit/5902428c50d4) (PR [#7](https://github.com/opentensor/subtensor/pull/7)). Live on mainnet as of **spec_version 419** (`main`).
