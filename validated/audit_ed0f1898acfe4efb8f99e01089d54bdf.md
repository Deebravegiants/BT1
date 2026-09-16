## Title
`CallDispatcher.dispatch()` has no access control, letting anyone steal any residual funds it holds - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is the shared, publicly known contract (one instance is reused across `IntentGatewayV2`, `IntentsBase`, `HyperFungibleToken`, and `WrappedHyperFungibleToken`) that executes attacker/solver/user-supplied `Call[]` batches during predispatch, postdispatch and calldata-execution flows. Its `dispatch(bytes memory encoded)` function is `external` with **no caller restriction whatsoever** — no `onlyGateway`, no `msg.sender` check, nothing. [1](#0-0) 

This mirrors the root cause of the referenced Dodo report: a contract designed to be driven only by a trusted flow (there, Aave's flashloan callback; here, the gateway's predispatch/postdispatch step) executes attacker-controlled calldata with no verification of who triggered it, and that contract is documented to hold tokens/ETH, even if only transiently.

### Finding Description
`CallDispatcher` is explicitly designed to "hold tokens temporarily during execution" per the project's own documentation: [2](#0-1) 

and it accepts arbitrary ETH via an unrestricted `receive()`: [3](#0-2) 

Because `dispatch()` is callable by anyone, any value ever left sitting in the dispatcher's balance — ETH sent to it directly (by mistake, by an unrelated flow, or as swap-router dust/rewards), or ERC20 tokens that are not part of the `assets`/`outputsLen` list the gateway sweeps back after execution — is immediately withdrawable by any third party. All the sweep logic in `IntentsBase._execute` and `IntentGatewayV2.placeOrder` only recovers the specific tokens the order declares: [4](#0-3) [5](#0-4) 

Any token acquired by the dispatcher outside those enumerated lists (e.g., reward/airdrop tokens returned by a DEX swap invoked from `order.predispatch.call`/`order.output.call`, unswept surplus ETH, or tokens someone sends directly to the well-known deployed address referenced in the docs) is never recovered by protocol code and remains in the dispatcher's balance indefinitely. Since `dispatch()` trusts any caller, an attacker simply calls it with `Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})` (or a native-ETH `Call` with `value` equal to the dispatcher's balance) to drain it — exactly the same "unauthenticated privileged executor of a contract that holds funds" pattern as the Dodo `executeOperation` bug, where `_swapApproveTarget`/`_tradeAssets` were attacker-controlled because the caller was never checked.

### Impact Explanation
Any ETH or ERC20 tokens that accumulate in the shared `CallDispatcher` — through dust from swaps invoked during predispatch/postdispatch, un-enumerated reward tokens, or mistaken direct transfers to its published address — can be stolen outright by any unprivileged address. This is concrete theft of funds reachable from a plain, unprivileged `dispatch()` call, satisfying the High-severity theft criterion.

### Likelihood Explanation
`CallDispatcher` is shared across multiple gateways (`IntentGatewayV2`, `IntentsBase`, `HyperFungibleToken`/`WrappedHyperFungibleToken`) and is invoked with fully attacker/solver-controlled `Call[]` payloads (`order.predispatch.call`, `order.output.call`, HFT `data`) on every order/transfer that uses calldata execution. Given the volume of cross-chain calldata executions and DEX interactions routed through it, residual balances (swap dust, reward tokens, rounding remnants, stray transfers to the known address) are a realistic and recurring occurrence, and exploitation requires only a single unprivileged `dispatch()` call with no special timing or race condition.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a designated caller (e.g., an owner/allow-listed gateway set at construction, or per-deployment dedicated dispatcher instances rather than one shared singleton), and/or add a sweep-any-leftover-token safety valve that only the legitimate order's beneficiary/gateway can invoke. At minimum, never let `dispatch()` be callable by arbitrary `msg.sender` when the contract is expected, even transiently, to hold value.

### Proof of Concept
1. A predispatch/postdispatch `Call[]` (from any user's order) swaps through a DEX that returns a small amount of a reward/dust token not listed in `order.output.assets`/`order.predispatch.assets`; `IntentsBase._execute`/`IntentGatewayV2.placeOrder` only sweeps the declared assets, so the reward token remains in the shared `CallDispatcher`.
2. Alternatively, anyone sends ETH directly to the publicly documented `CallDispatcher` address via its unrestricted `receive()`.
3. An attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, IERC20(token).balanceOf(address(dispatcher)))})]))` (or an ETH-value `Call` to themselves for the native case).
4. `dispatch()` performs the transfer with no check on `msg.sender`, delivering the stranded funds to the attacker.

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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
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
