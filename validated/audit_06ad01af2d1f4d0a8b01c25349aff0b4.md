### Title
Withdrawals drain a shared token balance reserved by sibling-hub cash books, leaving other markets' suppliers unpaid - (File: contracts/pool/src/ops/withdraw.rs)

### Summary
Each market is keyed by `(hub_id, asset)`, so the same token can be listed in multiple hubs with independent cash books. However, all those books are backed by one physical token balance in the single pool contract. Withdrawal liquidity checks (`require_reserves`) validate only the withdrawing market's own `cash` book, never the aggregate of sibling-market books against the real token balance. A large withdrawal (or borrow/flash loan) in one hub can therefore extract tokens that a sibling hub's book still counts as its liquidity, so suppliers in the sibling hub — and liquidation collateral payouts in `SeizeMode::Transfer` — pass every pool guard and then revert inside the SAC transfer.

### Finding Description
- `withdraw::gate_and_debit` calls `cache.require_reserves(net_transfer)`, which only asserts `self.cash >= amount` on the per-market `Cache` (`contracts/pool/src/cache/cash.rs:15-21`), then `debit_cash` and `transfer_out` sends real tokens (`contracts/pool/src/ops/withdraw.rs:111-119`, `cash.rs:46-53`).
- The docs acknowledge the shared custody: "The same token can appear in multiple hubs. Its markets keep separate books but share one physical pool balance" (`docs/reference/architecture.md:63-65`), and the fuzz target explicitly notes "Markets on one asset share the token balance, so a per-market `cash <= balance` check cannot detect an overdraw" (`tests/fuzz/fuzz_targets/pool_native.rs:101-123`) — yet no production code enforces that aggregate.
- Same-token multi-hub listing is a supported configuration: `create_market` per `(hub_id, asset)`, exercised in `tests/test-harness/tests/controller/multi_hub.rs` and `tests/test-harness/tests/pool_money_flow_audit.rs`.

Concretely: hub-1 and hub-2 both list USDC. Bob supplies 1M USDC on hub 2 (book cash 1M). Alice withdraws/borrows the same token on hub 1, whose own book legitimately holds ≥1M cash. Hub 1's checks pass, `transfer_out` sends real USDC, and the physical balance drops below hub 2's book cash. Bob's `withdraw` then passes `require_reserves` (hub-2 book still shows 1M) but panics inside `token.transfer` with a SAC balance error — identical shape to the externally reported bug where `lockedLiquidity` is validated against a balance that another flow can drain. The pool's own test demonstrates exactly this failure mode for the unfunded-refund path (`contracts/pool/tests/flows.rs:3404-3476`).

### Impact Explanation
Temporary freezing of user funds (Medium): suppliers in the drained-from sibling hub cannot withdraw, and `SeizeMode::Transfer` liquidation legs pay collateral cash that no longer exists, so liquidations of that collateral revert until repayments or new supply refill the physical balance. Funds are not stolen (each book still balances), but exits are blocked for an unbounded period that depends on third-party repayments.

### Likelihood Explanation
Low-to-medium: requires the same token listed on ≥2 hubs (a governance-enabled but supported configuration) and liquidity migration large enough to undercut a sibling book — a bank-run or cross-hub refinance (`swap_collateral`/`multiply` already route same-token cross-hub flows, per `skills/xoxno-lending-contracts/composing.md:49-55`) suffices; no malicious token or privileged action needed.

### Recommendation
Track aggregate booked cash per `asset_id` across all hubs (a per-asset total in persistent storage updated by `credit_cash`/`debit_cash`), and have `require_reserves` — or equivalently `gate_and_debit` — assert the draw does not push the real token balance below the sum of sibling-market cash books, e.g. require `token.balance(pool) - draw >= total_cash_of_other_markets` before `transfer_out`. Alternatively reject `CreateLiquidityPool`/`create_market` for a token already pooled in another hub.

### Proof of Concept
1. Governance lists USDC on hub 1 and hub 2; each market accrues its own `cash` book against one pool USDC balance.
2. Suppliers deposit 1M USDC on hub 1 and 1M on hub 2 (physical balance 2M, books 1M each).
3. Alice (unprivileged) calls controller `borrow`/`withdraw` on hub 1 for ~2M-worth enabled by hub-1 book liquidity plus accumulated supply — or simply hub-1 suppliers withdraw after hub-1 utilization frees liquidity — pulling the physical balance to near zero while hub-2's book still reads 1M.
4. Bob calls `withdraw(account_id, [(hub2, USDC)], ...)`; `require_reserves` passes on hub-2's book, `transfer_out` reverts with SAC `BalanceError` — the same failure asserted in `test_unfunded_recapitalize_leaves_the_cash_book_overstating_custody` but reached through an ordinary cross-hub drain.