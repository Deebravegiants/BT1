Confirmed. The Tron variant of `IntentGatewayV2.withdraw()` and its `SweepDust` handler use a raw low-level `.call()` to invoke `IERC20.transfer` and only check that the *call itself* did not revert (`success`), never decoding/verifying the boolean return value of the ERC20 `transfer` function. This is the exact analog of the reported bug class.

### Title
ERC20 `transfer` return value not checked in Tron `IntentGatewayV2.withdraw()`/`SweepDust`, allowing escrow accounting to be burned without delivering funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.withdraw()` on the Tron deployment releases escrowed order tokens, refund tokens, and transaction fees to a beneficiary using a raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` and only checks the low-level `success` flag, never inspecting the returned `bool`. The same pattern is used in the `SweepDust` branch of `onAccept()`. Any ERC20/TRC20 token that returns `false` on a failed transfer instead of reverting (a well-documented pattern, e.g. classic USDT-style tokens common on Tron) will make this code treat a failed transfer as successful.

### Finding Description
In `withdraw()`: [1](#0-0) 
the code performs the transfer to `beneficiary` and then unconditionally decrements `_orders[body.commitment][token] -= amount;` regardless of whether the ERC20 `transfer` call actually moved tokens — it only reverts if the low-level call itself failed (e.g., target has no code, or the call reverted). If the token silently returns `false` instead of reverting on failure, `success` is still `true` and no error is raised.

The same unchecked pattern appears for transaction-fee redemption: [2](#0-1) 

and for governance-triggered dust sweeping: [3](#0-2) 

`withdraw()` is reachable by any relayer delivering a `RedeemEscrow` or `RefundEscrow` ISMP message via `onAccept()`: [4](#0-3) 
and also via `onGetResponse()` for source-chain cancellations: [5](#0-4) 

This contrasts with the non-Tron `IntentGatewayV2`/`IntentsBase` implementation, which correctly uses OpenZeppelin's `SafeERC20.safeTransfer`: [6](#0-5) 
`safeTransfer` decodes the return data and reverts if it is present and `false`, or if the call fails outright. The Tron file's raw `.call` pattern bypasses this protection entirely, even though it already imports and uses `SafeERC20 for IERC20` elsewhere in the same contract (e.g., `safeTransferFrom` on placeOrder paths), showing the omission here is inconsistent with the rest of the codebase's intended safety model.

### Impact Explanation
This is a High severity issue: since `_orders[body.commitment][token]` escrow accounting is decremented unconditionally, a solver or user beneficiary of a `RedeemEscrow`/`RefundEscrow`/cancellation flow can have their escrow balance zeroed out on-chain while no tokens are actually transferred to them if the underlying token silently fails the transfer (returns `false` without reverting). This permanently freezes/burns the escrowed funds — they can never be withdrawn again since the internal accounting has already been consumed — a direct, unrecoverable loss of user/solver funds. The same applies to escrowed protocol fees and to `SweepDust`-swept protocol dust.

### Likelihood Explanation
Reachability is high: `withdraw()` is invoked by the ordinary intent-fill/cancel/refund lifecycle, triggered by any relayer delivering an authenticated cross-chain message — no privileged role is required to trigger the call path itself. The likelihood of the underlying vulnerable condition (a whitelisted input/output token failing to revert on failed transfer) is dependent on which ERC20/TRC20 tokens are supported, but TRON's ecosystem has well-known token implementations (e.g., certain USDT-style TRC20 tokens) exhibiting exactly this no-revert-on-failure behavior, historically the root cause of the referenced report.

### Recommendation
Replace all raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` uses in `evm/tron/contracts/apps/IntentGatewayV2.sol` (in `withdraw()` for token payout, transaction-fee payout, and in the `SweepDust` handler in `onAccept()`) with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the rest of the codebase (`IntentsBase._withdraw`) which already uses `using SafeERC20 for IERC20;` and `safeTransfer`/`safeTransferFrom`.

### Proof of Concept
1. Deploy/whitelist a TRC20 token whose `transfer` function returns `false` on failure instead of reverting (e.g., insufficient balance edge case, paused state, or blacklist check that returns `false`).
2. User places an order on the Tron `IntentGatewayV2`, escrowing that token via `placeOrder` (uses `safeTransferFrom`, so escrow succeeds normally).
3. A solver fills the order cross-chain; Hyperbridge relays a `RedeemEscrow` message which reaches `onAccept()` → `withdraw()`.
4. If token `transfer(beneficiary, amount)` returns `false` (e.g., because the token contract has since paused, blacklisted the beneficiary, or hit some internal restriction) rather than reverting, `token.call(...)` still returns `success = true` (the call executed, it just returned encoded `false`), so `withdraw()` proceeds to `_orders[body.commitment][token] -= amount;` and emits `EscrowReleased`.
5. The beneficiary never actually receives the tokens, but the escrow record is now zero — the tokens are permanently stuck in the contract with no accounting path to recover them.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L717-723)
```text
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
