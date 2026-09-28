### Title
Bad-debt write-down clamps `supply_index` to `SUPPLY_INDEX_FLOOR` instead of zero, leaving wiped suppliers a residual claim that drains future deposits — (`contracts/pool/src/interest.rs`)

### Summary
The memory-corruption class maps onto state corruption via an index floor: when `apply_bad_debt_to_supply_index` socializes bad debt that meets or exceeds total supplied value, it clamps the resulting `supply_index` **up** to `SUPPLY_INDEX_FLOOR_RAW` (RAY/1000) rather than to zero. Surviving supply shares therefore keep a residual asset claim backed by nothing. The market stays open, so the first fresh deposits recapitalize those phantom claims, and the wiped holder can withdraw them, stealing the new depositor's cash. The pool's own tests prove the drain at cache level (`test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard`, `test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard`).

### Finding Description
In `contracts/pool/src/interest.rs:73-89`, `apply_bad_debt_to_supply_index` computes `remaining = total_supplied_value − min(bad_debt, total_supplied_value)`; on a full wipeout `remaining = 0`, so `new_supply_index = supply_index * 0 = 0`, but line 88 applies `.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))`, restoring the index to RAY/1000 [1](#0-0) . Every scaled supply share then unscales to roughly `scaled / 1000` asset units despite the market holding zero cash.

This function is reached by an unprivileged caller through `clean_bad_debt`: `execute_bad_debt_cleanup` builds `PoolSeizeEntry` items and calls `pool_seize_positions_call` [2](#0-1) , and the pool's seize op socializes each `Borrow` entry via `apply_bad_debt_to_supply_index` before burning the debt [3](#0-2) . No mechanism was found that closes or pauses the market after a wipeout, and `resolve_withdrawal`/`require_reserves` cap payouts only by the caller's scaled balance and pool cash, not by a fair-share-of-cash bound [4](#0-3) .

The unit tests demonstrate the exact exploit sequence: after a wipeout clamps the index to the floor, the wiped holder's `unscale_supply_floor` returns a positive "stranded" amount; a victim then deposits `c` units (`mint_supply` + `credit_cash`), and the wiped holder's `resolve_withdrawal(i128::MAX, scaled)` pays out exactly `c`, leaving `cash < bob_claim` — provable insolvency [5](#0-4) .

### Impact Explanation
Theft of user funds and protocol insolvency. Any supplier whose shares survive a full bad-debt write-down retains a phantom claim. When honest users (or the attacker themselves via a second address, or recapitalize flows) put new cash into the still-open market, the stranded holder withdraws real tokens exceeding their fair share, directly transferring the new deposit to the wiped position. The test asserts `gross == deposit` and `cash < bob_claim`, i.e., the fresh depositor loses their entire principal [6](#0-5) .

### Likelihood Explanation
Requires a market to suffer bad debt ≥ total supplied value — a full wipeout — which is tail-event territory but reachable: an unprivileged borrower whose collateral collapses (sharp price move, liquidation lag) leaves debt exceeding collateral; anyone can then call `clean_bad_debt`, which seizes the `Borrow` position and invokes the write-down. Once triggered, exploitation is deterministic: the attacker only needs to hold any supply shares in that market at wipeout time (even dust) and withdraw after the next deposit. Nothing prevents `supply`/`withdraw` on a floored market.

### Recommendation
On full write-down, either (a) reduce `supply_index` to zero and permanently close the market (reject `supply`, `borrow`, `seize` thereafter, allowing only proportional pro-rata claims against remaining cash), or (b) track a `stranded`/deferred-claim bucket so residual shares can only be paid from recovered funds, never ahead of fresh depositors. Withdrawals on a market whose index sits at `SUPPLY_INDEX_FLOOR_RAW` after a wipeout should be gated or made pro-rata to cash.

### Proof of Concept
1. Attacker supplies dust into market M (any scaled supply amount, e.g., `scaled_a`), and holds a separate underwater borrow position whose debt, after collateral seizure, exceeds M's total supplied value.
2. Any caller invokes `clean_bad_debt(account_id)`; `execute_bad_debt_cleanup` emits a `PoolSeizeEntry{side: Borrow}` and the pool calls `apply_bad_debt_to_supply_index`, which computes `reduction_factor = 0` and clamps `supply_index` to `SUPPLY_INDEX_FLOOR_RAW`.
3. The market remains open. `unscale_supply_floor(scaled_a)` returns `stranded > 0` while `cash == 0`.
4. Victim calls `supply(c)`; pool mints `scaled_b` and credits `c` cash.
5. Attacker calls `withdraw(i128::MAX)`; `resolve_withdrawal` unscales `scaled_a` at the floored index, `require_reserves` passes (`cash == c ≥ gross == stranded`), and `debit_cash(gross)` transfers the victim's deposit to the attacker. `cash` is now 0 while the victim's claim `b_claim == c` — insolvency, exactly as encoded in `test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard`.

Uncertainty note: the test names reference a "supply guard" that could conceivably live in the ops layer; I found no market-close/pause flag and `withdraw` only checks reserves-vs-cash, but I did not fully read `ops/withdraw.rs`/`guards.rs`. If a guard blocking withdrawals on floored markets exists there, the finding would be mitigated; nothing in the searched code indicates one.

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

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L42-50)
```rust
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Borrow,
            position: (&position).into(),
        });
    }
    let pool_addr = cache.cached_pool_address();
    pool_seize_positions_call(env, &pool_addr, &entries);

```

**File:** contracts/pool/src/ops/seize.rs (L24-28)
```rust
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
```

**File:** contracts/pool/src/cache/scale.rs (L94-105)
```rust
    /// Resolves a withdrawal request into (shares burned, gross asset amount).
    ///
    /// Caps against `pos_scaled` so the user cannot withdraw more than held.
    pub(crate) fn resolve_withdrawal(&self, amount: i128, pos_scaled: Ray) -> (Ray, i128) {
        resolve_withdrawal(
            &self.env,
            amount,
            pos_scaled,
            self.supply_index,
            self.params.asset_decimals,
        )
    }
```

**File:** contracts/pool/tests/interest.rs (L332-369)
```rust
        apply_bad_debt_to_supply_index(&mut cache, Ray::from(2_000_000 * RAY));
        assert_eq!(
            cache.supply_index().raw(),
            SUPPLY_INDEX_FLOOR_RAW,
            "wipeout must clamp supply index UP to the floor, not reset the base"
        );

        let stranded = cache.unscale_supply_floor(scaled_a);
        assert!(stranded > 0, "floor clamp leaves userA a phantom claim");
        assert_eq!(cache.cash(), 0, "empty market: no cash to extract yet");

        let c = stranded;
        let scaled_b = cache.calculate_scaled_supply(c);
        cache.mint_supply(scaled_b);
        cache.credit_cash(c);

        let b_claim = cache.unscale_supply_floor(scaled_b);
        assert_eq!(b_claim, c, "userB's honest claim equals their deposit");

        let (burn, gross) = cache.resolve_withdrawal(i128::MAX, scaled_a);
        cache.require_reserves(gross);
        cache.burn_supply(burn);
        cache.debit_cash(gross);

        assert!(gross > 0, "stranded position pays out non-zero");
        assert_eq!(
            gross, c,
            "userA drains exactly userB's fresh deposit out of the pool"
        );

        assert!(
            cache.cash() < b_claim,
            "pool cash ({}) can no longer cover userB's claim ({}): honest supplier lost funds",
            cache.cash(),
            b_claim
        );
        assert_eq!(cache.cash(), 0, "userA drained the pool to empty");
    });
```
