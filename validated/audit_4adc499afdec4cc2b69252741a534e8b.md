## Title
Missing access control on `CallDispatcher.dispatch()` allows anyone to drain any assets held by the shared dispatcher contract - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` is `external` with **no caller restriction whatsoever**, and the contract accepts arbitrary native token via `receive()`. It is deployed once and shared across *all* `IntentGatewayV2` orders (and referenced from `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata-execution flows) as `_params.dispatcher`. Any account holding a balance can invoke `dispatch()` directly — bypassing `IntentGatewayV2` entirely — and execute arbitrary `Call[]` (`to`, `value`, `data`) *as the CallDispatcher*, spending whatever native ETH or ERC-20 balance/approval the dispatcher happens to hold at that moment. This is the same bug class as the FEG `swapToSwap()` incident: an unvalidated, externally reachable entry point lets an unauthorized caller direct a shared contract's assets using attacker-chosen parameters. [1](#0-0) 

### Finding Description
`CallDispatcher` is designed to only ever be invoked internally by `IntentGatewayV2` (and similar hyperapps) with calldata attached to a specific order's `predispatch`/`postdispatch` fields: [2](#0-1) 

There is no `onlyGateway`/`onlyOwner` modifier and no `msg.sender` check anywhere in the contract — `dispatch(bytes memory encoded)` is a bare `external` function that decodes an arbitrary `Call[]` and blindly executes each `to.call{value: call.value}(call.data)`, reverting only if the target has no code or the call itself fails.

`IntentGatewayV2.placeOrder`/`fillOrder` (and the Tron variant) route funds through this single shared dispatcher instance in multiple places, always transferring value/tokens to `dispatcher` first and *then* calling `ICallDispatcher(dispatcher).dispatch(...)`: [3](#0-2) [4](#0-3) 

Because the dispatcher is a single, permanently-deployed, stateless-permission contract shared by every order and every user on the chain, any ERC-20/native balance that is not perfectly swept back within the same atomic call (e.g. a swap that yields a token not enumerated in that order's `inputs`/`outputs`, unconsumed `Call.value` ETH accepted by the unconditional `receive()`, or any other leftover) remains sitting on the dispatcher across transaction boundaries. Since `dispatch()` has zero access control, *any* address can call it directly at any time to move that balance (or any balance the dispatcher will ever hold, including via a malicious `approve()` call it can plant for itself) to itself — completely bypassing the intended order-scoped sweep-as-dust logic in `_execute()`/`placeOrder()`.

This mirrors the FEG root cause precisely: an externally reachable function accepts a caller-controlled `to`/`data` (analogous to FEG's unvalidated `path`) and lets it operate on the calling contract's own held assets without verifying that the caller is the intended, authorized flow (`IntentGatewayV2`).

### Impact Explanation
Any native ETH or ERC-20 balance the shared `CallDispatcher` accumulates — dust from imperfect swaps, unconsumed `Call.value` forwarded to it by `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution, or tokens sent to it by mistake — can be stolen by an unprivileged attacker who simply calls `dispatch()` themselves before the protocol's own dust-sweep runs (which only triggers inside a *subsequent* order's `placeOrder`/`fillOrder`/`_execute()` call). This is concrete theft of protocol/user funds reachable from a single unprivileged transaction, satisfying the "concrete theft ... of funds" bar. Given `CallDispatcher` is documented and used across `IntentGatewayV2` and the `HyperFungibleToken` cross-chain calldata-execution pattern (tokens/ETH minted or unlocked directly `to: CALL_DISPATCHER` before further calls run), the surface for stray balances landing on this unprotected contract is broad.

### Likelihood Explanation
High: exploitation requires only a plain, unprivileged call to a public function (`dispatch`) with no signature, no proof, and no special permissions — the attacker only needs to notice (or cause, e.g. by donating dust) a nonzero balance on the dispatcher and race the protocol's own sweep. No governance, consensus proof, or relayer involvement is needed.

### Recommendation
Restrict `CallDispatcher.dispatch()` to be callable only by the authorized hyperapp(s) that own it (e.g. an immutable `owner`/`gateway` address set at construction, checked via `if (msg.sender != owner) revert Unauthorized();`), or make each hyperapp deploy/use its own dispatcher instance so no cross-order/cross-user shared balance can ever exist. Additionally, ensure any dust the dispatcher could ever hold (including tokens not enumerated in a given order's `inputs`/`outputs`) is swept deterministically within the same transaction it is created, removing any window where a balance persists on a contract with an open `dispatch()` entry point.

### Proof of Concept
1. Any user calls `IntentGatewayV2.placeOrder()` with a `predispatch.call` that swaps native ETH for `TokenA` via Uniswap, but the swap's actual output/rounding leaves `TokenA` dust on `dispatcher` that is not part of `order.inputs` (so it is never captured by the `DustCollected` sweep loop keyed off `inputsLen`).
2. `CallDispatcher` now permanently holds a small `TokenA` balance (this happens continuously in production traffic).
3. An attacker directly calls `CallDispatcher.dispatch(abi.encode(Call[](to: TokenA, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, TokenA.balanceOf(dispatcher)))))` — no relationship to `IntentGatewayV2` is required, and the call succeeds because `dispatch()` has no caller restriction — transferring the dispatcher's `TokenA` balance to the attacker.
4. Repeated over time/across users, and across every hyperapp sharing this dispatcher, this drains all stray balances that Hyperbridge apps route through the CallDispatcher. [5](#0-4)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L1-63)
```text
// Copyright (C) Polytope Labs Ltd.
// SPDX-License-Identifier: Apache-2.0

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// 	http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
pragma solidity ^0.8.17;

import {ICallDispatcher, Call} from "@hyperbridge/core/interfaces/ICallDispatcher.sol";

/**
 * @title The CallDispatcher
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @notice This contract is used to dispatch calls to other contracts.
 */
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```
