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
    Balances::*,
    SubtensorModule::transfer_stake,
    SubtensorModule::schedule_swap_coldkey,   // legacy
    SubtensorModule::swap_coldkey,            // legacy / root-gated
}

NonFungible => deny {
    Balances::*,
    ... add_stake / remove_stake / move_stake / transfer_stake / burned_register /
    root_register / schedule_swap_coldkey / swap_coldkey / swap_hotkey ...
}

NonCritical => deny {
    SubtensorModule::dissolve_network,
    SubtensorModule::root_register,
    SubtensorModule::burned_register,
    Sudo::*,
}
```

Neither `announce_coldkey_swap` nor `swap_coldkey_announced` appears in any of these three blocks. Because the filter is a denylist, both are **allowed** for NonTransfer, NonFungible, and NonCritical delegates.

### 3. The new calls only `ensure_signed`

`pallets/subtensor/src/macros/dispatches.rs`:

- `announce_coldkey_swap` (call 125): `let who = ensure_signed(origin)?;` (line 2267). On the first announcement it bills the swap cost to `who` (`Self::charge_swap_cost(&who, swap_cost)?;`, line 2277) and records `ColdkeySwapAnnouncements[who] = (now + delay, new_coldkey_hash)` (line 2282).
- `swap_coldkey_announced` (call 126): `let who = ensure_signed(origin)?;` (line 2305); after the delay (`now >= when`, line 2316) and a hash match it runs `Self::do_swap_coldkey(&who, &new_coldkey)?;` (line 2318).

Under proxy dispatch (`pallets/proxy/src/lib.rs:1100-1130`), the inner call is dispatched with `frame_system::RawOrigin::Signed(real)` (line 1107), and the only authorization applied to a non-proxy-management inner call is `def.proxy_type.filter(c)` (line 1127). So for a NonTransfer/NonFungible/NonCritical delegate, `ensure_signed` resolves to the **victim** (`real`), and the filter returns `true`. The attacker is announcing and executing a coldkey swap as the victim.

### 4. `do_swap_coldkey` moves everything

`pallets/subtensor/src/swap/swap_coldkey.rs:6-47` transfers, from `old_coldkey` to `new_coldkey`:

- on-chain identity (lines 19-24),
- subnet ownership, auto-stake destination, and all coldkey stake per subnet (lines 26-30),
- staking-hotkey associations and hotkey ownership (lines 31-32),
- stake locks (line 35),
- and **all free TAO**, reaping the old account: `Self::transfer_all_tao_and_kill(old_coldkey, new_coldkey)?;` (line 38). `transfer_all_tao_and_kill` (`pallets/subtensor/src/coinbase/tao.rs:94-113`) sweeps the entire `Preservation::Expendable` reducible balance.

The only preconditions (lines 10-17) are on the new coldkey: `StakingHotkeys[new]` must be empty and `new` must not be an existing hotkey. The attacker chooses the new coldkey, so these are trivially satisfied with a fresh key.

### 5. `CheckColdkeySwap` does not block it — it whitelists it

`pallets/subtensor/src/guards/check_coldkey_swap.rs:53-66` only restricts other calls once an announcement exists; it explicitly permits the swap-family calls:

```rust
let is_allowed_direct = matches!(
    call.is_sub_type(),
    Some(
        Call::announce_coldkey_swap { .. }
        | Call::swap_coldkey_announced { .. }
        | Call::dispute_coldkey_swap { .. }
        | Call::clear_coldkey_swap_announcement { .. }
    )
);
```

So the dispatch extension is by design transparent to the attack, and (worse) it lets the attacker's proxied `clear_coldkey_swap_announcement` (call 133) pass through too, which is relevant to recovery races (see Impact).

## Proof of Concept / Attack Scenario

Preconditions: the victim coldkey V has granted attacker A a proxy of type NonTransfer (or NonFungible, or NonCritical). V holds TAO / stake / subnet ownership / hotkeys. A controls a fresh coldkey K (and knows `BlakeTwo256(K)`).

1. A submits `Proxy::proxy(real = V, force_proxy_type = Some(NonTransfer), call = announce_coldkey_swap{ new_coldkey_hash = BlakeTwo256(K) })`.
   - Inner call runs as `Signed(V)`; filter allows it; `charge_swap_cost(V, ...)` bills the swap cost to the victim; `ColdkeySwapAnnouncements[V] = (now + ~5 days, BlakeTwo256(K))`; `ColdkeySwapAnnounced{ who: V, new_coldkey_hash }` event emitted.
2. A waits for `ColdkeySwapAnnouncementDelay` (`runtime/src/lib.rs:1080`: 5 * 24 * 60 * 60 / 12 blocks ≈ 5 days in production).
3. A submits `Proxy::proxy(real = V, force_proxy_type = Some(NonTransfer), call = swap_coldkey_announced{ new_coldkey = K })`.
   - Inner call runs as `Signed(V)`; hash matches; `now >= when`; `do_swap_coldkey(V, K)` runs.

Result: all of V's TAO, stake, subnet ownership, hotkey ownership, identity, and stake locks now belong to K. V is reaped. The attacker has full control; the victim has nothing. The attack needs **zero** of the privileges these proxy types are advertised to withhold — NonTransfer/NonFungible exist precisely to forbid moving funds.

## Impact

- **Who:** any coldkey that has delegated a NonTransfer, NonFungible, or NonCritical proxy to a party it does not fully trust (e.g. an automation bot, a custody/ops service, a "read-only-ish" delegate). These proxy types are marketed as safe because they cannot move funds; this bug breaks that contract.
- **Worst case:** complete, irreversible coldkey takeover — total loss of free balance, all staked alpha across all subnets, subnet ownership, and every owned hotkey (validator/miner identity, UID, emission stream).
- **Attacker cost:** the swap cost is billed to the **victim**, not the attacker. The attacker only pays transaction fees and the proxy is already in place.

### Mitigating factors (why this is High, not Critical)

1. **Announcement delay:** the swap cannot complete until `ColdkeySwapAnnouncementDelay` (~5 days in production) elapses between step 1 and step 3. There is no path to an instant drain.
2. **Public, on-chain signal:** step 1 emits `ColdkeySwapAnnounced { who: V, ... }`. A vigilant victim (or a monitor) can detect the pending takeover.
3. **Dispute / governance recovery:** the victim can call `dispute_coldkey_swap` (call 127) signed by V to freeze the swap (`ColdkeySwapDisputes[V]` then blocks all of V's calls via CheckColdkeySwap until triumvirate resolves), and root can `reset_coldkey_swap` (call 128). So the loss is recoverable **if and only if** the victim notices and acts within the window.
4. **Precondition:** the attacker must already hold a delegated proxy — this is PR:L, not PR:N.

These factors lower confidentiality impact to None and make the takeover observable and disputable, but the integrity and availability impact on the victim's account is total if they fail to react. Net: High (CVSS 8.1).

> Note on the clear/dispute race: because CheckColdkeySwap lets a proxied `clear_coldkey_swap_announcement` (call 133) through, and dispute requires the victim to sign with V, a determined attacker can attempt to clear-and-re-announce to reset timers, but cannot bypass the delay itself. The dispute path remains the victim's defense and must stay reachable. This is why the remediation deliberately does **not** deny the victim-defensive `dispute_coldkey_swap`.

## Affected Code

- `support/macros/src/proxy_filter.rs:323-328` — `deny` compiles to `!matches!(c, ...)` (denylist semantics).
- `support/macros/src/proxy_filter.rs:382` — generated `proxy_type_filter()`.
- `runtime/src/lib.rs:653-658` — `NonTransfer => deny { ... }` (missing announce/swap calls).
- `runtime/src/lib.rs:660-678` — `NonFungible => deny { ... }` (missing announce/swap calls).
- `runtime/src/lib.rs:701-706` — `NonCritical => deny { ... }` (missing announce/swap calls).
- `runtime/src/lib.rs:778-781, 797-810` — `InstanceFilter` for ProxyType and `pallet_proxy::Config` wiring.
- `pallets/proxy/src/lib.rs:1100-1130` — `do_proxy` dispatches inner call as `RawOrigin::Signed(real)`, gated only by `def.proxy_type.filter(c)`.
- `pallets/subtensor/src/macros/dispatches.rs:2261-2289` — `announce_coldkey_swap` (call 125), `ensure_signed`, bills swap cost to `who`.
- `pallets/subtensor/src/macros/dispatches.rs:2299-2321` — `swap_coldkey_announced` (call 126), `ensure_signed`, calls `do_swap_coldkey`.
- `pallets/subtensor/src/macros/dispatches.rs:2466-2485` — `clear_coldkey_swap_announcement` (call 133).
- `pallets/subtensor/src/swap/swap_coldkey.rs:6-47` — `do_swap_coldkey` moves all assets, ownership, and TAO.
- `pallets/subtensor/src/coinbase/tao.rs:94-113` — `transfer_all_tao_and_kill`.
- `pallets/subtensor/src/guards/check_coldkey_swap.rs:58-66` — whitelists the swap family (does not block this attack).

## Remediation

Add the live coldkey-swap-execution calls to the three restricted deny blocks. Minimal, mechanical patch (`runtime/src/lib.rs`):

```diff
 NonTransfer => deny {
     Balances::*,
     SubtensorModule::transfer_stake,
     SubtensorModule::schedule_swap_coldkey,
     SubtensorModule::swap_coldkey,
+    SubtensorModule::announce_coldkey_swap,
+    SubtensorModule::swap_coldkey_announced,
 }

 NonFungible => deny {
     Balances::*,
     ...
     SubtensorModule::schedule_swap_coldkey,
     SubtensorModule::swap_coldkey,
     SubtensorModule::swap_hotkey,
+    SubtensorModule::announce_coldkey_swap,
+    SubtensorModule::swap_coldkey_announced,
 }

 NonCritical => deny {
     SubtensorModule::dissolve_network,
     SubtensorModule::root_register,
     SubtensorModule::burned_register,
     Sudo::*,
+    SubtensorModule::announce_coldkey_swap,
+    SubtensorModule::swap_coldkey_announced,
 }
