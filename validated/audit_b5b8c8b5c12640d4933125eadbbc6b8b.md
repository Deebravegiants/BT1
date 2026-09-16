### Title
Unchecked ERC20 `transfer` return value in Tron `IntentGatewayV2.withdraw`/`SweepDust` permanently freezes escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` moves escrowed ERC20/TRC20 tokens out with a raw low-level `.call` to the `transfer` selector and only checks that the call did not revert, never decoding the returned boolean. Any token that returns `false` on a failed transfer instead of reverting (blacklisted recipient, paused token, insufficient internal balance, etc.) will be treated as a successful payout even though no tokens moved, while the contract still marks the order `_filled` and decrements the escrow accounting. This permanently locks the escrowed tokens in the contract with no path to retry or recover them.

### Finding Description
`withdraw()` is invoked from `onAccept` when a `RedeemEscrow`/`RefundEscrow` message is delivered by a relayer, and from `onGetResponse` after a cancellation storage-proof response is delivered: [1](#0-0) 

```
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    address beneficiary = ...;
    _filled[body.commitment] = beneficiary;
    ...
    } else {
        (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
        if (!success) revert TransferFailed();
    }
    _orders[body.commitment][token] -= amount;
    ...
```

`success` here only reflects that the external call did not revert; it does not decode/verify the `bool` payload that a standards-compliant `transfer()` returns. A token contract that returns `false` (rather than reverting) on a failed transfer — this is explicit ERC-20 spec behavior, and real tokens implement it this way — makes `success == true` even though the beneficiary received nothing. The function nevertheless:
1. Sets `_filled[body.commitment] = beneficiary`, marking the order permanently resolved.
2. Decrements `_orders[commitment][token] -= amount`, erasing the escrow record.
3. Emits `EscrowReleased`/`EscrowRefunded`.

Because `_filled` is now non-zero, any later `cancelOrder` call reverts with `Filled`, and there is no other function that re-attempts the transfer for that commitment. The tokens remain stuck in the contract's balance with no beneficiary path and no user-facing recovery mechanism.

The same unchecked pattern is repeated in the `SweepDust` handler and in the predispatch dust-forwarding calls, so the same class of bug affects protocol-controlled dust sweeps too: [2](#0-1) 

This is a clear deviation from the sibling EVM implementation of the same protocol, `evm/src/apps/intentsv2/IntentsBase.sol`, which correctly uses OpenZeppelin's `SafeERC20.safeTransfer` (reverts if the token returns `false`): [3](#0-2) 

The Tron contract even imports `SafeERC20` and uses `safeTransferFrom` for inbound escrow deposits, but deliberately switches to the raw, return-value-ignoring `.call` pattern for outbound transfers: [4](#0-3) [5](#0-4) 

### Impact Explanation
Escrowed user funds (order inputs) can become permanently unreachable: the accounting marks the order filled/refunded and the escrow balance zeroed, but the tokens sit in the contract with no beneficiary credit and no retry path. This is a permanent freezing-of-funds condition reachable by any relayer delivering a legitimate `RedeemEscrow`/`RefundEscrow` message once a non-standard/false-returning token is used as an order input — no malicious relayer or governance action is required, only a token whose `transfer` can return `false`.

### Likelihood Explanation
Triggering requires an ERC20/TRC20-input token whose `transfer()` implementation returns `false` on failure (common on TRON where token behavior is inconsistent, and among tokens with recipient blacklists/pauses) combined with a transient failure condition on the beneficiary side (blacklist, pause, etc.) at redemption time. This is a realistic operational condition for a cross-chain intents system accepting arbitrary listed tokens, not a contrived edge case, though it needs an incompatible token to be listed/used as input.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()`, the `SweepDust` branch of `onAccept`, and the predispatch dust-forwarding loop with `SafeERC20.safeTransfer`/`safeTransferFrom` (already imported and used elsewhere in the same file), so a `false` return value reverts the whole `onAccept`/`withdraw` call instead of silently finalizing a phantom payout.

### Proof of Concept
1. List a TRC20 token as an order input whose `transfer()` returns `false` (rather than reverting) when the recipient is blacklisted/paused, e.g. a mock `FalseReturnToken`.
2. `placeOrder` escrows the token normally via `safeTransferFrom`.
3. Fill/redeem path triggers `onAccept(RedeemEscrow)` → `withdraw()`; blacklist the beneficiary right before delivery so `token.transfer(beneficiary, amount)` returns `false` but does not revert.
4. Observe: `success == true` (call didn't revert), `_filled[commitment]` is set, `_orders[commitment][token]` is decremented, `EscrowReleased` is emitted — yet `beneficiary`'s token balance is unchanged and the tokens remain in the contract with no function able to move them out again for that commitment.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L405-405)
```text
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
