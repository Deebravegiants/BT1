### Title
Flash-position solvency gate reuses a pre-callback price snapshot that the receiver can manipulate on Aquarius - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
`process_flash_position` snapshots oracle prices into the invocation-local `Context` *before* invoking the user-supplied receiver callback, then evaluates the post-callback solvency gate (`require_post_pool_risk_gates`) against that stale snapshot. When a collateral asset is priced from an Aquarius LP source, the receiver can restore the manipulated pool inside the callback, so the account's debt is validated against a valuation that no longer exists — mirroring CVE-2019-6133, where an authorization decision is made on a check whose underlying fact changed before it was used.

### Finding Description
The polkit bug class is "check cached/non-atomically bound to a mutable fact, act later." XOXNO Lending maps it directly:

1. `process_flash_position` calls `prefetch_strategy_prices(&mut cache, &account, &extra_assets)` which loads each needed asset price once via `cache.fetch_prices` — `Context::fetch_prices` retains already-cached entries and never refetches (`context.rs:142-151`), and `cached_price` panics rather than re-reading (`context.rs:154-160`). This is codified as INV-ORACLE-03: "a context retains fetched prices" (`docs/reference/invariants.md:320-328`). [1](#0-0) [2](#0-1) 

2. Immediately after the snapshot, `with_flash_guard` mints fee-free debt via `mint_and_forward` and calls `invoke_receiver` — arbitrary Wasm code controlled by the caller (`flash_position.rs:120-143`). The flash guard blocks reentry into the *controller*, but the receiver may freely call the Aquarius pool contract to trade. [3](#0-2) 

3. After the callback, `strategy_finalize` → `enforce_post_pool_risk_gates` → `require_post_pool_risk_gates` computes LTV-weighted collateral and HF from `cache.cached_price` — the pre-callback snapshot (`strategies/mod.rs:36-56`, `risk/validation.rs:29`). [4](#0-3) 

4. The price-aggregator supports Aquarius constant-product and stable-swap LP fair-value sources, whose price is a function of live pool reserves — exactly the "start time" fact that fork()-like callback interleaving desynchronizes from the decision.

Attack path (single unprivileged address, one transaction):
- Deploy a receiver contract that, inside `execute_flash_position`, sells the previously-pumped reserve asset back into the Aquarius pool, restoring the honest price, and pushes declared collateral to the controller.
- Earlier in the same transaction, pump the Aquarius pool underlying the collateral's LP oracle source (own trade on Aquarius is in-scope), so the aggregator's `prefetch` snapshot values the collateral at the inflated price.
- Call `flash_position(caller, 0, spoke, Multiply, debt_hub_asset, amount, receiver, data, collaterals, [])`. The gate prices collateral at the pumped snapshot; the true post-callback value is far lower; the account is left with real debt exceeding real collateral.

The same stale-snapshot shape exists in `multiply`/`swap_collateral`/`swap_debt`/`repay_debt_with_collateral` wherever `prefetch_strategy_prices` runs before a router call into an Aquarius venue that also backs a price source, but `flash_position` is the strongest path because the attacker controls arbitrary code between the snapshot and the gate.

### Impact Explanation
Debt is minted and left outstanding on an account whose collateral was validated at a manipulated, no-longer-real price. The resulting account is immediately under-collateralized (`HF < 1` at true prices) and resolves as bad debt socialized across suppliers via the supply-index write-down — protocol insolvency / theft of supplier funds.

### Likelihood Explanation
Requires the collateral asset's oracle config to include an Aquarius LP source (an admitted, documented configuration in `contracts/price-aggregator`) and a flashloanable debt market. All actions — the pump swap, `flash_position` with a self-controlled Wasm receiver, and the unwind swap — are reachable by one unprivileged address in a single transaction. No privileged role, leaked key, or off-chain component is needed; the cost is pool-manipulation capital partially recoverable by the unwind.

### Recommendation
Re-fetch (or invalidate) cached prices in `Context` after external callback boundaries — specifically after `with_flash_guard` in `process_flash_position` and after router `swap_tokens` calls in strategy legs — so `require_post_pool_risk_gates` always values the post-callback state. Alternatively, compute LP-derived prices from reserves captured at gate time, or disallow Aquarius LP sources on assets that can serve as collateral in flash-position strategies.

### Proof of Concept
```rust
// Attacker receiver contract
#[contractimpl]
impl FlashPositionReceiver for PocReceiver {
    fn execute_flash_position(
        env: Env, initiator: Address, account_id: u64, asset: Address,
        amount: i128, _fee: i128, amount_received: i128,
        controller: Address, data: Bytes,
    ) {
        // 1. Unwind the Aquarius pump: sell reserve token back, restoring
        //    the honest LP fair value. The controller's Context already
        //    cached the PUMPED price in prefetch_strategy_prices.
        aquarius.swap(&env, &reserve_in, &amount_in_reserve, &min_out);

        // 2. Push the declared collateral minimum to the controller.
        token::Client::new(&env, &collateral)
            .transfer(&env.current_contract_address(), &controller, &min_amount);
        // returned debt tokens stay on this receiver (fee-free, never repaid)
    }
}

// Same transaction, before flash_position:
//   aquarius.swap(/* buy to pump the LP-priced collateral asset */);
// Controller call:
//   flash_position(attacker, 0, SPOKE, Multiply, USDC_KEY, BIG_AMOUNT,
//                  poc_receiver, plan, [(COLL_KEY, dust_min)], []);
// Result: enforce_post_pool_risk_gates values COLL at the pumped snapshot,
// passes HF >= 1, persists BIG_AMOUNT of USDC debt. At restored prices the
// account is insolvent -> clean_bad_debt socializes the shortfall.
```
Key evidence: prices are fetched-and-retained per `Context` (`context.rs:142-160`), the snapshot precedes `invoke_receiver` (`flash_position.rs:117-143`), and the solvency gate consumes only the cached snapshot (`strategies/mod.rs:48-56`, `risk/validation.rs:29`).

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L113-143)
```rust
    let mut extra_assets = vec![env, debt.asset.clone()];
    for (hub_asset, _) in collaterals.iter() {
        extra_assets.push_back(hub_asset.asset.clone());
    }
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);

    // Guard both forwarding and the callback: token hooks can reenter first.
    let (amount_received, collateral_before, refund_before) =
        storage::with_flash_guard(env, || {
            let amount_received =
                mint_and_forward(env, &mut account, debt, amount, receiver, &mut cache);
            // Baselines exclude funding and forwarding; count callback receipts only.
            let collateral_before = snapshot_balances(
                env,
                &controller,
                collaterals.iter().map(|(hub_asset, _)| hub_asset.asset),
            );
            let refund_before = snapshot_balances(env, &controller, refund_assets.iter());
            invoke_receiver(
                env,
                receiver,
                caller,
                account_id,
                &debt.asset,
                amount,
                amount_received,
                &controller,
                data,
            );
            (amount_received, collateral_before, refund_before)
        });
```

**File:** contracts/controller/src/context.rs (L141-160)
```rust
    /// Fetches missing prices in one aggregator call; retains cached prices.
    pub(crate) fn fetch_prices(&mut self, assets: &Vec<Address>) {
        let missing = collect_uncached_keys(&self.env, assets, &self.token_prices);
        if missing.is_empty() {
            return;
        }
        let fetched = external::price_aggregator::fetch_prices(&self.env, &missing);
        for (asset, feed) in fetched.iter() {
            self.token_prices.set(asset, feed);
        }
    }

    /// Returns a previously loaded price; fails if the cache has no entry.
    pub(crate) fn cached_price(&mut self, asset: &Address) -> PriceFeed {
        let raw = self
            .token_prices
            .get(asset.clone())
            .unwrap_or_else(|| panic_with_error!(&self.env, OracleError::OracleNotConfigured));
        (&raw).into()
    }
```

**File:** contracts/controller/src/strategies/mod.rs (L48-56)
```rust
pub(crate) fn strategy_finalize(
    env: &Env,
    account_id: u64,
    account: &mut Account,
    cache: &mut Context,
) {
    let _ = enforce_post_pool_solvency(env, cache, account);
    finalize_position_flow(env, account_id, account, cache, PositionSides::Both, true);
}
```
