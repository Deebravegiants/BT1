Confirms this pattern (`withdraw`/`TransferFailed` raw `.call` with `transfer.selector`) is unique to `evm/tron/contracts/apps/IntentGatewayV2.sol` — the mainline EVM `IntentGatewayV2.sol` does not use this unsafe pattern in its withdrawal path.

### Title
Unsafe ERC20 return-value handling in Tron IntentGatewayV2 `withdraw`/`SweepDust` accepts failed `transfer()` calls as success, permanently freezing escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` imports and declares `using SafeERC20 for IERC20;` [1](#0-0)  and correctly uses `safeTransferFrom` when pulling funds into escrow during `placeOrder` [2](#0-1) . However, when paying funds *out* of escrow — in `withdraw()` (called from `onAccept` for `RedeemEscrow`/`RefundEscrow`) and in the `SweepDust` handler — the contract bypasses `SafeERC20` and instead performs a raw low-level `.call` with the `transfer` selector, checking only that the call itself did not revert (`success`), never decoding or checking the returned boolean.

### Finding Description
In `onAccept`, the `SweepDust` branch sweeps tokens with:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [3](#0-2) 

The internal `withdraw()` function, which releases escrowed order inputs to a beneficiary and marks the order as filled/refunded, uses the identical unsafe pattern for both the escrowed input tokens and the fee-token payout:
```solidity
_filled[body.commitment] = beneficiary;
...
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();

_orders[body.commitment][token] -= amount;
...
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
``` [4](#0-3) 

`success` here only reflects whether the external call reverted, not whether the token's `transfer()` actually moved funds. Many ERC20-family tokens (including TRC20 tokens common on Tron, and USDT-style implementations) return `false` on a failed transfer instead of reverting (e.g. transfer to a blacklisted/frozen address, paused token, or any other soft-fail condition). Because the code never inspects the ABI-decoded return value, such a `false` return is silently treated as a successful transfer:
- `_filled[body.commitment]` is already set to the beneficiary before any transfer occurs, marking the order permanently redeemed regardless of transfer outcome.
- `_orders[body.commitment][token] -= amount` decrements the escrow accounting as if funds were paid out, even though the beneficiary received nothing.
- There is no other function that lets the beneficiary re-claim the tokens once `_filled` is set and the escrow entry is zeroed, since `withdraw` reverts on `UnknownOrder` when `_orders[commitment][token] == 0` on any retry via `RedeemEscrow`/`RefundEscrow`.

This is the inverse-but-related failure mode of the reported bug class ("unsafe ERC20 operation when enforcing the return value of transfer"): rather than incorrectly reverting for tokens with no return value, this code incorrectly *accepts* a `false` return value as success for tokens that use that convention, silently swallowing failed payouts.

### Impact Explanation
A relayer/filler beneficiary who is entitled to escrowed order inputs, refunds, or transaction fees can have their payout silently dropped if the underlying token's `transfer()` returns `false` instead of reverting on failure. The order is nonetheless marked as filled (`_filled[commitment] = beneficiary`) and the escrow ledger is decremented, permanently freezing the tokens inside the `IntentGatewayV2` contract with no recovery path for the intended recipient. This is a permanent loss/freezing of user/filler funds triggered by a normal `onAccept` message delivery (a relayed cross-chain `RedeemEscrow`/`RefundEscrow` request or a governance-dispatched `SweepDust`), not by any admin/attacker misbehavior — it is a latent correctness bug reachable by any legitimate settlement flow when the input token happens to use the false-on-failure convention.

### Likelihood Explanation
Likelihood is moderate: it requires escrowing/paying out a token whose `transfer()` returns `false` rather than reverting on failure (a real, documented pattern for some TRC20/ERC20 tokens), combined with a transfer-failure condition (blacklist, pause, insufficient allowance edge case, etc.) at payout time. Given `IntentGatewayV2` is designed to be generic and accept arbitrary tokens specified in `order.inputs`/`order.output.assets`, and Tron/TRC20 tokens are exactly the class of tokens known to use non-reverting boolean-return semantics, this is a realistic and reachable condition rather than a purely theoretical one.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check in `withdraw()` (both the token loop and the `TRANSACTION_FEES` payout) and in the `SweepDust` handler with `SafeERC20.safeTransfer`, consistent with the rest of the contract (`using SafeERC20 for IERC20;` is already imported and used elsewhere for `safeTransferFrom`). `SafeERC20.safeTransfer` correctly handles both reverting tokens and tokens that return `false`/no return value, reverting in either failure case so escrow accounting and `_filled` state are never advanced on a failed payout.

### Proof of Concept
1. A user places an order in `IntentGatewayV2` (Tron) with an input token `T` whose `transfer()` implementation returns `false` on failure instead of reverting (e.g., transfer blocked because the beneficiary address becomes blacklisted before settlement).
2. A cross-chain `RedeemEscrow` `PostRequest` is relayed and accepted via `onAccept`, invoking `withdraw(body, false)`.
3. Inside `withdraw`, `_filled[body.commitment] = beneficiary` is set unconditionally at the top of the function [5](#0-4) .
4. The raw `token.call(...)` to `T.transfer(beneficiary, amount)` succeeds at the call level (no revert) but returns `false` because the beneficiary is blacklisted; `success` is `true` so no revert occurs [6](#0-5) .
5. `_orders[body.commitment][token] -= amount` executes, zeroing out the escrow record as if funds were paid [7](#0-6) .
6. The beneficiary never received the tokens (still held by the `IntentGatewayV2` contract), `_filled[commitment]` is already set, and `_orders[commitment][token]` is now `0`, so any retry of `RedeemEscrow`/`RefundEscrow` for the same commitment reverts with `UnknownOrder` — the funds are permanently stuck in the contract.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L405-405)
```text
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
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
```
