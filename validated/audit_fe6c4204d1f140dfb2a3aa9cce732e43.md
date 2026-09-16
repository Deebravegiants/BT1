### Title
Shared `CallDispatcher` balance-diff sweep in `placeOrder`/`_execute` lets an order attacker inflate escrow accounting with unrelated funds sitting on the dispatcher - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder`'s predispatch flow, and `IntentsBase._execute`'s output-sweep flow, both determine how many tokens were "received" from an order's calldata execution by diffing the shared `CallDispatcher` contract's balance before/after an arbitrary, order-controlled call, exactly the balance-diff accounting pattern flagged in the Tokemak `_claimRewards` report (comparing a balance snapshot before/after an external interaction and treating the delta as attributable solely to this operation).

### Finding Description
In `placeOrder`, when `order.predispatch.call.length > 0`, the gateway:
1. Transfers the order's predispatch assets to the shared `_params.dispatcher`.
2. Calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` — arbitrary, attacker(order-placer)-controlled calldata.
3. Snapshots `IERC20(token).balanceOf(dispatcher)` and sweeps the dispatcher's *entire current balance* of each input token to the gateway (`transferCalls[i]` forwards `balance`, not the deposited `amount`).
4. Computes `received = balanceOf(address(this)) - balancesBefore[i]` and sets `order.inputs[i].amount = received` (if `received <= requiredAmount`) — feeding directly into the commitment hash and escrow accounting. [1](#0-0) 

Because `_params.dispatcher` is a single shared `CallDispatcher` used across all orders (and across `_execute`'s output-side sweep too), and because the sweep transfers the dispatcher's *full* balance rather than only what this order deposited, any tokens left on the dispatcher from another order's incomplete/partial predispatch or postdispatch execution (see `_execute` in `IntentsBase.sol`, which also sweeps dispatcher's full balance after arbitrary calldata) get attributed to whichever order happens to sweep next. [2](#0-1) 

This mirrors the audit finding's root cause precisely: the amount "received"/"claimed" is derived from `balanceAfter - balanceBefore` on a shared account, rather than from an authoritative, per-operation return value. Since transactions execute atomically and sequentially in EVM (no true cross-tx interleaving), the primary exploitable channel is cross-order dust leakage on the shared dispatcher within/across transactions in the same block ordering the attacker controls (e.g., submitting predispatch calldata timed so their sweep captures dust left by a prior partially-executed order, or by directly funding the dispatcher then placing an order whose predispatch call is a no-op, causing the "received" measurement to scoop up value never actually deposited by this order).

### Impact Explanation
Because the swept "received" value feeds `order.inputs[i].amount`, which is what gets hashed into the order commitment and what is escrowed/required from a filling solver, an attacker can cause the gateway to record an input amount larger than what they actually deposited via this order — effectively laundering third-party dust or a competing order's leftover tokens into their own order's escrow, or conversely starve/reduce a legitimate order's expected escrow if a race empties the dispatcher balance mid-flow. This is a token-accounting integrity break within the IntentGatewayV2 escrow/commitment system reachable by any unprivileged order placer.

### Likelihood Explanation
Requires (a) the shared `_params.dispatcher` to actually hold residual balances between sweeps — plausible whenever predispatch/postdispatch calldata doesn't perfectly consume its input (a documented, expected occurrence the code explicitly handles via `DustCollected`), and (b) an attacker able to time their own `placeOrder`/`fillOrder` predispatch/output calldata to land while such dust exists. This is a realistic scenario for an unprivileged order placer/solver since the dispatcher is a persistent, shared, externally-observable contract and its balance can be inspected before crafting calldata.

### Recommendation
Do not rely on `balanceOf(dispatcher)` deltas to attribute value to a specific order. Instead:
- Have `CallDispatcher.dispatch` return the exact amounts moved for the specific calls belonging to this order, or
- Require calldata to transfer an explicit, order-scoped amount (not "whatever balance exists"), or
- Isolate dispatcher state per-order (e.g., ephemeral per-call proxy/clone) so residual balance from one order's calldata cannot be swept by another order's sweep logic.

### Proof of Concept
Conceptual sequence (illustrative, not executed):
1. Order A's `placeOrder` predispatch calldata partially fails to consume a token (e.g., swap leaves 5 USDC dust) — dispatcher now holds 5 USDC.
2. Before Order A's sweep step runs (or in a subsequent transaction if Order A's flow doesn't sweep to zero, e.g., a different token than the one order A escrows), Order B's `placeOrder` is submitted with predispatch assets of 0 and a no-op predispatch call for that USDC token.
3. Order B's sweep loop at [3](#0-2)  reads `balanceOf(dispatcher)` = 5 USDC (the leftover from Order A, not anything Order B deposited), sweeps it to the gateway, and the `received` calculation at [4](#0-3)  attributes it to Order B's `order.inputs[i].amount`, inflating Order B's committed escrow with funds Order B never paid for.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L260-311)
```text
            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
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

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-545)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

        Call[] memory sweepCalls = new Call[](outputsLen);
        uint256 sweepCount = 0;

        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

            if (token == address(0)) {
                uint256 balance = dispatcher.balance;
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({to: address(this), value: balance, data: ""});
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            } else {
                uint256 balance = IERC20(token).balanceOf(dispatcher);
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            }

            unchecked {
                ++i;
            }
        }

        if (sweepCount > 0) {
            Call[] memory finalCalls = new Call[](sweepCount);
            for (uint256 i; i < sweepCount;) {
                finalCalls[i] = sweepCalls[i];
                unchecked {
                    ++i;
                }
            }
            ICallDispatcher(dispatcher).dispatch(abi.encode(finalCalls));
        }
    }
```
