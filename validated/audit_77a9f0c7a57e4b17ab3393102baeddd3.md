### Title
Unchecked ERC20 return-value data lets a failed `transfer()` be treated as success, permanently freezing escrowed funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.sol` (Tron variant) redeems escrowed order tokens, dust, and transaction fees using a raw low-level `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks the boolean `success` returned by `.call()` — it never decodes/validates the ERC20 `bool` return payload itself.

### Finding Description
In `withdraw()` and the `SweepDust` handling branch of `onAccept`, tokens are moved with:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [1](#0-0) [2](#0-1) [3](#0-2) 

`success` here only reflects whether the target contract executed without reverting — it says nothing about the ABI-encoded boolean return value that ERC20's `transfer()` is supposed to return. Per the weird-erc20 catalogue referenced by the source report, several tokens return `false` on failure instead of reverting (e.g. some legacy/rebasing/blacklist tokens). With this pattern, if such a token's `transfer` call returns `false` (e.g., beneficiary is blacklisted, insufficient allowance edge case, paused token, etc.) but does not revert, `success` is still `true`, so the code proceeds as if the transfer succeeded.

Immediately after, the escrow accounting is unconditionally decremented (`_orders[body.commitment][token] -= amount;`) and the order is marked filled (`_filled[body.commitment] = beneficiary;`), even though no tokens actually moved. [4](#0-3) 

This is the inverse-but-related flavor of the reported bug class (missing-return-value tokens causing unwanted reverts): here, the code fails to validate the boolean return at all, so a token that signals failure via a `false` return (rather than reverting) is silently accepted as a success.

Note that the equivalent EVM-mainline contract, `IntentsBase.sol`, correctly uses OpenZeppelin's `SafeERC20.safeTransfer`, which validates both call success and the returned boolean: [5](#0-4) 
The Tron variant of `IntentGatewayV2` deliberately diverges from this safe pattern despite importing `SafeERC20` and declaring `using SafeERC20 for IERC20;` at the top of the file. [6](#0-5) 

### Impact Explanation
Because the escrow ledger (`_orders`) is decremented and the order marked filled/refunded regardless of whether the underlying token transfer actually delivered funds, a token whose `transfer()` returns `false` on failure (without reverting) would let this code path silently "burn" the escrow accounting entry while the beneficiary receives nothing. The funds remain locked in the contract with no accounting record pointing to them (the escrow slot has already been zeroed/decremented and the commitment marked filled), making recovery impossible through the normal withdrawal path. This is a permanent freezing-of-funds condition reachable by a normal `RedeemEscrow`/`RefundEscrow` request or a `SweepDust` governance dispatch once such a token is configured for an order.

### Likelihood Explanation
This requires escrowing/dispatching orders denominated in an ERC20 that returns `false` instead of reverting on failure — a real but non-universal category of tokens (some deflationary/blacklist/pausable tokens follow this convention). The Tron ecosystem in particular has TRC20 tokens with idiosyncratic transfer semantics, which is presumably why this contract avoids `safeTransfer` in the first place — but the mitigation applied (checking only call `success`) does not actually address the root problem and instead removes a safety check that was already available via the imported `SafeERC20` library.

### Recommendation
Decode and validate the ERC20 return value explicitly wherever a raw `.call` to `transfer` is used, e.g.:
```solidity
(bool success, bytes memory data) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success || (data.length != 0 && !abi.decode(data, (bool)))) revert TransferFailed();
```
This preserves compatibility with tokens that return no data (like USDT) while still rejecting tokens that explicitly signal failure via `false`. Alternatively, use OpenZeppelin's `SafeERC20.safeTransfer`, which already implements this exact check and is already imported/aliased in this file (`using SafeERC20 for IERC20;`).

### Proof of Concept
1. Deploy (or use) an ERC20/TRC20 token whose `transfer()` implementation returns `false` on failure rather than reverting (e.g. a blacklist-style token where the beneficiary has been blacklisted, or any token following this weird-erc20 pattern).
2. Create and fund an order in `IntentGatewayV2` using this token as one of `body.tokens`, escrowing `amount` in `_orders[commitment][token]`.
3. Trigger `RedeemEscrow`/`RefundEscrow` via `onAccept`, invoking internal `withdraw(body, ...)`.
4. The token's `transfer(beneficiary, amount)` call returns `false` (e.g. beneficiary blacklisted) but does not revert; `success` from the low-level `.call` is `true`.
5. `withdraw()` proceeds: `_orders[commitment][token] -= amount` executes and `_filled[commitment] = beneficiary` is set, emitting `EscrowReleased`/`EscrowRefunded` — even though the beneficiary received zero tokens.
6. The escrowed tokens remain stuck in the contract with no further code path to reclaim them, since the commitment is now marked filled and the accounting already zeroed.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L692-714)
```text
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L719-722)
```text
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
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
