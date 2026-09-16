## Finding [1](#0-0) 

### Title
`CallDispatcher.dispatch` has no access control, allowing anyone to drain residual token/ETH dust left by partial predispatch/postdispatch swaps - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher.dispatch()` is a fully public, unprotected function that executes an arbitrary attacker-supplied `Call[]` array using whatever balance the `CallDispatcher` contract currently holds. `IntentGatewayV2` routes all predispatch and postdispatch calldata execution through this same shared, stateless `CallDispatcher` instance, and only sweeps back the specific tokens declared in `order.inputs`/`order.output.assets`. Any token or native ETH that lands in the `CallDispatcher` outside of that declared set — from partial swaps, slippage, unexpected swap-output tokens, or any other execution path — is never swept by the protocol and is permanently claimable by anyone who calls `dispatch()` directly.

### Finding Description
`CallDispatcher.dispatch` has no `onlyGateway`/`onlyOwner` restriction and no reentrancy guard: [2](#0-1) 

It also accepts arbitrary ETH via a public `receive()`: [3](#0-2) 

`IntentGatewayV2` uses one shared `dispatcher` (`_params.dispatcher`) for both:
1. **Predispatch** (in `placeOrder`): predispatch assets are pushed to the dispatcher, `order.predispatch.call` is executed (e.g. a Uniswap swap), and afterward the gateway builds sweep calls **only for the tokens listed in `order.inputs`**, transferring that exact balance back: [4](#0-3) 

2. **Postdispatch/output calldata** (`IntentsBase._execute`): `order.output.call` is executed through the same dispatcher, and only tokens in `order.output.assets` are swept back as "dust": [5](#0-4) 

Both sweep loops iterate strictly over the token set declared in the order (`inputsLen`/`outputsLen`), not over the full set of assets the predispatch/postdispatch calldata could plausibly touch. Since the calldata itself is arbitrary (docs describe routing "through DEXes, lending protocols, or other DeFi primitives"), any of the following leaves stray balance permanently parked in the `CallDispatcher`:
- A DEX swap that yields a reward/bonus token not declared as an order input/output.
- Slippage/rounding leaving a small residual of an intermediate token.
- A partially-filled swap (e.g., limit/partial-fill DEX behavior) leaving unspent input tokens of a type not tracked by the sweep.
- Native ETH sent via `receive()` by mistake or as leftover `msg.value`.

Because `dispatch()` has zero access control, that stray balance can be swept by **any address**, at any time, simply by calling `CallDispatcher.dispatch()` with a `Call` that transfers the token (or ETH) to themselves — this is functionally identical to the reported analog where `UniswapSwapAdapter.swap` had no access control and let anyone claim tokens left behind by a partial swap.

### Impact Explanation
This is a direct, permanent loss-of-funds vector for the protocol/users: any residual token or ETH balance accumulated in the shared `CallDispatcher` from any order's predispatch/postdispatch execution can be stolen outright by an unrelated, unprivileged third party, bypassing the gateway entirely. Because the dispatcher is a single shared singleton used by every order across the deployment, even small per-order dust amounts accumulate into a persistent, monitorable, drainable balance.

### Likelihood Explanation
Likelihood is Medium-to-High: predispatch/postdispatch calldata in this system is explicitly designed to route through third-party DEX/DeFi calls (per the intent-gateway docs), which routinely produce slippage dust, unexpected reward tokens, or partial execution remainders. No attacker cooperation from the order creator is required — any bot watching for a nonzero balance on the known `CallDispatcher` address can immediately front-run or simply call `dispatch()` to claim it, since the function is public and requires no special state.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to only be callable by an authorized/registered gateway/app address (e.g. an `onlyAuthorizedCaller` modifier configured at deployment), rather than leaving it fully public.
- Alternatively/additionally, ensure the gateway's sweep logic in `placeOrder` and `_execute` enumerates and sweeps the dispatcher's *actual* full post-call balances (not just the declared `order.inputs`/`order.output.assets` set) so no dust can remain resident in the dispatcher between transactions.
- Consider making `CallDispatcher` per-order/ephemeral (e.g. deployed via a minimal proxy per call) so no cross-order shared balance can ever exist.

### Proof of Concept
1. A user places an order whose `order.predispatch.call` swaps ETH for DAI via UniswapV2/V3 through the shared `CallDispatcher` (as shown in `IntentGatewayV2.placeOrder`, lines 235-311). Due to slippage/router behavior, the swap also returns a small amount of a second token (or leaves unspent native ETH) that is not part of `order.inputs`.
2. `placeOrder`'s sweep loop only builds `transferCalls` for tokens present in `order.inputs`, so the extra token/ETH remains in the `CallDispatcher` contract's balance after the transaction completes.
3. An attacker (any EOA, no privileges needed) observes the nonzero balance on the well-known `CallDispatcher` address and calls:
   ```solidity
   CallDispatcher(dispatcher).dispatch(
       abi.encode([Call({ to: strayToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, strayBalance) })])
   );
   ```
   or, for stray ETH:
   ```solidity
   CallDispatcher(dispatcher).dispatch(
       abi.encode([Call({ to: attacker, value: address(dispatcher).balance, data: "" })])
   );
   ```
4. `dispatch()` executes the call with no ownership check [6](#0-5) , transferring the residual funds to the attacker.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L487-533)
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
```
