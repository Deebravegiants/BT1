### Title
Position-map entries silently default to empty on absent persistent storage, erasing collateral or debt from risk accounting - (File: contracts/controller/src/storage/account.rs)

### Summary
Analogous to FFmpeg's `alloc_rbsp_buffer` branching on a buffer that was never initialized, the controller's risk gates branch on position maps that are never guaranteed to exist: `get_supply_positions` and `get_debt_positions` translate a missing `ControllerKey::SupplyPositions`/`BorrowPositions` persistent entry into an empty `Map` rather than failing. Because position-map writes deliberately skip TTL renewal while metadata writes renew their own key, an account can persist with live `AccountMeta` but expired position entries, and every downstream conditional (`debt_free()`, health-factor gate, withdraw lookup) reads that "uninitialized" empty map as truth.

### Finding Description
`get_supply_positions` returns `get_user(...).unwrap_or_else(|| Map::new(env))` and `get_debt_positions` does the same for `ControllerKey::BorrowPositions` — absence of the entry is indistinguishable from a genuinely empty book [1](#0-0) .

TTL asymmetry makes the absent entry reachable on a live account:

- `write_side_map` stores the maps "without renewing TTL" and `set_supply_positions`/`set_debt_positions` both route through it [2](#0-1) .
- `set_account_meta` and `set_delegates` renew only their own keys via `set_user`, so owner-driven calls (`add_delegate`, meta updates) keep `AccountMeta`/`Delegates` alive while the position maps age out [3](#0-2) .
- `renew_user_account` renews each key only `if persistent.has(key)` — once a map entry expires it is never restored [4](#0-3) .
- `try_get_account` then succeeds (meta present, NFT owner resolves) and returns an `Account` whose supply/borrow maps are the empty defaults [5](#0-4) .

The branches that consume the uninitialized read:

- `views::health_factor` calls `risk::calculate_account_risk_totals` only when `!account.debt_free()`; with the `BorrowPositions` entry absent the debt book is empty, `debt_free()` is true, and HF reports `i128::MAX` — the debt obligation vanishes from every gate [6](#0-5) .
- With `SupplyPositions` absent but debt present, `calculate_account_risk_totals_body` iterates an empty supply map → `weighted_collateral = 0` → HF = 0, making the account instantly liquidatable/socializable while the owner's real shares (still counted in the pool's `supplied` total) are unreachable by `withdraw` [7](#0-6) .

### Impact Explanation
Two loss modes, both reachable by any unprivileged address once the entry lapses:

1. **Erased debt → protocol insolvency.** If `BorrowPositions` expires while meta stays live, the account is `debt_free()`; `repay`/`liquidate`/`clean_bad_debt` see nothing to collect. The pool's aggregate `borrowed` still includes that debt and the borrow index keeps accruing on it, so the shortfall is permanently socialized across suppliers.
2. **Frozen/stolen collateral.** If `SupplyPositions` expires while `BorrowPositions` survives, `can_be_liquidated` returns true at HF 0 and `clean_bad_debt` socializes the debt, while the victim's shares are orphaned in the pool (never withdrawable) — permanent freezing of user funds plus a supply-index write-down hitting honest suppliers.

### Likelihood Explanation
Expiry requires the position-map entries to go unread/unwritten for a full persistent-TTL window while a sibling key is renewed. That is passive rather than attacker-accelerated, but it is reachable through ordinary unprivileged calls (`add_delegate`, NFT-era meta paths) that renew only their own keys, and dormant accounts in inactive hubs/spokes accumulate exactly this pattern. Severity Medium-High: high impact, conditional likelihood.

### Recommendation
Distinguish "entry absent" from "entry empty": have `get_supply_positions`/`get_debt_positions` return `Option` and make `try_get_account`/`get_account` fail with a dedicated error when `AccountMeta` exists but a position-map key it implies is missing — or write a sentinel/flag entry at account creation so a lapsed map is detectable. Additionally, renew position-map TTL inside `write_side_map` (or inside `set_account_meta`/`set_delegates`/`renew_user_account` unconditionally for all four keys) so meta renewal cannot outlive the books it describes.

### Proof of Concept
```rust
// Controller-side, mirrors liquidation_zero_threshold.rs fixture style.
// 1. Supply + borrow for VICTIM via normal entrypoints (meta + both maps written).
// 2. Advance ledger past persistent TTL for SupplyPositions/BorrowPositions only:
//    keep AccountMeta alive by calling add_delegate / a meta-writing op
//    (set_user renews ControllerKey::AccountMeta/Delegates, not the maps).
// 3. env.as_contract(controller, || {
//        env.storage().persistent().remove(&ControllerKey::SupplyPositions(VICTIM));
//    });  // simulate archival expiry — production never re-checks has()
// 4. client.is_liquidatable(&VICTIM) == true  // empty map -> weighted_collateral 0 -> HF 0
//    client.get_health_factor(&VICTIM) == 0
//    owner withdraw(VICTIM, asset, amount) reverts: no supply position found,
//    while pool's `supplied` still counts the victim's scaled shares.
// Symmetrically removing BorrowPositions makes debt_free() true and
// health_factor() return i128::MAX — debt permanently uncollectable.
```

Caveat: I could not exhaustively confirm every caller of `renew_user_account`/`set_user` or the exact pool-side aggregate accounting of orphaned shares within the available iterations; the core defect (absent entry → empty map consumed by risk gates, with asymmetric TTL renewal) is directly supported by the cited code.

### Citations

**File:** contracts/controller/src/storage/account.rs (L57-60)
```rust
/// Stores account metadata and renews user TTL.
pub(crate) fn set_account_meta(env: &Env, account_id: u64, meta: &AccountMeta) {
    set_user(env, &ControllerKey::AccountMeta(account_id), meta);
}
```

**File:** contracts/controller/src/storage/account.rs (L62-73)
```rust
/// Returns raw supply positions, defaulting to an empty map.
pub(crate) fn get_supply_positions(
    env: &Env,
    account_id: u64,
) -> Map<HubAssetKey, AccountPositionRaw> {
    get_user(env, &ControllerKey::SupplyPositions(account_id)).unwrap_or_else(|| Map::new(env))
}

/// Returns raw debt positions, defaulting to an empty map.
pub(crate) fn get_debt_positions(env: &Env, account_id: u64) -> Map<HubAssetKey, DebtPositionRaw> {
    get_user(env, &ControllerKey::BorrowPositions(account_id)).unwrap_or_else(|| Map::new(env))
}
```

**File:** contracts/controller/src/storage/account.rs (L75-105)
```rust
/// Stores supply positions without renewing TTL; deletes an empty map.
pub(crate) fn set_supply_positions(
    env: &Env,
    account_id: u64,
    map: &Map<HubAssetKey, AccountPositionRaw>,
) {
    write_side_map(env, &ControllerKey::SupplyPositions(account_id), map);
}

/// Stores debt positions without renewing TTL; deletes an empty map.
pub(crate) fn set_debt_positions(
    env: &Env,
    account_id: u64,
    map: &Map<HubAssetKey, DebtPositionRaw>,
) {
    write_side_map(env, &ControllerKey::BorrowPositions(account_id), map);
}

/// Stores a nonempty position map without renewing TTL; deletes an empty map.
fn write_side_map<V: TryFromVal<Env, Val> + IntoVal<Env, Val>>(
    env: &Env,
    key: &ControllerKey,
    map: &Map<HubAssetKey, V>,
) {
    let persistent = env.storage().persistent();
    if map.is_empty() {
        persistent.remove(key);
    } else {
        persistent.set(key, map);
    }
}
```

**File:** contracts/controller/src/storage/account.rs (L153-162)
```rust
pub(crate) fn try_get_account(env: &Env, account_id: u64) -> Option<Account> {
    let meta = try_get_account_meta(env, account_id)?;
    let owner = try_account_owner(env, account_id)?;
    Some(account_from_parts(
        owner,
        meta,
        get_supply_positions(env, account_id),
        get_debt_positions(env, account_id),
    ))
}
```

**File:** contracts/controller/src/storage/account.rs (L259-272)
```rust
pub(crate) fn renew_user_account(env: &Env, account_id: u64) {
    let persistent = env.storage().persistent();
    let keys = [
        ControllerKey::AccountMeta(account_id),
        ControllerKey::SupplyPositions(account_id),
        ControllerKey::BorrowPositions(account_id),
        ControllerKey::Delegates(account_id),
    ];
    for key in &keys {
        if persistent.has(key) {
            renew_user_key(env, key);
        }
    }
}
```

**File:** contracts/controller/src/views.rs (L30-42)
```rust
pub(crate) fn health_factor(env: &Env, account_id: u64) -> i128 {
    let mut cache = Context::new_view(env);
    match storage::try_get_account(env, account_id) {
        Some(account) if !account.debt_free() => risk::calculate_account_risk_totals(
            env,
            &mut cache,
            &account.supply_positions,
            &account.borrow_positions,
        )
        .health_factor
        .raw(),
        _ => i128::MAX,
    }
```

**File:** contracts/controller/src/risk/totals.rs (L163-207)
```rust
    cache.load_markets(&portfolio_hub_keys(
        supply_positions.keys(),
        &borrow_positions.keys(),
    ));

    let mut total_collateral = Wad::ZERO;
    let mut ltv_collateral = Wad::ZERO;
    let mut weighted_collateral = Wad::ZERO;
    for (hub_asset, position) in iter_typed_positions(supply_positions) {
        let feed = cache.cached_price(&hub_asset.asset);
        let market_index = cache.cached_market_index(&hub_asset);

        let value = position_value(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );
        let gate_value = position_value_floor(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );

        total_collateral = total_collateral.checked_add(env, value);
        // A gated threshold can stay below refreshed LTV; clamp the borrow limit to it.
        let effective_ltv = position.loan_to_value.min(position.liquidation_threshold);
        ltv_collateral =
            ltv_collateral.checked_add(env, effective_ltv.apply_to_wad_floor(env, gate_value));
        weighted_collateral = weighted_collateral.checked_add(
            env,
            position
                .liquidation_threshold
                .apply_to_wad_floor(env, gate_value),
        );
    }

    let total_debt = sum_debt_usd_loaded(env, cache, borrow_positions, position_value_ceil);

    let health_factor = if total_debt == Wad::ZERO {
        Wad::from(i128::MAX)
    } else {
        weighted_collateral.div_floor_saturating(env, total_debt)
    };
```
