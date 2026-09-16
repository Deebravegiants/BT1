### Title
Non-standard ERC20 tokens (e.g., Tron USDT) can cause silent transfer failures and permanently stuck escrow funds in `IntentGatewayV2.withdraw` and dust-sweep on Tron - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2` on Tron consistently uses `SafeERC20.safeTransferFrom` for pulling tokens into escrow, but reverts to raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` calls for paying tokens *out* of the contract in `withdraw()` and the `SweepDust` handler. These raw calls only check that the external call did not revert; they never decode/validate the returned boolean. Non-standard ERC20 tokens that return `false` instead of reverting on a failed transfer (a documented class of tokens, and notably how some deployments of USDT behave) will make `success == true` even though no tokens were actually moved, while the contract still decrements escrow and marks the order as filled.

### Finding Description
The contract imports and uses `SafeERC20` for inbound transfers: [1](#0-0) 

But for outbound escrow release in `withdraw()`, it performs raw calls and only checks the low-level `success` flag, never inspecting the ABI-decoded boolean return value that `IERC20.transfer` is expected to produce: [2](#0-1) 

The same unsafe pattern appears in the `SweepDust` request handler, which pays tokens out to an arbitrary `req.beneficiary`: [3](#0-2) 

For a token that returns `false` on failed transfer (rather than reverting), `token.call(...)` will still return `success == true` (the call executed without reverting), so the `if (!success) revert TransferFailed();` guard never triggers. As a result:
1. `_orders[body.commitment][token] -= amount;` executes, permanently clearing the escrow accounting for that token.
2. `_filled[body.commitment] = beneficiary;` marks the order as finalized.
3. The beneficiary/solver never actually receives the tokens.

Since the order is now marked filled and escrow is zeroed, there is no retry path — the tokens remain stuck in the `IntentGatewayV2` contract with no accounting entry pointing to them, i.e., permanently locked funds.

This path is reachable by any relayer/solver: once a cross-chain `RedeemEscrow`/`RefundEscrow` message is delivered via `onAccept` and dispatches into `withdraw()`, or once a `SweepDust` message is processed, the transfer-out logic executes without verifying that the ERC20 transfer actually succeeded.

### Impact Explanation
Impact is High: escrowed user/solver funds can become permanently unrecoverable if any token integrated on the Tron deployment exhibits non-standard (return-false-instead-of-revert) transfer semantics. Given Tron's dominant token is USDT (TRC20), and TRC20 USDT's ERC20-compatibility wrapper is known to have return-value quirks in various implementations, this is a realistic asset for this specific chain deployment.

### Likelihood Explanation
Likelihood is Medium for the Tron deployment specifically, since USDT-TRC20 (the most heavily used token on Tron) is a plausible input/output token for `IntentGatewayV2` orders, and the contract's inconsistent use of `SafeERC20` (used for inflows, not outflows) shows the outbound path was not hardened against non-standard token behavior, unlike the main EVM `IntentGatewayV2.sol`/`IntentsBase.sol` which consistently use `safeTransfer`/`safeTransferFrom` everywhere for both directions.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` handler with `SafeERC20.safeTransfer`, consistent with how the file already handles inbound transfers via `safeTransferFrom`. This ensures failed transfers (whether via revert or a `false` return) properly cause the transaction to revert, preventing escrow state from being finalized without the underlying token movement actually succeeding.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with a mock ERC20 token whose `transfer` function returns `false` on failure instead of reverting (mirrors non-standard tokens like some USDT deployments).
2. A user places an order with this token as an escrowed input via `placeOrder` (uses `safeTransferFrom`, succeeds normally).
3. Configure the mock token so the subsequent `transfer` call to the beneficiary in `withdraw()` returns `false` (e.g., beneficiary is blacklisted or contract induces failure), without reverting.
4. Trigger `onAccept` with a `RedeemEscrow`/`RefundEscrow` body for that commitment (as a relayer would after settlement).
5. Observe: `withdraw()` completes without reverting, `_orders[commitment][token]` is decremented to zero, `_filled[commitment]` is set, but `token.balanceOf(beneficiary)` never increased and `token.balanceOf(address(intentGateway))` still holds the funds — the tokens are now stuck with no state pointing to them for recovery.

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
