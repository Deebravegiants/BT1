### Title
Silent-failure ERC20 sweep in IntentGatewayV2/CallDispatcher allows theft of trapped tokens from the shared CallDispatcher - (File: evm/src/utils/CallDispatcher.sol, evm/src/apps/IntentGatewayV2.sol, evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentGatewayV2.placeOrder` (predispatch path) and `IntentsBase._execute` (postdispatch path) sweep tokens off the shared `CallDispatcher` back to the gateway using a raw `IERC20.transfer.selector` call routed through `ICallDispatcher.dispatch`, instead of `safeTransfer`. `CallDispatcher.dispatch` only checks that the low-level `.call` did not revert — it never decodes/validates the ERC20 boolean return value. Combined with the fact that `CallDispatcher.dispatch` is a completely unrestricted `external` function callable by anyone with arbitrary `Call[]` data, a non-standard ERC20 token that returns `false` instead of reverting on a failed `transfer` will leave real user funds stuck in the CallDispatcher while the gateway proceeds as if the sweep succeeded — and any third party can then permissionlessly drain those stuck tokens straight out of the CallDispatcher.

### Finding Description
`CallDispatcher.dispatch` executes arbitrary calls and only checks the outer call's success: [1](#0-0) 

In `IntentGatewayV2.placeOrder`'s predispatch flow, the sweep call that pulls escrow tokens back from the shared `dispatcher` to the gateway is built with the raw `transfer` selector (not `safeTransfer`) and routed through this same unchecked `dispatch`: [2](#0-1) 

The gateway does infer "received" from a balance diff, which is fine for detecting under-transfer — but no revert occurs if `received == 0`; the code silently sets `order.inputs[i].amount = received` (which can be zero) and continues: [3](#0-2) 

The same unchecked-`transfer`-via-`dispatch` sweep pattern also appears in the postdispatch/output path shared by all intent flows: [4](#0-3) 

And identically in the Tron variant of the gateway: [5](#0-4) 

Critically, `CallDispatcher` is a single generic, stateless utility contract, and `dispatch()` has no access control — anyone can call it directly with any `Call[]`: [6](#0-5) 

Attack chain:
1. User places a same-chain order whose input token is a non-standard ERC20 that returns `false` on a failed `transfer` (e.g. due to a paused/blacklist state, or one that can be induced to fail — many production tokens like older USDT-style or custom compliance tokens follow this pattern) and whose predispatch step routes funds through the dispatcher.
2. User's real tokens are legitimately pulled via `safeTransferFrom(msg.sender, dispatcher, amount)` into the shared `CallDispatcher`, so they are real, moved funds. [7](#0-6) 
3. The subsequent sweep-back `transfer(address(this), balance)` call is dispatched through `CallDispatcher.dispatch`, and the token returns `false` (transfer fails) without the outer `.call` reverting; `dispatch()` sees `success == true` and does not revert.
4. Because no tokens actually moved, `IntentGatewayV2` computes `received = 0`, sets `order.inputs[i].amount = 0`, and the order is placed/escrowed with zero value for that input — the transaction completes "successfully" despite the real transfer failure that the report describes as the core hazard.
5. The user's actual tokens are now sitting, unswept, in the shared `CallDispatcher` contract balance.
6. Since `CallDispatcher.dispatch` is unrestricted, any other address — a bot watching for this condition — can call `dispatch()` directly with a `Call` targeting the same token's `transfer`/`transferFrom` function to sweep that balance to itself, stealing the trapped funds.

### Impact Explanation
This is concrete theft of user funds routed through the intent system's predispatch/postdispatch calldata flow: real, escrow-bound tokens can end up sitting in a shared, permissionless `CallDispatcher` and be drained by any unrelated third party, while the placing user's order proceeds with zero recorded input. This satisfies the "concrete theft ... of funds" bar because the loss is not merely resource exhaustion or a bookkeeping inconsistency — it is a direct external drain path via `CallDispatcher.dispatch`, reachable from any account, with no privileged role required.

### Likelihood Explanation
Reaching this requires a token whose `transfer`/`transferFrom` can return `false` without reverting under some condition (paused, blacklist, insufficient-approval-race, or similar non-standard ERC20 semantics) being configured as a supported input asset for an order that uses the predispatch/postdispatch calldata path. This is a realistic, medium-likelihood configuration risk for a permissionless intents system intended to support arbitrary ERC20s, and the drain itself requires no special privilege — merely observing the CallDispatcher's balance and calling its unrestricted `dispatch` function, which any relayer/bot can trivially automate.

### Recommendation
- Replace every raw `abi.encodeWithSelector(IERC20.transfer.selector, ...)` sweep call built for `CallDispatcher` dispatch (in `IntentGatewayV2.sol` predispatch sweep, `IntentsBase._execute` postdispatch sweep, and the Tron variant) with logic that verifies both call success and the ERC20 boolean return, e.g., by decoding `result` in `CallDispatcher.dispatch` and reverting when a non-empty return payload decodes to `false`, or by having the gateway construct these sweep calls to a small helper contract that internally calls `SafeERC20.safeTransfer`.
- Alternatively/additionally, revert in `IntentGatewayV2.placeOrder`/`IntentsBase._execute` if the post-sweep `received`/`balance` accounting shows an unexpectedly zero or reduced transfer for a token that should have moved, rather than silently proceeding with an amount of `0`.
- Add access control or a per-call scoping mechanism to `CallDispatcher.dispatch` so it cannot be invoked by arbitrary third parties to sweep out any balance the contract happens to be holding at a given moment.

### Proof of Concept
Not independently executed against a fork/testnet; the flow above is derived directly from the cited source. A concrete PoC would deploy a mock ERC20 whose `transfer` returns `false` (does not revert) under some triggerable condition, configure it as an order input token in `IntentGatewayV2`, place an order using the predispatch flow so the token is routed through `CallDispatcher`, trigger the `false`-return condition during the sweep, observe `order.inputs[i].amount == 0` after `placeOrder` while the token balance remains on `CallDispatcher`, then call `CallDispatcher.dispatch` directly from an unrelated address with a `Call` transferring that balance out. [1](#0-0)

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L244-251)
```text
                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L273-289)
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

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```

**File:** evm/src/apps/IntentGatewayV2.sol (L291-306)
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

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-544)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-449)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```

**File:** sdk/packages/core/contracts/interfaces/ICallDispatcher.sol (L26-37)
```text
/**
 * @title The ICallDispatcher
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @notice This interface is used to dispatch untrusted call(s)
 */
interface ICallDispatcher {
    /*
     * @dev Dispatch the encoded call(s)
     */
    function dispatch(bytes memory params) external;
}
```
