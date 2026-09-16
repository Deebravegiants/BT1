### Title
Unrestricted `CallDispatcher.dispatch()` combined with incomplete post-execution sweeps strands and exposes swap byproducts to theft by any third party - ([File: evm/src/utils/CallDispatcher.sol], [File: evm/src/apps/intentsv2/IntentsBase.sol], [File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2`'s predispatch and postdispatch calldata features route through a single, shared `CallDispatcher` instance whose `dispatch()` function has **no access control** — any address can call it directly with arbitrary `Call[]`. The gateway's sweep logic after executing user/solver-supplied calldata only recovers the specific tokens enumerated in `order.inputs`/`order.output.assets`; any other token or native value produced as a byproduct of the arbitrary calldata (DEX dust, refunds, wrong-token swap output, etc.) is left sitting in the CallDispatcher. Because `dispatch()` is unauthenticated, any third party monitoring the chain can call it directly to sweep out that stranded value before governance's own dust-sweep path ever runs.

### Finding Description
`CallDispatcher.dispatch()` performs no caller check: [1](#0-0) 

The IntentGateway uses this single shared dispatcher (`_params.dispatcher`) for both predispatch (swap-then-escrow) and postdispatch (fill-then-act) flows. On fill, `_execute()` dispatches the solver-supplied `order.output.call` and then sweeps back only the balances of the tokens explicitly listed in `order.output.assets`: [2](#0-1) 

Likewise, on order placement, the predispatch flow transfers assets to the dispatcher, executes `order.predispatch.call`, and sweeps back only the tokens enumerated in `order.inputs`: [3](#0-2) 

Neither sweep loop accounts for any token or ETH that the attached arbitrary calldata might produce outside the fixed input/output token list (e.g., a multi-hop swap leaving a different intermediate token, reward tokens, refunds, or excess native value from a router). Since the order's calldata is fully attacker/solver-controlled ("composable order fulfillment — solvers can route through DEXes, lending protocols, or other DeFi primitives"), any such byproduct remains permanently parked at the CallDispatcher's address. Because `CallDispatcher.dispatch()` has no restriction to the gateway, any unrelated address can then call it directly with a `Call` transferring that stranded balance to themselves — completely bypassing the protocol's own dust accounting and the governance-gated `_sweepDust` path, which only operates on funds already inside the gateway contract, not funds left in the shared dispatcher.

This mirrors the original report's "Arbitrary Router Contract Calls" and "insufficient balance checks" bug classes: the dispatcher is a low-level call primitive with no caller validation, and the surrounding accounting logic does not comprehensively track/reclaim everything that can end up on it.

### Impact Explanation
Any value inadvertently or maliciously stranded on the shared `CallDispatcher` (used by every order across the protocol on that chain) is permanently exposed to theft by an unprivileged third party, since `dispatch()` can be called by anyone to move that balance elsewhere. This is a concrete loss-of-funds vector reachable from a single submitted order/fill transaction containing calldata whose side effects are not perfectly enumerated by the fixed asset list, and it can be triggered opportunistically by any chain observer racing to call `dispatch()` before governance's periodic dust sweep.

### Likelihood Explanation
The predispatch/postdispatch calldata feature is a core, documented capability of `IntentGatewayV2` intended to let solvers route through arbitrary DeFi protocols. Any solver/user calldata that doesn't yield an exact 1:1 match with the declared `order.inputs`/`order.output.assets` set (extremely plausible with multi-hop swaps, slippage, reward tokens, or minor router refund quirks) leaves value on the dispatcher. Given `dispatch()` is public and unguarded, exploitation requires no special privileges — just observing the dispatcher's balance and racing a transaction.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to be callable only by whitelisted/trusted callers (e.g., the `IntentGatewayV2` and token app contracts that own it), or deploy a fresh, single-use dispatcher instance per call (e.g., via `CREATE2`/minimal proxy) so no shared, persistently-reachable balance ever exists.
- After executing arbitrary calldata, sweep the dispatcher's balance for *all* tokens actually touched/received (not just the tokens declared in `order.inputs`/`order.output.assets`), or otherwise ensure the dispatcher's balance is verifiably zero for every asset before returning control.
- Add an invariant check/assertion that the dispatcher holds zero balance for any token at the start and end of each gateway-driven operation, reverting if not, to prevent value from ever being silently stranded.

### Proof of Concept
1. A solver includes `order.output.call` that swaps the delivered output token through a DEX router which, due to slippage/fee-on-transfer/multi-hop routing, yields a small amount of an unrelated ERC-20 (or leaves dust ETH) not present in `order.output.assets`.
2. `_execute()` sweeps only the tokens in `order.output.assets`; the unrelated token/ETH remains on `CallDispatcher`.
3. Any third-party address calls `CallDispatcher.dispatch()` directly with `Call({to: strandedToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})` (or a native-value `Call` for stranded ETH) — this succeeds because `dispatch()` has no caller restriction — transferring the stranded funds to the attacker instead of the protocol's dust accounting.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-533)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L258-311)
```text
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

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
