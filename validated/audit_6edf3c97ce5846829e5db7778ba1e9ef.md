### Title
Unauthenticated `CallDispatcher.dispatch()` lets anyone drain tokens left stranded in the shared dispatcher by `IntentGatewayV2`'s partial-sweep flow - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
The `CallDispatcher` contract that `IntentGatewayV2` uses as an intermediate holder for `predispatch`/`postdispatch` calls exposes `dispatch(bytes)` with **no access control** at all. `IntentGatewayV2.placeOrder` (and the analogous `fillOrder` postdispatch flow) trust *whatever balance happens to sit in the dispatcher* as proof of value produced by the order's own predispatch call, then sweep only the tokens listed in `order.inputs`/`order.output`. Any token balance left in the shared dispatcher that is not part of that specific sweep list is left there — and because `dispatch()` is callable by anyone, an attacker can call it directly to walk off with that balance.

### Finding Description
`IntentGatewayV2.placeOrder` executes an attacker/user-supplied `predispatch.call` via the shared `CallDispatcher`, then measures "value produced" purely from `balanceOf(dispatcher)` and sweeps only the tokens named in `order.inputs`: [1](#0-0) 

The comment even documents that the mechanism is generic ("e.g., unwrapping LP tokens") — meaning a predispatch call is expected to be able to produce *more than one* output token, yet only the tokens declared in `order.inputs` are ever swept back into escrow: [2](#0-1) 

Any other token (or native ETH) that the predispatch/postdispatch call causes the dispatcher to hold is simply left sitting on the `CallDispatcher` contract's own balance. Because `CallDispatcher.dispatch()` has no `onlyGateway`/`onlyOwner` guard, it can be invoked directly by any external account, at any later block, to force the dispatcher to execute an arbitrary `Call[]` — including a plain ERC20 `transfer()` or ETH send out of the dispatcher's own balance: [3](#0-2) 

The `CallDispatcher` also has a public unrestricted `receive()`, so it is designed to accumulate balance during multi-step flows: [4](#0-3) 

This is the same root-cause pattern as the reported bug class: value custody/authorization is derived from an unauthenticated `balanceOf()` reading rather than from an invariant that ties the balance strictly to the caller/operation that is entitled to it. In the LinkDAO case, the pair's swap trusted a balance snapshot without validating it against the expected K-invariant; here, `CallDispatcher` lets *any* caller redeem whatever balance is present, with no check that the caller (or the transaction) is the one entitled to it.

### Impact Explanation
`_params.dispatcher` is a single, shared, long-lived contract used across every `placeOrder`/`fillOrder` call on a gateway deployment. Any token balance stranded there — whether from a predispatch call that unwraps into multiple assets, a postdispatch swap that leaves an untracked side-output, rounding dust, or a stray direct transfer — becomes freely claimable by anyone who calls `dispatch()` directly with a `transfer`-to-self call, completely bypassing `IntentGatewayV2`'s escrow/ownership accounting. This is concrete theft of user or protocol funds and can also permanently freeze funds intended for a user's escrow (since the dispatcher never returns unswept assets to the order owner).

### Likelihood Explanation
Reaching this path requires only: (1) an order whose predispatch/postdispatch calldata leaves any token balance on the dispatcher that is outside the declared `order.inputs`/output list (a normal usage pattern the docs explicitly call out — LP unwrapping, multi-hop swaps), and (2) a single unprivileged call to `CallDispatcher.dispatch()`. No proof, no privileged role, and no cross-chain message is required — it is directly reachable from a single transaction by any address, at any time after the stranded balance appears.

### Recommendation
- Add access control to `CallDispatcher.dispatch()` restricting callers to the configured `IntentGatewayV2` (or another explicitly authorized caller), OR
- Deploy a fresh, single-use `CallDispatcher` instance per order (e.g., via CREATE2 keyed to the commitment) rather than sharing one dispatcher across all orders, so no cross-order/cross-user balance can ever accumulate there, and
- After executing predispatch/postdispatch calls, sweep *all* token balances the dispatcher ends up holding (not only the ones declared in `order.inputs`/outputs) back to the gateway or to the order owner, so nothing is ever left unclaimed on the shared contract.

### Proof of Concept
1. A user places an order whose `predispatch.call` unwraps an LP token into `TokenA` and `TokenB`, but `order.inputs` only lists `TokenA` (a legitimate use case per the documented "unwrapping LP tokens" flow). [2](#0-1) 
2. `placeOrder` runs the predispatch call, then sweeps only `TokenA` out of the dispatcher into escrow: [5](#0-4) 
3. `TokenB`'s balance is now sitting on the shared `CallDispatcher` contract, unaccounted for by `IntentGatewayV2`.
4. Any attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: TokenB, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, TokenB.balanceOf(dispatcher))})]))` directly — this succeeds because `dispatch()` has no caller restriction: [6](#0-5) 
5. The attacker walks away with `TokenB`, which was never returned to the order owner nor credited to the protocol.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L185-187)
```text
     * 3. If the order includes predispatch calldata, executes it via the CallDispatcher
     *    (e.g., unwrapping LP tokens) before escrowing the resulting balances.
     * 4. Otherwise, transfers input tokens directly from the caller into escrow.
```

**File:** evm/src/apps/IntentGatewayV2.sol (L258-290)
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

```

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
