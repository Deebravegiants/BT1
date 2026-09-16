## Analog Found

### Title
`WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` assume the configured "WETH" contract implements standard `deposit()`/`withdraw(uint256)` on every chain, permanently freezing locked funds when it doesn't - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()`, `onAccept()` and `onPostRequestTimeout()` unconditionally call `IWETH(_underlying).deposit{value: ...}()` / `IWETH(_underlying).withdraw(amount)` whenever `_isWeth` is true, with no validation that `_underlying` actually implements this interface on the chain it is deployed to [1](#0-0) [2](#0-1) [3](#0-2) . This is the same bug class as the referenced report: the wrapped-native-token contract is assumed to exist with a fixed `deposit()`/`withdraw(uint)` ABI across every deployed chain, but the repo's own chain configuration shows this assumption is not safe — e.g. the Polygon entry stores what it explicitly labels a stale/wrong "wrapped native" address (`//wmatic, change it to wpol`) [4](#0-3) , and Gnosis's WXDAI required a dedicated wrapper (`GnosisUniswapV2Wrapper`) because it does not behave like standard WETH [5](#0-4) .

### Finding Description
`configure()` lets the owner set `isWeth: true` and an arbitrary `underlying` address with zero on-chain check that the token conforms to `IWETH` (`deposit() payable` / `withdraw(uint256)`) [6](#0-5) . When `isWeth` mode is used:

- `send()` locks native value by calling `IWETH(_underlying).deposit{value: params.amount}()` [1](#0-0) .
- `onAccept()` (invoked by `EvmHost.dispatchIncoming` when a relayer delivers the cross-chain message) and `onPostRequestTimeout()` both call `IWETH(_underlying).withdraw(message.amount)` with no fallback if that call reverts [2](#0-1) [3](#0-2) .

`EvmHost.dispatchIncoming` treats a reverting `onAccept` as retryable — it deletes the request receipt and returns without reverting the batch, so the message "stays deliverable" [7](#0-6) . Likewise, `handlePostRequestTimeouts` only refunds the relayer fee after the timeout callback succeeds, and "timeout can be resubmitted until callback succeeds" [8](#0-7) . If `_underlying` on the destination/source chain does not actually implement `withdraw(uint256)` (wrong address, a non-conforming "wrapped native" token, or no canonical WETH-equivalent on that chain at all — mirroring the original report's BNB/Polygon cases), **both** the delivery path and the timeout/refund path will revert on every single relayer attempt, forever. The locked underlying tokens from `send()` can then never be released to the recipient nor refunded to the sender — a permanent freeze with no recovery function in the contract.

The repository's own configuration data corroborates that this exact class of chain-specific WETH/interface mismatch already exists in production data: the Polygon (137) entry stores an address explicitly flagged as needing replacement (`WMATIC` vs `WPOL`) [4](#0-3) , and Gnosis needed an entirely separate wrapper contract because its native-wrap token doesn't behave like standard WETH [9](#0-8) .

### Impact Explanation
If `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` is configured with `isWeth = true` on any chain whose "WETH" address does not conform to the hardcoded `IWETH` ABI (deposit()/withdraw(uint256)) — whether due to a wrong/stale address, a chain lacking a canonical WETH, or a wrapped-native token with a nonstandard interface — user funds locked via `send()` become permanently unrecoverable: `onAccept` can never succeed to deliver the tokens on the destination chain, and `onPostRequestTimeout` can never succeed to refund them on the source chain. This is a permanent freezing of user funds, reachable by any ordinary user calling `send()` with native value.

### Likelihood Explanation
The contract is explicitly designed to be deployed across multiple EVM chains (`docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx` mentions BNB/native ETH interchangeably), and the `configure()` function performs no validation of the underlying token's interface — deployment is entirely operator-driven via a deploy script that just reads an `UNDERLYING` env var and an `IS_WETH` boolean [10](#0-9) . Given the project's own chain configs already show ambiguity/staleness around what the canonical wrapped-native address is per chain, misconfiguration is a realistic operational risk, not a hypothetical one.

### Recommendation
- Validate in `configure()` (or via a startup self-test) that `_underlying` actually implements `deposit()` and `withdraw(uint256)` with the expected semantics (e.g., a canary deposit/withdraw during configuration).
- Add a `try/catch` around `IWETH(_underlying).withdraw(...)` in `onAccept()` and `onPostRequestTimeout()`, falling back to delivering/refunding the raw ERC-20 `_underlying` balance (as WETH) instead of native ETH when the unwrap call fails, so funds are never irrecoverably stuck.
- Add an owner-gated emergency recovery path for funds that fail both the deliver and timeout-refund flows after some threshold.

### Proof of Concept
1. Owner deploys `WrappedHyperFungibleToken` on Chain X and calls `configure({ ..., underlying: TOKEN_X, isWeth: true })`, where `TOKEN_X` is intended to be the chain's wrapped-native token but does not implement `withdraw(uint256)` with the expected selector/behavior (e.g., a migrated/renamed token, or the wrong address as flagged in `chain.ts`'s Polygon entry).
2. A user calls `send{value: amount + fee}(params)`; `deposit{value: amount}()` succeeds (assuming `deposit()` exists), tokens are locked in the contract, and the cross-chain POST request is dispatched.
3. On the destination, `HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming` → `onAccept()` is invoked; `IWETH(_underlying).withdraw(message.amount)` reverts because `TOKEN_X` lacks that function/behavior. The receipt is deleted per `dispatchIncoming`'s failure handling, and every relayer retry hits the same revert.
4. After timeout, `handlePostRequestTimeouts` invokes `onPostRequestTimeout()` on the source chain, which also calls `IWETH(_underlying).withdraw(message.amount)` and reverts identically on every resubmission attempt.
5. The user's locked tokens are neither delivered nor refunded — permanently frozen in the contract with no recovery mechanism.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-273)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-324)
```text
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
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L344-365)
```text
    function onPostRequestTimeout(PostRequestTimeout calldata incoming) external override onlyHost whenNotPaused {
        HyperFungibleToken.Message memory message = abi.decode(incoming.request.body, (HyperFungibleToken.Message));
        address refundee = _toAddr(message.from);

        if (_isWeth) {
            // Try a native-ETH push first; if the refundee cannot accept native value
            // (e.g. the caller used the ERC-20 deposit path in `send()` from a
            // non-payable contract), re-wrap the withdrawn ETH and deliver the
            // underlying WETH as an ERC-20 transfer so the timeout still settles and
            // funds are not permanently locked.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = refundee.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(refundee, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(refundee, message.amount);
        }

        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** sdk/packages/sdk/src/configs/chain.ts (L739-739)
```typescript
			WETH: "0x360ad4f9a9A8EFe9A8DCB5f461c4Cc1047E1Dcf9", //wmatic, change it to wpol
```

**File:** evm/src/utils/uniswapv2/GnosisUniswapV2Wrapper.sol (L1-54)
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

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {IWETH} from "@hyperbridge/core/interfaces/IWETH.sol";

contract GnosisUniswapV2Interface {
    using SafeERC20 for IERC20;

    error DepositFailed();
    error WithdrawFailed();
    error MsgValueLessThanExactAmount();

    /**
     * @dev Returns the address for the wrapped native token on Gnosis mainnet
     */
    function WETH() public pure returns (address) {
        return address(0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d);
    }

    /**
     * @dev The native token for Gnosis itself is DAI so this method simply wraps
     * the native token and returns it to the caller.
     */
    function swapETHForExactTokens(uint256 amountOut, address[] calldata, address, uint256)
        external
        payable
        returns (uint256[] memory)
    {
        if (amountOut > msg.value) revert MsgValueLessThanExactAmount();

        (bool sent,) = WETH().call{value: msg.value}("");
        if (!sent) revert DepositFailed();

        IERC20(WETH()).safeTransfer(msg.sender, msg.value);

        uint256[] memory out = new uint256[](1);
        out[0] = msg.value;
        return out;
    }
```

**File:** sdk/packages/core/contracts/interfaces/IWETH.sol (L21-34)
```text
interface IWETH {
    /**
     * @notice Wraps native tokens into WETH
     * @dev Caller sends native tokens via msg.value, receives equivalent WETH balance
     */
    function deposit() external payable;

    /**
     * @notice Unwraps WETH back into native tokens
     * @dev Burns the specified amount of WETH and sends native tokens to the caller
     * @param amount The amount of WETH to unwrap
     */
    function withdraw(uint256 amount) external;
}
```

**File:** evm/src/core/EvmHost.sol (L794-817)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
```

**File:** docs/content/developers/evm/api/ihandler.mdx (L121-149)
```text
### handlePostRequestTimeouts()

Processes timed-out POST requests and triggers refunds.

```solidity lineNumbers
function handlePostRequestTimeouts(
    IHost host,
    PostRequestTimeoutMessage calldata message
) external
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | `IHost` | The IHost contract |
| `message` | `PostRequestTimeoutMessage` | Struct containing timeout proof and requests |

**Access:** Permissionless (can be called by anyone)

**Process:**
1. Verifies timeout proof
2. For each request:
   - Validates timeout timestamp has passed
   - Calls `onPostRequestTimeout()` on source application
   - Refunds relayer fee to payer (only if callback succeeds)

**Important:**
- Application timeout callback is called **before** refund
- If callback reverts, no refund occurs
- Timeout can be resubmitted until callback succeeds
```

**File:** evm/script/DeployWrappedHFT.s.sol (L9-30)
```text
contract DeployWrappedHFT is BaseScript {
    function deploy() internal override {
        address underlying = vm.envAddress("UNDERLYING");
        bool isWeth = vm.envBool("IS_WETH");

        CallDispatcher dispatcher = new CallDispatcher{salt: salt}();
        WrappedHyperFungibleToken whft = new WrappedHyperFungibleToken{salt: salt}(admin);

        whft.configure(WrappedHyperFungibleToken.WrappedConfigOptions({
            host: HOST_ADDRESS,
            dispatcher: address(dispatcher),
            underlying: underlying,
            isWeth: isWeth
        }));

        vm.stopBroadcast();
        console.log("=== WrappedHFT Deployment ===");
        console.log("WrappedHyperFungibleToken:", address(whft));
        console.log("CallDispatcher:", address(dispatcher));
        console.log("Underlying:", underlying);
        console.log("IsWETH:", isWeth);
    }
```
