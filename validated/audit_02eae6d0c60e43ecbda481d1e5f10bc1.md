### Title
Unbooked token balances sent to the pool (or stranded on the controller) are permanently locked — no recovery path exists - ([File: contracts/pool/src/cache/cash.rs])

### Summary
The lending pool tracks liquidity through an internal `cash` book, not the token's real balance. Only `supply`, `repay`, and `recapitalize` credit cash, and only owner (controller) entrypoints can move tokens out (`borrow`, `withdraw`, `repay`/`recapitalize` refunds, `claim_revenue`, `flash_loan`, `create_strategy`). Any tokens that arrive at the pool address outside a measured-receipt call — a direct `token.transfer` donation, a mistaken send, or venue rewards pushed permissionlessly — are never booked and can never be withdrawn by anyone, mirroring the stranded-unutilized-funds class of the BribeRewarder report.

### Finding Description
- `Cache` bookkeeping is separate from custody: `credit_cash`/`debit_cash` mutate only the `cash` field, and `transfer_out` moves tokens without touching the book (contracts/pool/src/cache/cash.rs:24-53). The docs confirm the split: "Tracked cash is a separate reserve balance that incidental token donations do not increase" (docs/reference/formulas.md, INV-ACCT-02 in docs/reference/invariants.md:104-109).
- The pool's entire exit surface debits or is bounded by booked `cash`: `debit_cash` reverts via `require_reserves` on insufficient cash, and `claim_revenue` is capped by cash (`burn_claimable_revenue` claims `min(cash, floor(revenue_value))`, contracts/pool/src/ops/revenue.rs:39-54). `recapitalize` credits only up to the backing shortfall `max(0, floor(supply_value) - (cash + ceil(debt_value)))` and refunds all excess to the payer (contracts/pool/README.md:79,113).
- There is no `sweep`/rescue entrypoint in the pool ABI (contracts/pool/README.md:99-115). The test `pool_all_money_paths_preserve_books_and_shared_token_custody` explicitly shows a direct `token.transfer(&payer, &market.pool, 7*UNIT)` leaves `token.balance(pool) = cash + other.cash + 7*UNIT` with no accounting hook (tests/test-harness/tests/pool_money_flow_audit.rs:86-96). The controller likewise has no sweep; recipient checks (GH-17) only prevent borrows/withdraws *addressed* to the contracts, not inbound transfers.
- Because one token can back markets in multiple hubs sharing a single physical pool balance (docs/reference/architecture.md:63-65), the stranded surplus accumulates unowned and unclaimable forever.

### Impact Explanation
Permanent freezing of funds: tokens pushed to the pool outside measured paths (accidental transfers, forced Aquarius venue-reward pushes noted in docs/explanation/threat-model.md:134-140) sit in the contract's balance with zero accounting claim and zero withdrawal path — no privileged function exists either, unlike `sweep_balance` on the swap-aggregator which was given exactly this remediation (contracts/swap-aggregator/src/lib.rs:187-203).

### Likelihood Explanation
Reachable by any unprivileged address via a plain `token.transfer` to the pool/controller — an explicitly allowed surface. Accidental sends and third-party reward pushes are realistic; magnitude scales with whatever is sent. Self-inflicted donations bound the individual loss, but funds once sent are unrecoverable for all parties including governance, matching the High-severity "funds stranded with no sweep" class of the reference report.

### Recommendation
Add an owner-authorized `sweep(hub_asset, recipient)`-style function to the pool (and a controller rescue for its own stray balances) that transfers `token.balance(pool) - sum of booked cash across all markets sharing that token`, so unbooked surplus can be recovered without touching any market's reserves.

### Proof of Concept
1. Deploy controller/pool with a USDC market; Alice supplies so `cash = C`.
2. Attacker (or Alice by mistake) calls `USDC.transfer(eve, pool, X)` directly — allowed surface.
3. `token.balance(pool) = C + X` but `get_reserves()` still returns `C` (per tests/test-harness/tests/pool_money_flow_audit.rs:86-96).
4. `claim_revenue` is capped by `cash` (revenue.rs:42) and `recapitalize` refunds excess rather than crediting it; no entrypoint can ever move `X`. `X` is permanently frozen.