### Title
Tokens transferred directly to the controller or pool are permanently locked with no recovery path - (contracts/controller/src/payments.rs)

### Summary
Soroban tokens have no `receive()` gate — any address can `token.transfer` to the controller or pool contract address at any time. The protocol deliberately excludes these unsolicited balances from every accounting and refund path, and neither contract exposes a sweep/recover entrypoint. The result is the direct analog of "ETH sent to the vesting contract can never be withdrawn": stray token balances are permanently stranded.

### Finding Description
The pool tracks liquidity via a `cash` field in `PoolStateRaw` (debited/credited only by ops) rather than the live token balance, so tokens pushed directly to the pool inflate `token::balance(pool)` but are invisible to `supplied`/`revenue`/`cash` accounting. `claim_revenue` only burns tracked revenue shares and pays `net_transfer` debited from `cash` — it can never reach the excess balance (contracts/pool/src/ops/revenue.rs:22-55).

For the controller, the design is explicit and enshrined in a test: `refund_controller_balance_delta` refunds only the balance *increase* since a snapshot, "preserving the pre-existing balance" (contracts/controller/src/payments.rs:41-52). The harness test `test_migrate_refund_ignores_preexisting_controller_balance` mints ETH directly to the controller, runs `migrate_from_blend`, and asserts `controller_eth == stuck` — "pre-existing controller ETH must remain (not used as refund or swept)". No controller entrypoint (supply/borrow/withdraw/repay/liquidate/flash/strategy paths) ever transfers out a pre-existing balance to its sender or to anyone else; the only consumer is `repay_debt_from_controller`, which may spend `debt_available` from controller custody to fund a *different* user's repayment leg — at best an involuntary donation, never a recovery for the sender (contracts/controller/src/strategies/legs.rs:40-81).

Root cause: custody accounting is strictly delta/scoped-balance based, and there is no owner-gated or permissionless skim for untracked balances.

### Impact Explanation
Permanent freezing of funds. Any user who transfers supported tokens directly to the pool or controller address (mistaken deposit, mis-integrated router, griefed counterparty instructing a wrong recipient) loses them irreversibly. Pool-sent funds are unreachable by all accounting; controller-sent funds are either inert forever or consumed as repayment funding for unrelated positions, still unrecoverable by the sender.

### Likelihood Explanation
Reachable by a single unprivileged address with one `token.transfer(user → controller/pool, amount)` call — explicitly in scope ("direct token transfers to the pool or controller"). Requires a user error rather than an attacker's profit motive, so realized frequency is low, but the recovery surface is zero once it happens.

### Recommendation
Add an owner-gated `recover_asset(asset, to)` on both contracts that pays out only the untracked excess — for the pool, `token::balance(pool) - cash` per market (enforce the subtraction against committed state); for the controller, the full balance of any asset, or restrict it so it cannot run while a strategy callback is mid-flight (reuse `with_flash_guard`/re-entrancy guard). Alternatively document the donation behavior and revert inbound flows where feasible (not possible for SAC transfers, so recovery is the realistic fix).

### Proof of Concept
1. Deploy pool + controller with an XLM SAC market (`create_market`).
2. Alice calls `token::Client::transfer(alice, controller, 100e7)` and `transfer(alice, pool, 100e7)`.
3. Enumerate every controller entrypoint: none accepts a "sweep" argument; `withdraw` requires a supply position, `repay`/`repay_debt_with_collateral` only move measured deltas, and `migrate_from_blend` explicitly preserves the pre-existing balance (test asserts `controller_eth == stuck`).
4. On the pool, `claim_revenue` pays only `burn_claimable_revenue()` output debited from `cash`; the donated 100 XLM sits in `balance(pool) - cash` with no accessor. Funds are permanently frozen.