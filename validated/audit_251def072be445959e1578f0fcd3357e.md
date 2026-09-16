### Title
Unrestricted arbitrary-call `CallDispatcher.dispatch()` lets any unprivileged user plant a persistent `approve()` backdoor and drain tokens later stranded in the shared dispatcher - (`evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single, shared, permissionless contract instance reused across `IntentGatewayV2.placeOrder` (predispatch), `IntentsBase._execute` (postdispatch), and `HyperFungibleToken`/`WrappedHyperFungibleToken.onAccept` (bridge-and-call). Its `dispatch()` function performs a raw, unrestricted `to.call{value}(data)` for every attacker-supplied `Call` with no allowlist of targets and no restriction on what the calldata does. This is structurally identical to the LiFi `SwapData.callTo/callData` primitive that was exploited: any caller can make the shared, fund-bearing contract execute `IERC20.approve(attacker, type(uint256).max)` on any token, planting an allowance that persists indefinitely on that ERC20's storage, independent of the specific transaction.

### Finding Description
`CallDispatcher.dispatch()` iterates over a caller-supplied `Call[]` and executes each with no restrictions beyond `extcodesize(to) != 0`: [1](#0-0) 

Because the same `CallDispatcher` address is the single shared dispatcher configured in `_params.dispatcher` for the whole `IntentGatewayV2` deployment (and the shared `CALL_DISPATCHER` referenced by `HyperFungibleToken`/`WrappedHyperFungibleToken`), any unprivileged user can call `placeOrder` with `order.predispatch.call` set to `abi.encode([Call({to: TOKEN, value: 0, data: approve(attacker, type(uint256).max)})])` and a minimal, self-funded `predispatch.assets` amount (their own funds): [2](#0-1) 

This grants the attacker an unlimited, permanent ERC20 allowance from the `CallDispatcher` address for `TOKEN`, at trivial cost. The design only ever sweeps back tokens that are explicitly declared in `order.inputs` / `order.output.assets` after a dispatch — any other token balance transiently held or stranded on the dispatcher (e.g., an intermediate hop token from a multi-step swap, or dust left by slippage) is never automatically recovered: [3](#0-2) 

Likewise, `HyperFungibleToken.onAccept()` mints/forwards bridged funds to the `CallDispatcher` and executes attacker-controlled `message.data` with no sweep-back safety net at all: [4](#0-3) 

Once the attacker's `approve()` backdoor exists for a popular token (e.g., WETH/USDC — common intermediate swap/bridge assets), any future dust, un-swept intermediate balance, or misconfigured `to` in another user's or solver's predispatch/postdispatch/bridge-and-call flow that ends up sitting on the shared `CallDispatcher` becomes permanently drainable by the attacker via a direct `transferFrom(dispatcher, attacker, amount)` call on the token contract — entirely outside of Hyperbridge's own call flow, since the allowance is a persistent state change on the token, not scoped to a single transaction.

### Impact Explanation
This is the same root cause class as the LiFi hack: an unrestricted, arbitrary-call primitive on a contract that ends up holding/approving funds on behalf of many unrelated parties, permitting `approve`/`transferFrom` abuse to move value the caller never owned. Here the abuse vector is the shared `CallDispatcher`: theft of any token balance/dust stranded there by any other user's or solver's predispatch/postdispatch/bridge-and-call operation, which the documentation itself acknowledges as a live risk ("Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution"). Given `CallDispatcher` is shared across the entire `IntentGatewayV2` and HFT/WrappedHFT deployment, this is not scoped to a single order — it is a systemic backdoor affecting funds from any unrelated user or solver that ever passes the exploited token through the dispatcher afterward.

### Likelihood Explanation
Reachable by any unprivileged address in a single transaction (`placeOrder` with attacker-controlled `predispatch.call`, or a bridged HFT `send` with attacker-controlled `data`), at negligible cost (gas plus a self-owned trivial escrow amount). No governance, relayer, or solver privilege is required to plant the backdoor. Realizing the drain requires a subsequent, unrelated transaction from another party to leave the targeted token balance on the dispatcher (via intermediate-hop dust, slippage residue, or a misrouted `to` in calldata-driven bridging), which is a normal, expected occurrence in multi-hop swap/bridge composition.

### Recommendation
- Scope `CallDispatcher` per-call (e.g., deploy a fresh, single-use dispatcher/clone per order or per bridged message) instead of reusing one shared, stateful contract across all users.
- Alternatively, have `CallDispatcher.dispatch()` explicitly revoke (`approve(spender, 0)`) any non-zero allowances it granted during the batch before returning, and/or block `approve`/`increaseAllowance`-selector calldata to arbitrary spenders outright.
- Enforce a mandatory, protocol-defined sweep-to-zero-balance step for *every* token touched by dispatched calls (not just tokens declared in `order.inputs`/`order.output.assets`), so no token can be silently stranded on the shared dispatcher.

### Proof of Concept
1. Attacker calls `IntentGatewayV2.placeOrder` with:
   - `order.inputs`/`order.output` minimal/self-funded.
   - `order.predispatch.assets = [{token: USDC, amount: 1}]` (attacker's own 1 wei).
   - `order.predispatch.call = abi.encode([Call({to: USDC, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)})])`.
2. `placeOrder` transfers the 1 wei USDC to `dispatcher`, then calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`, which executes `USDC.approve(attacker, max)` from the `CallDispatcher` address — this succeeds, no validation prevents it (`evm/src/utils/CallDispatcher.sol:44-62`, `evm/src/apps/IntentGatewayV2.sol:235-258`).
3. At any later time, once any other user's/solver's order or HFT bridge operation causes USDC to transiently sit on or be stranded on `dispatcher` (e.g., an un-swept intermediate hop token, or a bridged calldata swap whose final leg fails to fully forward output), attacker calls `USDC.transferFrom(dispatcher, attacker, balance)` directly, draining funds that never belonged to them.

<br> [5](#0-4)

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```
