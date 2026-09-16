### Title
Unchecked ERC20 `transfer` return value in `IntentGatewayV2.withdraw` (Tron) can falsely mark escrow as released without delivering tokens - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` imports and uses `SafeERC20` for escrow deposits (`safeTransferFrom` in `placeOrder`), but the escrow-release path in `withdraw()` and the `SweepDust` handler perform raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` calls and only check that the external call did not revert, never validating the boolean return value. This is precisely the "unchecked ERC20 transfer" bug class described in the external report (`CommunityRound.reserve` using unchecked ERC20 transfer instead of `SafeERC20`), reachable here by any relayer delivering an authenticated cross-chain settlement message.

### Finding Description
`withdraw()` is invoked from `onAccept` when a `RedeemEscrow`/`RefundEscrow` request is authenticated and delivered by a relayer [1](#0-0) . Inside `withdraw()`, ERC20 escrow payouts are performed with a raw `.call` and the code only reverts if the low-level call itself failed (`!success`), never inspecting/decoding the ABI-encoded boolean return data: [2](#0-1) 

The same unchecked pattern is used for fee-token payout in the same function [3](#0-2)  and for the governance-triggered `SweepDust` handler [4](#0-3) .

Any ERC20/TRC20 token that returns `false` on failure instead of reverting (a common pattern for older or non-standard tokens, and explicitly the pattern SafeERC20 exists to guard against) will cause this code to treat a failed transfer as successful: `success` from the low-level call is `true` (the call itself didn't revert, it just returned `false` in the payload), so the `if (!success) revert TransferFailed();` check passes, and the code proceeds to decrement `_orders[body.commitment][token] -= amount;` and mark `_filled[body.commitment] = beneficiary`, permanently finalizing the order despite the beneficiary never receiving the tokens. Notably, the contract already imports `SafeERC20` and uses `safeTransferFrom` for inbound escrow deposits [5](#0-4) , showing the intended safety pattern was simply not applied consistently to the outbound release path.

This differs from the mainline EVM `IntentsBase.sol` implementation, which correctly uses `IERC20(token).safeTransfer(beneficiary, amount)` in the equivalent `_withdraw` function [6](#0-5) , confirming the Tron contract is the outlier missing the SafeERC20 usage in this code path.

### Impact Explanation
If any escrowed input token or the fee token deviates from strict-revert-on-failure ERC20 semantics (returns `false` instead of reverting), the escrow accounting (`_orders[...]`) is decremented and the order is irreversibly marked `_filled` even though the beneficiary/solver never received their funds. Because `_filled` is checked to gate re-entry into `withdraw` (`UnknownOrder` / already-filled checks elsewhere in the order lifecycle), the user's or solver's escrowed tokens become permanently unrecoverable — a direct loss/freezing of funds for the affected party, matching the "permanent freezing of funds" impact class.

### Likelihood Explanation
Likelihood depends on the token's ERC20 implementation being listed/whitelisted for use with this Tron gateway; TRC20/ERC20-alike tokens with non-reverting failure semantics are not uncommon in the Tron ecosystem. The trigger requires only a normal, authenticated relayer-delivered `RedeemEscrow`/`RefundEscrow` message (no special privilege needed beyond normal protocol operation), making this reachable through the standard cross-chain settlement flow whenever such a token is configured as an order input or fee token.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check in `withdraw()` (both the token loop and the fee-token payout) and in the `SweepDust` handler with `IERC20(token).safeTransfer(beneficiary, amount)` using the already-imported `SafeERC20` library, consistent with `safeTransferFrom` used elsewhere in the same contract and with the mainline `IntentsBase._withdraw` implementation.

### Proof of Concept
1. Configure/whitelist an ERC20/TRC20 token (or fee token) whose `transfer` function returns `false` on failure rather than reverting (e.g., insufficient balance edge case, blacklist check, or a token contract that simply doesn't revert per legacy ERC20 style).
2. A user places an order and escrows this token via `placeOrder` (uses `safeTransferFrom`, so deposit succeeds normally) [7](#0-6) .
3. A relayer delivers an authenticated `RedeemEscrow`/`RefundEscrow` message that reaches `onAccept` → `withdraw()` [1](#0-0) .
4. Inside `withdraw()`, if the token's `transfer` call returns `false` (e.g., because the gateway's balance was drained/frozen through an unrelated path, or the token has some conditional transfer restriction) without reverting, `success` is still `true`, so `TransferFailed()` is not raised [2](#0-1) .
5. `_orders[body.commitment][token]` is decremented and `_filled[body.commitment]` is set to the beneficiary, permanently finalizing the order and emitting `EscrowReleased`/`EscrowRefunded`, even though the beneficiary's token balance never increased — the escrowed funds are stuck in the contract with no path to recovery.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-406)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-460)
```text
        } else {
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-710)
```text
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L719-722)
```text
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L465-469)
```text
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
