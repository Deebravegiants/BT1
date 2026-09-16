## Title
IntentGatewayV2 (Tron) escrow withdrawal uses unchecked low-level `.call` for ERC20 transfers, enabling silent transfer failures and permanent loss of escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` settles escrowed intent funds (order inputs, solver payouts, and protocol/transaction fees) using a raw low-level `.call()` to the token's `transfer` selector, checking only that the *call itself* did not revert. It never inspects the ABI-encoded boolean return value that ERC20/TRC20 `transfer()` is supposed to return. This is exactly the `_safeTransfer()` bug class from the reference report: some tokens return `false` on failure instead of reverting, producing a silent failure that the contract treats as success.

### Finding Description
In `withdraw()`, escrowed tokens and fees are released with: [1](#0-0) [2](#0-1) 

and in the `SweepDust` branch of `onAccept()`: [3](#0-2) 

Both call sites use `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and gate on `success` alone (i.e., whether the low-level call reverted), never decoding/verifying the actual boolean returned by `transfer()`. Per EIP-20, a compliant token may legitimately return `false` on failure without reverting; in that case `success` is `true` (the call executed without throwing) even though no tokens moved, exactly the silent-failure pattern flagged in the reference report against `TokenUtils._safeTransfer()`.

This is a real regression within this same file, not a hypothetical: the rest of the contract explicitly imports and uses OpenZeppelin's `SafeERC20` for other transfers: [4](#0-3) [5](#0-4) 

but the escrow-release path (`withdraw`) and dust-sweep path deliberately drop down to a raw `.call` that does not validate the return payload — unlike the non-Tron `IntentsBase.sol`, which correctly uses `safeTransfer`/`safeTransferFrom` throughout, including the equivalent withdrawal function: [6](#0-5) 

Critically, `withdraw()` marks the order as finalized *before/regardless of* whether the transfer actually delivered funds: [7](#0-6) 

and `onGetResponse` refuses to re-process an order once `_filled` is set: [8](#0-7) 

So if the escrowed/fee token silently returns `false` (rather than reverting) on a failed transfer — a known compatibility characteristic of several TRC20 tokens on Tron — the escrow accounting (`_orders[...] -= amount`, `_filled[...] = beneficiary`) is committed as if the payout succeeded, while the beneficiary receives nothing, and the order can never be redeemed again.

### Impact Explanation
This is reachable by any relayer delivering an authenticated `RedeemEscrow`/`RefundEscrow` POST request or `onGetResponse` for a filled/timed-out intent order — a core part of the intents escrow settlement path, not an admin-only or hypothetical flow. A silent `transfer` failure permanently freezes the solver's or user's escrowed principal and/or transaction fees: the contract's internal bookkeeping is decremented/finalized, but the tokens never leave the contract, and the `_filled` guard blocks any retry, resulting in a permanent loss of funds for the intended beneficiary.

### Likelihood Explanation
Likelihood is elevated specifically because this is the Tron variant of the gateway. TRC20 tokens (most notably USDT-TRC20 and various Tron-native tokens) are documented to deviate from strict EIP-20 semantics, including returning `false` on failure instead of reverting, or lacking a return value in some historical implementations. Since the contract already special-cases Tron by avoiding `SafeERC20` in these two call sites, it is plausible this was an intentional (but incomplete) accommodation for such tokens — leaving exactly the silent-failure gap the reference report describes.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` handler with OpenZeppelin's `SafeERC20.safeTransfer`, which the file already imports and uses elsewhere (`using SafeERC20 for IERC20;`). If raw calls must be kept for Tron-specific token quirks, decode and validate the returned boolean (when returndata is non-empty) in addition to checking `success`, and do not finalize (`_filled`) or decrement escrow accounting until the transfer is confirmed to have actually moved funds.

### Proof of Concept
1. Deploy (or use) a TRC20 token whose `transfer()` returns `false` on failure instead of reverting (e.g., insufficient allowance/balance edge cases, blacklist checks, or paused-transfer states common in some TRC20 implementations).
2. Place and fill an intent order on the Tron `IntentGatewayV2` using that token as an input/fee asset, so tokens are escrowed under a `commitment`.
3. Have hyperbridge relay a `RedeemEscrow` request (or trigger `onGetResponse` after a fill) for that commitment while the token is in a state where `transfer()` returns `false` (e.g., beneficiary temporarily blacklisted, or token paused).
4. Observe: `token.call(...)` returns `success = true` (no revert), so `TransferFailed` is never raised; `_orders[commitment][token] -= amount` executes and `_filled[commitment] = beneficiary` is set — yet the beneficiary's token balance is unchanged.
5. Any subsequent attempt to redeem is blocked by the `_filled` check in `onGetResponse`, permanently freezing the escrowed funds.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-406)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-700)
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
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
