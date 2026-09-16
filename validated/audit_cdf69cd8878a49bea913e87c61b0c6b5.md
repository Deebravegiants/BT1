## Title
Unchecked ERC20 return value in Tron `IntentGatewayV2.withdraw()`/`SweepDust` permanently locks escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron-chain `IntentGatewayV2` contract escrows and releases ERC20 tokens using low-level `.call()` with the `IERC20.transfer` selector, checking only that the external call did not revert (`success`) rather than decoding and validating the returned boolean. This is the exact bug class flagged in the referenced Sherlock finding (use `safeTransfer()` instead of raw `transfer()`), reintroduced here via a manual low-level call pattern instead of the `SafeERC20` library that is already imported and used elsewhere in the same file.

### Finding Description
In `withdraw()`, escrowed tokens are released to a beneficiary via:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [1](#0-0) 

The same pattern is used for the transaction-fee payout in the same function: [2](#0-1) 

and in the `SweepDust` handler inside `onAccept()`: [3](#0-2) 

This only checks that the call did not revert; it does not check `abi.decode(returndata, (bool))`. Any ERC20 token that follows the standard by returning `false` on a failed transfer (rather than reverting) will make `success == true` even though no tokens were moved. Despite this, the contract unconditionally proceeds to decrement the escrow accounting and mark the order as finalized:
```solidity
_orders[body.commitment][token] -= amount;
...
_filled[body.commitment] = beneficiary;
...
emit EscrowReleased(...) / emit EscrowRefunded(...)
``` [4](#0-3) 

The contract already imports `SafeERC20` and applies `using SafeERC20 for IERC20` and correctly calls `safeTransferFrom` in `placeOrder()`: [5](#0-4) [6](#0-5) 

but the token-release paths (`withdraw`, `SweepDust`) inconsistently bypass `SafeERC20.safeTransfer` in favor of the unchecked-return raw call, unlike the canonical EVM implementation (`evm/src/apps/intentsv2/IntentsBase.sol`), which correctly uses `safeTransfer` for all outbound token movements: [7](#0-6) 

### Impact Explanation
`withdraw()` is reachable from multiple unprivileged, message-driven entry points:
- Same-chain `cancelOrder()`, callable directly by the order owner: [8](#0-7) 
- Cross-chain escrow redemption/refund via `onAccept()` when a relayer delivers a `RedeemEscrow`/`RefundEscrow` POST message: [9](#0-8) 
- `onGetResponse()` after a relayer delivers a storage-proof GET response for a cross-chain cancellation: [10](#0-9) 

For any escrowed token whose `transfer()` returns `false` instead of reverting on failure (e.g., insufficient allowance/blacklist/paused states implemented that way, or any non-fully-conforming ERC20/TRC20 token), the beneficiary receives nothing, yet the protocol permanently records the order as filled/refunded and deletes the corresponding escrow accounting. The tokens remain stranded in the contract with no accounting path left to retrieve them (the order is already marked in `_filled`, so `UnknownOrder`/`Filled` checks in `cancelOrder`/`onAccept` block any retry), resulting in permanent loss of user or solver funds.

### Likelihood Explanation
This triggers deterministically whenever the escrowed token used in an order returns `false` on transfer failure. This can be forced by an attacker who selects such a token for the input side of an order (`placeOrder` accepts arbitrary ERC20 addresses) and then engineers a failure condition (e.g. self-blacklisting, exhausting an internal cap, or any token-specific rule causing `transfer` to return `false`) prior to `withdraw()` being invoked, causing accounted funds to be irrecoverably frozen. Even absent an active attacker, using a real-world non-conforming token as escrow collateral triggers the fund freeze under ordinary failure conditions.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` branch of `onAccept()` with `IERC20(token).safeTransfer(...)` from OpenZeppelin's `SafeERC20`, which is already imported and used elsewhere in the contract. This ensures both call-revert and boolean-return failures cause the transaction to revert, keeping escrow accounting consistent with actual token movement.

### Proof of Concept
1. An order is placed with an ERC20 input token that returns `false` (rather than reverting) when a transfer cannot be completed (e.g. due to an internal condition set after escrow, such as a blacklist toggle).
2. The order is filled/cancelled/refunded, triggering `withdraw()` via `cancelOrder()`, `onAccept()` (RedeemEscrow/RefundEscrow), or `onGetResponse()`.
3. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `success = true` (call succeeded) even though the wrapped `transfer` logically failed and returned `false`.
4. The contract proceeds: `_orders[commitment][token] -= amount`, `_filled[commitment] = beneficiary`, and emits `EscrowReleased`/`EscrowRefunded` as if the transfer succeeded.
5. The beneficiary never receives the tokens, and the escrow accounting no longer reflects any claimable balance, permanently freezing the funds in the contract.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L459-459)
```text
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L528-539)
```text
        if (isSameChain) {
            // Same-chain: validate locally and refund immediately
            // only owner can cancel
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

            // Verify we're on the correct chain
            if (orderSource != currentChain) revert WrongChain();

            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
