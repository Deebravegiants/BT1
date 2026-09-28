### Title
Tokens transferred directly to a lending pool or the controller are permanently locked — there is no rescue path (File: contracts/pool/src/lib.rs)

### Summary
The EAS report class is "value can enter a contract that has no way to send it back out." In XOXNO Lending the analog is a direct SAC `transfer` of a market asset to a `LiquidityPool` contract (or of any token to the controller). The pool deliberately tracks `cash` as a bookkeeping figure that unsolicited token donations never increase (INV-ACCT-02), and neither the pool nor the controller exposes any sweep/rescue entrypoint. The donated balance becomes dead collateral: it can never be credited to anyone and can never be withdrawn.

### Finding Description
`LiquidityPool` accounting treats `cash` as the only reserve book — "tracked cash, rather than an incidental token balance, is the reserve book" [1](#0-0) . `INV-ACCT-02` states explicitly that "token donations alone do not increase" cash [2](#0-1) , and the formulas doc repeats that "incidental token donations do not increase" tracked cash [3](#0-2) .

The pool's entire token-moving surface is `supply`, `borrow`, `withdraw`, `repay`, `seize_positions`, `claim_revenue`, `recapitalize`, `flash_loan`, and `create_strategy` — every mutator is `#[only_owner]` (the controller), and none of them reads `token.balance(pool)` except `flash_loan`, which only checks it with strict equality for its own lend/return invariant [4](#0-3) . There is no `sweep_balance`-style recovery function on the pool, and the controller's public surface likewise contains no way to withdraw arbitrary stray token balances — tests explicitly pin that pre-existing controller token balances are never swept or credited [5](#0-4) .

Contrast with the in-repo `sweep_balance` precedent on the swap aggregator, which exists precisely because stray balances otherwise become unrecoverable [6](#0-5) .

### Impact Explanation
Permanent freezing of funds. An unprivileged user who executes `token.transfer(user, pool, amount)` (or sends to the controller) loses the tokens forever:

- The donation is not credited to `cash`, so it buys no supply shares and cannot be withdrawn via `withdraw` — `require_reserves`/withdraw debits the cash book, and the donation is outside it.
- `backing_shortfall` computes `floor(supply) - (cash + ceil(debt))` from books only [7](#0-6) , so a donation cannot even be absorbed via `recapitalize` — `recapitalize` credits `min(measured_receipt, shortfall)` using the controller's measured balance delta, not the pool's existing balance [8](#0-7) .
- The excess sits in custody indefinitely; the pool's own money-flow test treats a donation as a permanent add-on to custody that no book ever claims [9](#0-8) .

The same applies to any token sent to the controller: refund paths in `repay`, `swap_debt`, `repay_debt_with_collateral`, and `migrate_from_blend` deliberately transfer only the measured strategy excess, leaving pre-existing balances untouched and unrecoverable [10](#0-9) .

### Likelihood Explanation
The reach rule explicitly includes "direct token transfers to the pool or controller," and on Stellar any wallet or dapp can address a SAC transfer to a contract address. Fat-finger deposits to a contract instead of the intended entrypoint are a well-documented real-world occurrence. There is no front-running or special condition required; every transfer of this kind is irrecoverable the moment it lands. Severity is capped at Medium because loss requires the victim's own mistaken transfer rather than an attacker action.

### Recommendation
Add an owner-only `sweep(asset, to)` on the pool that transfers only `balance - sum_of_cash_for_that_asset` (markets sharing one physical balance must protect every sibling market's cash book, as the fuzz harness notes [11](#0-10) ), routed through governance/timelock. For tokens not used by any market on that pool, the full balance is sweepable. Optionally expose a controller-level `claim_revenue`-style rescue for non-market tokens sent to the controller. Until then, document that direct SAC transfers to pool/controller addresses are unrecoverable.

### Proof of Concept
Conceptual Soroban sequence:

```rust
let pool = market.pool;          // LiquidityPool contract address
let token = token::Client::new(&env, &market.asset);

// User error: sends tokens straight to the pool contract.
token.transfer(&user, &pool, &1_000_0000000);

// No state changes: cash book ignores the donation (INV-ACCT-02).
assert_eq!(pool_client.get_reserves(&hub_asset), cash_before);

// No callable entrypoint can return the tokens:
//  - withdraw/borrow/claim_revenue only move cash-booked amounts;
//  - recapitalize applies min(measured receipt, backing_shortfall)=0 on a
//    backed market and refunds only the just-received amount;
//  - there is no sweep/rescue on pool or controller.
// Result: the 1_000 units are permanently locked in the pool's SAC balance.
```

This is exactly the scenario the pool's own audit test encodes: after `token.transfer(&payer, &market.pool, &(7 * UNIT))`, the balance is `cash + other_cash + 7 * UNIT` and the extra `7 * UNIT` belongs to no book and no claimant [12](#0-11) .

### Citations

**File:** certora/pool/spec/README.md (L84-88)
```markdown
### Cash and revenue

Tracked cash, rather than an incidental token balance, is the reserve book.
Claims, recapitalization, strategy fees, and liquidation fees must preserve
the relationship among cash, supplied shares, borrowed shares, and revenue.
```

**File:** docs/reference/invariants.md (L104-109)
```markdown
### INV-ACCT-02 — Cash is the reserve book

Reserve checks use tracked market cash; token donations alone do not increase
it. Cash credits and debits reject negative amounts. Credits reject overflow,
and debits reject insufficient reserves. Outbound token transfer and cash
bookkeeping remain separate actions.
```

**File:** docs/reference/formulas.md (L76-82)
```markdown
## Cash, supply, debt, and revenue

Revenue is a supply-share claim included in total supplied shares. Revenue
minting increases both totals equally; claiming revenue burns both equally.
Reclassifying seized collateral as revenue leaves total supply unchanged.
Tracked cash is a separate reserve balance that incidental token donations do
not increase.
```

**File:** docs/reference/formulas.md (L86-94)
```markdown
The market's backing check uses native units:

```rust
let shortfall = max(0, floor(supply_value) - (cash + ceil(debt_value)));
```

Addition and subtraction saturate. Supply entry rejects a positive shortfall.
Recapitalization credits at most that shortfall, refunds excess and mints no
shares.
```

**File:** contracts/pool/README.md (L61-88)
```markdown
controller's word, without verifying the transfer. `cash` is a bookkeeping
number. The only reconciliation against a real `token.balance()` is in
`flash_loan`, which checks it three times with strict equality.

## Surface

| Entrypoint | Role | Tokens |
| --- | --- | --- |
| `create_market` | Verify params, write state, indexes at `RAY` | — |
| `update_params` | Accrue on the **old** curve, then replace the rate model | — |
| `update_indexes` | Accrue each market in the vec; commit only if time elapsed | — |
| `supply` | Mint supply shares, credit cash | in |
| `borrow` | Mint debt shares, debit cash, transfer | out |
| `withdraw` | Burn supply shares, withhold liquidation fee, transfer net | out |
| `repay` | Burn debt shares, credit net, refund overpayment | in/out |
| `net_settle` | Offset a user's own supply against their own debt | — |
| `seize_positions` | Bad-debt write-down, or deposit → revenue | — |
| `claim_revenue` | Burn revenue shares, transfer to owner | out |
| `recapitalize` | Credit cash up to the backing shortfall, refund excess | in/out |
| `flash_loan` | Payout → callback → collect principal + fee | out/in |
| `create_strategy` | Borrow for a strategy, net of fee | out |
| `upgrade` | Replace contract Wasm | — |

Tokens column: `in` means the controller transferred to the pool before the
call and the pool only credits `cash`; `out` means the pool transfers. `in/out`
is an inbound amount with an outbound refund leg — `repay` returns
overpayment, `recapitalize` returns whatever exceeded the shortfall.
`flash_loan` is `out/in`: principal leaves, then principal plus fee returns.
```

**File:** tests/test-harness/tests/strategy/migrate_blend.rs (L529-535)
```rust
    let controller_eth = t.env.as_contract(&t.controller, || {
        soroban_sdk::token::Client::new(&t.env, &eth).balance(&t.controller)
    });
    assert_eq!(
        controller_eth, stuck,
        "pre-existing controller ETH must remain (not used as refund or swept)"
    );
```

**File:** contracts/swap-aggregator/src/lib.rs (L187-202)
```rust
    /// Transfers each token's balance above its reserved fee total to `recipient`. Owner only.
    #[only_owner]
    fn sweep_balance(env: Env, recipient: Address, tokens: Vec<Address>) {
        renew_instance(&env);
        let router = env.current_contract_address();
        let n = tokens.len();
        for i in 0..n {
            // `i < n == tokens.len()`, so the index is in range by construction.
            let token = tokens.get_unchecked(i);
            let client = token::Client::new(&env, &token);
            let balance = client.balance(&router);
            let reserved = storage::reserved_fee_balance(&env, &token);
            if balance > reserved {
                client.transfer(&router, &recipient, &(balance - reserved));
            }
        }
```

**File:** contracts/pool/src/ops/recapitalize.rs (L44-58)
```rust
pub(crate) fn accounting(
    env: &Env,
    hub_asset: HubAssetKey,
    amount: i128,
) -> RecapitalizationOutcome {
    require_nonneg_amount(env, amount);
    let mut cache = ops::renewed_market(env, &hub_asset);

    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();
```

**File:** tests/test-harness/tests/pool_money_flow_audit.rs (L86-102)
```rust
    // An unsolicited donation belongs to no market's cash book.
    market.token_admin.mint(&payer, &(7 * UNIT));
    token.transfer(&payer, &market.pool, &(7 * UNIT));
    let check = |supply, debt, label: &str| {
        let state = books(&t, &key, supply, debt);
        let other = books(&t, &second, secondary_supply, 0);
        assert_eq!(other.cash, 100 * UNIT);
        assert_eq!(
            token.balance(&market.pool),
            state.cash + other.cash + 7 * UNIT
        );
        println!(
            "{label}: cash={}, supply={}, debt={}, revenue={}",
            state.cash, state.supplied, state.borrowed, state.revenue
        );
        state
    };
```

**File:** tests/test-harness/tests/strategy/edge/swap.rs (L30-34)
```rust
    );
    assert_eq!(
        controller_eth_after, 50_0000000i128,
        "unrelated controller ETH balance must not be swept to the caller"
    );
```

**File:** tests/fuzz/fuzz_targets/pool_native.rs (L101-123)
```rust
/// Asserts that the driven and sibling market cash sums to at most the pool token balance.
///
/// Markets on one asset share the token balance, so a per-market `cash <= balance`
/// check cannot detect an overdraw.
fn assert_cash_matches_balance(
    env: &Env,
    pool: &LiquidityPoolClient<'_>,
    pool_addr: &Address,
    asset: &Address,
    state: &PoolStateRaw,
) {
    let sibling = pool_state(pool, &hub_asset_in(asset, SIBLING_HUB_ID)).cash;
    let tracked = state.cash + sibling;
    let balance = pool_balance(env, asset, pool_addr);
    assert!(
        tracked <= balance,
        "tracked cash across markets on this asset exceeds token balance: \
         driven={} sibling={} balance={}",
        state.cash,
        sibling,
        balance,
    );
}
```
