### Title
Unchecked ERC20 return-value in `IntentGatewayV2.withdraw()` on Tron incorrectly finalizes escrow release for tokens that return `false` instead of reverting - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` uses raw low-level `.call` with `IERC20.transfer.selector` in `withdraw()` and in the `SweepDust` branch of `onAccept()`, checking only that the call did not revert (`success`), without decoding and validating the returned boolean. Tokens that return `false` on failure without reverting (e.g. Tether Gold-style tokens per the EIP-20 "weird-erc20" classification cited in the source report) will make these transfers appear successful even though no tokens were actually moved, while escrow accounting and order-finalization state are updated as if the transfer succeeded.

### Finding Description
`withdraw()` decrements `_orders[body.commitment][token]` and marks `_filled[body.commitment] = beneficiary` unconditionally, then attempts to pay out via: [1](#0-0) 

The transfer check only inspects `success` from the low-level `.call`, never decoding `returndata` as a `bool`:
```
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
This is exactly the bug class from the source report: checking only for non-reverting behavior is insufficient, because some ERC20 tokens declare a `bool` return type but return `false` on failed transfers instead of reverting. Under this code, such a token's `false` return is silently ignored — `success` is `true` because the call itself didn't revert, so the code proceeds as though tokens were delivered.

The same unchecked pattern also occurs in the `SweepDust` branch of `onAccept()`: [2](#0-1) 

Notably, this raw `.call` pattern is inconsistent with the rest of the same file, which correctly uses `SafeERC20.safeTransferFrom` for inbound transfers (`escrow` funding) via `using SafeERC20 for IERC20;`: [3](#0-2) [4](#0-3) 
Only the outbound escrow-release/sweep paths use the unsafe raw call, indicating an inconsistent hardening of ERC20 interactions across the contract.

### Impact Explanation
`withdraw()` is reached from `onAccept()` (called by the host upon a relayed, otherwise-valid `RedeemEscrow`/`RefundEscrow` ISMP message) and from `onGetResponse()` (called after a relayed cancellation GET-response proof). Both are triggered by a relayer submitting a valid cross-chain proof — an unprivileged, permissionless action in the intended trust model. If the escrowed input token is one that returns `false` on failed transfers (rather than reverting), the transfer to the beneficiary silently fails while:
- `_orders[body.commitment][token]` is decremented as if the transfer succeeded,
- `_filled[body.commitment]` is set, permanently marking the order/commitment as settled.

Because state is already finalized, the tokens remain trapped in the `IntentGatewayV2` contract with no code path left to retry delivery or refund the beneficiary — this is a permanent freezing of escrowed user funds for the affected token, without requiring any admin/governance compromise, purely from relaying a legitimate settlement message for an integrated non-standard ERC20.

### Likelihood Explanation
Likelihood depends on which ERC20 tokens are configured as inputs/outputs for orders on the Tron deployment. Tokens exhibiting the "returns false instead of reverting" behavior are documented (Tether Gold and similar) in the weird-erc20 catalogue referenced by the source report. Any integrator listing such a token as an order input/output (or protocol fee token) on the Tron IntentGateway would trigger this path deterministically on any transfer failure (e.g., due to a blacklist, pause, or balance edge case in that token), and the resulting fund loss is permanent, not merely delayed.

### Recommendation
Replace the raw `.call(...)` + `success`-only check in `withdraw()` and the `SweepDust` handling in `onAccept()` with `SafeERC20.safeTransfer`, consistent with the rest of the file which already imports and uses `SafeERC20`:
```solidity
IERC20(token).safeTransfer(beneficiary, amount);
```
This correctly reverts both when the call reverts and when the token returns `false`, preventing state finalization on a failed transfer.

### Proof of Concept
1. Deploy a `ReturnsFalse`-style ERC20 (declares `bool` return, returns `false` on `transfer`, no revert) and configure it as an order input token on the Tron `IntentGatewayV2`.
2. A user calls `placeOrder` with this token, escrowing tokens successfully (inbound path uses `safeTransferFrom`, which works normally since inbound test conditions succeed).
3. A relayer submits a valid ISMP proof for `RedeemEscrow`/`RefundEscrow`, causing `onAccept` → `withdraw()` to execute.
4. Inside `withdraw()`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `success = true` (the call itself doesn't revert) but the token's internal transfer logic returns `false` and moves no funds.
5. `require(success)`-style check passes, `_orders[commitment][token]` is decremented, `_filled[commitment]` is set, and `EscrowReleased`/`EscrowRefunded` is emitted — even though the beneficiary received zero tokens.
6. The escrowed tokens remain stuck in the `IntentGatewayV2` contract balance with no remaining code path to reclaim them for this commitment, permanently freezing the user's/solver's funds.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-463)
```text
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;
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
