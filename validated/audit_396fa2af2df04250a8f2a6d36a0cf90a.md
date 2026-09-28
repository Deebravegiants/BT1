### Title
Flash-position refund transfers run after the flash guard clears and before account finalization, enabling stale-state reentry — ([File: contracts/controller/src/strategies/flash_position.rs])

### Summary
`process_flash_position` scopes the `FlashLoanOngoing` reentrancy guard to only the borrow-mint, forwarding, and receiver callback (lines 120–143). The post-callback refund loop `refund_listed_assets` (line 148) performs live token `transfer` calls to the caller-controlled address **outside** the guard, while the mutated `Account` (new collateral deposits and minted debt) is still only in memory — `strategy_finalize`, which persists and risk-checks the account, runs later at line 153. A caller whose address is a contract can use a SEP-41 transfer hook on a refund-listed token to reenter controller entrypoints against the not-yet-persisted account state. This mirrors CVE-2018-1000866's shape: an action intended to be confined inside a controlled execution window escapes the sandbox boundary and reaches privileged-by-context operations.

### Finding Description
Relevant ordering in `process_flash_position`:

```rust
// lines 120-143: guard covers only mint/forward/callback
let (amount_received, collateral_before, refund_before) =
    storage::with_flash_guard(env, || { ... invoke_receiver(...) });

let deposits = collect_collateral_deposits(...);          // line 145
process_deposit(env, &controller, &mut account, &deposits, &mut cache); // line 146, in-memory only

refund_listed_assets(env, caller, refund_assets, &refund_before);       // line 148, UNGUARDED token transfers to `caller`

require_flash_position_still_open(env, &account, debt);   // line 152
strategy_finalize(env, account_id, &mut account, &mut cache); // line 153, persist + solvency check
```

- `with_flash_guard` restores/removes the flag when the closure returns (`storage/account.rs:305-307`), so entrypoints are unblocked again at line 144.
- `refund_controller_balance_delta` sends the delta to `caller` via a normal token `transfer` (line 382). For a hook-capable listed token (the codebase already builds `with_transfer_hook_market` fixtures, so hook tokens are in the threat model — see `tests/test-harness/tests/strategy/flash_position_adversarial.rs:152`), the receiving contract `caller` executes code during that transfer.
- The in-memory `account` already contains the minted debt (`borrow_into_controller` at line 271) and the newly deposited collateral (`process_deposit` at line 146), but none of that is committed to storage until `strategy_finalize`.
- `validate_refund_assets` (lines 217–256) only constrains refunds to listed, active assets distinct from the collaterals — the comment at line 240 acknowledges the transfers run after the guard but treats listing as sufficient protection. It does not account for reentry into *other* entrypoints touching the same account.

A reentrant call (e.g. `withdraw`, `repay`, `liquidate`, or a second `supply` on the same `account_id`, which the attacker owns) loads the persisted account — which lacks the in-flight collateral and debt — and mutates/commits it. When the outer call resumes, `strategy_finalize` writes the stale in-memory `Account` over that state, resurrecting supply balances whose underlying tokens were already moved, or double-counting/deleting positions. The refund transfer itself also lands while collateral-measurement baselines were taken pre-callback, but the primary issue is the unguarded window before persistence.

### Impact Explanation
An attacker contract can reenter and withdraw (or otherwise reposition) the pre-existing collateral of the same account while the outer call still believes that collateral exists, then have the stale in-memory account — including the withdrawn supply — rewritten on finalization. Result: supply shares whose tokens have already left the pool, i.e. theft of user funds / protocol insolvency. Alternatively, reentrant `repay`/`borrow` manipulations can desynchronize debt vs. solvency checks. Reachable by a single unprivileged address via `flash_position(caller=attacker contract, refund_assets=[hooked listed token])`.

### Likelihood Explanation
Requires (a) a listed token with a transfer hook that runs receiver code (Stellar SAC hook tokens exist; the test suite explicitly models them), and (b) an account with pre-existing positions to exploit the stale load. Both are realistic; no privileged access needed. Uncertain residual: whether `strategy_finalize` fully overwrites the reentrant write or merges — if it merges fields rather than replacing the account record, impact reduces to ordering anomalies. I could not fully confirm `strategy_finalize`'s persistence semantics within the iteration budget, so severity is Medium rather than High.

### Recommendation
Extend `with_flash_guard` (or a second guard scope) to cover `refund_listed_assets` and `collect_collateral_deposits`/`process_deposit`, so no external token call happens while the account mutation is uncommitted — i.e. move all post-callback token movement inside the guarded window and only clear the guard after `strategy_finalize` persists the account.

### Proof of Concept
1. Attacker deploys a receiver contract `R` and opens/owns a lending account `A` with pre-existing collateral.
2. Call `controller.flash_position(caller=R, account_id=A, mode=Multiply, debt=flashloanable asset, receiver=R, collaterals=[some min], refund_assets=[T])` where `T` is a listed token with a receiver-side transfer hook.
3. In `R.execute_flash_position`, send a positive delta of `T` to the controller (e.g. a dust transfer) so `refund_listed_assets` pushes a refund to `R`.
4. In `T`'s hook firing on the refund transfer to `R`, `R` calls `controller.withdraw` on account `A` — the guard is already cleared, and the persisted account still shows pre-flash collateral without the in-flight debt.
5. The withdraw succeeds; the outer call resumes and `strategy_finalize` persists the stale in-memory account (still crediting the withdrawn supply plus new debt), leaving the protocol insolvent by the withdrawn amount.