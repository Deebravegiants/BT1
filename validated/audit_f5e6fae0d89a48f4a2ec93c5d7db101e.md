### Title
Unchecked ERC-20 boolean return value in escrow withdrawal permanently burns solver/user funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`withdraw()` and the `SweepDust` handler in `evm/tron/contracts/apps/IntentGatewayV2.sol` release escrowed tokens using a raw low-level `.call` to `IERC20.transfer` and only check that the call did not revert (`success`), never decoding or validating the ERC-20's returned boolean. This is the exact "unchecked transfer return value" bug class from the referenced report, applied to Hyperbridge's intent-escrow withdrawal path instead of a bidder deposit path.

### Finding Description
In `withdraw()`, escrowed input tokens and transaction fees are paid out to the beneficiary/solver like this: [1](#0-0) 

and the fee-token payout: [2](#0-1) 

The `SweepDust` handler in `onAccept` has the identical pattern: [3](#0-2) 

In all three cases, `success` from `token.call(...)` only tells the caller whether the external call reverted — it says nothing about the ABI-encoded `bool` that a compliant ERC-20 `transfer` returns. Any token whose `transfer()` returns `false` on failure instead of reverting (a legal, non-reverting ERC-20 implementation, and a pattern explicitly exercised elsewhere in this same codebase's fee-on-transfer test tokens, e.g. `evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2718-2724`) will make `success == true` while no tokens actually move. Because `token` is attacker-controlled (`order.inputs[i].token`, set by whoever places the order), an order creator can escrow a token contract engineered to return `false` under certain conditions (e.g. once its internal balance/allowance bookkeeping detects an edge case) without reverting.

Once `withdraw()` observes `success == true`, it unconditionally decrements the internal accounting (`_orders[body.commitment][token] -= amount;`) and, for the fee case, `delete`s the fee entry — permanently erasing the record that tokens are still owed, even though the beneficiary/solver received nothing.

### Impact Explanation
This causes permanent loss of escrowed funds for the party expecting payment (the solver who filled a cross-chain order, or the user being refunded), because:
1. The `_orders` mapping is the sole source of truth used to gate/prevent double-withdrawal (`if (_orders[body.commitment][token] == 0) revert UnknownOrder();`), so once decremented there is no retry path.
2. `_filled[body.commitment]` is also set unconditionally at the top of `withdraw()`, marking the order as settled regardless of whether the transfer succeeded, closing off `cancelOrder`/refund routes.
3. The `withdraw()` function is the terminal, cross-chain-triggered settlement point for both `RedeemEscrow` and `RefundEscrow` messages, reachable by any relayer delivering a valid ISMP proof for an order that was placed with such a token — this is a normal unprivileged flow through the Intent Gateway, not a privileged/admin path.

This matches "permanent freezing of funds" per the validation criteria.

### Likelihood Explanation
Likelihood is moderate: it requires the order's escrowed/fee token to be one that returns `false` on failure instead of reverting (a real, documented ERC-20 behavior class, distinct from tokens with no return value at all which this pattern correctly tolerates). Since `order.inputs[i].token` is fully attacker-controlled by whoever creates the order, a malicious user could deliberately choose or deploy such a token to grief a solver who fills their order (solver pays real output tokens on the destination chain expecting escrowed input tokens on the source chain, but `withdraw()` silently no-ops the payout while marking the order filled).

### Recommendation
Use `SafeERC20.safeTransfer` (as already done correctly in `placeOrder`'s `safeTransferFrom` calls and in `evm/src/apps/intentsv2/IntentsBase.sol`) for all outbound token transfers in `withdraw()` and the `SweepDust` handler, so that both a reverting call and a `false` boolean return revert the whole withdrawal instead of silently succeeding.

### Proof of Concept
1. Attacker deploys a token `T` whose `transfer()` returns `false` (without reverting) whenever called by the `IntentGatewayV2` contract for amounts above some threshold, while behaving like a normal ERC20 for `transferFrom` during `placeOrder` (so escrow succeeds normally via `safeTransferFrom`).
2. Attacker places a cross-chain order with `T` as an input token, escrowing it via `placeOrder` (this path uses `safeTransferFrom` and succeeds normally).
3. A solver fills the order on the destination chain, delivering real output tokens to the beneficiary, per `_fillCrossChain` in `evm/src/apps/intentsv2/ExtrinsicIntents.sol:164-220`.
4. The `RedeemEscrow` message is relayed back to the source chain; `onAccept` calls `withdraw()` (`evm/tron/contracts/apps/IntentGatewayV2.sol:691-730`).
5. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, solver, amount))` returns `success = true` but the encoded return data is `false`, so no `T` tokens actually reach the solver.
6. `_orders[body.commitment][token] -= amount` still executes and `_filled[commitment]` is set, permanently closing the order — the solver has paid real value on the destination chain but receives nothing on the source chain, with no recovery path.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-676)
```text
                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
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
