### Title
CallDispatcher cannot receive ERC721/ERC1155 tokens, permanently breaking composable cross-chain flows that mint or deposit NFTs to it - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher` is the shared, permissionless execution contract used by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and their upgradeable variants to run arbitrary post-mint/post-unlock `Call[]` sequences on the destination chain. It implements a payable `receive()` for native ETH, but never implements `IERC721Receiver.onERC721Received` or `IERC1155Receiver.onERC1155Received`. Any composed cross-chain call that ends with an NFT (e.g. a Uniswap-V4-style LP position, a receipt/vault-share NFT, or any `safeMint`/`safeTransferFrom`-based hand-off) being sent to the `CallDispatcher` will revert, permanently breaking that class of route.

### Finding Description
`CallDispatcher.dispatch` sequentially low-level `.call`s a list of attacker/user-supplied `Call{to, value, data}` entries on behalf of `HyperFungibleToken`/`WrappedHyperFungibleToken`'s `onAccept`: [1](#0-0) 

The documented and tested design pattern for these bridged-token apps is: mint/unlock tokens directly to the `CallDispatcher` address, then let the dispatcher execute the composed calls (approve+swap, approve+stake, approve+deposit) while holding the funds: [2](#0-1) [3](#0-2) 

`onAccept` in `HyperFungibleToken`/`WrappedHyperFungibleToken` mints/unlocks to `beneficiary` and then unconditionally forwards `message.data` to `ICallDispatcher(_dispatcher).dispatch(...)`, with the explicit contract-level guarantee that "If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock": [4](#0-3) [5](#0-4) 

`ICallDispatcher`/`Call` is a generic arbitrary-call interface with no restriction on target contract type: [6](#0-5) 

Many common downstream protocols that these composable flows are explicitly designed to reach — DEX LP positions (e.g. Uniswap V3/V4 `PositionManager.mint`), lending-market receipt NFTs, or any soulbound/receipt token implemented as ERC721/ERC1155 — use `_safeMint`/`safeTransferFrom` semantics that call `onERC721Received`/`onERC1155Received` on the recipient. Since `CallDispatcher` implements neither hook (only a bare `receive()` for ETH), any such call in the sequence will revert when the NFT-minting contract checks for receiver-hook support, exactly the same root cause identified in the referenced report for `Anchor.sol` (an ERC721/1155-holding contract missing `onERC721Received`/`onERC1155Received`).

### Impact Explanation
Because `onAccept` reverts entirely when any call in the dispatched sequence reverts (this is an explicitly documented, intended safety property so that failed multi-step compositions don't leave partial state), any cross-chain message whose `Call[]` payload results in an NFT being minted or transferred to the `CallDispatcher` will cause the whole message delivery to fail on every relayer attempt, indefinitely, until the message times out. This is a "route unable to deliver messages" condition for that class of destination workflow: composable transfer-and-stake/transfer-and-deposit/transfer-and-LP flows that yield an ERC721/ERC1155 receipt cannot ever be relayed, since the same deterministic revert occurs regardless of which relayer submits it. While the bridged fungible tokens themselves are eventually refunded to the sender after timeout (avoiding permanent fund loss for the base asset), the intended composed action (and any value/gas paid to attempt delivery) is permanently unexecutable, and no relayer can ever complete delivery for that message — a systemic route-level failure rather than a one-off revert.

### Likelihood Explanation
This is reachable by any unprivileged token bridger: any caller of `HyperFungibleToken.send`/`WrappedHyperFungibleToken.send` (or the upgradeable equivalents) can set the `to` recipient to the `CallDispatcher` address and supply an ABI-encoded `Call[]` in `data` — this is exactly the pattern the project's own documentation instructs integrators to use for "transfer-and-stake" or "transfer-and-deposit into a lending protocol" workflows. Any protocol in such a composed call that issues an ERC721/ERC1155 receipt via safe-mint/safe-transfer semantics (a common pattern for LP positions and vault receipts) will trigger this failure deterministically on every relay attempt.

### Recommendation
Have `CallDispatcher` implement `IERC721Receiver.onERC721Received` and `IERC1155Receiver.onERC1155Received` (and `onERC1155BatchReceived`), returning the appropriate magic values, so that composed downstream calls which mint or transfer NFTs to the dispatcher (e.g., LP position managers, receipt-token vaults) do not revert. Optionally emit an event/allow a subsequent `Call` step in the same sequence to forward the received NFT to its final recipient, mirroring how ERC20/native value is currently handled.

### Proof of Concept
1. Deploy `HyperFungibleToken` (or `WrappedHyperFungibleToken`) with a configured `CallDispatcher` on chain B.
2. User on chain A calls `send(SendParams{ dest: B, to: abi.encodePacked(CALL_DISPATCHER), amount, data: abi.encode(calls) })`, where `calls` includes: (a) `approve` on the bridged token for a position manager, and (b) `positionManager.mint(...)` with `recipient = CALL_DISPATCHER` (an ERC721-minting call using `_safeMint`).
3. Relayer submits the proof; `onAccept` mints/unlocks tokens to `CALL_DISPATCHER`, then calls `ICallDispatcher(_dispatcher).dispatch(message.data)`.
4. Inside `dispatch`, the `positionManager.mint` call triggers `_safeMint` → `IERC721Receiver(CALL_DISPATCHER).onERC721Received(...)`; since `CallDispatcher` has no such function, the call reverts with no matching function selector (falls back to `receive()` only if `msg.value == 0` and no calldata — but calldata is present here, so it reverts outright), causing `CallFailed` to bubble up and revert the entire `onAccept`, and thus the entire cross-chain message delivery, for every relayer attempt until timeout. [7](#0-6)

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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L86-96)
```text
## Calldata Execution

Both contracts support optional calldata execution on the destination chain via the `CallDispatcher`. By passing a non-empty `data` field in `SendParams`, the sender can trigger arbitrary contract calls on the destination chain immediately after tokens are minted or unlocked. This enables composable cross-chain workflows like transfer-and-swap (e.g., bridge USDC then swap to WETH via UniswapV2), transfer-and-stake, or transfer-and-deposit into a lending protocol — all in a single cross-chain operation.

The `data` field is an ABI-encoded `Call[]` array, where each `Call` specifies a target contract, a native value to forward, and the calldata to execute. On the destination chain, the HFT contract mints or unlocks tokens to the `to` address, then forwards the entire `data` payload to the `CallDispatcher`, which executes each call sequentially. If the calls need to spend the bridged tokens (e.g., approve then swap), set `to` to the `CallDispatcher` address so tokens are delivered directly to it.

For code examples, see the [HyperFungibleToken](/developers/evm/hyper-fungible-token/hyper-fungible-token#calldata-execution) and [WrappedHyperFungibleToken](/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token#calldata-execution) pages.

### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L301-313)
```text
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-328)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** sdk/packages/core/contracts/interfaces/ICallDispatcher.sol (L17-37)
```text
struct Call {
    // contract to call
    address to;
    // value to send with the call
    uint256 value;
    // target contract calldata
    bytes data;
}

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
