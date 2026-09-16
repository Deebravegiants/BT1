## Title
Non-standard ERC20 tokens with silent-failure `transfer` can leave sweep proceeds permanently stuck in `CallDispatcher` - (File: `evm/src/utils/CallDispatcher.sol`, `evm/src/apps/IntentGatewayV2.sol`, `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`CallDispatcher.dispatch` only checks the boolean `success` of a raw low-level `.call`, never the ABI-encoded return data of the call it executes. `IntentGatewayV2.placeOrder` and `IntentsBase._execute` both use this dispatcher to sweep token balances back from the (shared) `CallDispatcher` by encoding a raw `IERC20.transfer.selector` call instead of using `SafeERC20.safeTransfer`. For non-standard ERC20 tokens that return `false` on failure instead of reverting (e.g. `ZRX`-style tokens), the low-level call itself succeeds (so `CallDispatcher` reports success), while the actual token transfer silently fails — leaving the tokens permanently stuck inside `CallDispatcher`, which exposes no rescue function.

### Finding Description
`CallDispatcher.dispatch` executes each call and only checks the raw call success flag: [1](#0-0) 

In `IntentGatewayV2.placeOrder`, when an order has predispatch calldata, tokens are first sent to `dispatcher`, a call is executed, and then the resulting balances are swept back to the gateway using a raw `transfer` call (not `safeTransfer`) built as calldata for `CallDispatcher`: [2](#0-1) 

The gateway then measures what it "received" purely from the balance delta and silently sets `order.inputs[i].amount = received` (0 in the failure case) instead of reverting when the transfer produced no balance change: [3](#0-2) 

The same raw-`transfer`-via-`CallDispatcher` sweep pattern (with no return-value check) appears in the dust-sweep of `IntentsBase._execute`, used after a solver's `fillOrder` postdispatch call: [4](#0-3) 

Because `token` in both `order.inputs` and `order.output.assets` is fully attacker/user-controlled (`address(uint160(uint256(order.inputs[i].token)))`), a user or solver can supply a token address that behaves this way, or this can occur "naturally" for any real deployed non-standard ERC20. When the transfer returns `false` without reverting:
- `CallDispatcher.dispatch` sees `success == true` and does not revert.
- The tokens obtained by the predispatch/postdispatch call remain in `CallDispatcher`'s balance.
- `CallDispatcher` has no owner-only sweep/rescue function — its only external entry point is `dispatch`, which only executes attacker/caller-supplied calls; there is no path to recover arbitrary ERC20 balances left on it.
- The gateway silently proceeds with `amount = 0` (in `placeOrder`) or emits a `DustCollected` event claiming funds were collected (in `_execute`) that never actually arrived.

This is the exact bug class described in the external report (unchecked ERC20 `transfer` return value with non-reverting-on-failure tokens), reachable here not through a naive `PayrollManager`-style contract but through Hyperbridge's `IntentGatewayV2` order-placement and fill-execution paths, both callable by any unprivileged user/solver via a single transaction.

### Impact Explanation
Tokens escrowed as part of an intent order's predispatch flow, or output tokens swept as dust in `_execute` after a fill, can become permanently and irrecoverably locked inside the shared `CallDispatcher` contract, which has no privileged withdrawal mechanism for arbitrary ERC20 balances. This is a genuine, permanent freezing-of-funds condition for whichever order/token combination is affected.

### Likelihood Explanation
Low-to-moderate: requires the involved token to belong to the small set of ERC20 tokens that return `false` on failed transfers instead of reverting (same caveat as the original report). However, unlike the referenced `PayrollManager` example, triggering this doesn't require an unusual failure condition on a "normal" ERC20 — the predispatch/postdispatch calldata is user-controlled, so a griefer could deliberately choose a known non-standard-failure token (or manipulate balances/allowances upstream to force a `false` return) to lock funds intentionally.

### Recommendation
Replace the raw `abi.encodeWithSelector(IERC20.transfer.selector, ...)` calls built for `CallDispatcher` sweeps in `IntentGatewayV2.placeOrder` and `IntentsBase._execute` with `SafeERC20.safeTransfer`-encoded calldata (or have `CallDispatcher` itself decode and check `abi.decode(result, (bool))` for calls that are known-ERC20 transfers), so silent `false` returns cause a revert instead of appearing to succeed. Additionally, consider adding a privileged rescue function to `CallDispatcher` as defense-in-depth against otherwise-stuck balances.

### Proof of Concept
1. A user calls `IntentGatewayV2.placeOrder` with `order.predispatch.call`/`assets` set, and `order.inputs[0].token` set to a non-standard ERC20 that returns `false` (instead of reverting) when its internal transfer condition fails (e.g., insufficient balance edge case or a blocklist condition on the recipient).
2. `_params.dispatcher` (the shared `CallDispatcher`) receives the predispatch assets and executes the predispatch call, ending up holding a balance of the non-standard token.
3. `IntentGatewayV2` builds a sweep `Call` with `abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)` and dispatches it via `ICallDispatcher(dispatcher).dispatch(...)`.
4. The token's `transfer` returns `false` (does not revert); `CallDispatcher.dispatch` observes `success == true` from the low-level call and does not revert.
5. `IntentGatewayV2` measures `received = IERC20(token).balanceOf(address(this)) - balancesBefore[i] == 0`, sets `order.inputs[i].amount = 0`, and the order proceeds — while the actual token balance remains stuck in `CallDispatcher` with no way for the user or protocol to retrieve it.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L260-290)
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

```

**File:** evm/src/apps/IntentGatewayV2.sol (L291-311)
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
