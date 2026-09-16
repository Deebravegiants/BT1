## Analysis Result

### Title
Unauthenticated `CallDispatcher.dispatch()` lets anyone drain tokens/approvals transiting the shared dispatcher used by IntentGatewayV2 and HyperFungibleToken - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single, shared, permissionless executor contract reused across `IntentGatewayV2`/`intentsv2` (predispatch and postdispatch calldata) and the `HyperFungibleToken`/`WrappedHyperFungibleToken` contracts (cross-chain calldata execution). Its `dispatch()` entrypoint has no access control, so any address — not just the gateway or token contract that is supposed to own the current flow — can invoke it directly and operate on whatever token balance or standing approval the dispatcher happens to hold at that moment.

### Finding Description
`CallDispatcher.dispatch()` is declared `external` with no caller restriction: [1](#0-0) 

It executes the supplied `Call[]` with a plain `.call{value}(data)` (not `delegatecall`), so any token transfer or approval performed inside `dispatch()` is made *from the CallDispatcher's own identity/balance*. This is the same "shared executor holding value" pattern flagged in the external report, except worse: the report's `MetaSwap`/`Spender` risk requires a *newly added adapter* to be malicious, whereas here the unrestricted `dispatch()` function is reachable by any caller from day one, with no adapter registration step at all.

`CallDispatcher` is used as a single shared instance across the protocol:
- `IntentGatewayV2.placeOrder` transfers `predispatch.assets` into the dispatcher and then calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` before sweeping the result back into escrow: [2](#0-1) 
- `IntentsBase._execute` (used for both same-chain and cross-chain postdispatch fills) invokes `dispatch()` on the same shared `_params.dispatcher`, then sweeps back only the balances of the tokens explicitly listed in `order.output.assets`: [3](#0-2) 
- `WrappedHyperFungibleTokenUpgradeable.onAccept` also forwards arbitrary cross-chain calldata to the same kind of `_dispatcher` after minting/unlocking tokens to it: [4](#0-3) 

Real order flows routinely leave standing, unrevoked approvals on the CallDispatcher to third-party routers. The project's own test suite constructs a postdispatch flow that approves a Uniswap router for `type(uint256).max` directly from the dispatcher: [5](#0-4) 

and the documentation for the HFT `CallDispatcher` explicitly acknowledges the danger: *"Token approvals in the Call[] should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution."* [6](#0-5) 

Because the dust-sweep logic in `_execute` only reclaims the specific tokens declared in `order.output.assets`/`predispatch.assets` — not an open-ended balance check — any token that legitimately or accidentally ends up on the dispatcher outside that expected list (slippage residue, a byproduct token from a swap, a race between two flows using the same instance) is left sitting on a contract whose `dispatch()` any address can call to move it out (`token.transfer(attacker, balance)`), or to exercise any router allowance that was left approved from a prior order's calldata.

### Impact Explanation
Any leftover token balance or standing approval on the shared `CallDispatcher` is directly stealable by an unprivileged third party calling `dispatch()` themselves, since the function performs the call as the dispatcher and has zero access control. This is concrete theft of funds transiting the dispatcher on behalf of users/solvers across both the Intent Gateway and HyperFungibleToken flows — a single shared, unauthenticated executor contract is a much larger blast radius than the "new adapter" scenario from the source report, because it requires no governance action or new deployment to exploit.

### Likelihood Explanation
Exploitability requires only that some token/allowance ends up (even transiently) attached to the dispatcher outside the exact set the sweep logic checks — plausible via slippage in predispatch/postdispatch swaps, byproduct tokens, or `type(uint256).max` approvals left to external routers (a pattern the codebase's own tests exercise). No privileged role, adapter registration, or governance compromise is needed — a bare, unprivileged call to `dispatch()` is sufficient, satisfying the "unprivileged... reach" requirement.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the trusted contracts that are supposed to own the current execution context (e.g., an `onlyAuthorizedCaller` modifier checking `msg.sender` against `IntentGatewayV2`/`HyperFungibleToken` deployments), or move to a per-call ephemeral executor (a minimal proxy/clone deployed per dispatch and self-destructed/never reused) so no state (balance or approval) can persist between unrelated calls. At minimum, ensure every `Call[]` that grants an approval also revokes it (or use `forceApprove`-then-zero patterns) within the same `dispatch()` invocation, and broaden the sweep logic in `_execute`/`placeOrder` to reclaim any non-zero balance of any token actually touched by the predispatch/postdispatch calls rather than only the declared input/output token set.

### Proof of Concept
1. A user's `placeOrder` predispatch swap (or a solver's postdispatch swap) leaves a small residual balance of an unexpected token on the shared `CallDispatcher` (e.g., a reward token from a router, or dust below the exact output amount the sweep loop checks for).
2. An attacker observes the dispatcher's balance (it is a single well-known, permanently deployed address referenced by `_params.dispatcher`) and calls `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, residualBalance)})]))` directly.
3. Since `dispatch()` has no caller restriction and executes as the dispatcher itself, the residual tokens are transferred to the attacker with no reversion, regardless of which order/flow originally left them there.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L235-258)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-528)
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
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L355-357)
```text
        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L1358-1363)
```text
        // Call 1: Approve Uniswap router
        postdispatchCalls[0] = Call({
            to: address(usdc),
            value: 0,
            data: abi.encodeWithSelector(IERC20.approve.selector, uniswapRouter, type(uint256).max)
        });
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L90-96)
```text
The `data` field is an ABI-encoded `Call[]` array, where each `Call` specifies a target contract, a native value to forward, and the calldata to execute. On the destination chain, the HFT contract mints or unlocks tokens to the `to` address, then forwards the entire `data` payload to the `CallDispatcher`, which executes each call sequentially. If the calls need to spend the bridged tokens (e.g., approve then swap), set `to` to the `CallDispatcher` address so tokens are delivered directly to it.

For code examples, see the [HyperFungibleToken](/developers/evm/hyper-fungible-token/hyper-fungible-token#calldata-execution) and [WrappedHyperFungibleToken](/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token#calldata-execution) pages.

### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.
```