```

Scope notes:

- **Deny only the takeover levers (`announce_coldkey_swap`, `swap_coldkey_announced`).** Do **not** deny `dispute_coldkey_swap` (call 127): a delegate may be a legitimate operator that needs to fire the victim-defensive dispute, and disputing only freezes the account (it cannot move assets). Denying it would remove a defensive option without closing any attack.
- Treat `clear_coldkey_swap_announcement` (call 133) with care: a proxied clear lets an attacker reset/replay the announcement timer for the victim. Consider denying it for these restricted types as well, since clearing serves the swap lifecycle the restricted proxy should not drive. (Confirm against any operator workflow that relies on proxied clears before denying.)
- **Strategic fix:** fund-moving / ownership-moving gates should be **allowlists**, not denylists, so that newly added extrinsics fail closed. The denylist pattern guarantees this class of regression on every future call addition or rename.

Regression test (add to `runtime/tests/pallet_proxy.rs`): enumerate the entire coldkey-swap family — `announce_coldkey_swap`, `swap_coldkey_announced`, `swap_coldkey`, `schedule_swap_coldkey`, and (per decision above) `clear_coldkey_swap_announcement` — and assert `!ProxyType::NonTransfer.filter(call)`, `!ProxyType::NonFungible.filter(call)`, `!ProxyType::NonCritical.filter(call)`. This locks the gate so a future call rename or version bump cannot silently re-open it. Note the current tests (`runtime/tests/pallet_proxy.rs:311-342`) do **not** cover these calls.

## Verification

I independently re-verified every cited claim against source at main @ 49164bd6 (spec_version 417, confirmed `runtime/src/lib.rs:280`):

- **Denylist semantics confirmed** — `proxy_filter.rs:323-328` generates `ProxyType::#pt => !matches!(c, ...)`; unlisted calls are allowed. The generated function is `proxy_type_filter` (`proxy_filter.rs:382`), wired via `InstanceFilter` for ProxyType (`lib.rs:778-781`) and `pallet_proxy::Config { type ProxyType = ProxyType }` (`lib.rs:800`).
- **Deny blocks omit the new calls** — read `lib.rs:653-678` and `701-706`; only legacy `swap_coldkey`/`schedule_swap_coldkey` are listed; `announce_coldkey_swap`/`swap_coldkey_announced` are absent from all three.
- **New calls only `ensure_signed`** — `dispatches.rs:2267` and `2305`; swap cost billed to `who` (the victim under proxy) at `2277`; `do_swap_coldkey(&who, ...)` at `2318`.
- **Proxy executes as the victim, gated only by filter** — `pallets/proxy/src/lib.rs:1107` (`RawOrigin::Signed(real)`) and `1127` (`def.proxy_type.filter(c)`).
- **`do_swap_coldkey` drains everything** — `swap/swap_coldkey.rs:26-38`, including `transfer_all_tao_and_kill` (`coinbase/tao.rs:94-113`, `Preservation::Expendable`). Its only guards (lines 10-17) constrain the attacker-chosen new key and do not block the attack.
- **`CheckColdkeySwap` does not block** — `guards/check_coldkey_swap.rs:58-66` whitelists the swap family.
- **No existing test refutes it** — `runtime/tests/pallet_proxy.rs` filter tests (lines 311-342) cover transfer/stake/register/sudo but not the coldkey-swap calls; the in-pallet `check_coldkey_swap.rs` tests confirm announce/swap are authorized during an active swap, reinforcing the gap.

