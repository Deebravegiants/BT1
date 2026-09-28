### Title
Excess strategy funds and repay refunds are sent to `caller` (delegate) instead of the account owner — (File: contracts/controller/src/strategies/swap.rs, contracts/controller/src/strategies/legs.rs, contracts/controller/src/strategies/flash_position.rs)

### Summary
Analogous to Predy's reallocation bug (excess `quoteToken` sent to `msg.sender` — the Market intermediary — instead of the reallocator), XOXNO's controller strategies refund leftover tokens to `caller`, the immediate invoker, rather than to the account owner whose debt/collateral actually funded the operation. Because `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, `multiply`, and `flash_position` all authorize via `require_owner_or_delegate`, a delegate (governance-approved position manager / keeper) that executes a strategy on someone else's account receives all excess funds personally, while the owner bears the resulting debt.

### Finding Description
Three refund sites all use `caller` as the recipient:

1. `swap_tokens` refunds unspent swap input to `refund_to`, and every strategy passes `caller`:
   - `contracts/controller/src/strategies/swap.rs` lines 49–52: `let leftover = amount_in - actual_spent; if leftover > 0 { token_in_client.transfer(&controller, refund_to, &leftover); }`
   - `contracts/controller/src/strategies/swap_debt.rs` lines 65–72 passes `caller` — the `leftover` here is unspent newly-borrowed `new_debt` tokens, an asset backed by the *account's* fresh debt.

2. `repay_debt_from_controller` snapshots the controller balance and refunds the pool's overpayment (excess of `received` over actual debt burned in `pool/ops/repay.rs` line 32 `transfer_out(payer, overpayment)` where `payer` = controller) to `caller`:
   - `contracts/controller/src/strategies/legs.rs` lines 59–80: `refund_controller_balance_delta(env, &req.debt.asset, controller_balance_before_repay, caller)`.

3. `flash_position` refunds every caller-listed `refund_assets` balance delta to `caller`:
   - `contracts/controller/src/strategies/flash_position.rs` lines 148, 372–384.

Meanwhile, authorization only requires the caller to be owner *or* delegate: `account::require_owner_or_delegate(env, account_id, caller, &account.owner)` in `swap_debt.rs` line 48 (same pattern in the other strategies). Per `abi.md`, a delegate is "an active governance-approved position manager" — not the NFT owner. Nothing ever redirects refunds to `account.owner`.

### Impact Explanation
Theft/misdelivery of funds belonging to the position owner. In `swap_debt`, the account takes on new debt (`borrow_into_controller` mints debt on the owner's position); if the router spends less than `amount_in` or the swapped output exceeds the existing debt, the surplus — which is economically the owner's, since the owner's account carries the liability — is transferred to the delegate caller. Same for `repay_debt_with_collateral` (excess withdrawn collateral or repay overpayment) and `flash_position` (`refund_assets` deltas). The delegate keeps assets it never paid for, exactly as the Predy Market contract kept the reallocator's excess quote tokens.

### Likelihood Explanation
Any delegate/keeper executing a strategy on a managed account triggers it whenever the router under-spends the input or the repay leg over-funds the pool — both routine occurrences (routers consume `Fixed`/`Ppm` modes that rarely equal `amount_in` exactly, and debt ceilings/floor rounding routinely produce overpayment). It requires only a delegated call, not owner cooperation at execution time. Rated Medium: funds loss is bounded to per-call excess amounts and requires an active delegation, matching the Predy judge's medium reasoning.

### Recommendation
Route all strategy refunds to `account.owner` (or a recipient designated by the owner), not `caller`. In `swap_tokens`/`repay_debt_from_controller`/`refund_listed_assets`, pass `&account.owner` as `refund_to`; alternatively restrict strategy entrypoints to the NFT owner and have delegates use a path that cannot redirect value to themselves.

### Proof of Concept
1. Owner mints position NFT and grants delegate status to keeper K (governance-approved manager).
2. K calls `swap_debt(caller=K, account_id, existing_debt=ETH, new_debt_amount=1.0 WBTC, new_debt=WBTC, swap=route)` on the owner's account.
3. `borrow_into_controller` mints 1.0 WBTC debt on the owner's account and sends the cash to the controller.
4. The router consumes only 0.9 WBTC; `swap_tokens` computes `leftover = 0.1 WBTC` and transfers it to `refund_to = K` (`swap.rs` line 51). Separately, any pool overpayment on the ETH repay leg is forwarded to `K` (`legs.rs` line 75).
5. The owner's account carries the full 1.0 WBTC debt; K pockets the excess. K is unprivileged with respect to the funds — it holds no collateral and paid nothing.