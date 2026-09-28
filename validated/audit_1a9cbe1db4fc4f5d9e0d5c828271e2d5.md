### Title
Stale risk params of a delisted collateral are never cleaned up — `restamp`/`sync` skip unlisted assets, leaving outdated LTV/LT/bonus stamps that inflate health factor forever - (File: contracts/controller/src/risk/params.rs)

### Summary
The Linux bug: `unaccount_slab()` skipped freeing `slab->obj_exts` when `mem_alloc_profiling_enabled()` was false, so stale per-object state survived feature shutdown. The XOXNO analog: every per-position risk restamp path iterates supply positions but `continue`s when `cached_spoke_asset` returns `None` for a removed listing. The stored `loan_to_value`, `liquidation_threshold`, `liquidation_bonus`, and `liquidation_fees` on that position are never reset or removed, so a delisted collateral keeps contributing its old risk parameters to HF and liquidation math indefinitely.

### Finding Description
Each `AccountPosition` carries a stamped copy of the listing's risk tuple, copied at creation in `get_or_create_supply_position` and refreshed only through three paths, all of which bail out early on unlisted assets:

- `restamp_listed_supply_ltv` skips with `continue` when `cache.cached_spoke_asset(...)` is `None` (`contracts/controller/src/risk/params.rs:48-50`).
- `sync_account_thresholds` (the `update_account_threshold` entrypoint) does the same (`contracts/controller/src/risk/params.rs:183-185`).
- `merge_supply_leg` / `merge_withdraw_leg` refresh stamps via `refresh_supply_risk_params`, which likewise reads the live listing; a missing listing means no restamp.

There is no path that clears or zeroes the stored tuple once the spoke listing is deleted (`edit_asset_in_spoke` / spoke removal is a governance op, but the stale *user-facing* state it leaves behind is the analog of the leaked `obj_exts`). Meanwhile `calculate_account_risk_totals` and the liquidation bonus path (`get_account_bonus_params`) read the **stored** threshold/bonus, not the listing (per `docs/reference/runbooks/liqvid-listing-params.md` — "the controller uses the stored values, not the live listing"). The code even acknowledges the asymmetry: `update_or_remove_supply_position` only removes a position when `scaled_amount == 0`, never when its backing listing is gone (`contracts/controller/src/account.rs:190-200`).

### Impact Explanation
An unprivileged borrower who supplied an asset while it had a high LT/LTV keeps that stamp after governance removes the listing. Two concrete consequences:

1. **Blocked liquidation → bad debt.** The stale `liquidation_threshold` (e.g. 8000–9800 bps for a now-worthless or delisted asset) keeps the account's computed HF above 1.0 or inflates it, so liquidators cannot act on genuinely undercollateralized positions while the collateral's real value falls to zero. When HF eventually does break (via the debt index growing), the residual must be socialized through `clean_bad_debt` — protocol insolvency borne by suppliers.
2. **Over-borrowing against phantom LTV.** The stored `loan_to_value` still feeds the borrow-limit check for existing positions, so an account whose collateral was delisted retains borrowing power it should have lost.

This matches the kernel bug's shape exactly: a feature (the listing) is disabled, and the teardown path skips cleanup of the associated state because the "is it enabled/listed?" guard returns false.

### Likelihood Explanation
Requires a governance listing removal (not itself attacker-controlled), after which *any* unprivileged holder of the stale-stamped collateral benefits passively; no timing or race is needed. Every existing position of the removed listing is affected, and no permissionless path (`update_account_threshold`, supply, withdraw, liquidate) can ever restamp it — the stale params are permanent for the life of the position. Severity Medium-High: the trigger needs an admin action, but the cleanup gap is deterministic and the damage (unliquidatable accounts, socialized bad debt) falls within scope.

### Recommendation
When `cached_spoke_asset` returns `None` during any restamp, actively sanitize the position instead of `continue`ing: e.g. zero the stored `loan_to_value`/`liquidation_threshold`/`liquidation_bonus` (excluding it from HF and borrowing power) or mark the position as non-collateral, so a delisted asset cannot contribute stale risk parameters. At minimum, add a permissionless sweep that restamps-or-zeroes positions whose listing no longer exists, mirroring "clean up `obj_exts` always".

