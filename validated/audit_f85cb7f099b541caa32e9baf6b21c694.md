## Analysis: Permissionless `CallDispatcher.dispatch()` allows theft of any residual funds left in the shared dispatcher

The external report's core bug class — an unrestricted low-level `call{value:}` forwarding function that can move funds it shouldn't be able to — maps onto `CallDispatcher.dispatch()`, which is a completely permissionless function that forwards arbitrary `to.call{value: call.value}(call.data)` on behalf of whatever balance the contract happens to hold, with **no caller restriction at all**.### Title
Permissionless `CallDispatcher.dispatch()` lets anyone drain residual native/ERC20 balance left in the shared IntentGatewayV2 call dispatcher - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher.dispatch()` is `external` with no caller restriction, and forwards attacker/order-supplied `Call{to, value, data}` entries using the contract's own balance (`to.call{value: call.value}(call.data)`), exactly the "raw value-forwarding call" primitive the external report flags. Every escrow flow that uses this shared, singleton dispatcher (`_params.dispatcher` in `IntentGatewayV2`/`ExtrinsicIntents`/`IntrinsicIntents`) only sweeps back the specific tokens declared in `order.inputs`/`order.output.assets` after execution, so any balance the dispatcher ends up holding outside that declared set (e.g. leftover native ETH or an intermediate/incidental token from a swap executed via `order.predispatch.call` / `order.output.call`) is never retrieved by the protocol and sits in the dispatcher indefinitely, fully claimable by any third party who simply calls `dispatch()` directly.

### Finding Description
`CallDispatcher.sol` has a `receive()` and a public `dispatch(bytes memory encoded)` function with no modifier and no `msg.sender` check whatsoever: [1](#0-0) 

`IntentsBase._execute` (used by both `IntrinsicIntents` and `ExtrinsicIntents` fill paths) only sweeps balances for the tokens listed in the order's declared `output.assets` array: [2](#0-1) 

Similarly, the predispatch flow in `evm/tron/contracts/apps/IntentGatewayV2.sol` only transfers back the exact tokens in `order.inputs`, computed via `balance = IERC20(token).balanceOf(dispatcher)` for the declared input tokens only: [3](#0-2) 

Because the calldata executed through the dispatcher (`order.predispatch.call` / `order.output.call`) is attacker/solver-controlled and can route through arbitrary external DeFi contracts (swaps, routers, etc.), it is straightforward for any such call to leave a balance in a token or in native ETH that is **not** part of the order's declared `assets`/`inputs` list — e.g. dust from slippage, referral rebates, incorrect change/refund handling by a router, or a token intentionally omitted from the declared list. Since the sweep logic only iterates over the declared asset list, that residual balance is never returned to the gateway and remains parked in the singleton `CallDispatcher` contract, which is shared across *all* orders and *all* users of the gateway.

Because `dispatch()` has zero access control, any address can then call `CallDispatcher.dispatch()` directly with a `Call[]` encoding `{to: attacker, value: <residual balance>, data: ""}` (for native ETH) or an ERC20 `transfer(attacker, balance)` call, and drain that stranded balance — it is not limited to being called through the `IntentGatewayV2`/`IntentsBase` logic at all.

### Impact Explanation
This is a direct theft-of-funds vector: any value that ends up stuck in the shared `CallDispatcher` (whether from a rounding edge case, an order whose `output.call`/`predispatch.call` interacts with a token not declared in the order's asset list, or a partially-failed sweep) is permanently and trivially stealable by an unprivileged third party, with no relationship to the order that generated the residue. Given the dispatcher is a single shared contract across the whole gateway, this converts any accounting edge case in the sweep logic into an open bounty for MEV bots/attackers monitoring the dispatcher's balance.

### Likelihood Explanation
The trigger requires the dispatcher to briefly or persistently hold an asset outside the order's declared asset list — plausible whenever `order.output.call`/`order.predispatch.call` executes a swap or DeFi interaction whose output token set doesn't exactly match what the order declares (a case the protocol does not prevent, since the calldata is attacker/solver supplied and only loosely constrained by `DustCollected`/sweep logic for the *known* tokens). No privileged role is needed to exploit the drain once residue exists — a single call to the public `dispatch()` function suffices.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the registered gateway/authorized caller (e.g. an `onlyAuthorized` modifier checking `msg.sender` against a configured gateway address, or deploying a per-order/per-transaction ephemeral dispatcher instead of a shared singleton). Additionally, harden the sweep logic in `IntentsBase._execute` and the predispatch transfer-back logic in `IntentGatewayV2.sol` to enumerate and sweep *all* tokens actually touched by the executed calldata (or require the calldata to fully account for every asset it can produce), not just the tokens declared in the order.

### Proof of Concept
1. A solver fills a cross-chain order whose `order.output.call` swaps output tokens via an external router, and due to slippage/rebate the router returns a small amount of an ERC20 not present in `order.output.assets` (or leftover native ETH) to the `CallDispatcher`.
2. `IntentsBase._execute` sweeps only the tokens in `order.output.assets`; the extra token/ETH balance remains on the `CallDispatcher`.
3. Any third party observes the `CallDispatcher`'s balance and calls `CallDispatcher.dispatch(abi.encode([Call({to: attacker, value: <balance>, data: ""})]))` (or an ERC20 `transfer` call for the residual token) directly — since `dispatch()` has no access control, this succeeds and the funds are stolen. [4](#0-3)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-62)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}

    /**
     *  @dev reverts if the target is not a contract or if any of the calls reverts.
     */
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L387-450)
```text
        // escrow tokens
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

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
        } else {
```
