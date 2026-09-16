### Title
Unchecked ERC20 return value in escrow withdrawal/dust-sweep allows silent transfer failure with orders marked as settled, permanently freezing solver/user funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of the IntentGateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) still uses low-level `.call()` with `IERC20.transfer.selector` and only checks the outer `success` boolean from the call, never decoding/validating the ERC20 return data, in `withdraw()` and the `SweepDust` handler in `onAccept()`. This is the exact bug class described in the external report (unsafe, unchecked ERC20 `transfer`), which the main EVM codebase (`evm/src/apps/intentsv2/IntentsBase.sol`) has already fixed by switching to OpenZeppelin's `SafeERC20.safeTransfer`, but the Tron fork was not updated to match.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, both `withdraw()` and the `SweepDust` branch of `onAccept()` release escrowed tokens using: [1](#0-0) 
and [2](#0-1) 

These only assert that the low-level `call` did not revert (`success`). They never decode the returned bytes to check the ERC20 boolean result. Some (T)RC20 tokens return `false` on a failed transfer instead of reverting — the same non-standard behavior the referenced Hifi report warns about. With this pattern, such a failed transfer is treated as a success: `_orders[body.commitment][token] -= amount;` still executes, `_filled[body.commitment] = beneficiary;` is set, and `EscrowReleased`/`EscrowRefunded`/`DustSwept` are emitted — even though the beneficiary received nothing. [3](#0-2) 

This is the same file/pattern used for the transaction-fee payout inside `withdraw()`: [4](#0-3) 

By contrast, the shared/canonical EVM base contract already fixed this exact issue by using `safeTransfer`: [5](#0-4) [6](#0-5) 

The Tron deployment imports `SafeERC20` and even has `using SafeERC20 for IERC20;` declared, but does not use it in these payout paths, confirming the fix was applied elsewhere but missed here. [7](#0-6) 

### Impact Explanation
`withdraw()` is the internal function that finalizes order fills/refunds and releases escrowed solver/user input tokens and relayer/transaction fees after a relayed cross-chain message is delivered via `onAccept`/`RedeemEscrow`/`RefundEscrow`. Because the state (`_orders`, `_filled`) is updated unconditionally once the low-level call itself doesn't revert, a non-compliant or misbehaving token contract that returns `false` on failure (rather than reverting) causes the protocol to consider escrowed value paid out while it is actually still trapped in the contract with no recorded claim on it. This is a direct fund-freezing/loss condition for solvers and users relying on Hyperbridge's intents escrow on the Tron deployment, satisfying the "permanent freezing of funds" bar in scope.

### Likelihood Explanation
The path is reachable by any relayer submitting a valid Hyperbridge proof that triggers `onAccept` (`RedeemEscrow`/`RefundEscrow`/`SweepDust`), which is a normal, permissionless part of intent settlement — no privileged role or governance action is needed to trigger the vulnerable code path. The only precondition is that the token deployed as an intent's input/output/fee token exhibits the boolean-return-on-failure pattern instead of reverting (a well-known real-world ERC20/TRC20 non-compliance pattern the referenced Hifi report explicitly calls out), making exploitation dependent on token choice rather than attacker sophistication.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check pattern in `withdraw()` and the `SweepDust` handler of `evm/tron/contracts/apps/IntentGatewayV2.sol` with `IERC20(token).safeTransfer(...)` (the contract already has `using SafeERC20 for IERC20;` available), mirroring the fix already applied in `evm/src/apps/intentsv2/IntentsBase.sol`'s `_withdraw()` and `_sweepDust()`.

### Proof of Concept
1. Deploy/register a TRC20 token that returns `false` (instead of reverting) on a failed `transfer` (e.g., insufficient balance/allowance edge case in the token's own logic, or a token that returns `false` on transfers to specific blacklisted/paused states).
2. Place and fill/cancel an intent order on the Tron `IntentGatewayV2` using that token as an input/output/fee token, engineering a state where the token's internal `transfer` call would return `false` under the withdrawal conditions (e.g., a pausable/blacklist-capable token temporarily blocking the beneficiary).
3. Relay the corresponding `RedeemEscrow`/`RefundEscrow` message so `onAccept` invokes `withdraw()` at [1](#0-0) .
4. Observe that the low-level `call` succeeds (no revert) even though the token returned `false`; `_orders[...]` is decremented, `_filled[...]` is set, and `EscrowReleased`/`EscrowRefunded` is emitted — while `beneficiary`'s token balance is unchanged, permanently freezing the escrowed funds with no remaining accounting path to recover them.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-470)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L639-656)
```text
    function _sweepDust(SweepDust memory req) internal {
        uint256 outputsLen = req.outputs.length;
        for (uint256 i; i < outputsLen;) {
            TokenInfo memory info = req.outputs[i];
            address token = address(uint160(uint256(info.token)));
            uint256 amount = info.amount;

            if (token == address(0)) {
                _sendValue(req.beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(req.beneficiary, amount);
            }
            unchecked {
                ++i;
            }
            emit DustSwept(token, amount, req.beneficiary);
        }
    }
```