### Proof of Concept
1. `supply(alice, account, DELIST_ME, X)` while spoke listing has `ltv=7500, threshold=8000` — position stamps those values via `get_or_create_supply_position`.
2. `borrow(alice, account, USDC, amount)` up to the LTV limit.
3. Governance removes the spoke listing for `DELIST_ME` (or the whole spoke, as in `test_update_account_threshold_deprecated_spoke_retains_spoke_params`).
4. Price of `DELIST_ME` collapses, or interest accrues.
5. Any caller invokes `update_account_threshold(caller, true, [account])` → `sync_account_thresholds` hits `cached_spoke_asset == None` → `continue` → stamps unchanged (`params.rs:183-185`). Same for `restamp_listed_supply_ltv` (`params.rs:48-50`) on every borrow/withdraw.
6. `liquidate(...)` computes HF with the stale `liquidation_threshold=8000` on a worthless asset → HF stays ≥ 1 → liquidation reverts `HealthFactorNotLow`; the position eventually lands in `clean_bad_debt`, writing the loss into the supply index (`recapitalize`-style socialization), i.e. protocol insolvency. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/controller/src/risk/params.rs (L44-64)
```rust
pub(crate) fn restamp_listed_supply_ltv(cache: &mut Context, account: &mut Account) -> bool {
    let mut changed = false;
    let keys = account.supply_positions.keys();
    for hub_asset in keys.iter() {
        let Some(listed) = cache.cached_spoke_asset(account.spoke_id, &hub_asset) else {
            continue;
        };
        let config: AssetConfig = (&listed).into();
        let Some(raw) = account.supply_positions.get(hub_asset.clone()) else {
            continue;
        };
        let mut position = AccountPosition::from(&raw);
        if position.loan_to_value.raw() == config.loan_to_value.raw() {
            continue;
        }
        position.loan_to_value = config.loan_to_value;
        update_or_remove_supply_position(account, &hub_asset, &position);
        changed = true;
    }
    changed
}
```

**File:** contracts/controller/src/risk/params.rs (L182-205)
```rust
    for hub_asset in assets.iter() {
        let Some(spoke_config) = cache.cached_spoke_asset(account.spoke_id, &hub_asset) else {
            continue;
        };
        let asset_config = AssetConfig::from(&spoke_config);

        let raw = expect_invariant(env, account.supply_positions.get(hub_asset.clone()));
        let mut updated = AccountPosition::from(&raw);

        let changed = refresh_supply_risk_params(
            env,
            cache,
            &account,
            &hub_asset,
            &mut updated,
            &asset_config,
            scope,
        );
        if !changed {
            continue;
        }

        any_changed = true;
        update_or_remove_supply_position(&mut account, &hub_asset, &updated);
```

**File:** contracts/controller/src/account.rs (L189-213)
```rust
/// Updates the in-memory supply position, removing it when scaled supply is zero.
pub(crate) fn update_or_remove_supply_position(
    account: &mut Account,
    hub_asset: &HubAssetKey,
    position: &AccountPosition,
) {
    upsert_or_remove_position(
        &mut account.supply_positions,
        hub_asset,
        (position.scaled_amount != Ray::ZERO).then(|| position.into()),
    );
}

/// Updates the in-memory debt position, removing it when scaled debt is zero.
pub(crate) fn update_or_remove_debt_position(
    account: &mut Account,
    hub_asset: &HubAssetKey,
    position: &DebtPosition,
) {
    upsert_or_remove_position(
        &mut account.borrow_positions,
        hub_asset,
        (position.scaled_amount != Ray::ZERO).then(|| position.into()),
    );
}
```

**File:** tests/test-harness/tests/controller/keeper.rs (L343-364)
```rust
fn test_update_account_threshold_deprecated_spoke_retains_spoke_params() {
    let mut t = LendingTest::new()
        .with_market(usdc_preset())
        .with_spoke(2, STABLECOIN_SPOKE)
        .with_spoke_asset(2, "USDC", true, true)
        .with_dust_disabled_all_markets()
        .build();

    let account_id = t.create_spoke_account(ALICE, 2);
    t.supply_to(ALICE, account_id, "USDC", 1_000.0);

    assert_eq!(supply_threshold_bps(&t, account_id, "USDC"), 9800);

    t.remove_spoke_category(2);
    t.update_account_threshold(true, &[account_id]);

    assert_eq!(
        supply_threshold_bps(&t, account_id, "USDC"),
        9800,
        "a deprecated spoke's positions keep reading the spoke's own threshold (no spoke-0 fallback)"
    );
}
```

**File:** docs/reference/runbooks/liqvid-listing-params.md (L361-390)
```markdown

Each supply position stores its own LTV, LT, base bonus and liquidation fee.
It copies them from the spoke listing when it is created
(`get_or_create_supply_position`). After that, the controller uses the
stored values, not the live listing:

- HF uses the stored LT (`calculate_account_risk_totals`).
- The borrow limit uses the lower of the stored LTV and the stored LT.
- The base bonus `b0` is the USD-weighted stored bonus. The maximum bonus `M`
  comes from the stored LT. The fee is the stored fee
  (`get_account_bonus_params`).
- The curve (`H`, `K`, `f`) is not stored. Each liquidation reads it from the
  spoke. `configureSpokeCurves` changes it for all accounts of the spoke at
  the same time.

Thus an `editAssetInSpoke` that lowers LT changes only the positions created
after it and the positions that the controller refreshes. Every borrow and
every withdrawal refreshes the stored LTV of each listed supply position
without a condition. The stored LT, bonus and fee refresh together, and only
in these paths:

| Path | Code |
|---|---|
| A supply of the asset into the account | `merge_supply_leg` calls `refresh_supply_risk_params` |
| A withdrawal of the asset that is not a liquidation and leaves a balance | `merge_withdraw_leg` |
| `update_account_threshold(caller, has_risks = true, account_ids)` | `sync_account_thresholds` |

A liquidation never refreshes them. `update_account_threshold` with
`has_risks = false` refreshes the LTV only.

```
