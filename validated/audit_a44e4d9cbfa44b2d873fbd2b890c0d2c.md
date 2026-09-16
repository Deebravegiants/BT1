Confirmed: this pattern in `evm/tron/contracts/apps/IntentGatewayV2.sol` is a real analog of the reported bug class. Let me verify the ERC20-return-value semantics one more time via the corresponding EVM (non-Tron) implementation to confirm the inconsistency is Tron-specific.### Title
Unchecked ERC20 return-value transfers in `withdraw`/`SweepDust` can permanently freeze escrowed user funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`evm/tron/contracts/apps/IntentGatewayV2.sol` imports and enables `SafeERC20` for `IERC20` and correctly uses `safeTransferFrom` for all inbound escrow deposits, but for outbound payouts in `withdraw()` and the `SweepDust` branch of `onAccept()` it instead performs raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks that the call did not revert (`success`), never decoding/validating the returned boolean. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
This is the exact bug class from the referenced Cooler.sol audit: unsafe (unchecked) ERC20 operations. Solidity's low-level `.call` only reports `success = true` if the callee did not revert; it does not verify the ABI-decoded boolean return value of `transfer`. Many real-world ERC20 tokens (e.g. tokens with blacklists, pausable transfers, or legacy tokens that follow the pre-EIP20 pattern of returning `false` instead of reverting on failure) can execute `transfer` successfully at the EVM-call level while returning `false` to signal a failed transfer. `IntentGatewayV2.withdraw()` treats any non-reverting call as a successful payout:

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [4](#0-3) 

Immediately after this unchecked "success," the function decrements the escrow accounting for the commitment:
```solidity
_orders[body.commitment][token] -= amount;
``` [5](#0-4) 

and marks the order as filled/refunded (`_filled[body.commitment] = beneficiary;`), emitting `EscrowReleased`/`EscrowRefunded`. [6](#0-5) [7](#0-6) 

`withdraw()` is reachable from two unprivileged, message-driven paths within `onAccept`, which is the entry point Hyperbridge's own relayers use to deliver cross-chain `RedeemEscrow`/`RefundEscrow` requests, and from `onGetResponse` for source-chain cancellation refunds:
```solidity
if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
    authenticate(incoming.request);
    WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
    return withdraw(body, kind == RequestKind.RefundEscrow);
}
``` [8](#0-7) 
```solidity
function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
    if (incoming.response.values[0].value.length != 0) revert Filled();
    WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
    withdraw(body, true);
}
``` [9](#0-8) 

The identical unchecked pattern is present in the `SweepDust` admin-message handler as well:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [10](#0-9) 

Notably, the same contract already imports `SafeERC20` and correctly uses `safeTransferFrom` for every inbound token pull (`placeOrder`, fill flows, fee escrow), demonstrating that the codebase is aware of the safe-ERC20 requirement but failed to apply it consistently to the outbound legs of the same escrow lifecycle: [11](#0-10) [12](#0-11) 

### Impact Explanation
If the escrowed output/input token is a non-standard ERC20 that returns `false` on a failed `transfer` call (rather than reverting) — for instance a token with a temporary transfer restriction, a blacklist hit on the beneficiary, a paused state, or any other soft-failure condition — `withdraw()` will still record `_orders[...] -= amount`, mark the commitment as filled/refunded, and emit the release/refund event, even though the beneficiary received zero tokens. Because the escrow slot is zeroed and the commitment is marked filled, the funds can never be reclaimed through any other code path (no retry mechanism exists once `_filled`/`_orders` state has been mutated). This is a permanent freezing/loss of escrowed user funds, matching the report's "loss of funds" impact class, and warrants Medium severity consistent with the original finding.

### Likelihood Explanation
Likelihood depends on the token used for an order's inputs/outputs (or the protocol fee token) exhibiting non-reverting failure semantics. While most mainstream tokens (USDC, DAI, WETH) revert on failure, several tokens in production DeFi (e.g., some deflationary/blacklist tokens, or legacy tokens implementing the return-false pattern) do not. Since `IntentGatewayV2` does not restrict which ERC20s can be used as order inputs/outputs, a solver or user placing an order in such a token — or a token later transitioning into a restricted/paused state for the specific beneficiary before settlement — can trigger this condition without any special privilege, satisfying the "unprivileged … intent solver" reachability requirement.

### Recommendation
Replace all raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` payout patterns in `withdraw()` and the `SweepDust` handler with `SafeERC20.safeTransfer`, which is already imported and used elsewhere in this same contract for inbound transfers:
```solidity
using SafeERC20 for IERC20;
...
IERC20(token).safeTransfer(beneficiary, amount);
```
This ensures both call-level reverts and ABI-decoded boolean failures are treated as failures, preventing escrow accounting from being mutated on a failed payout.

### Proof of Concept
1. Deploy an ERC20 token whose `transfer` function returns `false` (instead of reverting) when the recipient is on an internal deny-list, or when the contract is paused (many real tokens implement this pattern).
2. A user places a cross-chain order via `IntentGatewayV2.placeOrder`, escrowing this non-standard token as an input, using `safeTransferFrom` (succeeds normally).
3. A solver fills the order on the destination chain; Hyperbridge relays a `RedeemEscrow` request back to the source chain, invoked through `onAccept` → `withdraw(body, false)`.
4. Prior to delivery, the intended beneficiary (solver) address becomes deny-listed/paused on the escrowed token (e.g., due to an unrelated compliance action on the token side).
5. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `success = true` at the EVM level (the call itself doesn't revert) while the ABI-encoded return data is `false` and no tokens move.
6. `withdraw()` proceeds to execute `_orders[body.commitment][token] -= amount`, marks `_filled[commitment] = beneficiary`, and emits `EscrowReleased`. The escrowed tokens remain stuck in the `IntentGatewayV2` contract, unrecoverable by the beneficiary or the original depositor, constituting a permanent loss/freezing of funds.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L458-460)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L725-729)
```text
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
