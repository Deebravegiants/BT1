### Title
Tokens sent to the controller during a `flash_position` callback are permanently locked when not declared in `refund_assets` — (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
Analogous to leftover ETH being `selfdestruct`-ed into `RocketVault` with no recovery path, the XOXNO Lending controller has no sweep or recovery endpoint. During `flash_position`, the receiver callback may transfer arbitrary tokens to the controller, but only assets explicitly listed in `refund_assets` are refunded; undeclared tokens received by the controller are neither credited to the account nor returned, and no privileged or unprivileged entrypoint can ever move them out.

### Finding Description
`process_flash_position` mints debt into the controller, forwards it to the caller-selected `receiver`, and snapshots controller balances for two disjoint token sets before invoking `execute_flash_position` on the receiver:

- `collaterals` — measured deltas are deposited into the caller's supply positions (`collect_collateral_deposits` → `process_deposit`, lines 145–146).
- `refund_assets` — measured positive deltas are refunded to the caller (`refund_listed_assets`, lines 148, 372–384).

Validation enforces that the two sets are disjoint: `validate_refund_assets` rejects any refund asset equal to a collateral asset (lines 248–254). Any token the receiver sends to the controller that is in neither set is simply left in the controller's custody — there is no deposit, no refund, and no event for it. This is confirmed by the protocol's own documentation: "Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint." (`docs/reference/endpoints.md`).

Unlike the swap-aggregator — which has `sweep_balance` for stray tokens (`contracts/swap-aggregator/src/lib.rs:189`) and accrues residuals to an admin bucket (`contracts/swap-aggregator/src/execute/residual.rs`) — the controller implements no equivalent recovery path. A `token::Client::transfer` into the controller is not gated; any Soroban token can push tokens to it.

Reachability by a single unprivileged address: call `flash_position` with a self-deployed Wasm `receiver` (the only requirements are `is_flashloanable` on the debt market and receiver ≠ controller/pool, lines 69–90) and have the receiver's `execute_flash_position` transfer an extra token — e.g., a third asset produced by a partial swap, or simply a token held by the receiver — to the controller without listing it in `refund_assets` (or with the list already at `max_supply_positions`, since `refund_assets.len() <= limits.max_supply_positions` caps the list, lines 226–230, so a callback that legitimately produces more distinct residual tokens than the cap cannot declare them all). The transaction succeeds, risk checks pass, and the extra tokens are stranded forever.

### Impact Explanation
Permanent freezing of funds: tokens transferred to the controller during the callback but not declared as collateral or refund assets are locked in the contract for its lifetime. There is no user-facing or admin-facing entrypoint that transfers arbitrary token balances out of the controller (`claim_revenue` only forwards measured receipts of accrued revenue). For a flash receiver that produces an unexpected intermediate asset (a very common outcome of multi-hop swaps inside the callback), the entire residual amount is irrecoverable — the same "forcefully sent, unrecoverable" shape as the RocketVault bug.

### Likelihood Explanation
Medium. The loss requires the caller (or receiver contract) to send an undeclared token, which is partly self-inflicted; however, multi-hop callback routes routinely produce intermediate token residuals, `refund_assets` is hard-capped at `max_supply_positions`, and the list is also constrained to assets listed in `(debt.hub_id, spoke)` (line 241–247), so tokens outside that listing can *never* be declared and are guaranteed to be locked if received. No privileged action is needed to trigger it; `flash_position` is open to any account.

### Recommendation
Implement a recovery path for unaccounted controller balances, mirroring the router's `sweep_balance` (e.g., an owner-only sweep limited to balance above any tracked obligation), or make `refund_assets` unconditional — refund the positive balance delta of *any* token received during the callback that was not deposited as collateral, rather than only a pre-declared allowlist. At minimum, emit an event documenting stranded receipts.

### Proof of Concept
1. Deploy a Wasm receiver whose `execute_flash_position` buys collateral, transfers it to the controller (covers `collaterals` minimums), and also `transfer`s `X` units of token `T` (not a collateral asset, not listable as a refund asset) to the controller.
2. Call `controller.flash_position(account_id, spoke_id, Multiply, debt_key, amount, receiver, data, collaterals, refund_assets)` — omitting `T` from `refund_assets`.
3. Call succeeds; `token::Client(T).balance(controller)` increases by `X`; no entrypoint can reduce it. Funds are locked permanently, exactly as ETH selfdestructed into `RocketVault` was.