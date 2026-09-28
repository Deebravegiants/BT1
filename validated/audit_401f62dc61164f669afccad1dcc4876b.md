### Title
Tokens sent to the controller outside the declared `collaterals`/`refund_assets` lists are permanently locked — the controller has no rescue path - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
In `flash_position`, collateral is credited only via measured controller balance deltas for the explicitly declared `collaterals` list, and leftover tokens are refunded only for the explicitly declared `refund_assets` list. Any token the callback pushes to the controller that appears in neither list is silently kept by the contract. No controller entrypoint lets anyone — owner, governance, or the sender — sweep such stray balances, so they are frozen forever. The same applies to any direct token transfer to the controller address.

### Finding Description
`process_flash_position` snapshots controller token balances for `collaterals` (line 125-129) and `refund_assets` (line 130) before invoking the receiver callback (`invoke_receiver`, lines 131-141). After the callback, `collect_collateral_deposits` credits only the deltas of declared `collaterals` (lines 325-352) and `refund_listed_assets` returns only deltas of declared `refund_assets` to the caller (lines 372-384).

Two gaps make any other inbound balance unrecoverable:

1. **Coverage is closed.** `validate_refund_assets` (lines 217-256) requires every refund asset to be a listed asset in the account's spoke and the debt hub, and explicitly forbids refund assets that overlap with `collaterals` (lines 248-254). A token that is not listed in `(account.spoke_id, debt.hub_id)` can therefore never be in `refund_assets`, and it cannot be in `collaterals` either because `require_can_supply` rejects non-suppliable assets (line 202). So any callback receipt of an unlisted/other-spoke/other-hub token is in neither snapshot set and is simply retained.

2. **No sweep exists.** The controller exposes no `sweep`/`rescue`/`recover` entrypoint — the public interface is limited to the documented position/strategy/keeper verbs (`contracts/controller/src/lib.rs`, `docs/reference/endpoints.md`), and the endpoints doc explicitly states "Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint." The surplus sits on the controller balance untouched by `supply`/`repay` measured pulls (which snapshot their own deltas), so it can never be withdrawn.

This mirrors the Cooler bug: value transferred into the contract under user control has no corresponding exit path once the declared lists fail to cover it.

### Impact Explanation
Permanent freezing of user funds. A user or integrating contract that transfers tokens to the controller inside the callback — e.g., a router paying out to `controller` for a token the caller forgot to declare, or a token in a different hub/spoke than the `collaterals` keys — loses those tokens irrevocably. Likewise, any third party or fat-fingered direct transfer to the controller address is burned in practice. The impact class "permanent freezing of funds" is met; there is no timelock or privileged recovery.

### Likelihood Explanation
Moderate. `require_wasm_receiver` forces the callback to be a Wasm contract, and such integrations commonly aggregate swaps that pay the controller directly; multi-hub markets where the same token address exists in several spokes/hubs make it easy for a receiver to deliver the right token under the wrong `(hub_id, asset)` declaration, which `collect_collateral_deposits` will measure and credit only if the token address matches a declared entry — an undeclared listing of the same token still counts toward the declared one only if the address matches, but any genuinely different token is stranded. Separately, plain user error (forgetting to list a refund asset, or sending tokens to the controller directly) requires no attacker action at all.

### Recommendation
Add a sweep/rescue entrypoint — e.g., `sweep(env, caller, asset, to)` — that transfers the controller's full balance of tokens that are not accounted for, or at minimum emits/permits recovery of positive deltas of assets not consumed by `process_deposit`. Alternatively, widen `refund_assets` to accept arbitrary token addresses (not only listed spoke/hub assets) so any callback residue can be returned to the caller.

### Proof of Concept
1. Alice deploys a Wasm receiver and calls `flash_position(caller=alice, account_id=0, spoke_id=S, mode=Multiply, debt=(hub1, USDC), amount=X, receiver=receiver, collaterals=[(hub1, XLM, min)], refund_assets=[], data=…)`.
2. Inside `execute_flash_position`, the receiver swaps the flash USDC and returns XLM to the controller (credited), but the swap also yields a small amount of a third token `Y` — or the receiver mistakenly sends some USDC change back to the controller without declaring USDC in `refund_assets`.
3. `collect_collateral_deposits` ignores `Y` (not in `collaterals`); `refund_listed_assets` iterates an empty `refund_assets`. The transaction succeeds with `Y` (and the USDC change) sitting on the controller balance.
4. There is no entrypoint Alice, governance, or anyone else can call to move `Y` out — it is frozen permanently.