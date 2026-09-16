Based on my investigation, I found a directly analogous vulnerability in `IntentGatewayV2.placeOrder`'s predispatch handling.

### Title
Sweeping the CallDispatcher's *entire* token balance during `placeOrder` predispatch lets an order steal funds belonging to other in-flight orders or dust sitting in the shared `CallDispatcher` - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder`, when an order carries `predispatch` calldata, sweeps the *entire* current token balance of the shared, stateless `CallDispatcher` contract into the gateway and treats the delta as "actual received" for that specific order, exactly the balance-diff accounting pattern flagged in the reference report (relying on an observed balance change instead of the amount actually attributable to the current operation).

### Finding Description
In the predispatch branch of `placeOrder`, the gateway builds a sweep call that transfers the dispatcher's *full* balance, not the amount produced by this order's own predispatch call: [1](#0-0) 

It then measures "received" purely as the difference between the gateway's own balance before and after the sweep: [2](#0-1) 

`CallDispatcher` is a generic, shared, stateless relay contract with no access control tying it to a single order or caller — any `Call[]` can be dispatched to it by anyone holding a reference to it, and it simply forwards value/calldata to arbitrary targets: [3](#0-2) 

Because the dispatcher's balance is a *global, shared* piece of state rather than state scoped to the current `placeOrder` call, anything that leaves tokens sitting in the dispatcher between the time another order's/user's predispatch call runs and the time it is swept — e.g., a predispatch swap that produces slightly more output than expected (rounding, MEV, partial fill, prior failed/incomplete sweep, or a concurrent transaction that lands a `dispatch()` call against the same dispatcher in the same block) — becomes fair game for the *next* caller who reaches this code path with any predispatch order. The `balancesBefore[i]` and `requiredAmount` checks only assert the dispatcher holds *at least* `requiredAmount`; the actual sweep always takes the whole balance, so any dispatcher balance in excess of `requiredAmount`, however it got there, is credited to the *current* placer's order as `received`, inflating `order.inputs[i].amount` and the resulting escrow commitment.

This mirrors the report's root cause precisely: the contract infers "the amount that belongs to this operation" from an externally-influenceable balance snapshot rather than from a return value or a bound, order-specific accounting entry, so a balance that is inflated or interfered with by anything other than the current order's own predispatch call gets misattributed to that order.

### Impact Explanation
Misattributed balance is directly convertible to value: it becomes `order.inputs[i].amount`, which is escrowed and eventually paid out to whichever solver fills the order (via `_withdraw` in `IntentsBase`). An attacker who can arrange for the dispatcher to transiently hold tokens that "belong" to another pending order or operation (e.g., another user's predispatch call executed moments earlier in the same block, or leftover swap output the protocol expected to sweep for someone else) can have those tokens swept into their own order's escrow, effectively stealing them from the rightful order/depositor. This is a direct theft-of-funds vector reachable by any unprivileged user simply by calling `placeOrder` with `predispatch` data.

### Likelihood Explanation
Likelihood depends on whether the CallDispatcher can plausibly hold a transient excess balance attributable to someone else at the moment a competing `placeOrder` sweeps it — e.g., through predispatch swap slippage, back-to-back predispatch calls in the same block from different users, or a reentered/failed sweep leaving residual dust. Given `CallDispatcher` is shared infrastructure with no per-caller isolation and `dispatch()` can be invoked by anyone with no restriction, and given the sweep unconditionally takes the *entire* balance rather than only the amount produced by the current call, this is a realistic and directly reachable condition rather than a purely theoretical one.

### Recommendation
Do not sweep the dispatcher's entire balance. Instead, have the predispatch call itself return (or have the gateway compute) the exact amount produced by *this* order's operation, and transfer only that amount from the dispatcher. Alternatively, scope the dispatcher per-order (e.g., deploy an ephemeral dispatcher/proxy per `placeOrder` call, or require the predispatch call to push tokens to `address(this)` directly rather than accumulating in a shared contract), so that the swept amount cannot include value produced or deposited by any unrelated caller.

### Proof of Concept
1. User A submits `placeOrder` with `predispatch.call` that performs a swap on the shared `dispatcher`, producing `requiredAmount + X` tokens (`X` from slippage/rounding) still sitting in `dispatcher` when A's transaction is momentarily interrupted or when A's sweep call for some token in `order.inputs` reverts/partially executes such that only part of the accumulated balance is swept in that iteration (or more simply, when A's `dispatch()` for predispatch runs but A's placeOrder call reverts later — e.g., on a later input token's `InsufficientNativeToken`/`InvalidInput` check — leaving the dispatcher holding A's tokens since `dispatch()` and the sweep are two *separate* `ICallDispatcher(dispatcher).dispatch(...)` calls at lines 258 and 289, not atomically bound to A's own placeOrder success).
2. Attacker B observes the dispatcher holding excess tokens and immediately submits their own `placeOrder` with `predispatch` for the same token, ahead of/around A's retry. B's `balancesBefore[i] = IERC20(token).balanceOf(dispatcher)` snapshot before line 274 already includes A's leftover balance (since it's not order-scoped), so B's sweep at lines 276-280 (`balance = IERC20(token).balanceOf(dispatcher)`) transfers the *entire* combined balance to B, and B's `received` calculation at lines 292-299 credits all of it — including A's tokens — to B's own order.
3. B's order commitment/escrow now reflects value that rightfully belonged to A, which a solver later withdraws to B's benefit via `_withdraw`, without A ever recovering the difference.

Note: I was not able to trace every caller of `dispatch()` or confirm whether other protections (e.g., a dispatcher-per-tx invariant enforced elsewhere, or a private/internal-only dispatcher deployment per gateway instance) fully prevent concurrent/leftover balances from accumulating; the `CallDispatcher` contract itself, as shown, has no such isolation built in, so this should be verified against the full call-graph of who else can invoke `ICallDispatcher.dispatch` on the configured `_params.dispatcher` address.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L273-282)
```text
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L291-299)
```text
            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }
```

**File:** evm/src/utils/CallDispatcher.sol (L44-62)
```text
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
    }
```
