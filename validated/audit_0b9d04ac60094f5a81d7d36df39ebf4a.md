### Title
Pool `supply`/`repay`/`recapitalize` trust the declared `action.amount` instead of the measured token receipt, so fee-on-transfer (or any under-delivering) tokens mint unbacked shares, burn unbacked debt, and drain refunds - (File: contracts/pool/src/ops/supply.rs)

### Summary
The pool ops credit `cash` and mutate positions purely from the caller-supplied `PoolAction.amount`, never measuring the token balance delta that actually arrived. The controller-side prefund path measures receipts correctly (`transfer_amount_measured` in `settle_repay` / `process_deposit`), but the pool entrypoints are directly callable by any address, so an unprivileged user can pre-transfer an under-delivering token and then declare the full pre-fee amount, desynchronizing the cash book from custody and extracting value.

### Finding Description
`supply::apply` mints scaled supply shares and calls `cache.credit_cash(amount)` using `entry.action.amount` verbatim (`contracts/pool/src/ops/supply.rs:24-38`). `repay::accounting` burns debt shares and credits `net_repay` from `action.amount`, then refunds `overpayment` to `payer` via `transfer_out` (`contracts/pool/src/ops/repay.rs:40-66`). `recapitalize::accounting` likewise credits `applied` and refunds `refund` computed from the declared `amount` (`contracts/pool/src/ops/recapitalize.rs:44-66`). None of these read `token::Client::balance`; the only custody-mutating call is the outbound `Cache::transfer_out` (`contracts/pool/src/cache/cash.rs:46-53`).

The controller is careful — `settle_repay` measures the pool's delta and submits `amount_in` (`contracts/controller/src/positions/debt.rs:144-152`), and `process_deposit` does the same (`contracts/controller/src/positions/supply.rs:118-129`) — but that protection is bypassed entirely when a user calls `pool.supply`/`pool.repay`/`pool.recapitalize` directly, which the harness test does without any controller auth (`tests/test-harness/tests/pool_money_flow_audit.rs:53-64`).

### Impact Explanation
- Supply theft: transfer `N` of a fee-on-transfer token to the pool (pool receives `N·(1−f)`), call `supply` with `amount=N`. Shares worth `N` are minted against `N·(1−f)` real custody; `withdraw` then extracts `N`, draining other suppliers (protocol insolvency / theft of user funds).
- Repay theft: burn `N` of debt shares while funding only `N·(1−f)` — debt repayment at a discount.
- Refund drain: declare `amount` exceeding debt/shortfall; the pool transfers the `overpayment`/`refund` in real tokens for an inflated declared amount.
- Even without malicious FOT intent, a market configured with an under-delivering token silently accrues a cash-vs-custody gap = accumulated fees, i.e., progressive insolvency.

### Likelihood Explanation
Medium-to-high: the pool endpoints are public Soroban contract functions with no caller check in `apply`, the prefund amount is not verified, and the only prerequisite is a market whose token charges on transfer (or any token a user can make under-deliver). The victim is other suppliers' principal.

### Recommendation
In each inbound pool op (`supply`, `repay`, `recapitalize`), snapshot the market asset balance before trusting `action.amount`, or require the controller entrypoint pattern on the pool itself: measure `balance(post) − balance(pre)` of the pool around an internal pull, and use the measured delta for `credit_cash`, share minting, and refund computation — mirroring `transfer_amount_measured` (`common/src/token.rs:16-31`).

### Proof of Concept
```rust
// pool asset = FOT token with 10% fee; attacker has 0 supply
// 1. Fund the pool (pool receives 900)
token::Client::new(&env, &fot).transfer(&attacker, &pool, &1_000);
// 2. Declare the pre-fee amount
let r = pool.supply(&vec![&env, PoolSupplyEntry {
    action: PoolAction { hub_asset: key, position: pos(0), amount: 1_000 },
}]).get(0).unwrap();
// shares for 1_000 minted; cash book +1_000; custody +900
// 3. withdraw -> attacker receives 1_000 real tokens, cost 900 effective
```

The same shape applies to `pool.repay` (debt burned at a 10% discount) and `pool.recapitalize` (over-declared `amount` refunded in full).