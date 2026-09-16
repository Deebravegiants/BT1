### Title
Unsafe ERC20 transfers in Tron `IntentGatewayV2.withdraw()` and `SweepDust` handling ignore return value - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` redeems escrowed ERC20 tokens and sweeps dust using raw low-level `.call()` invocations of `IERC20.transfer`, checking only that the call itself did not revert (`success`) rather than decoding and validating the boolean return value the ERC20 standard mandates. Tokens that signal transfer failure by returning `false` (instead of reverting) will pass this check even though no tokens moved, while escrow accounting is still permanently updated as if the transfer succeeded.

### Finding Description
`withdraw()` is invoked from `onAccept()` when a `RedeemEscrow` or `RefundEscrow` cross-chain message is delivered by a relayer [1](#0-0) . Inside `withdraw()`, escrowed tokens are released to the beneficiary via an unchecked low-level call:

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [2](#0-1) 

The same pattern is used for the transaction-fee payout in the same function [3](#0-2) , and for dust sweeps handled via the `SweepDust` request kind in `onAccept()` [4](#0-3) .

`success` here reflects only whether the external call reverted — it does not decode/validate the ABI-encoded `bool` that a compliant `IERC20.transfer` is supposed to return. Per EIP-20, some non-conforming (but widely deployed) tokens return `false` on failure rather than reverting; for such tokens `token.call(...)` returns `success = true` with return data encoding `false`, so `if (!success) revert TransferFailed();` never fires.

Immediately following the (silently failed) transfer, `withdraw()` unconditionally decrements the escrow accounting (`_orders[body.commitment][token] -= amount;`) and marks the order as filled/finalized (`_filled[body.commitment] = beneficiary;`), and emits `EscrowReleased`/`EscrowRefunded` [5](#0-4) . Because `_filled` is set and `_orders` is decremented regardless of whether tokens actually moved, the beneficiary has no path to retry or reclaim the funds — the escrowed collateral is permanently lost while the protocol's own bookkeeping shows the order as settled.

This is inconsistent with the main EVM `IntentGatewayV2.sol`/`IntentsBase.sol`/`IntrinsicIntents.sol`/`ExtrinsicIntents.sol` implementations, which correctly use `SafeERC20.safeTransfer`/`safeTransferFrom` throughout [6](#0-5) [7](#0-6) . The Tron port dropped `SafeERC20` for these two specific paths (`withdraw` and `SweepDust`) even though it imports and uses `SafeERC20` elsewhere in `placeOrder`/`fillOrder` [8](#0-7) .

### Impact Explanation
If a source-chain deployment of this Tron gateway supports an ERC20/TRC20 collateral or fee token that returns `false` instead of reverting on failed transfers (e.g., due to insufficient contract balance from a bug, blacklist logic, paused state, or any non-standard implementation), a relayer delivering a legitimate `RedeemEscrow`/`RefundEscrow`/`SweepDust` message will cause the contract to mark the user's/solver's escrow as released without any tokens actually leaving the contract. This is a permanent loss of user/solver funds: the beneficiary receives nothing, the escrow slot is zeroed out, and the order is marked filled, so there is no recovery mechanism. This qualifies as concrete permanent freezing/loss of escrowed funds reachable by any relayer relaying a normal cross-chain settlement message — no privileged role is required to trigger it, only a token whose `transfer` can non-revertingly return `false`.

### Likelihood Explanation
Triggering the bug requires the escrowed/fee token used in an order to be a non-standard ERC20 that returns `false` on failure rather than reverting, or a token that can be put into a state where `transfer` returns `false` (e.g., paused/blacklist implementations exist among widely used tokens). Users/solvers pick the input/output/fee tokens when placing/filling orders, so this can occur without any admin or attacker action once such a token is used and a transfer condition causes failure — it is not merely a theoretical edge case, mirroring exactly the underlying issue class described in the referenced report.

### Recommendation
Use OpenZeppelin's `SafeERC20.safeTransfer` (already imported and aliased via `using SafeERC20 for IERC20;` in this same file) instead of raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` in `withdraw()` (both the per-token loop and the fee payout) and in the `SweepDust` branch of `onAccept()`, so that non-standard `false`-returning tokens cause a revert instead of a silent state-corrupting success.

### Proof of Concept
1. Configure/whitelist an ERC20 collateral token on the Tron `IntentGatewayV2` deployment whose `transfer` function returns `false` on failure instead of reverting (e.g., a token that returns `false` when the recipient is blacklisted, or a legacy-style token).
2. A user places a cross-chain order escrowing this token via `placeOrder` (uses `safeTransferFrom`, so escrow deposit succeeds normally).
3. The order is filled on the destination chain and a `RedeemEscrow` (or `RefundEscrow`) message is dispatched back to the source-chain gateway.
4. A relayer submits the proof and the host calls `onAccept()` → `withdraw()` on the Tron gateway [1](#0-0) .
5. At the moment of payout, the token's `transfer(beneficiary, amount)` call returns `false` (e.g., because the beneficiary address happens to be blacklisted or another failure condition specific to the token) without reverting.
6. `token.call(...)` returns `success = true` (call didn't revert), so `if (!success) revert TransferFailed();` does not trigger [9](#0-8) .
7. `_orders[body.commitment][token]` is decremented and `_filled[body.commitment]` is set, and `EscrowReleased`/`EscrowRefunded` is emitted, even though the beneficiary never received the tokens — the funds are permanently stuck in the gateway contract with no accounting record left to claim them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L38-56)
```text
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

import {IUniswapV2Router02} from "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
import {ICallDispatcher, Call} from "../../../src/interfaces/ICallDispatcher.sol";


/**
 * @title IntentGatewayV2
 * @author Polytope Labs (hello@polytope.technology)
 *
 * Implements the IntentGatewayV2 contract for Tron
 *
 * @dev The IntentGateway allows for the creation and fulfillment of same-chain & cross-chain orders.
 */
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-676)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-729)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L191-196)
```text
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
```
