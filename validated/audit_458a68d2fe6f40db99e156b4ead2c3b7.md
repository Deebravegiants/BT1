## Title
`CallDispatcher.dispatch` has no access control, letting anyone drain any token/ETH balance left in the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
The FeeBuyback bug's root cause is a shared, funds-holding contract whose "submit"-style entrypoint executes fully attacker-controlled calldata and only sweeps back the specific token/amount it expects, leaving anything else that lands in the intermediary contract grabbable via that same unrestricted entrypoint. Hyperbridge's `IntentGatewayV2` has a structurally identical intermediary: `CallDispatcher`, which momentarily custodies escrowed input/output tokens during `predispatch`/`postdispatch` swap execution.

### Finding Description
`CallDispatcher.dispatch(bytes memory encoded)` is `external` with **no caller restriction whatsoever** — not `onlyOwner`, not "only IntentGatewayV2": [1](#0-0) 

`IntentGatewayV2` relies on this same public `CallDispatcher` instance (`_params.dispatcher`) as a temporary vault: it transfers user funds into it, invokes `dispatch()` with attacker-supplied `order.predispatch.call` / `order.output.call` (arbitrary target + arbitrary calldata + arbitrary value), and afterwards sweeps back **only the specific tokens named in `order.inputs` / `order.output.assets`**: [2](#0-1) [3](#0-2) 

Because the sweep is scoped to a fixed, order-defined token list, any value that ends up in `CallDispatcher` outside that list — e.g. a swap in the user's own arbitrary `predispatch.call`/`output.call` that produces an unlisted intermediate token, dust from a multi-hop router, accidental ETH sent to `CallDispatcher.receive()`, or any residual balance from a partially-executed multi-call batch — is never retrieved by the gateway. Since `dispatch()` itself is permissionless, **any unrelated address** can subsequently call `CallDispatcher.dispatch()` directly with a `Call` that transfers that leftover balance to itself. This is exactly the FeeBuyback pattern: an arbitrary-calldata-executing intermediary that only reconciles a caller-declared subset of balances, so anything outside that subset is free for the taking through the same permissionless entrypoint.

### Impact Explanation
Any token or native value that transiently or accidentally resides in the single shared `CallDispatcher` contract used by all `IntentGatewayV2` orders can be permanently stolen by an unprivileged third party who simply calls `dispatch()` with a transfer `Call`. Because `CallDispatcher` is a single, chain-wide singleton reused across every order, this is not confined to the order's own creator/solver — it is reachable by any address monitoring on-chain state for a nonzero balance at that address.

### Likelihood Explanation
`dispatch()` requires no authorization and no relationship to `IntentGatewayV2`, so exploitation only requires observing (or engineering, e.g. via a crafted `predispatch`/`output` swap route that intentionally produces an unlisted token) a nonzero balance at the `CallDispatcher` address, then racing to call `dispatch()` before the legitimate sweep (if any) occurs. Given `predispatch`/`output.call` are fully attacker(order-creator)-controlled arbitrary call sequences, producing such "unswept" residue is straightforward and does not require any privileged role.

### Recommendation
Restrict `CallDispatcher.dispatch` to only be callable by the registered `IntentGatewayV2` instance (or an allow-listed caller set at deployment), and/or make `CallDispatcher` deploy an ephemeral, single-use instance per call (e.g., via `CREATE2`/minimal proxy) instead of a single persistent shared contract, so no cross-order or cross-user balance can ever accumulate there for a third party to sweep.

### Proof of Concept
1. A user places an order whose `predispatch.call` (fully attacker-controlled, per `evm/src/apps/IntentGatewayV2.sol` `placeOrder`) routes through a swap that yields a small amount of an unlisted intermediate token X (not present in `order.inputs`), which the gateway's sweep logic ignores because it only reconciles tokens explicitly listed in `order.inputs`.
2. Token X now sits in the shared `CallDispatcher` contract.
3. Any third-party address calls `CallDispatcher.dispatch(abi.encode([Call({to: X, value: 0, data: transfer(attacker, balance)})]))` directly — this succeeds because `dispatch()` has no caller restriction — and receives token X for free, regardless of who placed the original order.

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
