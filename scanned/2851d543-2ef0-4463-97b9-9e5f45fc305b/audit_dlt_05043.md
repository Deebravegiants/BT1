# [H] NonFungible proxy denylist omits live swap_hotkey_v2 (call 72), letting a scoped delegate reassign a victim's hotkey identity

## Summary
Severity: High
Chain: Bittensor
Component: opentensor/subtensor
CWE: Incorrect Authorization
Published: 2026-06-17
Source: https://github.com/RaoFoundation/subtensor/security/advisories/GHSA-qh57-vpv2-3fvp
Type: github-advisory

## Details
## Summary

The NonFungible proxy type is a denylist that blocks the deprecated `swap_hotkey` extrinsic (`call_index` 70) but not its live superset `swap_hotkey_v2` (`call_index` 72). Because a denylist permits anything it does not name, a NonFungible-scoped proxy delegate can dispatch `swap_hotkey_v2` as the victim's coldkey origin and reassign the victim's hotkey (UID, axon/Prometheus, weight commits, loaded emission, TLS cert, and — depending on `keep_stake` — staked alpha) to an attacker-chosen hotkey. A repo-wide grep confirms `swap_hotkey_v2` appears nowhere under `runtime/`. The inverse mistake exists on the dedicated SwapHotkey proxy type, whose allowlist only permits the deprecated call 70, so a SwapHotkey delegate cannot drive the live extrinsic. This is an incorrect-authorization (privilege-scope) flaw, not a coldkey-principal theft: the new hotkey's owner is set to the victim's coldkey, so the TAO/alpha principal remains in victim custody, but operational control of the neuron identity moves to the attacker.

## Details

### 1. The filter DSL is a denylist, and v2 is not on the list

`runtime/src/lib.rs:660-678` defines the NonFungible rule as a `deny { ... }` block. The terminal entry is `SubtensorModule::swap_hotkey` (line 677); `swap_hotkey_v2` is absent:

```rust
NonFungible => deny {
    Balances::*,
    SubtensorModule::add_stake,
    ...
    SubtensorModule::swap_coldkey,
    SubtensorModule::swap_hotkey,   // line 677 — call 70 only
}
```

The proxy-filter proc-macro compiles a deny block to a negated `matches!`, i.e. allow everything not listed (`support/macros/src/proxy_filter.rs:323-327`):

```rust
FilterKind::Deny { calls } => {
    let patterns = self.call_refs_to_patterns(calls);
    quote! {
        ProxyType::#pt => !matches!(c, #(#patterns)|*),
    }
}
```

`InstanceFilter::filter` for ProxyType delegates directly to this generated function (`runtime/src/lib.rs:778-781`):

```rust
impl InstanceFilter<RuntimeCall> for ProxyType {
    fn filter(&self, c: &RuntimeCall) -> bool {
        proxy_type_filter(self, c)
    }
```

Since `RuntimeCall::SubtensorModule(Call::swap_hotkey_v2 { .. })` matches none of the listed patterns, `proxy_type_filter(&NonFungible, call)` returns true — the call is permitted for a NonFungible delegate. pallet_proxy enforces this filter in `proxy`/`proxy_announced` before dispatching the inner call with the real account (the victim coldkey) as origin.

### 2. The two hotkey-swap extrinsics are equivalent at the do_-layer

`pallets/subtensor/src/macros/dispatches.rs:1030-1042` defines the deprecated call 70, and `:1055-1067` defines the live call 72. Both forward to the same handler, differing only in the `keep_stake` flag:

```rust
#[deprecated(note = "Please use swap_hotkey_v2 instead. ...")]
#[pallet::call_index(70)]
pub fn swap_hotkey(origin, hotkey, new_hotkey, netuid) -> ... {
    Self::do_swap_hotkey(origin, &hotkey, &new_hotkey, netuid, false)   // line 1041
}

#[pallet::call_index(72)]
pub fn swap_hotkey_v2(origin, hotkey, new_hotkey, netuid, keep_stake) -> ... {
    Self::do_swap_hotkey(origin, &hotkey, &new_hotkey, netuid, keep_stake)  // line 1066
}
```

