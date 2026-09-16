## Title
Unchecked ERC20 transfer return value in Tron `IntentGatewayV2.withdraw()` and `SweepDust` handler causes silent loss of escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed order funds using a raw low-level `.call()` to the ERC20 `transfer` function and only checks that the call itself did not revert, never inspecting the ABI-encoded boolean return value. Non-reverting-on-failure ERC20 tokens (which return `false` instead of reverting) will make the low-level call report `success = true` while the tokens are never actually moved, yet the escrow accounting is unconditionally decremented as if the transfer succeeded.

### Finding Description
In `withdraw()`, escrow release/refund for ERC20 tokens is performed like this: [1](#0-0) 

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
```

`success` here only reflects whether the external call reverted — it does not decode/require the ERC20 `transfer` function's returned `bool`. Per EIP-20, non-conforming tokens are permitted to return `false` on failure rather than reverting; several widely known token implementations exhibit exactly this pattern. If such a token is escrowed (or configured as the fee token), a failing `transfer` (e.g., due to a paused/blacklisted state, or any application-level failure the token signals via `false`) will not revert the call, so `success == true`, and `_orders[body.commitment][token] -= amount` executes anyway — permanently marking the escrow as released even though the beneficiary received nothing.

The same unchecked pattern exists for the fee-token payout in the same function and in the governance-triggered `SweepDust` handler in `onAccept`: [2](#0-1) [3](#0-2) 

This contract does import and use `SafeERC20`/`IERC20` elsewhere (`using SafeERC20 for IERC20;` and `safeTransferFrom` calls during `placeOrder`), confirming that the withdraw/sweep paths deviate from the safe pattern used for token inflows: [4](#0-3) 

By contrast, the main EVM `IntentsBase.sol` correctly uses `safeTransfer` for the equivalent escrow-release logic, showing this is a real regression specific to the Tron contract: [5](#0-4) 

### Impact Explanation
`withdraw()` is the sole function that pays out escrowed user funds — for cross-chain fills via `onAccept` (`RedeemEscrow`/`RefundEscrow` messages) and for source-chain cancellations via `onGetResponse`. If the escrowed token (or the fee token) returns `false` on a failed transfer instead of reverting, the beneficiary receives no tokens while `_orders[commitment][token]` is decremented and `EscrowReleased`/`EscrowRefunded` is emitted as if payment succeeded. Since the escrow slot is now zeroed/reduced, the funds cannot be re-claimed through any retry path — this is a permanent loss (freezing/burning) of the user's or solver's escrowed assets, reachable by any relayer submitting a legitimate, otherwise-valid settlement or cancellation proof for an order that used such a token.

### Likelihood Explanation
Likelihood depends on the intent gateway allowing/whitelisting a non-standard ERC20 as an order input or as the configured Hyperbridge fee token. Given `IntentGatewayV2` is a general-purpose, permissionless order/token gateway (any ERC20 address can be specified as `order.inputs[i].token`), and Tron/TRC20 tokens in particular are known for inconsistent standard compliance (many exhibit exactly this "return false / no revert" behavior), the precondition is realistic rather than contrived.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` handler with OpenZeppelin's `SafeERC20.safeTransfer`, which is already imported and used elsewhere in this same contract, so the transfer's return value is properly validated (or the call is required to revert) before the escrow accounting is mutated.

### Proof of Concept
1. Deploy/whitelist a TRC20/ERC20 token `T` whose `transfer` returns `false` (does not revert) once some internal condition fails (e.g., a pausable or blacklist-style token, common on Tron).
2. A user places a cross-chain order with `order.inputs[0].token = T` via `placeOrder` (uses `safeTransferFrom`, so escrow succeeds normally).
3. A solver fills the order on the destination chain; the `RedeemEscrow` message is relayed back and delivered via `onAccept`, invoking `withdraw()`.
4. At the point `T.transfer(beneficiary, amount)` internally fails and returns `false` (e.g., token later paused, or beneficiary blacklisted at settlement time), `token.call(...)` still returns `success = true` because the call did not revert.
5. `_orders[body.commitment][token] -= amount` executes, `EscrowReleased` is emitted, but `beneficiary` never received the tokens — the escrowed `T` is permanently stuck/lost with no remaining accounting path to reclaim it.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-681)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-710)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-723)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
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
