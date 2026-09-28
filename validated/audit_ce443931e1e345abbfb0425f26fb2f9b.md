### Title
Undeclared callback assets pushed to the controller are permanently stranded — (`File: contracts/controller/src/strategies/flash_position.rs`)

### Summary
The analog of "native coin sent is lost" is Soroban-shaped: instead of `msg.value`, a flash-position receiver delivers tokens to the controller during the callback. `flash_position` measures and credits only the assets declared in `collaterals` and refunds only the assets listed in `refund_assets`; any other token the callback transfers to the controller is neither credited nor returned, and the controller exposes no sweep/rescue entrypoint. The tokens are permanently frozen.

### Finding Description
`process_flash_position` snapshots balances only for declared collateral assets and `refund_assets` (`snapshot_balances` at lines 125–130), then:

- `collect_collateral_deposits` (lines 325–352) measures deltas only for `collaterals` assets and deposits positive deltas into the account.
- `refund_listed_assets` (lines 372–384) calls `refund_controller_balance_delta` only for each asset in `refund_assets`.

The callback (`invoke_receiver`, lines 297–323) lets the receiver push arbitrary tokens to the controller. If the receiver transfers a token that is neither a declared collateral nor a declared refund asset, the transfer succeeds, the delta is never measured, and no code path moves it back. The docs confirm intent: "Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint" (`docs/reference/endpoints.md:86`, `skills/xoxno-lending-contracts/flash-loans.md:134`). The delta-based refund helper itself (`refund_controller_balance_delta`, `payments.rs:41–52`) only pays out the post-snapshot increase for the exact asset it is invoked on.

This mirrors the CPortModule bug directly: an order paid in the wrong medium (native coin vs ERC20) silently absorbed funds; here, callback-delivered assets in the "wrong" token are silently absorbed by the controller with no revert and no recovery path.

### Impact Explanation
Tokens delivered to the controller outside the declared sets are lost permanently — the controller has no withdrawal, sweep, or admin rescue for stray balances. Like the original bug, the loss is real token value (e.g., XLM/USDC SAC balances) belonging to the position owner or receiver operator. Losses are unbounded by the protocol, up to whatever amount the callback transfers.

### Likelihood Explanation
Reachable by any unprivileged account holder: `flash_position(caller, account_id, spoke_id, mode, debt, amount, receiver, data, collaterals, refund_assets)` only requires NFT owner/delegate auth and a Wasm receiver. A receiver that (by bug or misconfiguration of `collaterals`/`refund_assets`, e.g., declaring XLM collateral while pushing USDC, or omitting an asset from `refund_assets`) transfers an undeclared token leaves it stranded. The protocol accepts the transfer without reverting instead of enforcing declaration completeness — the same failure mode as the original, hence Medium.

### Recommendation
Revert or recover rather than absorb. Concretely, in `process_flash_position` after `refund_listed_assets`, either:
- require (via a snapshot of all received assets or a post-callback check) that the only non-zero controller deltas are declared collateral/refund assets — i.e., detect any undeclared positive delta and panic; or
- automatically refund positive deltas for every listed asset, not just declared ones (bounded by a transfer count cap), so undeclared pushes return to `caller`.

### Proof of Concept
1. Alice owns a `Multiply` account and deploys a Wasm receiver `R`.
2. Alice calls `controller.flash_position(caller=alice, account_id, spoke_id, mode=Multiply, debt=(hub,USDC), amount=1_000e6, receiver=R, data, collaterals=[((hub,XLM),1)], refund_assets=[])`.
3. Inside `execute_flash_position`, `R` supplies the declared XLM collateral and also transfers 100 EURC (a listed asset the caller forgot to declare in `collaterals`/`refund_assets`) to the controller.
4. `collect_collateral_deposits` measures only XLM; `refund_listed_assets` iterates an empty list. The 100 EURC delta is never measured or moved.
5. Transaction succeeds; the EURC sits on the controller with no reachable code path (no sweep endpoint) to recover it — permanent loss for Alice.