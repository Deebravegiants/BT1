## Title
Unrestricted `CallDispatcher.dispatch()` allows anyone to drain any token/ETH balance stranded in the shared dispatcher contract — ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher` is a single, permanently deployed, shared contract used by `IntentGatewayV2` (predispatch/postdispatch order execution) and `HyperFungibleToken`/`WrappedHyperFungibleToken` (calldata-on-receive) to execute arbitrary calls on behalf of orders and cross-chain deliveries. Its `dispatch` function has **no caller restriction whatsoever** and simply executes whatever `Call[]` it is given, with whatever value/calldata is supplied, against any target. Because tokens are routinely (and sometimes unavoidably, e.g. fee-on-transfer tokens, rounding, or accidental direct transfers to its well-known, documented address) left temporarily or permanently on this contract's balance, any unprivileged caller can call `dispatch()` directly with a `Call` that transfers out the dispatcher's entire current token or ETH balance to an address of their choosing. This is the same bug class as the UNCX report: a function moves the *entire* balance of the contract (rather than only the amount belonging to the specific in-flight operation) to a caller-controlled destination.

### Finding Description
`CallDispatcher.dispatch` is defined with no access control: [1](#0-0) 

There is no `onlyGateway`, `onlyHost`, or `msg.sender` check of any kind — any EOA or contract can call it directly on-chain.

The contract is a shared, persistent singleton (deployed once via CREATE2 and reused across every order and HFT deployment on a chain), and it is *designed* to temporarily hold token/ETH balances:
- `IntentGatewayV2.placeOrder` transfers `predispatch.assets` to the dispatcher, then calls `dispatch(order.predispatch.call)`: [2](#0-1) 
- `HyperFungibleToken`/`WrappedHyperFungibleToken` mint/unlock tokens directly to the dispatcher's address (per documented usage, so attached calldata can spend them) and then call `dispatch(message.data)`: [3](#0-2) 

Because `dispatch` places no constraint on which calls can be made or what fraction of the dispatcher's balance they may move (it simply forwards `call.value`/`call.data` to `call.to`), any residual balance left on the dispatcher — from fee-on-transfer tokens, partial swap execution (e.g. `swapExactTokensForTokens` consuming less than the full approved/minted amount), rounding, a reverted-and-retried delivery, or a user mistakenly sending tokens straight to the dispatcher's publicly documented address — becomes permissionlessly extractable. An attacker simply calls `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, token.balanceOf(dispatcher))})]))` to sweep it to themselves. The same applies to any stray ETH via `Call({to: attacker, value: address(dispatcher).balance, data: ""})`.

This mirrors the UNCX root cause precisely: the vulnerable operation (`_convertPositionToFullRange` there, `dispatch` here) acts on the contract's *entire* balance rather than only the amount tied to the specific caller/operation, and the caller fully controls the destination of that swept balance.

### Impact Explanation
Any tokens or native ETH transiently or accidentally held by the `CallDispatcher` — which multiple production flows (`IntentGatewayV2` predispatch/postdispatch, `HyperFungibleToken` calldata-on-receive) are explicitly designed to place there before calling `dispatch` — can be permanently stolen by any unprivileged third party monitoring the chain. This is a direct theft-of-funds vector reachable from a single unauthenticated transaction, with no privileged role required, satisfying the "concrete theft of funds" bar.

### Likelihood Explanation
The likelihood is high: the dispatcher's address is documented and intentionally used as a token-receiving address by integrators (per the HFT calldata-execution docs), fee-on-transfer or amount-mismatch scenarios naturally leave dust, and an attacker only needs to watch the dispatcher's balance and race to call `dispatch()` — a trivial, cheap, and repeatable attack requiring no special access, timing precision beyond normal front-running, or privileged role.

### Recommendation
Restrict `CallDispatcher.dispatch` to only be callable by the specific caller that funded it within the same transaction context, or redesign so the dispatcher never holds discretionary residual balance across calls — e.g., make it a minimal, ephemeral per-call proxy (deployed and destroyed within a single transaction), require an `onlyAuthorizedCaller` allowlist (e.g., only registered `IntentGatewayV2`/HFT instances may invoke `dispatch`), and/or have those callers sweep back any un-consumed balance to themselves atomically within the same transaction rather than relying on `dispatch`'s target calls to do so. At minimum, add a reentrancy-safe balance check ensuring `dispatch` cannot be invoked by an address other than the intended gateway/token contract.

### Proof of Concept
1. A `HyperFungibleToken` transfer-and-swap message is delivered where the attached DEX call only partially consumes the minted amount (e.g., a fee-on-transfer output token, or `swapTokensForExactTokens` with slack), leaving residual token balance on `CallDispatcher`.
2. Attacker calls `CallDispatcher.dispatch` directly (no relationship to any gateway) with:
```solidity
Call[] memory calls = new Call[](1);
calls[0] = Call({
    to: leftoverToken,
    value: 0,
    data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, IERC20(leftoverToken).balanceOf(address(dispatcher)))
});
dispatcher.dispatch(abi.encode(calls));
```
3. `CallDispatcher` executes the call as-is (no caller check), transferring the entire stranded balance to `attacker`. [1](#0-0)

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

**File:** evm/src/apps/IntentGatewayV2.sol (L234-258)
```text
        uint256 msgValue = msg.value;
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/hyper-fungible-token.mdx (L149-162)
```text
IHyperFungibleToken(tokenAddress).send{value: nativeFee}(
    IHyperFungibleToken.SendParams({
        dest: StateMachine.evm(42161),
        // mint to the CallDispatcher so the swap can spend the tokens
        to: abi.encodePacked(CALL_DISPATCHER),
        amount: amount,
        timeout: 3600,
        relayerFee: relayerFee,
        data: abi.encode(calls)
    })
);
```

Tokens are minted to `to` first, then the `CallDispatcher` executes each call in sequence. If the calls need to spend the minted tokens, set `to` to the `CallDispatcher` address so tokens are minted directly to the dispatcher.
```