`swap_hotkey_v2` is therefore a strict superset (adds the `keep_stake` parameter). Denying 70 while allowing 72 fully defeats the deny entry's intent.

### 3. The handler authorizes on the origin coldkey, which the proxy supplies as the victim

`pallets/subtensor/src/swap/swap_hotkey.rs:33-55`:

```rust
pub fn do_swap_hotkey(origin, old_hotkey, new_hotkey, netuid, keep_stake) -> ... {
    let coldkey = ensure_signed(origin)?;                    // line 41 — = victim coldkey under proxy
    ensure!(Self::coldkey_owns_hotkey(&coldkey, old_hotkey), // line 44 — victim owns its own hotkey: passes
        Error::<T>::NonAssociatedColdKey);
    if Self::hotkey_account_exists(new_hotkey) {             // line 50 — only if new hotkey already exists globally
        ensure!(Self::coldkey_owns_hotkey(&coldkey, new_hotkey),
            Error::<T>::NonAssociatedColdKey);
    }
    ...
}
```

Under `Proxy::proxy(real = victim_coldkey, ...)`, `ensure_signed` returns the victim's coldkey, which trivially owns the victim's own `old_hotkey`. The new_hotkey-ownership check added in commit 1112fe9eb ("check new_hotkey") only triggers when `new_hotkey` already exists globally; an attacker simply supplies a freshly generated keypair that has never been registered or staked, so the check is skipped and the swap proceeds.

### 4. What moves to the attacker-controlled hotkey

`perform_hotkey_swap_on_all_subnets` / `perform_hotkey_swap_on_one_subnet` reassign the neuron's operational identity:

- Owner set to the victim coldkey, not the attacker — `set_hotkey_owner(coldkey, new_hotkey)` at swap_hotkey.rs:222. (This is why staked principal is not stolen.)
- `Uids` / `Keys` reassigned to new_hotkey — swap_hotkey.rs:412-418.
- Prometheus — :428-429; Axons — :435-437.
- WeightCommits — :449-450.
- LoadedEmission rewritten to new_hotkey — :460-466.
- NeuronCertificates — :476-477.

Because the attacker chose `new_hotkey` and holds its private key, they can now sign `set_weights`, serve a malicious axon, and operate the UID — i.e. they capture the neuron's operational/consensus role and the emissions that flow to it, even though the staked principal remains nominally owned by the victim coldkey.

## Proof of Concept / Attack Scenario

Precondition: the victim coldkey has granted the attacker a NonFungible proxy (`Proxy::add_proxy(delegate = attacker, ProxyType::NonFungible, 0)`). NonFungible is documented as "Nothing involving moving TAO" (common/src/lib.rs:155) and explicitly denies the deprecated `swap_hotkey`, so a victim reasonably believes hotkey reassignment is out of scope for this delegate.

1. Attacker generates a fresh keypair `attacker_hk` (never registered/staked, so `hotkey_account_exists(attacker_hk) == false`).
2. Attacker (delegate) submits:
   ```
   Proxy::proxy {
     real: victim_coldkey,
     force_proxy_type: Some(NonFungible),
     call: SubtensorModule::swap_hotkey_v2 {
       hotkey: victim_hotkey,
       new_hotkey: attacker_hk,
       netuid: None,            // all subnets
       keep_stake: false,       // or true; see below
     }
   }
   ```
3. `proxy_type_filter(&NonFungible, swap_hotkey_v2{..})` returns true (call 72 not on the deny list) → filter passes.
4. `do_swap_hotkey` runs with `coldkey = victim_coldkey`: ownership of `victim_hotkey` passes; the new_hotkey ownership guard is skipped because `attacker_hk` does not yet exist; rate-limit/swap-cost are charged to the victim coldkey.
5. UID, axon, Prometheus, weight commits, loaded emission, TLS cert (and, with `keep_stake=false`, the alpha stake position) migrate to `attacker_hk`.

