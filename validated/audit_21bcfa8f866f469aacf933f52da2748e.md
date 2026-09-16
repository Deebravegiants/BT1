### Title
Unchecked ERC20 return value on outbound `transfer` in `withdraw`/`sweepDust` permanently freezes escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed intent funds using a raw low-level `.call()` to `IERC20.transfer`, checking only that the call itself succeeded (`success`) without decoding/validating the boolean return data. On tokens that return `false` on transfer failure instead of reverting (the exact "no revert on failure" weird-ERC20 class the external report is about), the gateway will treat the payout as successful, decrement the escrow accounting and mark the order as filled/refunded, even though the beneficiary never received the tokens — permanently freezing those funds in the contract.

### Finding Description
`withdraw()` releases escrowed order tokens to a beneficiary: [1](#0-0) 

For each token, it does:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
This only checks that the external call did not revert (`success == true`); it never decodes `returndata` to confirm the token itself reported a successful transfer. On ERC20/TRC20 tokens whose `transfer()` returns `false` on failure rather than reverting, `success` is `true` and `returndata` decodes to `false`, but the code proceeds as if the transfer succeeded — exactly the unchecked-return-value class described in the referenced report (`_callOptionalReturn` decoding `results == false` while `success == true`).

Immediately after the faulty transfer check, escrow accounting is unconditionally decremented and the order is marked filled: [2](#0-1) [3](#0-2) 

The same unchecked pattern also appears in the fee payout inside `withdraw` and in the `SweepDust` handling branch of `onAccept`: [4](#0-3) [5](#0-4) 

Notably, this project elsewhere correctly relies on OpenZeppelin's `SafeERC20.safeTransfer`, which reverts on a `false` return, for the equivalent EVM-chain codepath: [6](#0-5) 

The Tron contract even imports `SafeERC20` and applies `using SafeERC20 for IERC20;` at the top of the file, but bypasses it for the payout path via a raw `.call`: [7](#0-6) 

`withdraw` is reachable from two unprivileged/relayer-triggered entry points: `onAccept` for `RedeemEscrow`/`RefundEscrow` requests delivered via Hyperbridge (i.e., relayed cross-chain messages that any relayer can submit once accompanied by a valid consensus proof), and `onGetResponse` for order-cancellation refunds: [8](#0-7) [9](#0-8) 

### Impact Explanation
If the escrowed token's `transfer()` returns `false` on failure (rather than reverting) — a real behavior for some TRC20/ERC20 tokens on Tron — the beneficiary's payout silently fails while the contract still marks the order `filled`/`refunded` and decrements `_orders[commitment][token]`. Because `_filled[commitment]` is set unconditionally and the escrow balance is reduced regardless of transfer outcome, there is no retry path: the tokens remain stuck in the `IntentGatewayV2` contract with no accounting entry pointing to them and no beneficiary able to reclaim them, i.e., a permanent freezing of escrowed user/solver funds. This satisfies the "permanent freezing of funds" criterion for the token-bridge/intents escrow codepath.

### Likelihood Explanation
This requires only that one of the tokens supported by the intent gateway on the Tron deployment implements the no-revert-on-failure `transfer()` semantics and that a transfer condition triggers failure (e.g., blacklist, pause, insufficient balance edge case, or any token-specific restriction) at the moment of payout. This is a single-transaction outcome triggered by any relayer submitting a normal `RedeemEscrow`/`RefundEscrow` message or `GET` response — no privileged role or malicious actor collusion is needed beyond the normal, permissionless relaying flow that Hyperbridge is designed to support. Likelihood is Medium (token/behavior dependent) but the impact (fund freezing) is severe given no in-repo mitigation exists in this exact file.

### Recommendation
Use `SafeERC20.safeTransfer` (which the file already imports and aliases via `using SafeERC20 for IERC20;`) for all outbound payouts in `withdraw()` and in the `SweepDust` branch of `onAccept`, instead of raw `.call()` with only `success` checked:
```solidity
IERC20(token).safeTransfer(beneficiary, amount);
```
This reverts the whole transaction if the token reports failure via either a revert or a `false` return, keeping escrow accounting and `_filled` state consistent with actual token movement, and avoiding permanently stranded escrow funds.

### Proof of Concept
1. Deploy `IntentGatewayV2` on Tron with an escrowed token `T` implementing `transfer()` that returns `false` on failure instead of reverting (e.g., due to an internal blacklist or paused state applied to the beneficiary at redemption time).
2. A user places an order and escrows `T` via `placeOrder`; solver fills it on the destination chain.
3. A relayer delivers the `RedeemEscrow` message via `onAccept`, which calls `withdraw(body, false)`.
4. Inside `withdraw`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `(true, abi.encode(false))` — the call succeeds but the token internally rejects the transfer.
5. Because only `success` is checked, `withdraw` proceeds: `_orders[commitment][token] -= amount;` and `_filled[commitment] = beneficiary;` execute despite the beneficiary never receiving `amount` of `T`.
6. The tokens remain locked in the `IntentGatewayV2` contract with no escrow record and no mechanism to reclaim them — permanent loss of the escrowed funds for that order.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-636)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-722)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-470)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```
