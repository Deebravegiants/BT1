### Title
Supply-index floor clamp leaves wiped suppliers with phantom claims that drain fresh deposits - (File: contracts/pool/src/interest.rs / contracts/pool/src/cache/scale.rs)

### Summary
The bug class behind CVE-2018-8807 is use-after-free: an object is read after the resource backing it has been released. The lending analog is a *claim-after-write-down*: `apply_bad_debt_to_supply_index` frees the token backing of all supply shares in a market by writing down `supply_index`, but clamps the index at `SUPPLY_INDEX_FLOOR_RAW` (`RAY/1000`). When a wipeout would require an index below the floor, every scaled supply share `S_old` keeps a claim priced at the clamped index — a pointer to value that no longer exists. A later `withdraw` resolves that claim against cash contributed by *fresh* suppliers, paying out tokens that were never owed.

### Finding Description
The pool README documents that `supply_index` "is not monotone" and that `apply_bad_debt_to_supply_index` scales it down to socialize a loss, "floored at `SUPPLY_INDEX_FLOOR_RAW` (`RAY/1000`)" and that "anything caching an index must tolerate a decrease" [1](#0-0) . Bad-debt socialization is reachable permissionlessly via `clean_bad_debt` / post-liquidation `check_bad_debt_after_liquidation` [2](#0-1) .

When the socialized debt is large enough that `supply_index * (1 - loss/supplied_claim)` falls below `RAY/1000`, the clamp pins the index at the floor instead of zeroing supplier claims. The pool's own regression test demonstrates the exploit end-to-end in `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` [3](#0-2) :

- `apply_bad_debt_to_supply_index(cache, 5_000 RAY)` on a 1,000-unit-supply market clamps `supply_index` up to the floor, leaving `unscale_supply_floor(old_scaled) > 0` — "floor clamp leaves S_old a phantom claim" while `cash == 0` [4](#0-3) .
- A fresh supplier then deposits `fresh_cash = stranded`; the phantom holder calls the withdraw path (`resolve_withdrawal(i128::MAX, old_scaled)` → `require_reserves(gross)` → `burn_supply` → `debit_cash`), and `gross == fresh_cash` — "S_old drains exactly the fresh deposit," after which pool cash can no longer cover the fresh supplier's claim: "funds lost" [5](#0-4) .

This is the UAF shape exactly: the write-down logically frees the collateral backing every supply share, but the floor clamp leaves the share handle dereferenceable, and `withdraw` dereferences it against unrelated cash. The `revenue <= supplied` invariant (`require_revenue_backed`) does not catch it because `revenue` is untouched; only `require_reserves` gates the payout, and it passes as soon as any honest depositor refills `cash`.

### Impact Explanation
Theft of user funds / protocol insolvency. Any holder of pre-wipeout scaled shares (including the attacker, who can supply before manufacturing the bad debt) withdraws real tokens whose backing was already written off. The payment comes out of later depositors' principal, so the pool ends with `cash < supplied_claim(floor)` — a permanent deficit that `recapitalize` may fill but which, per the docs, occurs *without* restoring the lost index [6](#0-5) . Each phantom withdrawal transfers loss from the wiped suppliers to fresh suppliers.

### Likelihood Explanation
Reachable by a single unprivileged address. `clean_bad_debt` is permissionless once debt exceeds collateral and collateral is at most the $5 dust cap [7](#0-6) . An attacker needs a market where socialized debt exceeds `supplied * (1 - RAY/1000 / supply_index)`, i.e., bad debt exceeding ~99.9% of the supply claim — achievable in a thin/spoke market where the attacker controls both the insolvent borrower (letting price move or accruing debt) and is among the pre-existing suppliers, then supplies or waits for a victim to supply and calls `withdraw`. The limiting factor is that socializable debt is capped by the dust threshold for *collateral*, not for debt size — `clean_bad_debt` requires only `debt > collateral` and `collateral <= $5`, with no bound on debt magnitude, so a deeply insolvent account with negligible collateral satisfies the gate. Likelihood is Moderate: requires a market thin enough for the write-down to hit the floor, but no privileged access.

### Recommendation
When `apply_bad_debt_to_supply_index` would clamp to `SUPPLY_INDEX_FLOOR_RAW`, the residual unbacked claim must be extinguished rather than preserved: either (a) scale `supplied`/`revenue` scaled-share totals down by the same factor the index *would* have taken so claims stay collateralized, or (b) track the clamped shortfall explicitly and treat post-clamp `unscale_supply_floor` results exceeding `cash + outstanding_debt` as zero-payable in `resolve_withdrawal`. At minimum, `require_reserves` in the withdraw path should compare `gross` against `cash + outstanding_debt(ceil)` attributable to *backing* rather than raw cash, so phantom claims cannot consume fresh deposits.

### Proof of Concept
The codebase's own test is the PoC (`contracts/pool/tests/interest.rs:372`). Conceptually on live contracts:

1. In a thin market, attacker supplies `S` and opens a borrow position that accrues/becomes deeply insolvent with negligible collateral (≤ $5 dust).
2. Any caller invokes permissionless `clean_bad_debt(account_id)` → `execute_bad_debt_cleanup` → `pool_seize_positions_call` → pool applies `apply_bad_debt_to_supply_index`; write-down exceeds the floor, index clamps at `RAY/1000`, all `S_old` shares keep `scaled_amount` priced at the floored index.
3. Victim calls `supply` on the same hub-asset; `mint_supply`/`credit_cash` puts real cash in the pool.
4. Attacker calls `withdraw` (`resolve_withdrawal` → `require_reserves` passes on fresh cash → `debit_cash`), extracting the victim's principal. Subsequent withdraw of the victim now reverts on `require_reserves` or pays less than `unscale_supply_floor` — permanent loss.

### Citations

**File:** contracts/pool/README.md (L187-190)
```markdown
`borrow_index` only ever grows — `update_borrow_index` is its sole writer.
`supply_index` is **not** monotone: `apply_bad_debt_to_supply_index` scales it
down to socialize a loss across suppliers, floored at `SUPPLY_INDEX_FLOOR_RAW`
(`RAY/1000`). Anything caching an index must tolerate a decrease.
```

**File:** contracts/controller/src/positions/liquidation/apply.rs (L301-316)
```rust
pub(crate) fn check_bad_debt_after_liquidation(
    env: &Env,
    cache: &mut Context,
    account_id: u64,
    account: &Account,
    totals: &AccountRiskTotals,
) {
    if account.borrow_positions.is_empty() {
        account::cleanup_account_if_empty(env, account, account_id);
        return;
    }

    if is_socializable_bad_debt(totals.total_debt, totals.total_collateral) {
        bad_debt::execute_bad_debt_cleanup(env, cache, account_id, account, totals);
    }
}
```

**File:** contracts/pool/tests/interest.rs (L372-427)
```rust
#[test]
fn test_raw_cache_floor_clamp_strands_claim_without_supply_guard() {
    let t = TestSetup::new();
    t.as_contract(|| {
        let old_scaled_raw = 1_000 * RAY;
        let mut cache = t.fresh_cache(PoolStateRaw {
            supplied: old_scaled_raw,
            borrowed: 0,
            revenue: 0,
            borrow_index: RAY,
            supply_index: RAY,
            last_timestamp: 0,
            cash: 0,
        });
        let old_scaled = Ray::from(old_scaled_raw);

        apply_bad_debt_to_supply_index(&mut cache, Ray::from(5_000 * RAY));
        assert_eq!(
            cache.supply_index().raw(),
            SUPPLY_INDEX_FLOOR_RAW,
            "wipeout clamps supply_index UP to RAY/1000 instead of resetting shares to 0",
        );

        let stranded = cache.unscale_supply_floor(old_scaled);
        assert!(stranded > 0, "floor clamp leaves S_old a phantom claim");
        assert_eq!(
            cache.cash(),
            0,
            "no cash yet: invariant only masked by require_reserves"
        );

        let fresh_cash = stranded;
        let fresh_scaled = cache.calculate_scaled_supply(fresh_cash);
        cache.mint_supply(fresh_scaled);
        cache.credit_cash(fresh_cash);

        let fresh_claim = cache.unscale_supply_floor(fresh_scaled);
        assert_eq!(
            fresh_claim, fresh_cash,
            "fresh supplier's claim equals deposit"
        );

        let (burn, gross) = cache.resolve_withdrawal(i128::MAX, old_scaled);
        cache.require_reserves(gross);
        cache.burn_supply(burn);
        cache.debit_cash(gross);

        assert!(gross > 0, "stranded wiped position pays out real tokens");
        assert_eq!(gross, fresh_cash, "S_old drains exactly the fresh deposit");
        assert!(
            cache.cash() < fresh_claim,
            "pool cash ({}) can no longer cover fresh supplier claim ({}): funds lost",
            cache.cash(),
            fresh_claim,
        );
    });
```

**File:** docs/reference/invariants.md (L463-469)
```markdown
### INV-LIQ-04 — Bad-debt socialization is explicit and total

Permissionless cleanup requires ceil risk debt greater than half-up unweighted
collateral and collateral at or below the fixed $5 dust threshold. Owner-only
forced cleanup omits the dust cap. Both require debt, readable account and NFT
state, valid required prices and no active flash guard. Listing flags and
global pause do not block standalone cleanup.
```

**File:** docs/reference/invariants.md (L477-479)
```markdown
Ordinary liquidation and cleanup apply no final account-health or full-backing
assertion. The index floor can leave a shortfall. Recapitalization fills that
shortfall without restoring the lost index or deleted account.
```
