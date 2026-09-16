### Title
Unrestricted `CallDispatcher.dispatch()` lets anyone drain funds momentarily or permanently held by the shared dispatcher - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher` is a shared, permission-less infrastructure contract used by `IntentGatewayV2`/`IntentsBase`, `ExtrinsicIntents`, and the `HyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` apps to execute arbitrary, caller-supplied calls (`predispatch.call`, `order.output.call`, or cross-chain `message.data`). Its `dispatch(bytes)` entrypoint has **no access-control modifier and no restriction on the call target**, matching exactly the bug class from the external report: a trusted/privileged contract performing low-level calls to a fully attacker-chosen `to`/`data`.

### Finding Description
`CallDispatcher.dispatch` decodes an arbitrary `Call[]` array and blindly forwards `.call{value: call.value}(call.data)` to any `to` address, with only an `extcodesize` check: [1](#0-0) 

Crucially, this function is `external` with **no caller restriction whatsoever** — any EOA or contract, not just `IntentGatewayV2`/`ExtrinsicIntents`/`HyperFungibleToken`, can invoke `CallDispatcher(dispatcherAddr).dispatch(...)` directly, and it also has a public `receive()` so it can accumulate native token balance from anyone.

The dispatcher is used as an intermediate custodian of real user/solver funds during intent fulfillment. In `IntentsBase._execute`, output assets and predispatch assets are transferred to `dispatcher` before `ICallDispatcher(dispatcher).dispatch(order.output.call)` is invoked with calldata that is fully controlled by the order creator (an untrusted end user), and only *afterwards* is the residual balance swept back: [2](#0-1) 

The Tron `IntentGatewayV2` mirrors this: predispatch assets are transferred into `dispatcher`, then `dispatch(order.predispatch.call)` executes attacker-supplied calldata against those freshly-deposited funds, before the contract computes the remaining balance and sweeps it back as escrow/dust: [3](#0-2) 

Because `dispatch()` itself is unauthenticated and the dispatcher's balance is externally visible on-chain, any residual balance the dispatcher is holding at any point — dust from a previous order's swap that wasn't enumerated in that order's `outputs`/`inputs` token list, ETH sent to its `receive()`, or assets transferred in but not yet swept within the same call sequence — is reachable by an attacker who calls `dispatch()` directly with a `Call` targeting that token/`transfer`/`transferFrom` to themselves. The dispatcher performs no bookkeeping of "whose" funds it is holding; it trusts whoever calls `dispatch()` to only reference their own assets, exactly the "no data validation on low-level call target/data" flaw described in the source report.

### Impact Explanation
Any funds the `CallDispatcher` transiently custodies during an intent fill/predispatch flow, or protocol dust it hasn't yet had swept out, can be stolen by an unprivileged third party simply by calling `dispatch()` with a `Call{to: token, data: transfer(attacker, balance)}`. Since `IntentsBase`/`IntentGatewayV2` route real escrowed user and solver funds through this same dispatcher on every fill, this is a direct path to theft of user/solver funds, matching the report's "malicious users can... transfer funds to themselves" impact.

### Likelihood Explanation
Every intent fill or send that includes calldata (`predispatch.call`, `order.output.call`, `HyperFungibleToken` message `data`) routes real funds through the dispatcher and is user-triggerable with a single transaction (`fillOrder`/`placeOrder`/`send`), and `CallDispatcher.dispatch` is directly callable by anyone with no gating — the likelihood of a griefer/attacker racing or front-running dust before the protocol's own sweep step, or scavenging leftover balances from token types not enumerated in a given order's asset list, is high given normal MEV/relayer conditions.

### Recommendation
- Short term: Restrict `CallDispatcher.dispatch` to only be callable by the specific intent/gateway contract instance that just deposited funds into it (e.g. an `onlyOwner`/`onlyCaller` pattern set at construction, or make the dispatcher single-use/ephemeral per order via `CREATE2` cloning), and ensure any residual balance is swept atomically before returning control, so no window exists where balance is externally drainable.
- Long term: Do not custody real user/solver funds in a generic, permission-less arbitrary-call executor; replace with a scoped callback interface that only allows pre-approved actions (e.g. token transfer to a fixed recipient computed from escrow state) rather than fully attacker-controlled `to`/`data`.

### Proof of Concept
1. A solver fills an order via `IntentGatewayV2`/`ExtrinsicIntents` with a `predispatch.call`/`order.output.call` that performs a swap leaving 1 unit of an ERC20 token (not listed in that order's `inputs`/`outputs`) inside the `CallDispatcher`.
2. Because that token isn't part of the sweep loop in `IntentsBase._execute`/`IntentGatewayV2._fillOrder` (only tokens in `order.inputs`/`order.output.assets` are swept), the balance remains in the dispatcher indefinitely.
3. An attacker directly calls `CallDispatcher(dispatcherAddress).dispatch(abi.encode([Call({to: leftoverToken, value:0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, leftoverBalance)})]))` — this succeeds because `dispatch` has no access control, transferring the leftover funds to the attacker. [1](#0-0)

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L487-545)
```text
    /**
     * @dev Executes arbitrary calldata attached to an order's output via the CallDispatcher.
     * After dispatching the calls, any residual token balances left on the dispatcher
     * are swept back to this contract and accounted for as protocol dust.
     *
     * This enables composable order fulfillment — solvers can route through DEXes,
     * lending protocols, or other DeFi primitives as part of filling an order.
     *
     * @param order The order containing the output calldata to execute.
     * @param outputsLen The number of output assets to sweep after execution.
     */
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L391-450)
```text

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
