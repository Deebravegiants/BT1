## Finding: ERC20 return value not checked on outbound transfers in Tron IntentGatewayV2 escrow withdrawal

### Title
Unchecked ERC20 `transfer` return value in `withdraw()`/`SweepDust` allows permanent loss of escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` uses OpenZeppelin's `SafeERC20.safeTransferFrom` for all *inbound* token transfers (escrow funding, fee collection), but reverts to raw low-level `.call()` for all *outbound* transfers in `withdraw()` and the `SweepDust` handler. These raw calls only check that the external call did not revert (`success`), never the ABI-decoded boolean return value of `transfer()`. Any token that signals failure by returning `false` instead of reverting will pass this check, causing the contract to permanently mark escrow as released/refunded while the beneficiary receives nothing.

### Finding Description
`IntentGatewayV2` imports and applies `SafeERC20` for inbound flows: [1](#0-0) 

Inbound token pulls correctly use `safeTransferFrom`, e.g. escrowing order inputs and fees: [2](#0-1) [3](#0-2) 

However, `withdraw()` — which pays out escrowed input tokens and fees to the beneficiary on `EscrowReleased`/`EscrowRefunded` — uses a raw `.call()` and only checks the boolean returned by the low-level call (i.e., "did the call revert"), not the ERC20 function's own return value: [4](#0-3) 

The same unchecked pattern is used in the `SweepDust` request handler: [5](#0-4) 

Because `success` here only reflects whether the target contract call reverted, a non-standard ERC20 that returns `false` on a failed transfer (rather than reverting) — for example due to insufficient balance edge cases, blacklists, paused states, or any custom failure semantics — will make `success == true` even though no tokens moved. The contract nonetheless decrements `_orders[commitment][token]`, deletes the fee entry, and emits `EscrowReleased`/`EscrowRefunded`, permanently closing out the order's accounting as if funds were paid, while the tokens remain stuck in the gateway.

`withdraw()` is reachable from `onAccept` (processing a relayer-delivered `RedeemEscrow`/refund POST request) and from `onGetResponse` (processing a relayer-delivered GET response proof) — both are triggered by an unprivileged relayer submitting a valid cross-chain message/proof, not by any privileged actor.

### Impact Explanation
This causes permanent freezing/loss of escrowed user or solver funds: the on-chain escrow accounting (`_orders[commitment][token]`) is zeroed and the release/refund event is emitted, but the actual ERC20 balance was never transferred to the beneficiary if the token returns `false` on failure. There is no retry path once the escrow slot is deleted, so the funds become permanently stuck in the `IntentGatewayV2` contract with no way for the beneficiary to reclaim them. This directly matches an "Accept only concrete theft or permanent freezing of funds" outcome for intents escrow, which is explicitly in scope.

### Likelihood Explanation
Likelihood depends on a token used as an order input/output/fee token implementing non-reverting failure semantics (return `false` instead of revert on failed transfer) — a known and not uncommon ERC20 implementation pattern (as cited in the original report referencing Aave and prior audits). Since `IntentGatewayV2` supports arbitrary ERC20 tokens configured by users placing orders (not just a fixed allowlist), any such token used as an input asset or fee token exposes this path. The trigger requires no special privilege — any relayer delivering a valid `RedeemEscrow`/refund message or GET response naturally invokes `withdraw()`.

### Recommendation
Replace the raw `.call()` outbound transfer pattern in `withdraw()` and the `SweepDust` handler with `SafeERC20.safeTransfer`, consistent with how inbound transfers already use `SafeERC20.safeTransferFrom` elsewhere in the same contract:
```diff
- (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
- if (!success) revert TransferFailed();
+ IERC20(token).safeTransfer(beneficiary, amount);
```
Apply the same fix to the fee-token transfer in `withdraw()` and to the token branch of `SweepDust`.

### Proof of Concept
1. Deploy a mock ERC20 whose `transfer()` returns `false` on failure instead of reverting (e.g., when the recipient is blacklisted or a custom condition triggers), while still returning `true` on normal success.
2. Place an order on the Tron `IntentGatewayV2` using this token as an input asset; escrow is funded via `safeTransferFrom`, which succeeds normally.
3. Trigger a condition under which the token's `transfer()` call to the beneficiary returns `false` (e.g., beneficiary temporarily blacklisted, or contract-specific failure condition) at the moment a relayer delivers the corresponding `RedeemEscrow`/refund message invoking `withdraw()`.
4. Observe: `token.call(...)` returns `success = true` (the call itself didn't revert), so `withdraw()` proceeds to decrement `_orders[commitment][token]` to zero and emit `EscrowReleased`/`EscrowRefunded`, even though the beneficiary's token balance did not increase.
5. The tokens remain locked in the gateway contract with no escrow record left to reclaim them — permanent loss of funds.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-460)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-488)
```text
        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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
```
