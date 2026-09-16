### Title
Reentrancy in `IntentGatewayV2.withdraw` allows draining escrowed funds via external call before state update - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` executes the token/native transfer to the beneficiary **before** decrementing the corresponding `_orders[commitment][token]` escrow balance, and unlike the canonical EVM `IntentGatewayV2` (which inherits `ReentrancyGuardTransient` and settles state before performing transfers in `IntentsBase._withdraw`), this contract has no reentrancy guard at all. This mirrors the analog bug class in ALPINE-CVE-2025-0665, where a single resource (an fd / here, an escrow balance) is released to the caller without the accounting being finalized first, letting the same resource be consumed more than once through a re-entrant callback.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `withdraw()` is invoked from `onAccept()` (for `RedeemEscrow`/`RefundEscrow` messages) and `onGetResponse()` — both `onlyHost`-gated, but neither the `IntentGatewayV2` contract nor its ancestors apply any reentrancy protection (`nonReentrant`/`ReentrancyGuardTransient`) anywhere in this file, confirmed by the absence of any `nonReentrant` match in the file. [1](#0-0) 

The vulnerable ordering:
```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    _filled[body.commitment] = beneficiary;

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

        _orders[body.commitment][token] -= amount;   // <-- state settled AFTER the external call
        ...
``` [1](#0-0) 

`beneficiary.call{value: amount}("")` (for the native-token branch) or a malicious/hookable ERC-20's `transfer()` hands execution control to attacker-controlled code **while `_orders[commitment][token]` still holds its pre-withdrawal (nonzero) value**. This is the same bug-class root cause as the CVE: the resource-release check (`_orders[...] == 0` revert / the fd-closed flag) is not updated before the release action completes, so a second concurrent release of the exact same resource succeeds.

By contrast, the production EVM version correctly follows checks-effects-interactions and is reentrancy-guarded:
```solidity
_orders[body.commitment][token] = escrowed - amount;
if (token == address(0)) {
    _sendValue(beneficiary, amount);
} else {
    IERC20(token).safeTransfer(beneficiary, amount);
}
``` [2](#0-1) 
and the top-level contract inherits `ReentrancyGuardTransient`: [3](#0-2) 

### Impact Explanation
An attacker who can be named as `beneficiary` of a `WithdrawalRequest` (any solver/user who fills or is refunded an order can set their own beneficiary address to a contract they control) can re-enter during the native-token `.call{value: amount}("")` callback (or via a token with a transfer hook) and trigger a second `onAccept`/`onGetResponse` delivery for the same `commitment`/token before `_orders[commitment][token]` is decremented, draining escrowed input tokens beyond what was actually deposited — a direct theft/loss of escrowed user funds, which is exactly the concrete-theft impact class required.

### Likelihood Explanation
Exploitability depends on being able to trigger `onAccept`/`onGetResponse` twice for the same commitment while the first call is still executing (e.g., via a relayer/host call path that permits nested dispatch, or a token whose `transfer()` calls back into the host). This requires the host/dispatcher call stack to permit reentrant delivery of a second message during the external call — a condition not fully verifiable from the available files alone. The absence of any reentrancy guard in this file, in contrast to the guarded canonical implementation, is nonetheless a genuine code-quality/security regression that should be treated as reachable given a hookable token or forwarding beneficiary contract.

### Recommendation
Apply the checks-effects-interactions pattern here exactly as done in `IntentsBase._withdraw`: decrement `_orders[body.commitment][token]` **before** performing the external call/transfer, and add a `nonReentrant` guard (e.g., `ReentrancyGuardTransient`) to `onAccept`/`onGetResponse`/`withdraw` in `evm/tron/contracts/apps/IntentGatewayV2.sol`, matching the mitigations already present in `evm/src/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Attacker places/fills an order such that they control the `beneficiary` address encoded in the `WithdrawalRequest` for a native-token (`token == address(0)`) escrow.
2. A relayer submits a valid `RedeemEscrow`/`RefundEscrow` proof, causing the host to call `onAccept` → `withdraw()`.
3. During `beneficiary.call{value: amount}("")` (line ~703), the attacker's contract's `receive()`/fallback re-enters the message-delivery path (via the host/handler) with a second, distinct but still-valid proof/message causing `withdraw()` to run again for the same `commitment`/`token` before `_orders[body.commitment][token] -= amount;` (line 710) has executed for the first call.
4. Because `_orders[commitment][token]` is still nonzero, the `UnknownOrder` check passes again and a second transfer of `amount` is sent to `beneficiary`, resulting in more funds paid out than were escrowed.

Note: full confirmation that the host/handler call stack actually permits a second, concurrent `onAccept` delivery for the same commitment during an in-flight external call was not verifiable from the indexed portions of `EvmHost.sol`/`HandlerV2.sol` alone; this should be validated against the complete dispatch code before treating likelihood as fully proven.

### Citations

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L24-60)
```text
import {ReentrancyGuardTransient} from "@openzeppelin/contracts/utils/ReentrancyGuardTransient.sol";
import {Initializable} from "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {IUniswapV2Router02} from "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
import {
    PaymentInfo,
    TokenInfo,
    DispatchInfo,
    Order,
    SweepDust,
    Params,
    ParamsUpdate,
    DestinationFee,
    WithdrawalRequest,
    FillOptions,
    SelectOptions,
    CancelOptions,
    Deployment
} from "@hyperbridge/core/apps/IntentGatewayV2.sol";

/**
 * @title IntentGatewayV2
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @dev The IntentGateway allows for the creation and fulfillment of same-chain & cross-chain orders.
 * This is the concrete entry-point contract that composes all intent logic via inheritance:
 *
 *            EIP712
 *              |
 *          IntentsBase
 *           /       \
 *  IntrinsicIntents  ExtrinsicIntents
 *           \       /
 *        IntentGatewayV2
 */
contract IntentGatewayV2 is IntrinsicIntents, ExtrinsicIntents, ReentrancyGuardTransient, Initializable {
```
