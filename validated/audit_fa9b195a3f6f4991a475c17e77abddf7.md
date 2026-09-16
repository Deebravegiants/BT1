## Analog Found

### Title
Escrow withdrawal in `IntentGatewayV2.sol` (Tron) uses raw low-level `.call` with `IERC20.transfer.selector` instead of the already-imported `SafeERC20.safeTransfer`, silently ignoring a `false` return value - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.sol` (Tron variant) imports `SafeERC20` and declares `using SafeERC20 for IERC20;`, and correctly uses `safeTransferFrom` in `placeOrder`, but its escrow-release logic in `withdraw()` (and the `SweepDust` admin action) bypasses `SafeERC20` and instead performs a raw low-level call, checking only that the call did not revert while ignoring the ABI-decoded boolean return value.

### Finding Description
The contract imports and uses `SafeERC20` elsewhere: [1](#0-0) 

But in the internal `withdraw()` function, which is the only path that releases escrowed user funds back to a beneficiary on `RedeemEscrow`/`RefundEscrow`, and in the `SweepDust` admin action, token transfers are done with a raw low-level call whose result is checked only for `success` (i.e., the call did not revert), not for the decoded boolean return value of `transfer`: [2](#0-1) [3](#0-2) 

`OpenZeppelin`'s `SafeERC20.safeTransfer` both tolerates tokens that omit a return value and reverts when a token explicitly returns `false`. This raw `.call(...)` pattern does neither correctly: it happens to tolerate tokens with missing return data (so it won't spuriously revert on non-standard tokens like Tron's USDT-TRC20), but it also silently accepts tokens whose `transfer` function returns `false` to signal failure (e.g., paused, blacklisted-recipient, or otherwise policy-restricted ERC20-like tokens) without reverting.

### Impact Explanation
Because `success` from the raw call is the only thing checked, a token contract that returns `false` on failed transfer (rather than reverting) will cause:
- `withdraw()` to still decrement `_orders[body.commitment][token]` and mark `_filled[body.commitment] = beneficiary`, permanently finalizing the order, even though the beneficiary never received the tokens: [4](#0-3) 
- The `SweepDust` governance-only path similarly marks dust as swept (`emit DustSwept`) without confirming actual receipt: [3](#0-2) 

Since the order/escrow state is irreversibly updated (escrow balance zeroed, order marked filled/refunded) regardless of whether tokens actually moved, the escrowed tokens become permanently stuck in the `IntentGatewayV2` contract with no legitimate withdrawal path left for the intended beneficiary — a permanent freezing of user funds reachable directly from the token-bridge/intents escrow redemption flow (a single relayed/authenticated redeem or refund request).

### Likelihood Explanation
This is triggerable whenever any input/output token used in an intent order behaves this way (returns `false` instead of reverting on transfer failure) — a known pattern for compliance/blacklist-capable stablecoins and pausable tokens deployed on Tron/EVM chains that this same `IntentGatewayV2` explicitly supports (fee-on-transfer and non-standard token handling is already a first-class concern in this codebase, as seen by the `IERC20.transfer.selector` sweep patterns and FOT tests elsewhere in the repo). No privileged role is required beyond the normal `RedeemEscrow`/`RefundEscrow` request flow that any solver/user interaction can trigger.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` branch with `IERC20(token).safeTransfer(beneficiary, amount)`, consistent with the `using SafeERC20 for IERC20;` declaration already present and already used for `safeTransferFrom` in `placeOrder`.

### Proof of Concept
1. Deploy or use a token whose `transfer()` returns `false` on failure instead of reverting (e.g., a paused/blacklist-style token) as an intent's input/output token.
2. A user places an order escrowing this token via `placeOrder`, using `safeTransferFrom` correctly.
3. When the order is later redeemed/refunded via a `RedeemEscrow`/`RefundEscrow` request, if the token transfer to the beneficiary fails and returns `false` (e.g., beneficiary got blacklisted after order placement), `withdraw()` still executes `_orders[body.commitment][token] -= amount`, sets `_filled[body.commitment] = beneficiary`, and emits `EscrowReleased`/`EscrowRefunded` as if successful.
4. The escrowed tokens remain in the contract balance but are now unreachable: the order is finalized and any retry attempt reverts (via `UnknownOrder` since escrow was already decremented), permanently freezing those funds. [5](#0-4)

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-681)
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
