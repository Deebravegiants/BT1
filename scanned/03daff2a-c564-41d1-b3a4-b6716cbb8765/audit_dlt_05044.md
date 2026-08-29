# [H] Restricted proxies (NonTransfer/NonFungible/NonCritical) can take over an entire coldkey via the announce/swap coldkey-swap lifecycle

## Summary
Severity: High
Chain: Bittensor
Component: opentensor/subtensor
CWE: Incorrect Authorization
Published: 2026-06-17
Source: https://github.com/RaoFoundation/subtensor/security/advisories/GHSA-m759-m8mv-q3m5
Type: github-advisory

## Details
## Summary

The subtensor proxy filter compiles every `deny { ... }` block as a **denylist** — `ProxyType::X => !matches!(c, <listed calls>)` — so any extrinsic not explicitly listed is **permitted** for that proxy type. When the coldkey swap was migrated to the two-step `announce_coldkey_swap` (call 125) → `swap_coldkey_announced` (call 126) lifecycle, the `NonTransfer`, `NonFungible`, and `NonCritical` deny blocks were not updated: they still list only the legacy `swap_coldkey` / `schedule_swap_coldkey`. Both new calls gate only on `ensure_signed`, and under `pallet_proxy::proxy` they execute as `RawOrigin::Signed(real)` (the victim). A delegate holding any of these "cannot move my funds" proxy types can therefore drive a full coldkey swap on the victim's behalf, moving **all TAO, all stake, subnet ownership, and hotkey ownership** to a coldkey the attacker controls. The only thing standing between the delegate and full account takeover is the ~5-day `ColdkeySwapAnnouncementDelay`, the public `ColdkeySwapAnnounced` event, and the victim manually disputing in time.

## Details

### 1. `deny { ... }` is a denylist (unlisted == allowed)

`support/macros/src/proxy_filter.rs:323-328`:

```rust
FilterKind::Deny { calls } => {
    let patterns = self.call_refs_to_patterns(calls);
    quote! {
        ProxyType::#pt => !matches!(c, #(#patterns)|*),
    }
}
```

The generated `proxy_type_filter()` (`proxy_filter.rs:382`) returns `true` (allow) for any call that does not match the listed patterns. `runtime/src/lib.rs:778-781` wires this into the proxy pallet:

```rust
impl InstanceFilter<RuntimeCall> for ProxyType {
    fn filter(&self, c: &RuntimeCall) -> bool {
        proxy_type_filter(self, c)
    }
    ...
}
```

and `runtime/src/lib.rs:797-810` sets `type ProxyType = ProxyType;` for `pallet_proxy::Config`, so this filter is the real on-chain authorization gate for proxied calls.

### 2. The deny blocks omit the live swap calls

`runtime/src/lib.rs:653-678` and `701-706`:

```rust
NonTransfer => deny {
```

_Trimmed to 38 lines — full report: https://github.com/RaoFoundation/subtensor/security/advisories/GHSA-m759-m8mv-q3m5_
