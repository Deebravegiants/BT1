### Title
Undeclared tokens sent to the controller during `flash_position` are permanently locked - ([File: contracts/controller/src/strategies/flash_position.rs](contracts/controller/src/strategies/flash_position.rs))

### Summary
The `flash_position` entrypoint settles the receiver callback by measuring balance deltas only for the assets the caller declared in `collaterals` and `refund_assets`. Any other token the receiver transfers to the controller inside the callback — including a listed lending asset the user simply forgot to declare, or a token delivered by a swap venue to the controller — is never credited, deposited, or refunded. The controller exposes no sweep or rescue entrypoint, so the funds are permanently locked, exactly mirroring the "ETH sent alongside an ERC20 funding is silently kept" bug class from the reference report.

### Finding Description
`process_flash_position` snapshots controller balances for two fixed sets only:

- `collaterals` (`HubAssetKey, min`) — measured after the callback via `collect_collateral_deposits` and deposited into the account (lines 125–129, 325–352).
- `refund_assets` — measured after the callback and refunded to `caller` via `refund_listed_assets` (lines 130, 148, 372–384).

Both snapshots are taken *after* `mint_and_forward` and immediately before `invoke_receiver` (lines 120–143). The consequence is twofold:

1. A token that is not present in either vector earns a zero attribution: `balance_delta_since` is never invoked for it, so a positive transfer into the controller during `execute_flash_position` is invisible to settlement. The protocol docs state this plainly: "An undeclared token left on the controller is neither deposited nor refunded" (`skills/xoxno-lending-contracts/flash-loans.md`, line 134).
2. Even a *listed* token cannot be rescued retroactively: because the baseline for `refund_assets` is snapshotted inside the same transaction, a balance stranded by an earlier `flash_position` (or any accidental direct transfer to the controller) is part of the baseline and yields `delta == 0` for the next caller.

`refund_assets` is additionally constrained: each entry must be a listed, active asset in the same `(spoke_id, hub_id)` as the debt (`validate_refund_assets`, lines 217–256) and must not collide with a collateral. There is no bound on how much value a receiver can push to the controller with an undeclared token, and grep confirms no `rescue`/`sweep`/`recover` function exists anywhere in `contracts/controller/src`. The only recovery path would be a Wasm upgrade, which is a privileged governance action — not a user-reachable fix.

### Impact Explanation
Permanent freezing of user funds. A receiver that delivers the wrong token, an extra token from a multi-output swap, or a correct token the caller failed to declare loses it irrecoverably at the controller address. This matches the accepted impact class of the source finding (user funds locked in the contract, unrefundable) and the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Reachable by any unprivileged address through `controller::flash_position` with its own `FlashPositionReceiver` contract (the allowlist explicitly includes "own flash receiver"). The callback legitimately *must* push tokens to the controller by plain `transfer`, so a simple implementation mistake — forgetting one leg of a multi-asset route, declaring the collateral but not the residual token-out, or a venue paying an unrequested rebate token to the controller — lands value in the one place settlement never inspects. Likelihood is user-error-dependent, consistent with Medium severity, identical in character to the accidental `msg.value` case.

### Recommendation
For each callback, either (a) require `collaterals ∪ refund_assets` to cover every token whose controller balance changed during `invoke_receiver` (e.g., iterate a caller-supplied `handled_assets` set and revert on any positive undeclared delta), or (b) snapshot a declared superset and revert if any undeclared asset's controller balance increased. Alternatively, document and implement a governance-gated `sweep` restricted to tokens with no open positions — though option (a) removes the footgun entirely.

### Proof of Concept
1. User deploys a receiver whose `execute_flash_position` swaps the borrowed USDC into XLM *and* also transfers a leftover balance of a second listed token (e.g., AQUA) to the controller — or simply forgets to declare it.
2. User calls `controller.flash_position(caller, account_id=0, spoke_id, mode=Long, debt=(hub,USDC), amount, receiver, data, collaterals=[(hub,XLM,min)], refund_assets=[])` — AQUA is not declared anywhere.
3. `collect_collateral_deposits` credits only the XLM delta; `refund_listed_assets` iterates an empty vector. The AQUA delta is never measured.
4. The AQUA balance remains on the controller address. No subsequent `flash_position` can recover it (`refund_before` snapshots include it in the baseline, yielding delta 0), and no other controller entrypoint transfers arbitrary tokens out of the controller. The funds are permanently locked.