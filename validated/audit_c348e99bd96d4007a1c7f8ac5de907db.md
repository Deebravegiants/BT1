### Title
Strategy borrows mint full `amount` of debt but deliver `amount - flashloan_fee`, with no caller-supplied fee bound — ([File: contracts/pool/src/ops/strategy.rs](contracts/pool/src/ops/strategy.rs))

### Summary
The Union Finance finding's bug class — "the user's increased debt is `amount + fee`, where the fee parameter can change between quote and execution and the user cannot bound it" — maps onto XOXNO Lending's strategy borrow path. `multiply`, `swap_debt`, and `migrate_from_blend` open debt through `borrow_into_controller` → `pool_create_strategy_call` with `charge_fee = true`. The pool mints scaled debt for the full requested `amount` but only transfers `amount - fee` to the receiver, where `fee` is computed from the market's `flashloan_fee` bps read at execution time. No entrypoint argument lets the caller cap the fee.

### Finding Description
In `contracts/controller/src/positions/debt.rs:260-307`, `borrow_into_controller` calls `pool_create_strategy_call(env, &pool_addr, &controller, pool_action, charge_fee)` for a single `amount` of `hub_debt`. The strategies `multiply` and `swap_debt` (and `migrate_from_blend` for its `debt_caps` legs) invoke this with `charge_fee = true`; `flash_position` is the documented no-fee path.

In `contracts/pool/src/ops/strategy.rs:58-88`, `accounting`:
- computes `fee = flashloan_fee_bps * amount` via `compute_fee` (lines 94-100),
- calls `borrow::mint_debt(env, &mut cache, &mut position, amount)` — minting debt shares for the **full** `amount` (line 70),
- books `fee` as protocol revenue (line 73), and
- debits cash and transfers only `amount - fee` (lines 75-82).

So the account's debt increases by `amount`, but the proceeds that fund the leverage leg, the debt swap, or the Blend migration are reduced by an execution-time fee the caller never sees in the call arguments. The only guard is `fee <= amount` (`StrategyFeeExceeds`), which merely prevents fee > principal. `flashloan_fee` is a mutable market parameter (`MarketParamsRaw`), so its value at execution can differ from what the user simulated or was quoted. The analogous exposure exists even without a parameter change: the debt is recorded in scaled shares via `cache.calculate_scaled_borrow(amount)` (`contracts/pool/src/ops/borrow.rs:68`), and interest accrual between quote and execution changes the effective debt, while no `max_fee`/`min_received` argument exists anywhere in the `borrow`/`multiply`/`swap_debt`/`migrate_from_blend` signatures (`contracts/controller/README.md:84-90`).

### Impact Explanation
A user opening a leveraged position via `multiply` or rotating debt via `swap_debt` incurs strictly more debt than the tokens delivered to the strategy leg. If `flashloan_fee` is raised (or is simply higher than the UI/quote assumed) between transaction construction and ledger inclusion, the account mints debt for the full `amount` while receiving proportionally less collateral-buying power or less `existing_debt`-repayment output. For `swap_debt`, a shortfall after the swap can leave residual old debt plus the full new debt — a worse position than intended with no revert. The excess accrues to protocol revenue, i.e., a direct transfer of user value; on marginal accounts the inflated debt-to-proceeds gap also pushes the post-action solvency gate closer to failure. This is a loss of user funds / debt larger than consented, matching the Medium severity of the source finding.

### Likelihood Explanation
Any unprivileged account owner or delegate reaches the path by calling `multiply` or `swap_debt` on their own account. The trigger is an ordinary market-parameter update to `flashloan_fee` landing between the user's simulation and execution — a routine operational event, not an adversarial precondition — and even absent a change, a caller who misjudges the fee has no on-chain way to bound it. Likelihood is moderate; impact is bounded by `flashloan_fee` bps per operation, consistent with Medium.

### Recommendation
Add a caller-supplied bound to the strategy entrypoints, e.g. `multiply(..., max_fee: i128)` / `swap_debt(..., max_fee: i128)`, and enforce `fee <= max_fee` inside `pool::create_strategy` accounting (or equivalently a `min_received` check on `amount_received` in `borrow_into_controller`). Revert when the execution-time fee exceeds the bound so the user's debt never grows beyond what they authorized.

### Proof of Concept
1. Market `(hub, USDC)` is listed with `flashloan_fee = 0`. Alice supplies collateral and prepares `multiply(caller=alice, account_id, spoke_id, collateral=XLM, debt_to_flash_loan=1000 USDC, debt=USDC, mode=..., swap=...)`, expecting 1000 USDC of debt and ~1000 USDC swapped into XLM collateral.
2. Before her transaction executes, `update_params` raises `flashloan_fee` to 1000 bps (10%).
3. Alice's `multiply` executes: `strategy::accounting` mints debt shares for 1000 USDC (`borrow::mint_debt` on `amount`), books 100 USDC as protocol revenue, and transfers only 900 USDC to the swap leg. Her account now owes 1000 USDC (plus accrued index) while only 900 USDC of collateral was purchased — a strictly worse HF and 100 USDC more debt than the funds deployed, with no argument in her call that could have prevented it.