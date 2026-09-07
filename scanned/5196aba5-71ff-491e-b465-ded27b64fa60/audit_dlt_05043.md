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

_Trimmed to 38 lines — full report: https://github.com/RaoFoundation/subtensor/security/advisories/GHSA-qh57-vpv2-3fvp_
