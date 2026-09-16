### Title
`CallDispatcher.dispatch()` has no caller restriction, letting anyone drain any ETH/ERC20 balance temporarily or residually held by the shared dispatcher - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
The external report describes Ruby's `Net::FTP` blindly trusting an attacker/peer-supplied address (the PASV response) to decide where to "connect back to," letting an unauthenticated party redirect the client's outbound action. The structurally equivalent bug class here is a component that executes an externally supplied "destination + payload" instruction without verifying who is allowed to invoke it. `CallDispatcher.dispatch(bytes)` in `evm/src/utils/CallDispatcher.sol` is exactly that: it decodes an arbitrary `Call[]` and blindly `to.call{value: call.value}(call.data)`s to any attacker-chosen `to` with any attacker-chosen `value`/`data`, and the function carries **no `msg.sender` check at all**.

### Finding Description
`CallDispatcher` is a shared, singleton utility contract used by multiple production apps — `HyperFungibleToken`/`HyperFungibleTokenUpgradeable`, `WrappedHyperFungibleToken(Upgradeable)`, and `IntentsBase`/`IntentGatewayV2` — to execute arbitrary calldata attached to cross-chain messages or solver-filled orders: [1](#0-0) 

```solidity
function dispatch(bytes memory encoded) external {
    Call[] memory calls = abi.decode(encoded, (Call[]));
    ...
    (bool success, bytes memory result) = to.call{value: call.value}(call.data);
    if (!success) revert CallFailed(to, result);
}
```

There is no `onlyHost`, `onlyApp`, or any access-control modifier on `dispatch`. Any external account can call it directly with an arbitrary `Call[]`, bypassing the intended flow where only `onAccept` (gated by `onlyHost`) or `IntentsBase._execute` are supposed to invoke it. [2](#0-1) , the `receive() external payable {}` fallback, means the contract can and does accumulate ETH.

This becomes exploitable because `CallDispatcher` transiently and sometimes persistently holds funds:
- `IntentsBase._execute` first dispatches the solver-supplied `order.output.call` through the shared dispatcher, and only afterward issues a second `dispatch()` call to sweep any residual ETH/ERC20 "dust" back to `IntentsBase`: [3](#0-2) 
- Between the first and second `dispatch()` calls (and any time dust is left over because `outputsLen` didn't cover every asset, or a solver's own external call leaves residue), the dispatcher contract genuinely holds a spendable ETH/ERC20 balance.
- Because `dispatch()` is public and unrestricted, any unprivileged actor (or the solver-controlled contract invoked inside the first `dispatch()` call, which can reenter `dispatch()` before `IntentsBase`'s own sweep runs) can call `CallDispatcher.dispatch()` directly with a `Call[]` that transfers that balance to itself, stealing dust/funds before the legitimate sweep executes.
- Since the dispatcher is shared across `HyperFungibleToken`, `WrappedHyperFungibleToken`, and the intents apps, any ETH sent to it (deliberately or accidentally, e.g. via `receive()`) from any of these flows is equally exposed to any caller, not just the app that funded it.

This mirrors the CVE's root cause: a component that performs a sensitive "connect/execute" action driven by an externally supplied target, with no check that the invocation is coming through the trusted, authenticated channel.

### Impact Explanation
Any unprivileged address can call `CallDispatcher.dispatch()` to move out ETH/tokens currently held by the dispatcher — including funds temporarily parked there mid-execution by `IntentsBase._execute` while filling an intent/order (escrowed order funds routed through the CallDispatcher for composable DeFi execution), or accumulated ETH from its unconditional `receive()`. This is concrete theft of funds reachable from a single order-fill/dispatch transaction, satisfying the "concrete theft ... of funds" bar.

### Likelihood Explanation
High likelihood for the dust/residual case: `IntentsBase._execute` explicitly documents that "any residual token balances left on the dispatcher are swept back," acknowledging balances are expected to sit there between calls — and that window is trivially reachable by any address, including a malicious solver's own callee contract, which can simply call `CallDispatcher.dispatch()` in the same transaction before the legitimate sweep executes. No privileged role or forged proof is required — only a normal `fillOrder`/order-execution flow that leaves any non-zero ETH/token balance on the dispatcher momentarily.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the authorized apps that are meant to use it (e.g., an allowlist of `IntentsBase`/`HyperFungibleToken` instances, or make each app deploy its own dispatcher instance instead of sharing one), and/or ensure the dispatcher never carries a balance across calls (transfer any residual value out atomically within the same call rather than relying on a follow-up `dispatch()` invocation that any third party could preempt).

### Proof of Concept
1. A solver fills an intent via `IntentGatewayV2`/`IntentsBase.fillOrder`, with `order.output.call` set to a benign or attacker-influenced sequence that leaves ETH or an ERC20 balance on the shared `CallDispatcher` (e.g., a swap that returns slightly more than consumed, or a call that intentionally sends value to the dispatcher).
2. Inside the callee invoked by the first `dispatch()` call (attacker-controlled contract chosen as one of `order.output.call`'s `to` targets), reenter `CallDispatcher.dispatch()` directly with a `Call[]` of `{to: attacker, value: dispatcher.balance, data: ""}`.
3. Because `dispatch()` has no caller restriction, this reentrant/parallel call succeeds and transfers the dispatcher's balance to the attacker before `IntentsBase._execute`'s own sweep call runs, draining funds intended to be returned to `IntentsBase` as protocol dust.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-544)
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
```
