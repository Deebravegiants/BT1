### Title
Bad-debt socialization clamps supply index at floor without burning residual supplier shares, letting wiped positions drain fresh deposits - (File: contracts/pool/src/interest.rs)

### Summary
`apply_bad_debt_to_supply_index` socializes bad debt by scaling down the supply index, but clamps the result at `SUPPLY_INDEX_FLOOR_RAW` (`RAY / 1000`) instead of zeroing or burning the outstanding scaled supply. The callee-side clamp creates a "lost reference" analog to the CVE: when bad debt meets or exceeds total supplied value, surviving supplier shares keep a phantom claim worth roughly `1/1000` of face value, while the cash backing was fully consumed. The seizing caller (`ops::seize::apply`) performs no compensating supply burn or residual accounting, so the invariant `claim <= cash + debt` is silently broken. The repo's own tests demonstrate that, absent an external guard, a stranded holder extracts a fresh depositor's full deposit.

### Finding Description
In `contracts/pool/src/interest.rs`, `apply_bad_debt_to_supply_index` computes `reduction_factor = remaining / total_supplied_value` and sets `new_supply_index = old_index * reduction_factor`, then clamps with `.max(SUPPLY_INDEX_FLOOR_RAW)` [1](#0-0) . When `bad_debt >= total_supplied_value`, `remaining = 0`, the reduction factor is 0, and the index is pushed *up* to the floor rather than to zero — so `supplied` scaled shares retain `scaled * FLOOR` of claim despite the pool having zero backing.

The calling side, `ops::seize::apply` (Borrow branch), invokes this and only burns the debt shares; no supply shares are burned and no residual check is performed [2](#0-1) . This mirrors the kernel pattern: `cachefiles_bury_object()` expects callers to arrive holding 2 dentry refs, and `cachefiles_cull()` was the one caller not converted to `start_removing_dentry()` — here, the index write-down expects the caller to neutralize residual claims when the floor binds, and the seize path does not.

The project's own unit tests prove the drain on raw-cache primitives: after the floor clamp, `unscale_supply_floor(old_scaled) > 0` ("floor clamp leaves a phantom claim"), a fresh deposit is booked, and the stranded holder's `resolve_withdrawal` "drains exactly the fresh deposit", leaving cash < the fresh supplier's claim [3](#0-2) . A second test shows the same for a survivor whose shares were never burned ("seize wipeout clamps supply_index UP ... leaving unburned shares a residual"; "Alice extracts exactly Bob's fresh deposit") [4](#0-3) . The test names acknowledge a "supply guard" is required, but `seize::apply` contains none — the only protection is `require_reserves` at withdraw time, which merely defers the insolvency until new cash exists.

### Impact Explanation
Theft of user funds / protocol insolvency. After a full socialization (bad debt ≥ total supplied value), every pre-existing supply share retains a claim ≈ 1/1000 of its face value against a pool with zero backing. Any subsequent `supply` deposits real cash that a wiped-out holder can immediately withdraw via `withdraw`, extracting funds belonging to the fresh supplier — the pool ends the sequence owing more than it holds.

### Likelihood Explanation
Reachable by a single unprivileged address through `liquidate` or `clean_bad_debt` on an underwater position, which drives `PoolSeizeEntry{side: Borrow}` into `ops::seize::apply`. Triggering the full wipe requires accrued bad debt ≥ total supply value in one `(hub, token)` book — achievable in illiquid/high-rate markets or via a self-inflicted position where collateral is seized first and the residual debt is then socialized. The floor clamp is a hard-coded constant, not a governance parameter, so no privileged configuration is needed beyond a market that can accrue debt against thin supply. Confidence is moderate: the arithmetic and the missing residual handling are proven by the repo's tests, but whether controller-side dust thresholds or a keeper path incidentally prevents reaching `seize` with `bad_debt >= supplied*index` was not fully verified.

### Recommendation
When `bad_debt >= total_supplied_value` (i.e., `reduction_factor` would be 0 and the floor binds), the pool must also retire the outstanding scaled supply — e.g., in `ops::seize::apply`'s Borrow branch, detect `remaining == Ray::ZERO` and set `supplied`/`revenue` scaled balances to zero (burn all residual shares) rather than clamping the index upward. Alternatively, revert seizes whose socialization would hit `SUPPLY_INDEX_FLOOR_RAW`, forcing recapitalization before bad-debt cleanup. Add a regression test asserting `unscale_supply_floor(supplied) == 0` (or claim ≤ cash) after any Borrow-side seize that triggers the clamp.

### Proof of Concept
1. Attacker (or market conditions) creates a position in market `(hub, T)` whose debt grows until `unscale_borrow_ceil_ray(position) >= supplied * supply_index` (e.g., borrow against collateral that is fully seized, leaving residual unpaid debt).
2. Call `liquidate`/`clean_bad_debt`; controller emits `PoolSeizeEntry{side: Borrow, position.scaled_amount = debt_scaled}` → `ops::seize::apply` → `apply_bad_debt_to_supply_index` clamps `supply_index` to `SUPPLY_INDEX_FLOOR_RAW`; `burn_debt` clears the debt. Pre-existing supplier `S_old` retains `scaled` shares.
3. Victim Bob calls `supply` with amount `D ≈ S_old * FLOOR / RAY` (the stranded claim value); pool books `cash = D`.
4. `S_old` calls `withdraw` with `amount = i128::MAX`: `resolve_withdrawal` unscales at the floor index, `require_reserves(gross)` passes since `gross ≤ D`, and `S_old` receives `D`.
5. Bob's claim `> cash = 0` — fresh depositor's funds are lost; the market is insolvent.

### Citations

**File:** contracts/pool/src/interest.rs (L80-89)
```rust
    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
}
```

**File:** contracts/pool/src/ops/seize.rs (L24-34)
```rust
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
        AccountPositionType::Deposit => {
            cache.absorb_supply_as_revenue(position);
        }
    }

    cache.commit()
```

**File:** contracts/pool/tests/interest.rs (L388-426)
```rust
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
```

**File:** contracts/pool/tests/interest.rs (L448-494)
```rust
        let bad_debt = cache.unscale_borrow_ceil_ray(borrow_scaled);
        apply_bad_debt_to_supply_index(&mut cache, bad_debt);
        cache.burn_debt(borrow_scaled);

        assert_eq!(
            cache.supply_index().raw(),
            SUPPLY_INDEX_FLOOR_RAW,
            "seize wipeout clamps supply_index UP to RAY/1000, leaving unburned shares a residual"
        );

        let alice_stranded = cache.unscale_supply_floor(alice_scaled);
        assert!(alice_stranded > 0, "wiped survivor keeps a stranded claim");
        assert_eq!(
            cache.cash(),
            0,
            "empty market: claim masked by require_reserves"
        );

        let deposit = alice_stranded;
        let bob_scaled = cache.calculate_scaled_supply(deposit);
        cache.mint_supply(bob_scaled);
        cache.credit_cash(deposit);

        let total_owed = cache.unscale_supply_floor(cache.supplied());
        assert!(
            total_owed > cache.cash(),
            "post-deposit books insolvent: owed {} > cash {}",
            total_owed,
            cache.cash()
        );

        let (burn, gross) = cache.resolve_withdrawal(i128::MAX, alice_scaled);
        cache.require_reserves(gross);
        cache.burn_supply(burn);
        cache.debit_cash(gross);

        assert!(gross > 0, "wiped position pays out real cash");
        assert_eq!(gross, deposit, "Alice extracts exactly Bob's fresh deposit");

        let bob_claim = cache.unscale_supply_floor(bob_scaled);
        assert!(
            cache.cash() < bob_claim,
            "cash {} cannot cover Bob's honest claim {}: fresh depositor lost funds",
            cache.cash(),
            bob_claim
        );
    });
```
