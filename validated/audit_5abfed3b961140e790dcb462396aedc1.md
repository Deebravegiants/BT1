Confirmed: `CallDispatcher` (`evm/src/utils/CallDispatcher.sol:25-63`) is a single, permanent, shared contract (`_params.dispatcher`) reused by every `placeOrder` call from every user, not a fresh per-order deployment. It exposes `receive()` and an unrestricted `dispatch(bytes)` that anyone can call directly, and it holds whatever token/native balance is currently sitting in it between transactions.

### Title
Donated/residual dispatcher balance is swept into unrelated orders' escrow, permanently freezing/misappropriating prior users' tokens - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder`'s predispatch path measures the input amount to escrow by sweeping the **entire current balance** of the shared `CallDispatcher` contract, rather than only the amount actually produced by the current order's predispatch call. Because `CallDispatcher` is a persistent, address-shared, publicly-callable contract, any balance left in it — from a stuck/reverted prior order, a griefing donation, or another order's predispatch output arriving late — gets swept into whichever order calls `placeOrder` next, exactly the "donate funds directly to a balance-based accounting entity to corrupt its calculation" pattern from the referenced report (there, `balanceOf(position)` was manipulated by direct donation; here, `balanceOf(dispatcher)` / `address(dispatcher).balance` is manipulated the same way).

### Finding Description
In `placeOrder` (`evm/src/apps/IntentGatewayV2.sol:235-311`), when an order carries predispatch calldata:

1. The user's declared predispatch assets are pushed to `dispatcher` (lines 239-256).
2. `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` executes arbitrary user-supplied calldata against `dispatcher` (line 258).
3. To sweep the results back into the gateway, the code reads `address(dispatcher).balance` / `IERC20(token).balanceOf(dispatcher)` — the **full current balance**, not a before/after delta relative to step 1-2 — and builds a sweep call that transfers that entire balance (lines 268-282):
```solidity
uint256 balance = IERC20(token).balanceOf(dispatcher);
if (balance < requiredAmount) revert InvalidInput();
transferCalls[i] = Call({
    to: token, value: 0,
    data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
});
```
4. The delta actually credited to the *current* commitment is `received = balanceOf(this) - balancesBefore[i]` (lines 292-306); any amount above `order.inputs[i].amount` is emitted as `DustCollected` and effectively donated to the protocol, and if below, `order.inputs[i].amount` is silently reduced.

Because `CallDispatcher` is one shared, immortal, permissionlessly-callable contract (`evm/src/utils/CallDispatcher.sol`) rather than an ephemeral per-order vault, its balance is **not necessarily attributable to the current order alone**. Any of the following put a residual balance there:
- A prior `placeOrder` predispatch call whose sweep loop reverted partway (e.g., a later asset failed `balance < requiredAmount`), leaving already-transferred tokens for earlier assets stuck in `dispatcher`.
- Anyone directly transferring tokens to `dispatcher` (its `receive()` and ERC20 `transfer` require no permission check) — a pure donation.
- A predispatch call that overshoots its own order's requirement (e.g., unwraps more LP than needed) leaving dust that should belong to that order's user but is next swept by a completely different order.

In all these cases, the next unrelated `placeOrder` call that uses the same `dispatcher` and same token sweeps that entire balance into **its own** escrow/commitment. The rightful owner of the leftover balance permanently loses it (their portion is credited to someone else's order, or simply reported as protocol "dust"), while the attacker/next caller's own order absorbs it as free surplus that is subsequently treated as protocol dust anyway — so there is no clean "victim gets liquidated" narrative like the lending-position analog, but there **is** a clear irreversible loss of funds for whoever's tokens were actually stuck/donated: they are swept away with no accounting path back to them, and the balance-based check `balance < requiredAmount` at line 275 (and 270) can also be satisfied purely by an attacker donation, letting a malicious `placeOrder` caller pass the sweep despite their own predispatch call producing nothing.

### Impact Explanation
This is a "balance-of shared contract used as a proof of value produced" flaw of the exact class flagged in the report: `getAssetValue`/`_getMinReqAssetValue` used `IERC20.balanceOf(position)` for a shared, donatable account, letting external donations corrupt collateral/weight accounting and cause wrongful liquidation. Here, `IntentGatewayV2` uses `IERC20.balanceOf(dispatcher)` / `dispatcher.balance` for a shared, donatable/publicly-callable `CallDispatcher`, letting external transfers or residue from other orders corrupt what is credited to the current order's escrow. Funds belonging to a different order (or a griefer's donation) are irreversibly redirected into an unrelated commitment, and a malicious predispatch call can satisfy the `balance >= requiredAmount` gate without producing any real value of its own, using someone else's leftover/donated balance instead. This is concrete theft/permanent freezing of funds for whoever's balance was actually stuck at `dispatcher`.

### Likelihood Explanation
Medium-to-High. `dispatcher` is a fixed, protocol-wide address (`_params.dispatcher`) reused by every order that uses predispatch calldata, and its `dispatch()`/`receive()` functions have no access control, so any address can top up or trigger balance changes on it between transactions. A partial-revert in a multi-asset predispatch sweep (any asset failing the `balance < requiredAmount` check after earlier assets already transferred) is a realistic operational occurrence that leaves residue behind, and the next `placeOrder` caller using the same token will silently absorb it.

### Recommendation
Track the amount actually attributable to *this* order's predispatch call using a strict before/after delta computed immediately before and after step 2 (the `dispatch(order.predispatch.call)` invocation), the same pattern already correctly used in the non-predispatch branch (lines 312-329, `balBefore` captured right before `safeTransferFrom`). Do not use the dispatcher's absolute balance as the sweep amount; instead snapshot `balanceOf(dispatcher)` immediately before the predispatch call and take the delta after it, then sweep only that delta (capped/matched with `requiredAmount`), so no ambient/donated/residual balance in the shared `CallDispatcher` can be attributed to an unrelated order.

### Proof of Concept
Not executed (read-only analysis); the vulnerable code path and the shared, permissionless nature of `CallDispatcher` are shown above and are sufficient to demonstrate the flaw: (1) any address can `transfer` tokens directly to `dispatcher` (`evm/src/utils/CallDispatcher.sol`), (2) `placeOrder`'s predispatch sweep at `evm/src/apps/IntentGatewayV2.sol:268-282` reads `dispatcher`'s absolute balance rather than a call-scoped delta, and (3) the resulting "received" amount from `evm/src/apps/IntentGatewayV2.sol:292-306` becomes part of the placed order's commitment/escrow regardless of whether that balance originated from the current caller's predispatch call or from someone else's donation/leftover funds.