**Severity adjustment from the seed:** the seed proposed Critical. I assess **High (CVSS 8.1, AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)**. The downgrade reflects three real mitigating factors I confirmed in source: the ~5-day `ColdkeySwapAnnouncementDelay` (`lib.rs:1080`), the public `ColdkeySwapAnnounced` event (`dispatches.rs:2284`), and the working dispute/reset recovery path (`dispute_coldkey_swap` call 127 + `reset_coldkey_swap` call 128). The takeover is therefore non-instant, observable, and recoverable if the victim reacts within the window — but total and irreversible if they do not, and it requires only a granted restricted proxy (PR:L). The vulnerability itself (incorrect authorization / fail-open denylist) is fully **CONFIRMED** and exploitable as described.

## Reproduction

**Status: REPRODUCED — passing compiled test.**

The relevant portion of the reproduction is inlined below (a runtime integration test). The filter returns `true` when a call is **allowed** for a proxy type; the bug is that fund/ownership-moving calls are allowed for proxy types meant to forbid them. The test asserts the buggy behavior, and **passes** against main @ 49164bd6 (spec_version 417), demonstrating the vulnerability is live.

```rust
use frame_support::traits::InstanceFilter;
use node_subtensor_runtime::RuntimeCall;
use subtensor_runtime_common::{AccountId, NetUid, ProxyType, TaoBalance};

fn acct() -> AccountId {
    AccountId::new([0u8; 32])
}

// ---- coldkey-swap lifecycle calls ----
fn announce_coldkey_swap() -> RuntimeCall {
    RuntimeCall::SubtensorModule(pallet_subtensor::Call::announce_coldkey_swap {
        new_coldkey_hash: Default::default(),
    })
}
fn swap_coldkey_announced() -> RuntimeCall {
    RuntimeCall::SubtensorModule(pallet_subtensor::Call::swap_coldkey_announced {
        new_coldkey: acct(),
    })
}
fn swap_coldkey_legacy() -> RuntimeCall {
    RuntimeCall::SubtensorModule(pallet_subtensor::Call::swap_coldkey {
        old_coldkey: acct(),
        new_coldkey: acct(),
        swap_cost: TaoBalance::from(0u64),
    })
}
fn transfer_stake() -> RuntimeCall {
    RuntimeCall::SubtensorModule(pallet_subtensor::Call::transfer_stake {
        destination_coldkey: acct(),
        hotkey: acct(),
        origin_netuid: NetUid::from(1),
        destination_netuid: NetUid::from(1),
        alpha_amount: Default::default(),
    })
}

/// NonTransfer and NonFungible proxies (the two "cannot move my funds" types)
/// ALLOW the new coldkey-swap lifecycle, so a restricted delegate can take over
/// the whole coldkey. Reproduced by asserting the calls are NOT filtered.
#[test]
fn restricted_proxies_allow_coldkey_swap_lifecycle() {
    let announce = announce_coldkey_swap();
    let exec = swap_coldkey_announced();

    // These two proxy types DO block direct exfiltration (transfer_stake denied) ...
    for pt in [ProxyType::NonTransfer, ProxyType::NonFungible] {
        assert!(
            !pt.filter(&transfer_stake()),
            "precondition: {pt:?} should deny transfer_stake (it is a fund-protection type)"
        );
        // ... but they FAIL to block the swap lifecycle that exfiltrates everything:
        assert!(
            pt.filter(&announce),
            "VULN reproduced: {pt:?} ALLOWS announce_coldkey_swap (should be denied)"
        );
        assert!(
            pt.filter(&exec),
            "VULN reproduced: {pt:?} ALLOWS swap_coldkey_announced (should be denied)"
        );
        // Contrast: the legacy swap_coldkey they replaced IS denied — proving the gap is
        // specifically the un-listed new lifecycle calls.
        assert!(
            !pt.filter(&swap_coldkey_legacy()),
            "{pt:?} correctly denies legacy swap_coldkey — the new calls were simply never added"
        );
    }
}

/// Scope correction: NonCritical is NOT a fund-protection type — it already permits
/// transfer_stake — so the coldkey-swap gap is not an escalation for it.
#[test]
fn noncritical_is_not_a_fund_protection_type() {
    assert!(
        ProxyType::NonCritical.filter(&transfer_stake()),
        "NonCritical already allows transfer_stake, so coldkey-swap adds no new capability"
    );
}
```

**Scope refinement (from reproduction).** The test confirmed NonCritical already permits `transfer_stake`, so it is **not** a fund-protection proxy and the coldkey-swap gap is not a new escalation for it. The genuine victims are **NonTransfer** and **NonFungible**. The remediation still adds the deny to NonCritical as defense-in-depth, but the impact framing applies to NonTransfer/NonFungible.

## References

- Source: subtensor main @ 49164bd6, spec_version 417
- Corroborating internal analysis: `.agents/SECURITY_AUDIT_REPORT.md` (independent write-up of the same root cause, same file:line)
- Related sibling finding (same denylist root cause): NonFungible permits the live `swap_hotkey_v2` (call 72) because only the deprecated `swap_hotkey` (call 70) is denied — reinforces the recommendation to convert these gates to allowlists.


---

## Patch

Fixed in [`opentensor/subtensor@d48eea5bb519`](https://github.com/opentensor/subtensor/commit/d48eea5bb519) (PR [#5](https://github.com/opentensor/subtensor/pull/5)).

Live on mainnet as of **spec_version 419** (`main`).