Attacker gains: operational control of the victim's neuron UID across subnets — ability to set weights, serve a hostile axon, and capture emissions routed through that hotkey's activity. Victim loses: control of their validator/miner identity and ongoing emission stream; pays the swap fee and burns a rate-limited tx slot. The victim coldkey still owns `attacker_hk` on-chain, so the staked principal is not directly transferred out of victim custody.

## Impact

- Affected: any coldkey that has delegated a NonFungible proxy to a third party (e.g. delegated operational management while intending to withhold stake-movement and identity-swap rights).
- Worst case: full operational hijack of a validator/miner UID — malicious `set_weights` (consensus corruption / self-dealing weight assignment), emission capture, and denial of the victim's neuron operation. With `keep_stake=false` the alpha position also migrates to the attacker-controlled hotkey, though ownership stays with the victim coldkey.
- Mitigating factors: (1) requires a pre-existing NonFungible proxy grant — not a permissionless attack against arbitrary victims; (2) the coldkey-level ownership of the new hotkey is forced to the victim coldkey (swap_hotkey.rs:222), so the staked TAO principal is not stolen outright — this is the reason the rating is High rather than Critical; (3) tx rate limit and recycled swap fee gate repeated abuse; (4) the move is on-chain and observable via the `HotkeySwapped` event, so the victim can detect it and, holding the coldkey, can swap the hotkey back. Conversely, this also blocks immediate stealthy fund exfiltration.

## Affected Code

- runtime/src/lib.rs:660-678 — `NonFungible => deny { ... }`; lists `swap_hotkey` (line 677), omits `swap_hotkey_v2`.
- runtime/src/lib.rs:743-745 — `SwapHotkey => allow { SubtensorModule::swap_hotkey }`; the dedicated swap proxy allows only the deprecated call 70, not the live call 72 (inverse breakage).
- runtime/src/lib.rs:778-781 — `InstanceFilter::filter` delegates to `proxy_type_filter`.
- support/macros/src/proxy_filter.rs:323-327 — Deny codegen as `!matches!(...)` (denylist semantics).
- pallets/subtensor/src/macros/dispatches.rs:1030-1042 — `swap_hotkey` call 70 (deprecated, keep_stake=false).
- pallets/subtensor/src/macros/dispatches.rs:1055-1067 — `swap_hotkey_v2` call 72 (live, takes keep_stake).
- pallets/subtensor/src/swap/swap_hotkey.rs:33-55 — origin/ownership checks; new_hotkey guard only when it already exists globally.
- pallets/subtensor/src/swap/swap_hotkey.rs:220-235, 412-418, 428-437, 449-450, 460-466, 476-477 — identity/state migration to new_hotkey.
- common/src/lib.rs:149-168 — ProxyType enum; `NonFungible // Nothing involving moving TAO`.
- runtime/tests/pallet_proxy.rs:559-574 — filter enumeration test includes `swap_hotkey` (call 70) but not `swap_hotkey_v2`, so it does not catch this gap.

## Remediation

1. Add the live call to the NonFungible deny block (and review every other denylist that names `swap_hotkey`):

```diff
 NonFungible => deny {
     ...
     SubtensorModule::swap_coldkey,
     SubtensorModule::swap_hotkey,
+    SubtensorModule::swap_hotkey_v2,
 }
```

2. Add the live call to the dedicated SwapHotkey allowlist so the intended proxy type can actually drive the current extrinsic:

```diff
 SwapHotkey => allow {
     SubtensorModule::swap_hotkey,
+    SubtensorModule::swap_hotkey_v2,
 }
```

