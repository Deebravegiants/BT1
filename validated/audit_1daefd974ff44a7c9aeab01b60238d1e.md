### Title
Unchecked ERC20 return value in `IntentGatewayV2.withdraw()` / `SweepDust` allows silent transfer failure for non-reverting tokens - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`, `evm/src/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2` uses a raw low-level `.call` to invoke `IERC20.transfer` when releasing escrowed funds to fillers/beneficiaries and when sweeping dust, but only checks that the call did not revert (`success`) — it never inspects the ABI-encoded boolean return value. Some ERC20 tokens return `false` on a failed transfer instead of reverting. For such tokens, `success` will be `true` even though no tokens moved, causing the gateway to mark the order as filled/refunded and decrement its escrow accounting while the beneficiary receives nothing.

### Finding Description
In `withdraw()`, both the escrowed-token payout loop and the transaction-fee payout use: [1](#0-0) 

```
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```

`success` here only reflects whether the external call reverted — it says nothing about the return data. A token whose `transfer` function returns `false` on failure (per the ERC20 spec, this is legal behavior; reverting is not mandated) will make this call succeed with `success == true`, so the `if (!success) revert TransferFailed()` guard never fires. Right after this, the code unconditionally decrements the internal escrow accounting: [2](#0-1) 

and marks the order as filled (`_filled[body.commitment] = beneficiary`) regardless of whether the transfer actually succeeded.

The identical unchecked pattern is used in the `SweepDust` handler: [3](#0-2) 

Both `withdraw()` and the `SweepDust` branch are reached from `onAccept`, which dispatches based on the ISMP request kind (`RedeemEscrow`, `RefundEscrow`, `SweepDust`) delivered via a relayed, proof-verified cross-chain message: [4](#0-3) 

The same `IERC20.transfer.selector` raw-call pattern (without decoding the returned bool) is also present in the non-Tron production contract `evm/src/apps/IntentGatewayV2.sol`, confirmed by grep matches for `TransferFailed`/`selector` there.

Elsewhere in the same codebase (e.g. `send()`/deposit paths, and `HyperFungibleToken`/`WrappedHyperFungibleToken`), the project correctly uses OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom`, which decode and check the return value: [5](#0-4) [6](#0-5) 

This inconsistency confirms the payout paths in `IntentGatewayV2.withdraw()`/`SweepDust` are the outlier that omits the return-value check.

### Impact Explanation
For any ERC20 that is fillable/escrowed via IntentGatewayV2 and that returns `false` instead of reverting on transfer failure (a legal ERC20 behavior — e.g., due to insufficient balance in an unusual edge case, paused/blacklisted-recipient tokens, or other conditionally-failing tokens), a relayed `RedeemEscrow`/`RefundEscrow`/`SweepDust` message will silently "succeed": the escrow ledger (`_orders[commitment][token]`) is decremented and the order is marked filled, but the beneficiary receives no tokens. This permanently locks/loses the escrowed funds — they are debited from the internal accounting without being delivered, and cannot be re-claimed since the order is already marked filled. This is a concrete freezing/loss-of-funds bug reachable by a normal relayer message delivery, not requiring any privileged role.

### Likelihood Explanation
The bug only manifests for ERC20 tokens that return `false` on failure rather than reverting, so it depends on the specific token being escrowed. However, IntentGatewayV2 is designed to support arbitrary listed tokens for cross-chain intents, and such non-reverting-failure tokens exist in the wild. Once a token behaves this way (or a transfer conditionally fails, e.g., blacklist/pause on the recipient side), every relayed withdrawal/refund/sweep for that token silently fails while accounting proceeds as if funds moved — this requires no attacker action beyond normal protocol operation, only reliance on the vulnerable code path being executed.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` handler with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the rest of the codebase (e.g., as already done in `WrappedHyperFungibleToken.onAccept`). This decodes and validates the return value (and also handles tokens that don't return a bool at all), ensuring escrow accounting is only decremented and orders only marked filled when the transfer genuinely succeeded.

### Proof of Concept
1. List a token `T` in `IntentGatewayV2` whose `transfer` implementation returns `false` on failure instead of reverting (this is spec-compliant ERC20 behavior).
2. A user creates an intent escrowing `T`; a filler fills it, and Hyperbridge relays a `RedeemEscrow` request to the source chain via `onAccept`.
3. If `T.transfer(beneficiary, amount)` returns `false` (e.g., because the beneficiary is blacklisted or some other spec-legal failure condition), the low-level `.call` still returns `success = true` since the callee did not revert: [7](#0-6) 
4. The `if (!success) revert TransferFailed()` check passes, `_orders[body.commitment][token] -= amount` executes, and `_filled[body.commitment] = beneficiary` is set — despite the beneficiary having received zero tokens.
5. The escrowed `T` tokens are now permanently unaccounted for: the order is marked filled/refunded so no retry is possible, and the beneficiary never receives their funds.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L630-635)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L249-251)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L320-324)
```text
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```
