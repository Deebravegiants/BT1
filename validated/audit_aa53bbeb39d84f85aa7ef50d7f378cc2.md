### Title
Non-standard ERC20 return values are not validated in Tron `IntentGatewayV2.withdraw()` and `SweepDust`, allowing escrow funds to be marked settled without actual transfer - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` uses `SafeERC20` throughout `placeOrder`/`fillOrder` for pulling and forwarding tokens, but the internal `withdraw()` function (used for `RedeemEscrow`/`RefundEscrow` settlement) and the `SweepDust` handler bypass `SafeERC20` and instead perform raw low-level calls, checking only that the call itself did not revert (`success`) without decoding/validating the returned boolean.

### Finding Description
In `withdraw()`, escrowed tokens are released to a beneficiary via: [1](#0-0) 

and accumulated fees are released the same way: [2](#0-1) 

The same pattern appears in the `SweepDust` admin-triggered handler: [3](#0-2) 

In every case, the code does `(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...)); if (!success) revert TransferFailed();`. This only checks whether the low-level call reverted — it never inspects `returndata` to confirm the token actually returned `true`. Any ERC20 implementation that signals failure by returning `false` (rather than reverting) will pass this check silently: `success` will be `true` (the call did not revert) even though the token transfer did not occur.

Meanwhile, `withdraw()` unconditionally decrements the escrow accounting before/alongside this unchecked transfer: [4](#0-3) 

and marks the order as filled/refunded: [5](#0-4) 

This is exactly the bug class from the referenced report: relying on ad-hoc success checks against low-level `IERC20.transfer` calls instead of `SafeERC20.safeTransfer`, which correctly reverts on both no-return-data and explicit `false`-return failures. This contract already imports and uses `SafeERC20` elsewhere (`placeOrder`/`fillOrder` use `safeTransferFrom`), showing the intended pattern, but `withdraw()`/`SweepDust` deviate from it for the outbound legs.

### Impact Explanation
Because `_orders[commitment][token]` is decremented and `_filled[commitment]` is set to the beneficiary regardless of whether the token transfer actually succeeded semantically (returned `true`), a token that returns `false` on failure (insufficient balance in the gateway due to a bug/edge case, blacklist, paused state, etc., depending on the token implementation) will result in the escrowed funds being permanently stuck: the order is marked settled/refunded, so the same `commitment` can never be withdrawn again, yet the beneficiary never actually received the tokens. This is a permanent freezing/loss-of-funds condition affecting user-escrowed and solver-earned funds routed through the Tron IntentGateway.

### Likelihood Explanation
Likelihood depends on whether any token supported by the Tron IntentGateway deployment returns `false` instead of reverting on transfer failure (a legitimate, EIP-20-compliant behavior that several real-world tokens exhibit). Given the protocol is designed to be permissionless with respect to which ERC20s can be escrowed/settled (`placeOrder` accepts arbitrary `TokenInfo.token` addresses), and it already treats fee-on-transfer and other non-standard token behaviors as first-class considerations elsewhere in the codebase, integrating with such a token is a realistic operational scenario rather than a purely theoretical one.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check in `withdraw()` and `SweepDust` with `SafeERC20.safeTransfer`, consistent with the rest of the contract (and consistent with the main-chain `evm/src/apps/intentsv2/IntentsBase.sol` `_withdraw()` implementation, which already correctly uses `IERC20(token).safeTransfer(beneficiary, amount)`): [6](#0-5) 

### Proof of Concept
1. Deploy (or use) an ERC20 token whose `transfer` function returns `false` on failure instead of reverting (EIP-20-compliant behavior).
2. A user places an order on the Tron `IntentGatewayV2` escrowing this token via `placeOrder`, which correctly uses `safeTransferFrom` to pull funds in.
3. A condition causes the token's internal `transfer` to fail and return `false` when the gateway tries to pay out the beneficiary in `withdraw()` (e.g., a paused/blacklist state on the token side that arises between escrow and settlement).
4. `withdraw()`'s low-level call succeeds (no revert) but the token itself returns `false`; the code does not check this and proceeds to decrement `_orders[...]`, set `_filled[commitment]`, and emit `EscrowReleased`/`EscrowRefunded`.
5. The beneficiary never receives the tokens, and because the commitment is now marked as filled/refunded, there is no remaining code path to retry or reclaim the escrowed balance — the funds are permanently stuck in the contract's balance while accounting shows them as already paid out.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-694)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L695-714)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-723)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
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