3. Add a regression test that enumerates every `swap_*` extrinsic in `pallet_subtensor::Call` and asserts the expected filter result for each relevant proxy type (deny for NonFungible/NonTransfer, allow for SwapHotkey). A diff-resistant enumeration (iterating call metadata / call_index ranges) prevents future `_vN` successors from silently bypassing the policy. Extend runtime/tests/pallet_proxy.rs:559-604 to cover call 72.

4. Process hardening: when an extrinsic is duplicated under a new call_index (`_v2`), require a checklist item to update every proxy allow/deny list and the filter enumeration test in the same change.

## Verification

- Re-read runtime/src/lib.rs:660-678 and :743-745: confirmed NonFungible deny block lists `swap_hotkey` (line 677) and not `swap_hotkey_v2`; SwapHotkey allow block lists only `swap_hotkey` (line 744).
- `grep -rn "swap_hotkey_v2" runtime/` returns no hits — the live call is referenced nowhere in the runtime crate (filters or tests).
- Confirmed denylist semantics in support/macros/src/proxy_filter.rs:323-327 (`!matches!`), and that `InstanceFilter::filter` calls `proxy_type_filter` at runtime/src/lib.rs:778-781. A call not present in a deny block evaluates to true (permitted).
- Confirmed call indices and equivalence at dispatches.rs:1033-1041 (call 70, deprecated, keep_stake=false) and :1055-1067 (call 72, live, parameterized keep_stake); both call `do_swap_hotkey`.
- Confirmed origin handling in swap_hotkey.rs:41-55: authorization is on the signed coldkey (the proxy real), and the new_hotkey-ownership guard (added in commit 1112fe9eb, "check new_hotkey") only fires when `new_hotkey` already exists globally — bypassable with a fresh attacker keypair.
- Confirmed state migration: owner forced to victim coldkey (:222), and UID/Keys/Prometheus/Axons/WeightCommits/LoadedEmission/NeuronCertificates reassigned to new_hotkey (:412-477).
- Confirmed the existing proxy filter enumeration test (runtime/tests/pallet_proxy.rs:567) covers call 70 only, so CI does not detect the gap.

Adjustments from the seed: Verdict CONFIRMED. Severity kept at High (not Critical): the new hotkey's on-chain owner is set to the victim coldkey (swap_hotkey.rs:222), so the staked TAO/alpha principal is not exfiltrated to the attacker's coldkey; the realized harm is operational hijack (weights, axon, emission capture) and denial of the victim's neuron, gated by a pre-existing NonFungible proxy grant. CVSS v3.1 8.7 (AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H): PR:L reflects the delegated-proxy precondition; I:H/A:H reflect identity/consensus integrity loss and neuron-availability loss; C:N and the principal-ownership invariant are the reasons it is not Critical.

## Reproduction

Status: REPRODUCED — passing compiled test.

- Test: `ghsa_2026_002_nonfungible_allows_swap_hotkey_v2_gap`
- File: `runtime/tests/ghsa_repro.rs`
- Run: `cargo test -p node-subtensor-runtime --test ghsa_repro`

The test asserts the buggy behavior (and a contrast assertion of the safe/expected behavior); it passes against main @ 49164bd6 (spec_version 417), demonstrating the vulnerability is live.

## References

- Source: subtensor main @ 49164bd6, spec_version 417.
- 1112fe9eb "check new_hotkey" — adds the conditional new_hotkey ownership guard in `do_swap_hotkey` (only when the hotkey already exists globally; does not close this proxy gap).
- Deprecation note in dispatches.rs:1031: `swap_hotkey` to be removed "some time after June 2026" — until then both 70 and 72 are dispatchable, and only 70 is filtered.


---

## Patch

Fixed in [`opentensor/subtensor@c52dac0ff96f`](https://github.com/opentensor/subtensor/commit/c52dac0ff96f) (PR [#6](https://github.com/opentensor/subtensor/pull/6)).

Live on mainnet as of **spec_version 419** (`main`).
