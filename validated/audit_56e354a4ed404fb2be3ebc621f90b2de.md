`CallDispatcher.dispatch()` maps directly onto the FiberRouter bug class: an unrestricted, publicly reachable function that performs arbitrary external calls (attacker-controlled `to`/`data`) using the calling contract's own identity/assets, with no check on `msg.sender` or on which assets it may currently be holding.

### Title
Unrestricted, permissionless `CallDispatcher.dispatch()` allows anyone to drain any ETH/token balance or exploit standing approvals held by the shared dispatcher - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher` is a single shared, protocol-wide utility contract used by `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` to execute attacker/user-supplied `Call[]` batches (predispatch, postdispatch, and cross-chain calldata execution). [1](#0-0)  Its `dispatch(bytes memory encoded)` function is `external` with no caller restriction whatsoever — it is expected to be invoked only by the trusted gateway/token contracts as part of an atomic sequence, but the code enforces no such restriction. [2](#0-1)  This is structurally identical to the FiberRouter flaw: a contract that forwards arbitrary `to`/`data` to an external `.call()` without validating who may trigger it or what it may be used to reach, letting an attacker command the contract's own balance/approvals.

### Finding Description
`CallDispatcher.dispatch()` decodes a caller-supplied `Call[]` array and executes each `to.call{value: call.value}(call.data)` in the dispatcher's own context (not delegatecall), the only checks being that `to` has code and that the sub-call succeeds. [3](#0-2)  There is no `onlyGateway`/`onlyOwner`/allow-list check on `msg.sender`, and the contract additionally exposes a permissionless `receive()` that accepts ETH from anyone. [4](#0-3) 

The dispatcher is documented and used as a shared singleton across the Intent Gateway (predispatch/postdispatch swap flows) and the Hyper Fungible Token contracts (mint-then-call on receive), each of which routinely gives the dispatcher a temporary token/ETH balance and, in normal usage, sets ERC20 approvals from the dispatcher to external routers as part of composable swap flows. Tests demonstrate orders explicitly setting `type(uint256).max` approvals from the dispatcher to a router as part of postdispatch calldata. [5](#0-4)  The dust-sweep logic that is supposed to clear residual balances runs as a second, separate `dispatch()` call issued by `IntentsBase._execute` right after the main calldata dispatch, within the same transaction. [6](#0-5) 

Because `dispatch()` itself has no access control, any of the following give an unprivileged actor a direct drain path:
- Any ETH sitting in the dispatcher (from `Call.value` remainders, e.g. `WrappedHyperFungibleToken`'s pattern of forwarding native ETH via `Call.value` to a router, or accidental/forced sends via `receive()`) can be swept by anyone calling `dispatch()` with `Call({to: attacker, value: dispatcher.balance, data: ""})`.
- Any ERC20 token balance left on the dispatcher between the main `dispatch()` call and the follow-up sweep `dispatch()` call (e.g., via reentrancy from a malicious `Call.to` target invoked mid-batch, or any edge case where the sweep loop in `_execute` does not account for every token actually received) is directly stealable via `Call({to: token, data: transfer(attacker, balance)})`, since `msg.sender` for that transfer would be the dispatcher itself.
- Standing infinite/large approvals set by legitimate order calldata (like the `type(uint256).max` pattern in tests) to routers remain valid indefinitely; if the dispatcher later holds a balance of that approved token again (through any other flow using the same shared dispatcher), any external caller can call `dispatch()` directly, bypassing the owning gateway entirely, to trigger the approved router to move dispatcher-held funds to an attacker-chosen recipient.

This is the same root cause as the FiberRouter exploit: an externally-reachable function that performs unrestrained arbitrary calls using the contract's own funds/approvals, without validating the caller or the call's legitimacy.

### Impact Explanation
Any residual ETH or ERC20 balance held by the shared `CallDispatcher` — across all apps that use it (IntentGatewayV2, HyperFungibleToken, WrappedHyperFungibleToken) — is permanently and permissionlessly stealable by any address, at any time, with a single call. Because the dispatcher is shared infrastructure and standing approvals to external routers can be established as an ordinary part of normal calldata flows (as shown in the test suite), the blast radius includes funds from unrelated orders/users that happen to transiently pass through or leave approvals on the same dispatcher instance. This constitutes concrete theft of funds reachable from a single unprivileged transaction.

### Likelihood Explanation
Exploitation requires no privileges and no cooperation from the gateway contracts — an attacker simply calls `CallDispatcher.dispatch()` directly. The precondition (dispatcher holding a nonzero balance or standing approval) is realistic: `Call.value` remainders, `receive()` accepting arbitrary ETH, and calldata-driven `approve(router, type(uint256).max)` patterns are all present in documented/tested usage of the dispatcher today.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by an explicit allow-list of authorized gateway/token contracts (e.g., an `onlyAuthorizedCaller` modifier configured per deployment), add a reentrancy guard, and ensure no ETH/token balance or non-zero approval is ever left standing on the dispatcher after a batch completes (revert if post-execution balance changed unexpectedly for uninvolved tokens, and require exact-amount approvals instead of unlimited ones).

### Proof of Concept
1. Wait for (or induce, e.g., via a `Call.value` remainder or `receive()` donation) any ETH or ERC20 balance to exist on the shared `CallDispatcher` contract.
2. As any unprivileged address, call `CallDispatcher.dispatch(abi.encode(calls))` directly (bypassing `IntentGatewayV2`/`HyperFungibleToken` entirely) with `calls = [Call({to: <token or attacker>, value: <balance>, data: <transfer(attacker, balance) or "">})]`.
3. The call succeeds because `dispatch()` performs no caller check [3](#0-2) , transferring the dispatcher's balance to the attacker.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L15-25)
```text
pragma solidity ^0.8.17;

import {ICallDispatcher, Call} from "@hyperbridge/core/interfaces/ICallDispatcher.sol";

/**
 * @title The CallDispatcher
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @notice This contract is used to dispatch calls to other contracts.
 */
contract CallDispatcher is ICallDispatcher {
```

**File:** evm/src/utils/CallDispatcher.sol (L37-39)
```text
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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L1358-1363)
```text
        // Call 1: Approve Uniswap router
        postdispatchCalls[0] = Call({
            to: address(usdc),
            value: 0,
            data: abi.encodeWithSelector(IERC20.approve.selector, uniswapRouter, type(uint256).max)
        });
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```
