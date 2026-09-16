### Title
Wrong escrow validation in Tron `IntentGatewayV2.withdraw()` enables reentrant double-spend of escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron fork of `IntentGatewayV2.withdraw()` validates escrow sufficiency incorrectly, checking only that the per-token escrow balance is non-zero (`_orders[body.commitment][token] == 0`) instead of verifying it is at least the amount being paid out. Combined with performing the external value/token transfer *before* decrementing the escrow, this "wrong comparison" bug — structurally the same class as the ether-fi finding, which compared `balanceOf` against the wrong variable — allows a malicious beneficiary contract to reenter and drain escrowed funds multiple times.

### Finding Description
`withdraw()` in the Tron `IntentGatewayV2.sol` is reached from `onAccept()` for `RedeemEscrow`/`RefundEscrow` messages and from `onGetResponse()` for cancellations: [1](#0-0) 

The relevant check is:
```solidity
if (_orders[body.commitment][token] == 0) revert UnknownOrder();
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    ...
}
_orders[body.commitment][token] -= amount;
```

Like the ether-fi bug, which checked `eETH.balanceOf(msg.sender) < _amount` instead of `< share`, this check validates the *wrong quantity*: it only confirms the escrow slot is non-zero, never that it holds at least `amount`. Worse, unlike the original bug (which caused an unwanted revert), the external call to `beneficiary` for native-token payouts happens **before** `_orders[body.commitment][token]` is decremented, and there is no `nonReentrant` guard on `onAccept`/`onGetResponse`/`withdraw` in this file. A beneficiary that is a malicious contract can, inside its `receive()`/fallback triggered by `beneficiary.call{value: amount}("")`, re-enter through another relayed `RedeemEscrow`/`RefundEscrow` message (or `onGetResponse`) for the same commitment before the escrow balance is reduced. Because the guard only checks "is escrow non-zero," and the balance has not yet been decremented, the second call passes the same check and pays out `amount` again, repeating until the escrow is drained beyond what was actually deposited, or until gas/call-depth limits are hit.

Compare with the equivalent EVM path in `IntentsBase._withdraw`, which at least reads the escrow first and computes `escrowed - amount` (reverting via Solidity 0.8 checked arithmetic on underflow) with effects before any external call ordering discipline more consistent with checks-effects-interactions: [2](#0-1) 
The Tron contract diverges from this by doing the transfer first and never validating `amount <= escrowed`, reproducing the "compare against the wrong bound" defect that Solidity's own underflow protection can no longer save because the subtraction runs after the funds have already left.

### Impact Explanation
An attacker who can get itself named as `beneficiary` of a `WithdrawalRequest` (a legitimate solver filling a cross-chain order, or the user themselves on a refund/cancel path) can reenter `withdraw()` before the escrow decrement lands, resulting in multiple payouts against a single escrowed balance. This is concrete theft of escrowed user/solver funds from the IntentGateway's token/native balance, draining assets that back other users' pending orders — a direct loss-of-funds vulnerability reachable by any user who places or fills an intent order on the Tron deployment.

### Likelihood Explanation
This is reachable by a completely unprivileged actor: any user can place an order and control the destination `beneficiary` address used in `fillOrder`/`cancelOrder`, which becomes the target of the vulnerable `withdraw()` call once the settlement/cancellation message is delivered by a relayer. No special privileges, governance, or malicious relayer/node behavior are required — only a beneficiary contract with a reentrant `receive()`/token hook and normal use of the documented fill/cancel flow.

### Recommendation
Follow checks-effects-interactions: read `escrowed = _orders[body.commitment][token]`, revert if `escrowed < amount` (not just `== 0`), decrement `_orders[body.commitment][token]` to `escrowed - amount` **before** making the external call/transfer, and add a reentrancy guard (`nonReentrant`) on `onAccept`, `onGetResponse`, and `withdraw`, mirroring the pattern already used in `IntentsBase._withdraw` on the main EVM contract.

### Proof of Concept
1. User places a cross-chain order; solver fills it on the destination chain, naming a malicious contract address as the intended beneficiary of the resulting `RedeemEscrow` settlement (or a malicious user cancels their own order to become `beneficiary` of a `RefundEscrow`/GET-response refund).
2. A relayer delivers the `RedeemEscrow`/`RefundEscrow` POST (or GET response) to the Tron `IntentGatewayV2`, invoking `onAccept`/`onGetResponse` → `withdraw(body, ...)`.
3. Inside `withdraw`, for the native-token branch, `beneficiary.call{value: amount}("")` executes before `_orders[body.commitment][token] -= amount`.
4. The malicious beneficiary's fallback function calls back into the ISMP host (or directly, if callable) to trigger another delivery of a `RedeemEscrow`/`RefundEscrow`/GET-response message referencing the *same* `commitment`/`token`.
5. Because `_orders[body.commitment][token]` has not yet been decremented, the `== 0` check still passes, and `withdraw` sends `amount` again.
6. Repeat until the escrow balance for that token/commitment is drained beyond the originally escrowed amount, at the expense of the gateway's overall token/native balance backing other orders.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-469)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
