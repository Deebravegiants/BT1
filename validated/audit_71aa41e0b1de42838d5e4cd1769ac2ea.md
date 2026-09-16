## Confirmed root cause

The `CallDispatcher` (`evm/src/utils/CallDispatcher.sol:44-62`) is a shared, permissionless utility contract used by `IntentGatewayV2`/`IntentsBase` (predispatch and postdispatch flows) and by `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution:

```solidity
function dispatch(bytes memory encoded) external {
    Call[] memory calls = abi.decode(encoded, (Call[]));
    ...
    (bool success, bytes memory result) = to.call{value: call.value}(call.data);
    if (!success) revert CallFailed(to, result);
}
``` [1](#0-0) 

There is no `onlyGateway`/`onlyOwner`/allowlist check — **any address** can call `dispatch()` with an arbitrary `Call[]` and move any ETH/ERC20 balance currently held by this shared contract to any recipient.

Both the predispatch and postdispatch/"execute" flows only sweep back the tokens explicitly declared in the order (`order.inputs[]` or `order.output.assets[]`), not "whatever the arbitrary calldata actually produced":

- Predispatch sweep only iterates `inputsLen` (`order.inputs[i].token`) and sweeps the entire `dispatcher` balance of just those tokens: [2](#0-1) 

- Postdispatch sweep (`_execute`) only iterates `outputsLen` (`order.output.assets[i].token`): [3](#0-2) 

If the predispatch/postdispatch calldata (e.g., a multi-hop swap/aggregator route) returns an additional, non-terminal token that is **not** in `order.inputs[]` / `order.output.assets[]` — exactly the Balancer `batchSwap` intermediate-token scenario from the report — that token is never swept and is left stranded in the shared `CallDispatcher`. Because `dispatch()` has no access control, that stranded balance can subsequently be drained by **any unrelated third party**, not just the gateway.

I could not fully verify (index limits) whether `_params.dispatcher` is a single globally-shared instance across all gateway deployments/networks or deployed per-gateway; the docs state "Existing `CallDispatcher` deployments are listed on the contract addresses page," implying a small number of long-lived shared instances reused across many orders, which is what makes accumulated dust theft practically relevant. This uncertainty affects blast radius but not the core root cause.

### Title
Unaccounted intermediate tokens from predispatch/postdispatch calldata become permanently stealable via the unauthenticated `CallDispatcher.dispatch()` - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`IntentGatewayV2`/`IntentsBase` only sweep back the tokens explicitly named in `order.inputs[]` (predispatch) or `order.output.assets[]` (postdispatch) after routing arbitrary calldata through the shared `CallDispatcher`. Any intermediate/extra token produced by that calldata — analogous to Balancer's `batchSwap` returning non-final tokens — is never swept and remains stranded in `CallDispatcher`. Since `CallDispatcher.dispatch()` has no access control, any external address can later call it directly to sweep that stranded balance to themselves.

### Finding Description
`placeOrder` with a `predispatch.call` moves user assets to `CallDispatcher`, executes arbitrary calldata via `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`, then sweeps back only the tokens matching `order.inputs[i].token`: [2](#0-1) 

Similarly, `_execute` (used for both same-chain full-fill and cross-chain postdispatch calldata) runs `order.output.call` via the same `CallDispatcher` and only sweeps balances for tokens in `order.output.assets`: [3](#0-2) 

Neither sweep loop performs a generic "sweep everything the dispatcher holds" pass; both are keyed to a fixed, order-declared token list, exactly the pattern flagged in the report ("only accounts for receipt of the final token…other tokens received…will not be registered"). Any token that a predispatch/postdispatch DEX route or multi-hop swap returns as a byproduct — but that isn't one of the declared input/output tokens — sits in the `CallDispatcher` indefinitely.

Critically, `CallDispatcher.dispatch()` itself is a fully public, unauthenticated function: [1](#0-0) 

Because the same `CallDispatcher` deployment is shared across many orders/gateways, once any dust/extra token accumulates there from an incompletely-swept flow, **any address** can call `dispatch()` directly with a `Call[]` that transfers that balance out — no relation to the original order or gateway is required. This converts a bookkeeping gap (unaccounted non-terminal tokens) into outright theft by an arbitrary third party, since the funds are sitting in a shared, permissionless contract rather than in per-order escrow.

### Impact Explanation
Stranded token balances in the shared `CallDispatcher` (from swaps/routes producing tokens outside the order's declared input/output list) are permanently unrecoverable by their rightful owner (the order placer or beneficiary) and are freely stealable by any unprivileged actor who notices the balance and calls `dispatch()`. This is a concrete theft/permanent-freezing-of-funds vector reachable from ordinary user-submitted transactions (placing or filling an order with calldata that yields a non-listed token), matching the "unauthorized app action" / fund-theft acceptance criteria.

### Likelihood Explanation
Likelihood depends on solvers/users routing predispatch or postdispatch calldata through multi-hop swaps, aggregators, or any DeFi primitive that can return more than one output token (the same class of interaction Balancer's `batchSwap` enables) — a realistic and encouraged use case per the docs ("solvers can route through DEXes, lending protocols, or other DeFi primitives as part of filling an order"). Once such dust exists, exploitation by a third party requires only a single unauthenticated call to `CallDispatcher.dispatch()`, with no special privileges.

### Recommendation
1. Add access control to `CallDispatcher.dispatch()` so only the calling gateway/app contract (or an allowlisted set of callers) can invoke it, preventing arbitrary third parties from ever draining its balance.
2. Replace the fixed, order-declared sweep lists in `IntentGatewayV2.sol` (predispatch) and `IntentsBase._execute` (postdispatch) with a generic sweep that returns *all* residual token balances left on the dispatcher after arbitrary calldata execution — not just the tokens named in `order.inputs`/`order.output.assets` — emitting `DustCollected` for any token not already part of the expected set, mirroring the recommended fix pattern (account for every asset actually moved, not just the "final" expected ones).

### Proof of Concept
1. User places an order with `predispatch.call` that swaps ETH for USDC via a multi-hop path that also yields a small leftover WETH balance sent to the `CallDispatcher`, while `order.inputs[]` only lists USDC.
2. `placeOrder` executes the predispatch call, then sweeps only the USDC balance back to the gateway (`evm/src/apps/IntentGatewayV2.sol:258-299`); the WETH remains in `CallDispatcher`.
3. Any third-party address (no relation to the order) calls `CallDispatcher.dispatch(abi.encode([Call({to: WETH, value:0, data: transfer(attacker, wethBalance)})]))` directly — this succeeds because `dispatch()` has no caller restriction (`evm/src/utils/CallDispatcher.sol:44-62`) — and the attacker walks away with the stranded WETH.
4. The same pattern applies to `_execute`'s postdispatch sweep in `IntentsBase.sol:498-533` for any output-side calldata that yields a token outside `order.output.assets`.

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
