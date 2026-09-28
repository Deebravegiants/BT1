### Title
Unbounded account creation via `supply(account_id = 0)` allows permanent ledger-state bloat that outruns the bounded renewal window, archiving live accounts — (File: contracts/controller/src/positions/supply.rs)

### Summary
The bug class is "memory allocation with an excessive size value" → resource-exhaustion DoS. On XOXNO Lending the analogous unbounded allocation is persistent ledger state, not RAM: `controller::supply` with `account_id = 0` mints a brand-new account (NFT token id + `AccountMeta` + `SupplyPositions` entries) on every call, with no per-address account cap and no minimum deposit. The repository's own test `poc_single_actor_spams_unbounded_dust_accounts` proves a single actor can mint arbitrary many persistent accounts at a cost of 1 stroop-like unit each (`tests/test-harness/tests/controller/supply.rs:313-344`). Because account ids are never reused and account/user entries only stay live while renewed — either by the keeper's windowed scan (`schedule.max_accounts_scan`, default 50,000 ids per TTL tick, wrapping) or by user activity — an attacker who pushes `max_account_id` far past the scan window makes a full renewal cycle take `ceil(max_account_id / max_accounts_scan)` TTL ticks. Accounts missed for longer than their TTL archive, and every controller entrypoint that reads `AccountMeta`/`SupplyPositions`/`BorrowPositions` then fails on that account until state is restored.

### Finding Description
`supply` resolves `account_id == 0` into `create_account`, which calls `position_nft.mint` (sequential counter, never reused) and writes `ControllerKey::AccountMeta(id)` plus the position map (`tests/test-harness/src/ops/account.rs:44-53`, `contracts/controller/src/storage/account.rs:63-105`). Nothing bounds: (a) the number of accounts per owner, (b) the amount required to open an account — the PoC succeeds with `amount = 1`, and (c) the global account counter relative to any renewal capacity. Renewal coverage is explicitly windowed: "Each discovery pass … scans a window of at most `schedule.max_accounts_scan` ids (default 50,000). Only a TTL tick moves the window forward" (`services/keeper/README.md:38-44`), and `plan_user_scan` wraps a fixed-size window over `1..=max_account_id` (`services/keeper/src/discovery.rs:798-812`). Unprivileged account growth therefore directly inflates the denominator of a fixed-rate renewal process — the exact shape of the reported bug (attacker-controlled size defeating a fixed allocation budget).

### Impact Explanation
**Temporary freezing of funds (Medium).** Once `max_account_id` exceeds what the renewal window can cover within one TTL lifetime (120-day user window), legitimately-held accounts at the tail of the id space archive. Any operation touching their persistent entries — withdraw, repay, liquidation reads of `AccountMeta`/position maps, NFT `renew` — reverts on the archived entry until a `restore_footprint` is performed. Unlike a fail-closed oversized-transaction DoS, the denial is not self-inflicted by the caller: the attacker grows the shared id space and other users' accounts lapse without those users submitting anything. The cost to the attacker is near-zero (1 unit of any listed asset per account, refundable by withdrawing the dust).

### Likelihood Explanation
Medium. Fully permissionless (`controller::supply` is caller-auth; `account_id = 0` is a documented creation path). Requires only repeated transactions; no privileged state, oracle manipulation, or timing dependency. The freezing manifests only after the id space grows beyond scan coverage, so impact realization depends on keeper configuration and TTL tick cadence — but the vulnerability itself (uncapped persistent allocation reachable for dust) is unconditional and already demonstrated by the in-repo PoC test.

### Recommendation
Enforce a minimum first-deposit (dust floor) or a per-owner account cap in the `account_id == 0` path of `supply`/`multiply`/`flash_position`/`migrate_from_blend`/liquidation `Credit(0)`; alternatively charge a non-refundable account-creation deposit sized to cover its perpetual storage rent, so the marginal cost of an account exceeds the marginal harm. Additionally consider auto-deleting accounts created below the dust threshold on withdrawal to shrink the live id range the renewal window must cover.

### Proof of Concept
```rust
// tests/test-harness/tests/controller/supply.rs (existing test)
const N: u64 = 64;
usdc.token_admin.mint(&attacker, &(N as i128));
for _ in 0..N {
    let dust = vec![&t.env, (hub_asset(asset.clone()), 1i128)];
    let id = ctrl.supply(&attacker, &0u64, &1u32, &dust); // mints a new account each call
    assert!(ctrl.account_exists(&id));                     // persistent bloat per unit spent
}
```
Repeating this loop until `max_account_id` exceeds `max_accounts_scan × ticks-per-TTL-window` guarantees accounts at the tail archive while still holding funds, freezing withdrawals for their owners until manual restore.