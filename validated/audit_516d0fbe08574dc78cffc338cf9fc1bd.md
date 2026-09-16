This confirms the vulnerability pattern: `withdraw()` and `onAccept`'s `SweepDust` branch in `evm/tron/contracts/apps/IntentGatewayV2.sol` use raw low-level `.call()` for ERC-20 `transfer()` and only check that the call itself didn't revert (`success`), never decoding/checking the boolean return value that `transfer()` itself returns. This is distinct from the rest of the codebase (`evm/src/apps/IntentGatewayV2.sol`, `IntentsBase.sol`) which consistently uses OpenZeppelin's `SafeERC20.safeTransfer`, which *does* check the returned boolean and reverts on `false`.

### Title
Unchecked ERC-20 `transfer()` return value lets escrow be marked released without funds ever leaving the gateway - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` performs escrow payouts and dust sweeps via raw low-level `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` calls, checking only that the low-level call did not revert (`success`), but never decoding and validating the boolean value that the ERC-20 `transfer()` function itself returns. Non-reverting-on-failure ERC-20 tokens (which return `false` instead of reverting when a transfer fails, e.g. due to insufficient balance, blacklist, or paused state) will cause silent transfer failures that go completely undetected.

### Finding Description
In `withdraw()`: [1](#0-0) 

and in the `SweepDust` branch of `onAccept()`: [2](#0-1) 

and again for the transaction-fee payout: [3](#0-2) 

each of these does:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
`success` here only reflects whether the low-level call reverted or not; it is `true` whenever the target contract executes the `transfer` function without reverting — regardless of what boolean `transfer()` actually returned. Per ERC-20, a compliant token is permitted to return `false` on failure rather than reverting. Because the returned bytes are discarded (`(bool success,)`), a `token.transfer(...)` call that legitimately executes but returns `false` is treated as a fully successful transfer.

Immediately after this unguarded call, `withdraw()` unconditionally decrements the escrow accounting (`_orders[body.commitment][token] -= amount;`) and marks the order `_filled`/emits `EscrowReleased`/`EscrowRefunded`, permanently finalizing the order as settled even though no tokens were actually delivered to the beneficiary.

This contrasts with the rest of the codebase, e.g. `IntentsBase.sol`, which uses `SafeERC20.safeTransfer`, a wrapper that explicitly decodes and enforces the ERC-20 return value: [4](#0-3) 

### Impact Explanation
This is reachable by the ordinary, permissionless intent-fill/settlement flow: any relayer delivering a `RedeemEscrow`/`RefundEscrow` POST request, or a `GetResponse` for order cancellation, triggers `withdraw()`; any Hyperbridge-governed `SweepDust` action triggers the dust-sweep loop. If the escrowed input token (chosen by the user at `placeOrder` time, so effectively attacker-controlled) is a non-standard ERC-20 that returns `false` instead of reverting on failure, the beneficiary receives nothing while the protocol still finalizes the order as filled/refunded and zeroes out the escrow balance for that token. This permanently freezes/loses the escrowed funds — they are neither delivered to the beneficiary nor recoverable, since escrow accounting has already been decremented and the order marked filled.

### Likelihood Explanation
Medium. It requires the escrowed input token to be a non-reverting ERC-20 (a real, if not universal, class of tokens on EVM/Tron chains), and typically also requires some legitimate cause for a `transfer()` failure (e.g., token pausing, blacklisting a beneficiary, or a rare balance/rounding edge case). It does not require any privileged actor — a user placing an order with such a token, or a benign edge case on an otherwise normal token, is sufficient to trigger fund loss on the delivery/withdrawal path that any relayer executes.

### Recommendation
Use OpenZeppelin's `SafeERC20.safeTransfer` (already imported and used elsewhere via `using SafeERC20 for IERC20;` in this very file) instead of raw `token.call(...)` for all three transfer sites (`withdraw()`'s escrow loop, its fee payout, and the `SweepDust` branch), so that both call-reversion and a `false` return value cause the transaction to revert instead of silently finalizing escrow release.

### Proof of Concept
1. Deploy a minimal ERC-20-like token whose `transfer()` returns `false` on failure instead of reverting (e.g., returns `false` when `to` is blacklisted, or when balance is insufficient due to a fee-on-transfer quirk).
2. `placeOrder` an order using this token as an input, escrowing `amount` into `_orders[commitment][token]`.
3. Trigger settlement so that `onAccept`/`withdraw()` is invoked with this token in `body.tokens`, under conditions where the token's `transfer()` call returns `false` (e.g., the underlying implementation intentionally returns `false` instead of reverting for the beneficiary in question).
4. `token.call(...)` succeeds (`success == true`) even though the wrapped `transfer()` returned `false` and moved no funds.
5. `withdraw()` proceeds to decrement `_orders[commitment][token]` and emit `EscrowReleased`, permanently finalizing settlement — the beneficiary never receives the tokens, and the escrow can never be reclaimed since `_filled[body.commitment]` is now set.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-714)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L717-722)
```text
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
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
