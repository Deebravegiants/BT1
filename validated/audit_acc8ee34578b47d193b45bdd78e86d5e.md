### Title
Unrestricted `CallDispatcher.dispatch()` allows front-running/hijacking of funds transiently held during `IntentGatewayV2` predispatch/output-gathering sweeps - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher` is a single, shared, permissionless "call relay" contract used as an intermediary custody point by `IntentGatewayV2.placeOrder` (predispatch) and `ExtrinsicIntents`/`IntentGatewayV2.fillOrder` (output-gathering) to temporarily hold user tokens/ETH before they are swept back into the gateway. Just like `UniswapPoolHelper`/`BalancerPoolHelper.initializePool` in the referenced report — which assumed tokens sent in advance would still be present when an unrestricted function ran — `CallDispatcher.dispatch()` has no access control and blindly executes any caller-supplied `Call[]` against whatever balance the contract currently holds.

### Finding Description
`CallDispatcher.dispatch(bytes memory encoded)` is declared `external` with no modifier restricting the caller: [1](#0-0) 

`IntentGatewayV2.placeOrder` uses this shared contract as a temporary escrow: it transfers the order's `predispatch.assets` into `dispatcher`, invokes `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` to run arbitrary swap/unwrap logic, and only afterwards sweeps the dispatcher's *entire current token/ETH balance* into the gateway based on `IERC20(token).balanceOf(dispatcher)` / `address(dispatcher).balance` — not the amount actually produced by that specific call: [2](#0-1) 

The same pattern (transfer-in → arbitrary `dispatch()` → balance-based sweep-out) is used for output-gathering in the Tron variant and `ExtrinsicIntents.sol`: [3](#0-2) 

Because `CallDispatcher.dispatch` is not restricted to `IntentGatewayV2` (e.g., no `onlyGateway`/`onlyOwner` gate, no per-order authorization token), anyone who can trigger a call during the window in which funds sit inside `CallDispatcher` — for instance via a reentrant hook fired by the `predispatch.call` execution itself, or by a token/target contract invoked mid-dispatch that calls back into the well-known, singleton `CallDispatcher` address — can submit their own `dispatch()` call transferring out the balance the gateway is about to sweep. This is structurally identical to the reported class of bug: a fund-routing step assumes exclusive, uncontested access to a balance sitting in an intermediary contract, but the step that would move/consume it is left unauthenticated.

### Impact Explanation
An attacker able to trigger `CallDispatcher.dispatch()` during the narrow window between "assets deposited into the dispatcher" and "gateway sweeps the dispatcher's balance" can redirect the escrowed input tokens (or output tokens gathered for a fill) to an address of their choosing, resulting in theft of user funds mid-`placeOrder`/`fillOrder`, or in the sweep failing/reverting (denial of the order) because the balance is insufficient afterward. Given `IntentGatewayV2` is the core message-dispatching/escrow path reachable by any unprivileged user submitting an order, this is a direct fund-theft/fund-freezing vector.

### Likelihood Explanation
Exploitation requires a way to execute code during the `dispatch(order.predispatch.call)` window — e.g. a predispatch call target with a reentrant callback (common for ERC-777/ERC-1363-style tokens or DEX routers with hooks), since `CallDispatcher` itself has `receive() external payable` and no reentrancy guard, and its address is public/known ahead of time via `_params.dispatcher`. Because the order's own `predispatch.call` and `predispatch.assets` are fully attacker/user-controlled, a malicious order-placer (or an order interacting with an attacker-controlled/compromised token) can reliably construct this reentrant condition, making exploitation practical rather than purely theoretical.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by an authorized/allow-listed caller (e.g., only the `IntentGatewayV2` instance(s) that own the funds being routed), or redesign the flow so `CallDispatcher` never holds a shared balance across untrusted parties — for example, by deploying a per-order/per-call ephemeral executor, or by having the gateway pull an exact accounted amount rather than sweeping the dispatcher's full live balance.

### Proof of Concept
1. An order's `predispatch.call` includes a call to an ERC-777-style token (or any target with a callback hook) as part of the swap/unwrap logic executed via `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` in `placeOrder`. [4](#0-3) 
2. During that external call's execution, the callback re-enters and calls `CallDispatcher.dispatch()` directly (this call is not gated in any way) with a `Call[]` that transfers the token/ETH balance currently sitting in `CallDispatcher` to an attacker-controlled address. [1](#0-0) 
3. When `placeOrder` resumes and performs its balance-based sweep (`balanceOf(dispatcher)` / `dispatcher.balance`), the funds are gone or reduced, causing either theft of escrowed value or a revert (`InsufficientNativeToken`/`InvalidInput`) that denies the order. [5](#0-4)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L235-289)
```text
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L413-449)
```text
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
```
