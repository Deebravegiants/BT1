### Title
Unchecked ERC20 return value in `withdraw()`/`SweepDust` allows silent transfer failure, permanently losing escrowed funds - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` imports and uses `SafeERC20` for all *inbound* token pulls (`safeTransferFrom`), but for *outbound* payouts in `withdraw()` and the `SweepDust` handler it bypasses `SafeERC20.safeTransfer` and instead performs a raw low-level `call` to the token's `transfer` selector, checking only that the call did not revert — never decoding/validating the returned boolean. [1](#0-0) 

### Finding Description
In `withdraw()`, escrowed token payouts to the beneficiary and fee-token payouts are performed like this:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [2](#0-1) 

The same unchecked pattern is used in the `SweepDust` branch of `onAccept`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [3](#0-2) 

This checks only whether the external call itself reverted, not the ABI-decoded `bool` return value that ERC20-compliant `transfer()` implementations are required to return on failure. Per the ERC20 standard, a fully compliant token may return `false` instead of reverting when a transfer cannot be completed (e.g., insufficient balance edge cases, paused/blacklisted transfers, hooks that reject silently). For such a token, the low-level `call` succeeds (`success == true`) with return data encoding `false`, yet this code treats it as a successful transfer.

Meanwhile, escrow bookkeeping is unconditionally decremented right after the "successful" transfer:
```solidity
_orders[body.commitment][token] -= amount;
``` [4](#0-3) 

and `_filled[body.commitment]` is marked, with `EscrowReleased`/`EscrowRefunded` emitted, as if the beneficiary was paid. [5](#0-4) 

This is the inverse case of the referenced report (which flagged strict boolean-checked transfers reverting for USDT-like tokens that don't return data at all). Here the code deliberately relaxed the check to accommodate USDT-like tokens, but in doing so removed all validation of the returned boolean for tokens that *do* return `false` on failure, silently accepting a failed payout.

### Impact Explanation
Once `withdraw()` runs to completion without reverting, the commitment's escrow balance for that token is permanently decremented (or zeroed) and the order is marked filled/refunded. If the underlying token silently returned `false` rather than reverting, the beneficiary never receives the funds, and the escrow record no longer reflects any outstanding balance — there is no other code path to reclaim it. This results in a permanent loss/freezing of the escrowed funds for the affected beneficiary, reachable by any relayer delivering a valid `RedeemEscrow`/`RefundEscrow` message or dispatching a `SweepDust` request, with no privileged action required to trigger the loss (the failure mode is intrinsic to certain standard-compliant tokens' behavior, not attacker-controlled).

### Likelihood Explanation
Likelihood is moderate: it requires an output/escrowed token whose `transfer()` implementation returns `false` on failure instead of reverting (a legitimate ERC20 behavior, distinct from tokens that revert or tokens that return no data like USDT). Given IntentGatewayV2 is designed to support arbitrary tokens configured by users/solvers for cross-chain intents, such tokens are plausible in practice, and the failure is silent — it will not surface until the beneficiary notices missing funds.

### Recommendation
Use `SafeERC20.safeTransfer` (already imported via `using SafeERC20 for IERC20`) for outbound transfers in `withdraw()` and the `SweepDust` handler, consistent with how inbound transfers are already handled elsewhere in the same contract. `SafeERC20.safeTransfer` correctly handles both no-return-value tokens (USDT-style) and tokens that explicitly return `false`, reverting in the latter case so the escrow state is never advanced past a failed payout.

### Proof of Concept
1. A cross-chain intent order specifies an output/escrowed token `T` whose `transfer()` implementation returns `false` (without reverting) under some failure condition (e.g., a paused state, a blacklist check, or insufficient allowance-like internal condition).
2. A relayer delivers a valid `RedeemEscrow` (or `RefundEscrow`) POST request/GET response, invoking `withdraw()`.
3. `withdraw()` calls `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))`; the call itself does not revert (`success == true`), but the ABI-encoded return data is `false`.
4. The code does not inspect the return data, so it proceeds: `_orders[body.commitment][token] -= amount` and emits `EscrowReleased`/`EscrowRefunded`.
5. The beneficiary never received `T`, and the escrow accounting no longer shows any balance for that commitment/token — the funds are permanently stuck in the `IntentGatewayV2` contract with no remaining code path to distribute them to the rightful beneficiary. [5](#0-4)

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
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
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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
    }
```
