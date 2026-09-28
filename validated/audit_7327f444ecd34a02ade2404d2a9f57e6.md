### Title
Strategy borrower receives `principal - flashloan_fee` while debt is minted for full `principal`, with no minimum-received slippage control — (File: contracts/pool/src/ops/strategy.rs)

### Summary
In XOXNO Lending, plain `borrow` delivers the full principal to the recipient, but the strategy entry path (`pool_create_strategy_call` via `create_strategy`, used by `flash_position`/`multiply`-style flows) mints debt shares for the full requested `amount` while transferring only `amount - fee` to the receiver, where `fee` is computed from the market's admin-controlled `flashloan_fee` bps at execution time. Neither the controller's `borrow_into_controller` nor the pool's `strategy::accounting` accepts a caller-supplied minimum-received parameter. If `flashloan_fee` is raised (e.g., a ready governance operation executed in front of the user's transaction), the borrower owes the full `amount` but receives materially less — the exact Teller bug class.

### Finding Description
- `contracts/pool/src/ops/strategy.rs` `accounting` (lines 58-88): `borrow::mint_debt` mints debt for the full `action.amount`, then `compute_fee` (lines 94-101) derives the fee from `cache.params().flashloan_fee` — a mutable market parameter — and `transfer_out` sends only `amount_to_send = amount - fee` (lines 75-79). The only guard is `fee <= amount` (`StrategyFeeExceeds`), so a fee of up to 100% of principal is permitted.
- `contracts/controller/src/positions/debt.rs` `borrow_into_controller` (lines 260-308): the caller's `amount` is passed straight through with no `min_received` argument; the only assertions are internal consistency (`measured == result.amount_received`) and `measured > 0`. There is no way for the initiating account to bound the fee it pays.
- `contracts/pool/src/ops/flash.rs` shows the same parameter (`flashloan_fee`) is a per-market config value read at execution time (line 56), so it can change between a user's intent and execution — including via a governance `execute` of a ready timelock operation, which is reachable by an unprivileged caller.

Analogy to the external report: Teller deducts `protocolFee + marketplaceFee` from `bid.loanDetails.principal` and sends the remainder to the borrower; here `create_strategy` deducts `flashloan_fee` from the borrowed principal and sends `amount - fee` while the debt liability stays at `amount`. In both cases the fee parameters are settable values consumed at acceptance/execution time with no user-specified floor on the net proceeds.

### Impact Explanation
Theft of user funds / sub-optimal execution: a borrower requesting `X` through a strategy entrypoint can receive far less than `X` (down to zero net proceeds at a 100% fee) while the position's debt is recorded for the full `X`. The difference is booked as protocol revenue (`interest::add_protocol_revenue`, strategy.rs line 73), so the shortfall is not refunded — it is a permanent loss of the user's expected principal relative to the debt they now owe. Severity: **Medium** — real user-funds loss but contingent on a `flashloan_fee` change landing before the user's transaction.

### Likelihood Explanation
Requires the market `flashloan_fee` to be raised between the user forming the transaction and its execution. In Teller this was an owner front-run; here the analogous vector is a ready timelock/governance operation that any address can execute, or a queued fee change whose execution coincides with pending strategy transactions. Users have no way to express "revert if I receive less than `min`", so every strategy borrow is implicitly accepted at whatever fee is current. Likelihood is moderate: it needs a fee change to occur, but the user bears the entire risk with no protection.

### Recommendation
Add a caller-supplied minimum-received parameter to the strategy borrow path:
- Extend the controller strategy entrypoints (`flash_position`, `multiply`, and the `create_strategy` pool call signature in `contracts/controller/src/external/pool.rs` / `contracts/pool/src/lib.rs`) with `min_amount_received: i128`.
- In `pool::ops::strategy::accounting` (or `apply`), after computing `amount_to_send`, revert if `amount_to_send < min_amount_received`, e.g. `assert_with_error!(env, amount_to_send >= min_received, FlashLoanError::InsufficientStrategyProceeds)`.
- Alternatively, let the caller pass `max_fee_bps` and validate `flashloan_fee <= max_fee_bps` before minting debt.

### Proof of Concept
1. Market `flashloan_fee` is 0. A user submits a strategy borrow (`flash_position`/`multiply` → `borrow_into_controller` → `pool_create_strategy_call(amount = 1000 USDC, charge_fee = true)`), expecting ≈1000 USDC to deploy.
2. A ready governance operation setting `flashloan_fee = 4000` bps (40%) is executed first (or simply lands earlier in the same ledger sequence).
3. `strategy::accounting` computes `fee = 400`, mints debt for `amount = 1000`, and `transfer_out` sends only `600` to the receiver. `borrow_into_controller`'s assertions pass (`measured == amount_received == 600`, `measured > 0`), so no revert.
4. The account now owes 1000 USDC of debt but only received 600 USDC of principal — identical to the Teller scenario where the borrower expecting 1000 USDC receives 200.

Note: the plain `borrow` path (`process_borrow`/`pool_borrow_call`) transfers the full amount and is not affected; the analog is confined to the `charge_fee` strategy path. I did not fully verify the controller's `flash_position.rs` call-site arguments, so the exact user-facing entrypoint signature should be confirmed, but `borrow_into_controller` clearly forwards `charge_fee` to `pool_create_strategy_call` without any slippage bound.