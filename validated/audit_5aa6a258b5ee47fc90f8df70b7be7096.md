### Title
Bad-debt index floor leaves wiped suppliers with live withdrawal claims - (File: contracts/pool/src/ops/seize.rs)

### Summary
Debt seizure writes down `supply_index` but leaves every account’s scaled supply shares unchanged. When the write-down reaches `SUPPLY_INDEX_FLOOR_RAW`, those stale shares still unscale to a positive token amount, allowing a wiped-out supplier to withdraw tokens deposited later by a fresh supplier. [1](#0-0) [2](#0-1) 

### Finding Description
An unprivileged caller can invoke `clean_bad_debt(caller, account_id)` for an eligible insolvent account, or trigger the same cleanup through `liquidate`. [3](#0-2)  The controller forwards the account’s scaled debt positions to the pool. [4](#0-3) 

For a borrow-side entry, `seize::apply` converts the scaled debt to an asset amount, calls `apply_bad_debt_to_supply_index`, and burns the debt without changing outstanding supply-share balances. [5](#0-4)  The documented lower bound can preserve an unbacked residual claim rather than reducing old supply shares to zero. [6](#0-5) 

The in-repo regression model demonstrates the exact dangling-claim state: a `5_000`-unit write-down against `1_000` scaled supply clamps the index to `RAY/1000`, after which the old shares still unscale to a positive “stranded” claim. [7](#0-6)  A subsequent deposit then gives that wiped position real reserves to withdraw, leaving the fresh supplier’s claim uncovered. [8](#0-7) 

### Impact Explanation
This is theft of user funds and can create protocol insolvency. Every pre-wipeout scaled supply position remains a live claim for `scaled_amount * RAY/1000` after what should have been a full loss allocation. Once new liquidity enters the affected market, holders of those stale claims can withdraw real tokens even though their economic claims were already socialized away.

The loss is bounded by the residual stale claims, but scales with the wiped market’s share supply. A new depositor can permanently lose principal up to the aggregate residual amount.

### Likelihood Explanation
The trigger requires a bad-debt write-down large enough to reach the supply-index floor. That condition is reachable when high-utilization debt plus accrued interest exceeds the market’s remaining supply claim and the borrower’s collateral becomes dust or is exhausted during liquidation. Both `liquidate` and `clean_bad_debt` are unprivileged paths, and no administrative action or contract upgrade is required. [3](#0-2) [5](#0-4) 

After the clamp, the market is not tombstoned or reset; later deposits can mint fresh supply at the floored index while old scaled positions remain withdrawable.

### Recommendation
Represent a complete supply wipeout explicitly instead of relying on a nonzero index floor. For example:

- Add a market generation/epoch to supply positions. On full write-down, increment the epoch, clear `supplied` and `revenue`, and make pre-epoch scaled shares unscale to zero.
- Alternatively, support `supply_index == 0` as “all legacy supply claims are zero” and bootstrap the next deposit at a fresh index. This still requires an epoch or equivalent guard so stale share balances cannot be interpreted under the new index.
- Add a post-seizure invariant proving the floored value of outstanding supply claims does not exceed `cash + outstanding_debt`; special-case the full-wipeout branch so old shares cannot withdraw future cash.
- Add a public-flow regression that performs wipeout, fresh `supply`, and old-position `withdraw`, asserting the old withdrawal resolves to zero.

### Proof of Concept
1. `A` supplies `S` units of token `T`, receiving scaled supply `S_old`.
2. `B` supplies collateral and borrows nearly all available `T`.
3. `B`’s collateral collapses and accrued debt exceeds the value backing all `T` supply.
4. A liquidator calls `liquidate(B_account, debt_payments, SeizeMode::Transfer)` and leaves eligible residual debt, or any caller invokes `clean_bad_debt(B_account)`.
5. The pool calls `apply_bad_debt_to_supply_index`; the required write-down is clamped at `RAY/1000`, while `A` keeps `S_old`. [5](#0-4) 
6. `A`’s wiped position still has claim `R = floor(S_old * RAY/1000)`.
7. Victim `V` deposits at least `R` of `T`.
8. `A` performs a full withdrawal of its old supply position and receives `R` real tokens.
9. `V`’s booked claim remains, but pool cash no longer covers it. The indexed regression demonstrates this exact drain: the stale withdrawal pays the fresh deposit and leaves the fresh supplier undercollateralized. [9](#0-8)

### Citations

**File:** contracts/pool/src/ops/seize.rs (L20-34)
```rust
    let mut cache = ops::synced_market(env, &entry.hub_asset);
    let position = Ray::from(entry.position.scaled_amount);

    match entry.side {
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

**File:** contracts/pool/README.md (L187-190)
```markdown
`borrow_index` only ever grows — `update_borrow_index` is its sole writer.
`supply_index` is **not** monotone: `apply_bad_debt_to_supply_index` scales it
down to socialize a loss across suppliers, floored at `SUPPLY_INDEX_FLOOR_RAW`
(`RAY/1000`). Anything caching an index must tolerate a decrease.
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-200)
```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
}
```

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L35-49)
```rust
    for (hub_asset, position) in iter_debt_positions(&account.borrow_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Borrow,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Borrow,
            position: (&position).into(),
        });
    }
    let pool_addr = cache.cached_pool_address();
    pool_seize_positions_call(env, &pool_addr, &entries);
```

**File:** docs/reference/invariants.md (L240-247)
```markdown
### INV-IDX-02 — Supply index is bounded

The supply index stays within 10^24 to 10^36 raw RAY, inclusive. Interest
distribution cannot lower it; bad-debt writeoff applies the lower bound. These
are protocol constants, not per-market governance settings.

The lower bound prevents a zero conversion divisor but can preserve an unbacked
residual claim.
```

**File:** contracts/pool/tests/interest.rs (L388-397)
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
```

**File:** contracts/pool/tests/interest.rs (L403-426)
```rust
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
