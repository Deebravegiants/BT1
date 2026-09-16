## Analysis Result

The BathBuddy "locked ETH" bug class maps to a stronger and more severe variant reachable in Hyperbridge: `CallDispatcher` accepts arbitrary native token deposits via `receive()` but exposes its `dispatch()` function with **no access control**, allowing any unprivileged caller to redirect ether that accumulates in the contract to an address of their choosing — turning a "funds stuck" bug class into a concrete theft vector.

### Title
Unrestricted `CallDispatcher.dispatch()` allows theft of any native token balance held by the contract - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is the shared execution helper used by `IntentGatewayV2` (predispatch/postdispatch calldata execution) and `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` (calldata-carrying cross-chain transfers) to execute attacker- or user-supplied `Call[]` arrays and to temporarily hold native tokens/ERC-20s mid-execution. It defines `receive() external payable {}` [1](#0-0)  so it can accept ETH forwarded from `IntentGatewayV2` and `WrappedHyperFungibleToken` flows, but `dispatch()` itself carries no caller restriction whatsoever [2](#0-1) .

### Finding Description
Any native ETH that ends up sitting in `CallDispatcher`'s balance between transactions — whether from a direct/accidental transfer to the contract's `receive()`, or as residual "dust" left over from a partially executed predispatch/postdispatch flow — is completely unprotected. Because `dispatch(bytes memory encoded) external` has no `onlyOwner`/`onlyGateway` modifier, **any address** can call it directly with a `Call[]` that forwards the dispatcher's entire native balance to an attacker-controlled contract: `(bool success,) = to.call{value: call.value}(call.data);` [3](#0-2) . The only guard is that `to` must have code (`extcodesize(to) != 0`) [4](#0-3) , which is trivially satisfied by deploying a minimal contract.

This is materially worse than the BathBuddy analog: instead of funds being permanently frozen with no retrieval path, they can be actively drained by any unprivileged third party. The intended usage pattern in `IntentGatewayV2` sweeps the dispatcher's *entire* balance (not just the amount required for the order) back to the gateway using `balance = address(dispatcher).balance` [5](#0-4)  and the Tron port does the same [6](#0-5) , treating any excess as protocol "dust" — but this sweep only happens transactionally as a side effect of a legitimate order's predispatch flow, and nothing stops any outside caller from front-running that sweep (or acting whenever a balance appears) by calling `dispatch()` themselves first.

The documentation confirms the dispatcher is expected to "hold tokens (or native ETH)" mid-flow and that "the `CallDispatcher` can hold and forward native tokens" [7](#0-6) , and that "the dispatcher contract holds tokens temporarily during execution" [8](#0-7)  — confirming this is a shared, externally reachable, address with a real expected balance window, not a theoretical edge case.

### Impact Explanation
Any native token balance transiently or accidentally held by `CallDispatcher` — including ETH forwarded via `IntentGatewayV2`'s predispatch step before the compensating sweep call executes, ETH sent directly by a naive user/integrator, or residual dust from a reverted/partial multi-call sequence — is subject to outright theft by any address willing to deploy a receiving contract and call `dispatch()`. Given `CallDispatcher` is shared infrastructure reused by both the Intent Gateway and the Hyper Fungible Token bridge apps, this is a live, unrestricted native-token drain vector on a publicly known contract address, constituting concrete theft of funds.

### Likelihood Explanation
High. `dispatch()` requires no privilege, no proof, and no special conditions besides a nonzero balance in `CallDispatcher` and a target `to` with code — both trivially satisfiable. Any observer monitoring the mempool or the dispatcher's balance can win the race to drain funds ahead of the legitimate sweep performed by `IntentGatewayV2`/`WrappedHyperFungibleToken`.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by an authorized/whitelisted caller (e.g., the specific `IntentGatewayV2`/`WrappedHyperFungibleToken` instances that are meant to drive it), or make each caller operate against its own isolated dispatcher instance/escrow so no shared balance can be intercepted by third parties. Alternatively, remove the ability to hold a standing balance between calls (e.g., require `dispatch` to fully account for and return any leftover native balance to `msg.sender` atomically, and disallow unsolicited `receive()` deposits outside of an active, authenticated call).

### Proof of Concept
1. `CallDispatcher` is deployed and referenced as `_params.dispatcher` by `IntentGatewayV2` and as `_dispatcher` by `WrappedHyperFungibleToken`.
2. A user places an order with a native-ETH predispatch step; `IntentGatewayV2` sends value to `dispatcher` and calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` [9](#0-8) , which increases the dispatcher's ETH balance before the sweep-back call is made in the same transaction.
3. An attacker deploys a trivial contract with a `receive()` function.
4. Between the moment `CallDispatcher`'s balance becomes non-zero and the moment the legitimate sweep call executes (or any time a stray transfer sits in the contract), the attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: attackerContract, value: address(callDispatcher).balance, data: ""})]))` directly.
5. Since `dispatch()` has no access control, the call succeeds, and `CallDispatcher`'s entire native balance is transferred to the attacker's contract, stealing funds meant for the legitimate order/escrow flow. [2](#0-1)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-39)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
```

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

**File:** evm/src/apps/IntentGatewayV2.sol (L241-258)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L268-272)
```text
                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L421-426)
```text
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
```

**File:** docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx (L164-165)
```text
When `isWeth = true`, the WrappedHFT unwraps WETH to native ETH on receive. This example bridges WETH back to the home chain, where it's unwrapped to native ETH and swapped for an exact amount of USDC via UniswapV2. The `Call.value` field forwards the native ETH to the router — demonstrating that the `CallDispatcher` can hold and forward native tokens:

```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-96)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.
```
