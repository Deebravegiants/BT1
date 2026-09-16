## Title
Unrestricted `CallDispatcher.dispatch()` Allows Theft of Funds Held by the Shared Predispatch/Postdispatch Intermediary Contract - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` has no access control whatsoever — any address can call it with an arbitrary `Call[]` array. `CallDispatcher` is a single, shared, long-lived contract that `IntentGatewayV2` (and other Hyperbridge apps) use as a temporary custodian of user/solver funds during predispatch (swap-then-escrow) and postdispatch (fill-then-act) flows. Because sweep logic only recovers the tokens the order explicitly declared, and because the intermediary itself is permissionless, any balance that ends up sitting on `CallDispatcher` — whether from an un-swept byproduct token, a partially processed swap, or funds sent to it directly — can be drained by anyone, not just the gateway.

### Finding Description
`CallDispatcher.dispatch()` is fully public with no caller restriction: [1](#0-0) 

`IntentGatewayV2`/`IntentsBase` rely on this contract as a **shared holding account** for both predispatch and postdispatch flows. In the predispatch path, user assets are transferred to `dispatcher`, then `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` executes the swap, and only afterward does the gateway sweep back whatever balance sits on the dispatcher for the tokens declared in `order.inputs`: [2](#0-1) 

Similarly, in the postdispatch (fill) path, the `beneficiary` of a solver's output payment can legitimately be set to the dispatcher itself (confirmed by the test harness), after which `_execute()` runs the attached calldata and sweeps only the tokens listed in `order.output.assets`: [3](#0-2) [4](#0-3) 

The sweep loops in both `IntentGatewayV2.placeOrder` and `IntentsBase._execute` only iterate over the token set the order declares (`order.inputs`/`order.output.assets`). Any other asset that ends up on the dispatcher — a byproduct of a multi-hop swap, a different token than expected returned by an untrusted `swapTarget`-style call embedded in `order.predispatch.call`/`order.output.call`, dust from a partially-consumed approval, or tokens sent to the dispatcher address by mistake — is never recovered by the gateway's own sweep and is left sitting on a contract anyone can call directly. Because `dispatch()` has no `onlyGateway`/`onlyOwner` guard, any third party can submit `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: transfer(attacker, balance)})]))` to sweep out that balance for themselves at any time — this is the same class of bug as the JoJo report: an intermediary contract that "checks/uses the current balance" without any binding to who legitimately deposited it, reachable by an unprivileged third party racing (or simply calling ahead of) the intended sweep.

### Impact Explanation
This is a concrete theft-of-funds vector reachable from a single unprivileged transaction against a core, unprivileged-user-facing dispatch path (order placement/fill via `IntentGatewayV2`). Any token balance not covered by the declared input/output list, or observed mid-flight before the gateway's own scheduled sweep call executes, is permanently exploitable by any address — a classic "unauthorized app action" / permanent freezing-then-theft of user or solver funds through a shared, permissionless intermediary.

### Likelihood Explanation
Likelihood is high: `dispatch()` requires no privilege and no timing coordination with the gateway — an attacker only needs to observe (via mempool or on-chain state) that the dispatcher currently holds a non-zero balance of some token and submit a direct call. Orders with predispatch/postdispatch swaps routed through unpredictable DEX paths (multi-hop swaps, aggregator calldata under user/solver control) make byproduct or excess-token scenarios routine rather than exotic.

### Recommendation
Restrict `CallDispatcher.dispatch()` (or provide a gated variant) to only the registered `IntentGatewayV2`/app instances that are supposed to use it, e.g., an `onlyAuthorizedCaller` modifier set at construction/configuration. Alternatively, deploy a fresh, ephemeral `CallDispatcher`-equivalent per order/fill (e.g., via minimal proxy/clone) so no shared, cross-order balance can ever accumulate on a contract reachable by arbitrary third parties. If a single shared instance must be kept for gas reasons, the gateway's sweep logic should sweep the dispatcher's *entire* balance of every token that could plausibly appear (not just the declared list), and access to `dispatch()` should be locked down so an outside caller can never independently invoke it against the gateway's custodied balances.

### Proof of Concept
1. An order is placed with `predispatch.call` routing through a multi-hop swap or aggregator whose exact output token set is not fully known ahead of time (e.g., a swap that also yields a small amount of a reward/LP token, or partial slippage refund in a token other than `order.inputs[i].token`).
2. `IntentGatewayV2.placeOrder` executes the predispatch swap via `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`, leaving the byproduct token balance on `dispatcher` (only the declared `order.inputs` token is swept back to the gateway).
3. Anyone (no privilege required) calls `CallDispatcher.dispatch(abi.encode([Call({to: byproductToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})]))` directly against the same `CallDispatcher` instance, draining the byproduct balance to themselves — funds that were, in substance, part of the user's transaction outcome, never designed to be permissionlessly claimable by a third party. [5](#0-4)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L25-62)
```text
contract CallDispatcher is ICallDispatcher {
    /**
     * @dev error thrown when the target is not a contract.
     */
    error NotContract(address target);

    /**
     * @dev error thrown when a call fails.
     */
    error CallFailed(address target, bytes result);

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

**File:** evm/src/apps/IntentGatewayV2.sol (L258-299)
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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L1384-1392)
```text
        // Setup order output - beneficiary is dispatcher, it will receive USDC from solver
        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: usdcNeeded + 100 * 1e6}); // Solver sends more than needed

        PaymentInfo memory output = PaymentInfo({
            beneficiary: bytes32(uint256(uint160(address(dispatcher)))), // Dispatcher receives USDC
            assets: outputAssets,
            call: abi.encode(postdispatchCalls)
        });
```
