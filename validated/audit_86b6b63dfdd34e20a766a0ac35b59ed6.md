### Title
Unchecked ERC20 `transfer()` boolean return in `withdraw()`/`onAccept` lets escrow/fee accounting decrement while token transfer silently fails - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed tokens and swept dust using a raw low-level `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks that the *call itself* did not revert (`success`), never that the ERC-20 `transfer` actually returned `true`. This is the same bug class as CVE-2023-52687 (`crypto: safexcel` failing to check `dma_map_sg()`'s return value before proceeding as if the operation had succeeded): a fallible primitive's failure signal is ignored, and the caller proceeds to mutate authoritative state as if the transfer succeeded.

### Finding Description
`withdraw()` [1](#0-0)  and the `SweepDust` branch of `onAccept()` [2](#0-1)  both perform:

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```

For any ERC-20 token that does not comply with the ERC-20 spec's revert-on-failure convention and instead returns `false` on a failed transfer (a well-documented and common pattern, e.g. some legacy tokens and any token specifically deployed to interact with this bridge), the low-level `.call` reports `success = true` (the call didn't revert) even though the token transfer did not happen. The code never decodes/validates the returned `bool` from `abi.decode(returnData, (bool))`, so this failure is invisible.

Despite the check being ignored, the function unconditionally proceeds to decrement escrow accounting:
```solidity
_orders[body.commitment][token] -= amount;
```
and marks the order `_filled[body.commitment] = beneficiary;`, emitting `EscrowReleased`/`EscrowRefunded`. The escrow ledger is now permanently zeroed for tokens that were never actually delivered to the beneficiary — the tokens remain stuck in the contract with no ledger entry pointing to them, and the beneficiary receives nothing.

Compare this to the sibling non-Tron `IntentGatewayV2.sol`/`IntentsBase.sol`, which consistently uses OpenZeppelin's `SafeERC20.safeTransfer` (which does verify the boolean return, or requires a revert) [3](#0-2) . The Tron file even imports `SafeERC20` and applies `using SafeERC20 for IERC20;` [4](#0-3)  for its `placeOrder`/escrow-crediting paths, but the withdrawal/redemption path (`withdraw()` and dust-sweep) was written with a raw, insufficiently-checked `.call` instead — an inconsistency that strongly suggests an oversight, matching the "missing error-handling check" bug class of the reference CVE rather than an intentional design choice.

### Impact Explanation
This is reachable by any relayer/user driving the normal ISMP delivery path: a `RedeemEscrow`, `RefundEscrow`, or `SweepDust` incoming request handled via `onAccept` (called by the host after message delivery) reaches `withdraw()`/the dust-sweep loop. If the token configured for an order (or the fee token) is one that returns `false` instead of reverting on transfer failure (e.g., due to insufficient balance from prior partial dust-sweeps, a paused/blacklisting token, or a token intentionally crafted this way), the contract will silently "release" escrow that was never transferred:
- Funds become permanently stuck in the contract (frozen), since `_orders[...]` accounting no longer reflects the un-delivered balance and no other code path can reclaim it.
- The order is marked `_filled`, blocking any legitimate retry/refund route, compounding the freeze.
- For the `SweepDust`/fee-redemption path, this can silently drop protocol/relayer fee payouts without any on-chain signal of failure.

This satisfies "permanent freezing of funds" from the validation criteria for a Medium/High severity analog.

### Likelihood Explanation
Exploitability depends on the specific ERC-20 token used for an order's input/output/fee token returning `false` rather than reverting on failed transfers — this is not universal but is a well-known, non-exotic behavior among ERC-20 tokens (particularly ones with additional access controls, e.g., blacklist-style compliance tokens, or tokens with balance edge cases). No malicious admin/governance/relayer action is required; the trigger is simply a normal escrow redemption or dust sweep involving an ERC-20 that follows this pattern. Given fee/dust tokens are configurable via governance (`_params.feeToken`, arbitrary order input/output tokens), a griefing/permanent-freeze scenario is plausible whenever such a token is in use.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check in `withdraw()` and the `SweepDust` branch of `onAccept()` with `SafeERC20.safeTransfer` (already imported and used elsewhere in the same file), which validates both call success and the returned boolean (or absence of return data per EIP-20 non-standard tokens), reverting the whole transaction — including the escrow-decrement and `_filled` state changes — if the transfer did not genuinely succeed.

### Proof of Concept
1. Deploy a non-standard ERC-20 token whose `transfer()` function returns `false` (instead of reverting) when the transfer cannot be completed (e.g., insufficient balance, paused state, or blacklisted recipient), and register it as an order's escrowed token or as the protocol fee token.
2. Have a user `placeOrder` with this token as input, and a solver `fillOrder` normally so that a subsequent `RedeemEscrow` (or `RefundEscrow`) request is dispatched cross-chain and delivered via `onAccept` → `withdraw()`.
3. Arrange for the token's internal state (e.g., temporarily paused, or beneficiary blacklisted) so that `transfer()` returns `false` at the moment `withdraw()` executes.
4. Observe that `withdraw()` does not revert: `success` is `true` (the call did not revert) even though no tokens moved; `_orders[body.commitment][token] -= amount` executes, `_filled[body.commitment]` is set, and `EscrowReleased` is emitted — while the beneficiary's token balance is unchanged and the tokens remain permanently locked in the `IntentGatewayV2` contract with no outstanding escrow record pointing to them.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-683)
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L465-469)
```text
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
