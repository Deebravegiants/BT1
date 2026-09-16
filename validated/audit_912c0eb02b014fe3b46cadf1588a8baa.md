### Title
Fee-on-transfer output tokens let a solver finalize an order and drain the full escrow while the beneficiary receives less than the promised amount - (File: `evm/src/apps/intentsv2/IntrinsicIntents.sol`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`placeOrder` in `IntentGatewayV2.sol` was explicitly hardened to support fee-on-transfer tokens on the **input** side: it measures the gateway's balance before/after the `safeTransferFrom` and uses the actual received amount for the commitment and escrow accounting [1](#0-0) . The **output** side of order fulfillment (`_fillSameChain` and `_fillCrossChain`) has no equivalent handling: it transfers the nominal `totalRequired`/`beneficiaryTotal` amount via `safeTransferFrom` and then unconditionally treats the order as fully paid, regardless of what the beneficiary actually received.

### Finding Description
In `IntrinsicIntents._fillSameChain`, the solver's output payment is sent with: [2](#0-1) 
and the fill is immediately recorded as complete using the *requested* `fillAmount`/`totalRequired`, not the actual balance delta at the beneficiary: [3](#0-2) 

The escrowed inputs are then released in full to the solver via `_withdraw`, since `amountFilled == totalRequired` is computed from the nominal amount, not from what the beneficiary actually holds.

The same pattern exists in `ExtrinsicIntents._fillCrossChain`: [4](#0-3) 
`outputFills[i]` is recorded with `totalRequired` and a `RedeemEscrow` message is dispatched to the source chain to release 100% of the user's escrowed input to the solver, even though the actual amount delivered to `beneficiary` may be less due to a transfer fee.

If `order.output.assets[i].token` is a fee-on-transfer (deflationary) ERC20, `safeTransferFrom(msg.sender, beneficiary, totalRequired)` delivers `totalRequired - fee` to the beneficiary, yet the contract still finalizes the fill and releases the full escrowed input amount from `_orders[commitment][...]` to the solver — a direct value mismatch between what the order beneficiary received and what the order originator's escrow paid out.

### Impact Explanation
The order's beneficiary receives strictly less than the amount they were promised (`order.output.assets[i].amount`) while the full escrowed input collateral is unconditionally transferred to the solver and the order is marked filled/redeemed, with no mechanism to reclaim the shortfall. This is a direct loss of funds for the order placer/beneficiary — comparable to the referenced Sherlock finding where `CollateralEscrowV1` trusted a nominal amount instead of the actual balance delta, causing value to be lost on fee-on-transfer tokens. Because the escrow release is irreversible (same-chain: immediate `_withdraw`; cross-chain: `RedeemEscrow` message dispatched via Hyperbridge to release escrow on the source chain), the beneficiary has no recourse once the fill is finalized.

### Likelihood Explanation
Any order whose `output.assets` token is a fee-on-transfer/deflationary ERC20 is affected on every fill — no special solver behavior or malicious intent is required, since `_fillSameChain`/`_fillCrossChain` never validate what was actually received before finalizing. Given the contest/protocol's own comment that fee-on-transfer tokens must be supported ("For fee-on-transfer tokens, the gateway receives less than the requested amount" — explicitly handled for inputs in `IntentGatewayV2.placeOrder`), this is a realistic and directly reachable configuration, not a contrived edge case. Any unprivileged solver filling such an order (intentionally or not) triggers the shortfall.

### Recommendation
In `_fillSameChain` and `_fillCrossChain`, measure the beneficiary's balance before and after each output token transfer (the same pattern already used in `placeOrder` for inputs) and use the actual delivered amount to determine `amountFilled`/whether the order is fully filled, rather than trusting the nominal `totalRequired`/`fillAmount`. Only release the proportional escrowed input amount (or finalize the order) once the confirmed delivered amount meets the required threshold.

### Proof of Concept
1. User places a same-chain (or cross-chain) order requiring `1000` units of `FOT` (a fee-on-transfer token with e.g. 5% fee) as output, escrowing `1000 USDC` as input.
2. Solver calls `fillOrder` with `options.outputs[0].amount = 1000` for the `FOT` token.
3. `_fillSameChain`/`_fillCrossChain` executes `IERC20(FOT).safeTransferFrom(solver, beneficiary, 1000)`; due to the 5% fee, the beneficiary actually receives `950 FOT`.
4. The contract computes `amountFilled = alreadyFilled + fillAmount = 1000`, which equals `totalRequired`, so `isFullyFilled = true`.
5. `_withdraw` releases the **entire** `1000 USDC` escrow to the solver, and `OrderFilled`/`RedeemEscrow` finalizes the order.
6. Net result: the beneficiary got `950 FOT` instead of the promised `1000 FOT`, while the solver received the full `1000 USDC` input — a guaranteed 5% loss to the order beneficiary on every fill of such an order, with no on-chain check or recovery path.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L317-323)
```text
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L91-118)
```text
            uint256 amountFilled = alreadyFilled + fillAmount;
            _partialFills[commitment][outputToken] = amountFilled;
            uint256 beneficiaryTotal = fillAmount + beneficiaryShare;

            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }

            if (totalRequired > amountFilled) isFullyFilled = false;
            if (protocolShare > 0) emit DustCollected(token, protocolShare);

            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
            outputFills[i] = TokenInfo({token: outputToken, amount: fillAmount});
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L186-199)
```text
            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }
```
