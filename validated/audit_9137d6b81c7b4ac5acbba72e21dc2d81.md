### Title
RAY-scaled debt accrual overflows before the index cap and permanently freezes the market - (File: `common/src/rates/index.rs`)

### Summary
The Firefox memory-corruption class maps to unchecked numeric bounds in the lending protocol’s fixed-point accounting. Debt and supply shares are stored as RAY values, while every market mutation first accrues interest into the borrow and supply indexes. A sufficiently large high-utilization market can reach the `i128` RAY-value ceiling before `MAX_BORROW_INDEX_RAY`, after which index synchronization always panics with `MathOverflow`. Because repayment, withdrawal, liquidation, recapitalization, and parameter updates all accrue first, the market becomes unable to operate. [1](#0-0) [2](#0-1) 

### Finding Description
The protocol documents a token-to-RAY input maximum, but does not bound the later product of scaled shares and the borrow index. `Cache::calculate_utilization` converts total debt and total supply through `scaled_to_original`, so synchronization must materialize the accrued RAY value before it can update the market. [3](#0-2)  The checked conversion panics when total debt no longer fits `i128`; the borrow index may still be below its explicit ceiling, so the cap does not stop accrual before the value overflow. [4](#0-3) 

All user-facing recovery paths depend on a synchronized market. The permissionless controller exposes `update_indexes`, `repay`, `withdraw`, `liquidate`, `clean_bad_debt`, `recapitalize`, and borrowing, while the pool’s mutation pipeline explicitly runs `Cache::load`, `interest::global_sync`, mutation, guards, and commit for each market operation. [5](#0-4) [6](#0-5)  Once `global_sync` reaches the overflowing accrual, each such call rolls back at the same arithmetic point. [7](#0-6) 

### Impact Explanation
This causes permanent freezing of user funds and leaves the affected market unable to operate from a checked-arithmetic failure. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot reduce unsafe debt, and a payer cannot recapitalize the market because those paths first synchronize the corrupted market state. [8](#0-7) [7](#0-6)  The regression test demonstrates the terminal state: `update_indexes` returns `MathOverflow`, `withdraw` returns `MathOverflow`, and `repay` returns `MathOverflow`. [4](#0-3) 

### Likelihood Explanation
Likelihood is low and depends on an extreme book: the repository’s reproduction uses a billion-unit 18-decimal market at approximately 98% utilization under the XLM interest curve, then advances ledger time until accrued debt crosses the representable RAY-value domain before the index ceiling. [9](#0-8)  No privileged action or malicious token is required once such a market exists; any unprivileged caller can trigger and repeatedly observe the freeze through `update_indexes`. [10](#0-9) [11](#0-10) 

### Recommendation
Add an explicit market-level debt-value ceiling below the point at which `scaled * borrow_index` can overflow `i128`, and enforce it during market admission, cap changes, supply, borrow, and accrual. Index growth should be clamped before unscaling the enlarged debt value, or accrual should cap `borrow_index` and the associated debt expansion atomically so ordinary repayment and withdrawal remain possible. A safe recovery path is also needed for a market already at the boundary: an owner-authorized write-down or debt migration that does not first evaluate the overflowing `scaled_to_original` conversion.

### Proof of Concept
The repository already contains the executable scenario in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`. [12](#0-11) 

1. Create an 18-decimal `BIG18` market using the XLM rate curve and a separate collateral market.
2. Raise the relevant supply and borrow caps to the permitted domain.
3. Have one unprivileged account supply `1e9 * 10^18` units of `BIG18`, supply sufficient collateral, and borrow `0.98 * 10^9 * 10^18` units.
4. Advance ledger time and call the permissionless controller `update_indexes(caller, [BIG18])` until accrual fails.
5. Observe `MathOverflow` while the stored borrow index remains below `MAX_BORROW_INDEX_RAY`.
6. Call `withdraw` and `repay` for the same market; both return `MathOverflow` before any token settlement, leaving supplier funds and borrower collateral unusable. [13](#0-12)

### Citations

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-361)
```rust
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
#[test]
fn a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap() {
    let mut t = LendingTest::new()
        .with_market(big("BIG18", 18, xlm_curve()))
        .with_market(col())
        .with_max_utilization_disabled_all_markets()
        .build();
    lift_caps(&t, "BIG18", 18);
    lift_caps(&t, "COL", 7);
    let principal = BILLION * 10i128.pow(18);
    t.supply_raw(BOB, "BIG18", principal);
    let debt = principal / 100 * 98;
    t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
    t.borrow_raw(ALICE, "BIG18", debt);

    let mut years = 0u32;
    let failure = loop {
        years += 1;
        assert!(
            years <= 40,
            "no cliff within 40 years; the bound in docs/reference/formulas.md is wrong"
        );
        t.advance_time(YEAR_SECS);
        if let Err(e) = t.try_update_indexes_for(&["BIG18"]) {
            break e;
        }
    };
    let failed: Result<(), soroban_sdk::Error> = Err(failure);
    assert_contract_error(failed, errors::MATH_OVERFLOW);
    let last = book(&t, "BIG18");
    assert!(
        last.borrow_index < MAX_BORROW_INDEX_RAY,
        "the index cap did not engage before the value overflow"
    );
    // The market is frozen: exits and repayments accrue first and hit the same panic.
    assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
    assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
    std::println!(
        "ray-value cliff reached after {years} years at 98 percent utilization on the XLM curve; last index x{:.1}",
        last.borrow_index as f64 / RAY as f64
    );
}
```

**File:** docs/reference/formulas.md (L425-437)
```markdown
| Asset decimals 0..=18 | Exact token-to-RAY upscaling. Below 3: collateral only, no flash loans, no liquidation fee, its account's only supply position, at least 2 whole units while in debt |
| Both indexes initially RAY; ceiling 10^36 | 10^9 times initial index; protocol constants |
| Supply-index floor 10^24 | At most 1,000 times the shares minted at index one for the same deposit |
| Borrow APR maximum 2 RAY | 200% annual rate; not a bound on balance growth alone |
| Token-to-RAY input maximum `i128::MAX / 10^(27-d)` | About 170.14 billion whole tokens, before other limits |
| Deposit conversion at the supply-index floor | About 170.14 million whole tokens before scaled-share overflow |

The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```

**File:** contracts/pool/src/cache/scale.rs (L19-27)
```rust
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
    }
```

**File:** contracts/controller/src/lib.rs (L104-180)
```rust
    /// Borrows against `account_id`'s collateral, paying `to` or the caller.
    /// Requires owner or delegate authorization and post-borrow solvency.
    #[when_not_paused]
    fn borrow(
        env: Env,
        caller: Address,
        account_id: u64,
        borrows: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) {
        positions::process_borrow(&env, &caller, account_id, &borrows, to);
    }

    /// Withdraws collateral to `to` or the caller and returns actual amounts in
    /// asset units. Zero withdraws an asset's full position. Requires owner or
    /// delegate authorization and post-withdrawal solvency.
    fn withdraw(
        env: Env,
        caller: Address,
        account_id: u64,
        withdrawals: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) -> Vec<(HubAssetKey, i128)> {
        positions::process_withdraw(&env, &caller, account_id, &withdrawals, to)
    }

    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
    }

    /// Repays debt and seizes collateral at a health-factor-based bonus.
    /// Permissionless, including self-liquidation; requires liquidator authorization.
    /// Residual bad debt is socialized only at or below the collateral dust cap.
    ///
    /// `Transfer` pays pool cash and returns `0`. `Credit(id)` moves net supply
    /// shares to a different, authorized Normal-mode account on the same spoke;
    /// `Credit(0)` creates one. Credit mode needs no free collateral liquidity
    /// and returns the receiving account id.
    fn liquidate(
        env: Env,
        liquidator: Address,
        account_id: u64,
        debt_payments: Vec<(HubAssetKey, i128)>,
        seize_mode: SeizeMode,
    ) -> u64 {
        positions::liquidation::process_liquidation(
            &env,
            &liquidator,
            account_id,
            &debt_payments,
            seize_mode,
        )
    }

    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
    }

    /// Flash-loans `amount` of `asset` to a deployed Wasm `receiver`, invoking
    /// its callback with `data`. The pool recovers principal plus fee before return.
    /// Permissionless; requires caller authorization.
    #[when_not_paused]
    fn flash_loan(
        env: Env,
        caller: Address,
        asset: HubAssetKey,
        amount: i128,
        receiver: Address,
        data: Bytes,
    ) {
        strategies::flash_loan::process_flash_loan(&env, &caller, &asset, amount, &receiver, &data);
    }
```

**File:** contracts/controller/src/lib.rs (L367-395)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }

    /// Claims pool revenue and forwards measured receipts to the accumulator.
    /// Returns those amounts in asset units, in input order. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn claim_revenue(env: Env, caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128> {
        markets::claim_revenue(&env, caller, assets)
    }

    /// Refreshes supply LTV snapshots. With `has_risks`, also refreshes gated
    /// liquidation parameters and requires a final health factor of at least
    /// 1.05 WAD. Permissionless; requires caller authorization.
    #[when_not_paused]
    fn update_account_threshold(env: Env, caller: Address, has_risks: bool, account_ids: Vec<u64>) {
        risk::params::update_account_threshold(&env, caller, has_risks, account_ids);
    }

    /// Covers a pool backing shortfall using measured receipts from `payer`.
    /// Refunds excess and returns the amount applied in asset units.
    /// Permissionless; requires payer authorization.
    fn recapitalize(env: Env, payer: Address, hub_asset: HubAssetKey, amount: i128) -> i128 {
        markets::recapitalize(&env, payer, hub_asset, amount)
    }
```

**File:** contracts/pool/README.md (L159-176)
```markdown
Each mutation of an existing market runs this sequence:

```text
entrypoint (#[only_owner])
  → Cache::load             # read params + state, bump TTL
  → interest::global_sync   # accrue to now, in ≤1yr chunks
  → mutate                  # cache/shares.rs, cache/cash.rs
  → guards::*               # reserve, utilization, backing checks
  → commit → transfer_out → emit
```

Checks-effects-interactions holds everywhere except `flash_loan`, which inverts
by nature and compensates with balance reconciliation.

`ops::run_batch` gives each entry its own `Cache::load`, so two entries hitting
the same market in one batch compose correctly — the second reads the first's
committed state. Indexers: a market touched twice emits two snapshots in one
`PoolMarketStateBatchEvent`; take the last. An empty batch emits nothing.
```

**File:** contracts/controller/src/markets.rs (L119-125)
```rust
pub(crate) fn update_indexes(env: &Env, caller: Address, assets: Vec<HubAssetKey>) {
    validation::require_authorized_caller(env, &caller);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    pool_update_indexes_call(env, &pool_addr, &assets);
}
```
