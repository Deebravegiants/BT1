## Finding

### Title
`CallDispatcher.dispatch` is callable by anyone, letting an attacker drain any token/ETH balance stranded in the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
CVE-2020-24140 is an SSRF where an unauthenticated `pagename` parameter lets an outside caller force a backend component to issue arbitrary requests using the backend's own network position/privileges. The structural analog in Hyperbridge is `CallDispatcher.dispatch()` [1](#0-0) : it is a fully public, unrestricted "proxy" that will execute *any* attacker-supplied `Call[]` (arbitrary `to`, `value`, `data`) using whatever native ETH or token balance the `CallDispatcher` contract happens to hold at that moment - exactly like an SSRF endpoint that forwards attacker-chosen requests using the server's own trust/resources.

### Finding Description
`CallDispatcher` is a shared, singleton "untrusted call executor" wired as `_params.dispatcher`/`_dispatcher` into `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` [2](#0-1) . During normal flows, tokens or ETH are transferred to the `CallDispatcher` address immediately before `dispatch()` is invoked to route them (predispatch/postdispatch calldata execution, calldata-triggered swaps, etc.) [3](#0-2) .

The `dispatch()` function itself has **no access control** - no `onlyGateway`, `onlyHost`, or any `msg.sender` check:

```solidity
function dispatch(bytes memory encoded) external {
    Call[] memory calls = abi.decode(encoded, (Call[]));
    ...
    (bool success, bytes memory result) = to.call{value: call.value}(call.data);
    if (!success) revert CallFailed(to, result);
}
``` [1](#0-0) 

Because the contract also has a bare `receive() external payable {}` [4](#0-3) , it can accumulate a balance. `IntentsBase._execute` explicitly documents that "any tokens remaining in the CallDispatcher are swept back" only for the tokens listed in `order.output.assets` [5](#0-4)  — any token routed into the dispatcher by attacker-controlled `predispatch.call` / `output.call` calldata that is *not* one of the tracked output assets is never swept and is permanently left sitting in the dispatcher's balance.

Since `dispatch()` has no caller restriction, any unprivileged address can, in a completely separate transaction, call `CallDispatcher.dispatch()` directly with a `Call[]` that transfers out any stranded ERC20/ETH balance to themselves — regardless of which app (IntentGatewayV2, HyperFungibleToken, WrappedHyperFungibleToken) originally routed the funds there. This mirrors the SSRF class exactly: an internal-only utility meant to be invoked solely by a trusted caller (the gateway/token contract, analogous to the "back-end server") is instead reachable directly by any external, unauthenticated party, who can force it to reach out to and move value at arbitrary targets it should not otherwise be able to touch.

### Impact Explanation
Any dust, fee-on-transfer residue, wrongly-swept tokens, or intermediate balances that ever land in the shared `CallDispatcher` (a documented and expected occurrence per `_execute`'s own comments) can be permanently stolen by any address, since the function that moves the dispatcher's balance is public with no caller restriction. This is concrete theft of funds reachable by any unprivileged actor with a single transaction, not requiring any privileged role, matching the "concrete theft ... of funds" bar.

### Likelihood Explanation
Likelihood is high: the dispatcher is a shared, persistently deployed contract used across multiple production apps (`IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken`), so it is realistic for tokens/ETH to be routed to it via any order's `predispatch`/`output` calldata or a token transfer's `data` field. Since `dispatch()` requires no permission, exploitation is a single, trivial, always-available transaction by any address, at any time the dispatcher holds a non-zero balance.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the authorized caller(s) that are expected to route funds through it (e.g., an `onlyAuthorized`/allow-listed caller mapping configured per deploying app, or make `CallDispatcher` a non-shared, per-app instance with an immutable owner check), and/or ensure the contract never holds a residual balance across transactions by sweeping *all* balances (not just tracked `output.assets`) back to a safe owner at the end of every dispatch sequence.

### Proof of Concept
1. A user places an `IntentGatewayV2` order whose `predispatch.call` or `output.call` routes some token `X` (not listed in `order.output.assets`) into the shared `CallDispatcher`, e.g. via a swap that returns two tokens but only one is declared as an output asset.
2. `_execute`/predispatch flow sweeps only the declared output/input assets back to the gateway; token `X`'s balance remains in `CallDispatcher` [3](#0-2) .
3. Any attacker, in a separate transaction, calls:
```solidity
CallDispatcher(dispatcherAddr).dispatch(
    abi.encode([Call({to: address(X), value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, X.balanceOf(dispatcherAddr))})])
);
```
4. Because `dispatch()` performs no `msg.sender` check [1](#0-0) , this call succeeds and transfers the stranded token balance to the attacker.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-39)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
```

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

**File:** sdk/packages/core/contracts/interfaces/ICallDispatcher.sol (L26-37)
```text
/**
 * @title The ICallDispatcher
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @notice This interface is used to dispatch untrusted call(s)
 */
interface ICallDispatcher {
    /*
     * @dev Dispatch the encoded call(s)
     */
    function dispatch(bytes memory params) external;
}
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L487-497)
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
