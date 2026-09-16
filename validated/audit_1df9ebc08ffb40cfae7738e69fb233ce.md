### Title
Unsafe low-level `transfer` (no return-data check) for escrow payouts and fee/dust transfers in Tron `IntentGatewayV2` - (`File: evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` pays out escrowed ERC20/TRC20 tokens (order proceeds, protocol fees, and swept dust) using a raw low-level `.call()` encoded with the `transfer` selector, and only checks that the call did not revert (`success`). It never decodes/validates the returned boolean. Any TRC20/ERC20 whose `transfer` implementation returns `false` on failure instead of reverting will cause the gateway to treat a failed payout as successful, permanently corrupting escrow accounting and freezing user/solver funds.

### Finding Description
`withdraw()` releases escrowed input tokens and transaction fees to a beneficiary after a `RedeemEscrow`/`RefundEscrow` message is authenticated: [1](#0-0) 

For every non-native token it does:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
This only checks whether the external call reverted; it does **not** decode the returned bytes into a `bool`. If the token contract does not revert on a failed transfer but instead returns `false` (a well-known non-standard/legacy ERC20 behavior, and explicitly the failure mode called out in the referenced audit report for upgradable tokens like USDC), `success` will still be `true`. The function then unconditionally decrements the escrow (`_orders[body.commitment][token] -= amount`) and marks the order as filled (`_filled[body.commitment] = beneficiary`) even though no tokens actually moved.

The same unsafe pattern is used for the `SweepDust` admin-message handler: [2](#0-1) 

Notably, this is inconsistent with the deposit/escrow-creation side of the very same contract, which correctly uses `SafeERC20.safeTransferFrom`: [3](#0-2) 

and with the canonical EVM `IntentsBase._withdraw`, which uses `safeTransfer`: [4](#0-3) 

So the Tron `IntentGatewayV2` deliberately imports `SafeERC20` (`using SafeERC20 for IERC20;`) but bypasses it specifically for outbound escrow release, fee payout, and dust sweeping, reintroducing exactly the "unsafe transfer" class from the referenced report.

### Impact Explanation
Once a token used in an intent (input token or the protocol fee token) exhibits the "return false instead of revert" failure mode — which is common among non-standard ERC20/TRC20 tokens and is the exact behavior the cited report warns can appear in upgradable stablecoins — the contract will:
1. Mark the order as filled/refunded (`_filled[body.commitment] = beneficiary`), preventing any retry, since `onGetResponse`/other logic checks `_filled` to reject reprocessing.
2. Decrement internal escrow accounting as if funds were paid out.
3. Never actually deliver the tokens to the beneficiary (solver or user).

This results in permanent loss of the escrowed funds for the intended recipient, with no rescue mechanism, matching the "permanent freeze/loss of funds" impact bar for Medium/High severity.

### Likelihood Explanation
This path is reachable by any relayer delivering a legitimate `RedeemEscrow`/`RefundEscrow` ISMP message for an intent that used a non-strictly-reverting token as input or as the fee token — no privileged role is required to trigger it; it fires during normal, expected withdraw/fill/refund flow. The likelihood is tied to token behavior rather than an attacker action, but Tron's TRC20 ecosystem includes tokens with non-standard/legacy transfer semantics, making this a realistic trigger condition rather than a purely theoretical one.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` handler with `SafeERC20.safeTransfer` (already imported and used elsewhere in the same contract), which correctly verifies both call success and, when return data is present, that it decodes to `true`.

### Proof of Concept
1. Create an intent whose input token (or the configured fee token) is a TRC20/ERC20 implementation that returns `false` on a failed `transfer` instead of reverting (e.g., due to a blacklist, paused state, or insufficient contract balance edge case introduced by an upgrade).
2. Complete the intent normally so tokens are escrowed via `safeTransferFrom` in the deposit path.
3. Trigger fulfillment/cancellation so a `RedeemEscrow`/`RefundEscrow` ISMP message is delivered and `withdraw()` executes.
4. When the token's `transfer` call returns `false` without reverting, `token.call(...)` still reports `success = true`; `withdraw()` proceeds to decrement `_orders[...]` and set `_filled[commitment] = beneficiary`, while the beneficiary's token balance never increases — the escrowed funds are permanently stuck with no retry path.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-722)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L463-469)
```text

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
