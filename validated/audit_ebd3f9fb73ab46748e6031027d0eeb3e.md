### Title
Unchecked ERC20 `transfer` Return Value in `IntentGatewayV2.withdraw`/`onAccept` Can Permanently Freeze Escrowed Funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.withdraw` (and the `SweepDust` branch of `onAccept`) on the Tron variant of the intent gateway release escrowed tokens using a raw low-level `.call` to the ERC20 `transfer` selector, checking only that the call did not revert (`success`) but never decoding/validating the returned boolean. Escrow accounting and the "filled/redeemed" state are updated unconditionally right after, regardless of whether the token actually moved.

### Finding Description
In `withdraw`, called from `onAccept` for `RedeemEscrow`/`RefundEscrow` requests and from `onGetResponse` for cancellations, tokens are released via: [1](#0-0) 

```solidity
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}
_orders[body.commitment][token] -= amount;
```

`success` here only reflects whether the external call reverted, not the ERC20 `transfer` function's boolean return value. Per ERC20 (and unlike `SafeERC20.safeTransfer`, which decodes and validates the return data), some non-standard/legacy tokens return `false` instead of reverting on a failed transfer (e.g. under certain edge conditions, pausable/blacklist-style tokens, or tokens with idiosyncratic failure semantics). With this pattern, such a `false` return is silently treated as success.

Critically, `_filled[body.commitment] = beneficiary;` is set unconditionally at the top of `withdraw`, and `_orders[body.commitment][token] -= amount;` is decremented immediately after the unchecked call — both irreversibly marking the order as settled and the escrow as spent, even if the token transfer produced no actual balance change for the beneficiary. [2](#0-1) 

The same unchecked-success pattern (call succeeds but return data ignored) also appears in the fee-token release path and in the `SweepDust` handler: [3](#0-2) [4](#0-3) 

By contrast, the token-escrow *inbound* path in the same contract and in the EVM `IntentGatewayV2` correctly uses `SafeERC20.safeTransferFrom`, which reverts on a `false` return value: [5](#0-4) 

This inconsistency — safe transfer semantics on deposit, unchecked raw call on withdraw/redeem — is the root cause.

### Impact Explanation
If the escrowed token silently returns `false` on `transfer` failure (rather than reverting), the beneficiary receives nothing while:
- the order's `_filled` mapping is set, permanently preventing any future retry/redemption of that commitment, and
- `_orders[body.commitment][token]` is decremented, permanently zeroing out the internal escrow accounting for those funds.

The token remains physically locked in the `IntentGatewayV2` contract with no code path left to recover it for that commitment, since the withdrawal is considered already completed. This is a permanent freezing of escrowed funds reachable by a relayed `RedeemEscrow`/`RefundEscrow` message or GET-response-driven cancellation — a normal, unprivileged flow of the intent-fulfillment protocol.

### Likelihood Explanation
This triggers only for tokens whose `transfer` implementation can return `false` without reverting — a real but non-universal category of ERC20 tokens. Given intent gateways are designed to be permissionless and support arbitrary listed input tokens across chains, a token operator or governance configuring an inputs list is not guaranteed to exclude such tokens, and the loss condition requires no attacker action beyond a normal transfer being met by unusual token behavior (e.g. a paused/blacklisted state at redemption time). This gives it a plausible, if not certain, likelihood — warranting High severity for the potential of permanent, irreversible fund loss when it does occur.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check with `SafeERC20.safeTransfer` (already imported via `using SafeERC20 for IERC20;` in this contract) in `withdraw` (token loop and fee release) and in the `SweepDust` branch of `onAccept`, so that both call-reverted and returned-false failure modes revert the transaction and no escrow state is mutated on a failed transfer.

### Proof of Concept
1. Governance/operator adds a non-standard ERC20 token (one that returns `false` on failed `transfer` rather than reverting) as a valid intent input/output token.
2. A user places an order escrowing that token via `placeOrder`; a solver fills it, and a `RedeemEscrow` (or `RefundEscrow`) request is dispatched and delivered through Hyperbridge to `onAccept`.
3. At the time of settlement the token's `transfer` call to the beneficiary returns `false` (e.g., beneficiary temporarily blacklisted, or any other condition the token encodes as a `false` return instead of a revert).
4. `withdraw` observes `success == true` (the low-level call itself didn't revert) and proceeds to set `_filled[body.commitment] = beneficiary` and decrement `_orders[body.commitment][token] -= amount`, despite the beneficiary balance being unchanged.
5. The escrowed tokens remain stuck in the `IntentGatewayV2` contract; the commitment is now marked filled/redeemed, so there is no remaining path to reclaim the funds for that order.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L455-460)
```text
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-700)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-710)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-722)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
