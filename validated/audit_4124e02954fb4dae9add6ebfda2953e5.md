### Title
Fee-on-transfer output tokens let a solver under-deliver to the beneficiary while still claiming the full escrowed input - ([File: evm/src/apps/intentsv2/IntrinsicIntents.sol])

### Summary
The GPT PoC exploited a mismatch between a token's nominal transfer amount and the amount actually received/settled by a contract that trusted the nominal value instead of measuring real balance deltas. `IntentGatewayV2.placeOrder` explicitly defends against this class of bug on the **input** leg — it measures pre/post balances and mutates `order.inputs[i].amount` to the actually-received amount before computing the commitment and crediting escrow [1](#0-0) . However, the **output** leg (the solver paying the beneficiary) has no equivalent balance check.

### Finding Description
In `_fillSameChain` (`IntrinsicIntents.sol`) and `_fillCrossChain` (`ExtrinsicIntents.sol`), the solver's output tokens are moved to the beneficiary with a plain `safeTransferFrom` for the nominal `totalRequired`/`beneficiaryTotal` amount, and the contract immediately treats the order as filled/proportionally filled and releases escrow accordingly, without ever checking `IERC20(token).balanceOf(beneficiary)` before/after: [2](#0-1) [3](#0-2) 

Both functions compute `escrowedInputs`/`outputFills` from the nominal `order.output.assets[i].amount`/`fillAmount` (the amount *requested*, not the amount the beneficiary actually received), then release/redeem escrow and mark the order (partially or fully) filled based on that nominal figure: [4](#0-3) 

If `order.output.assets[i].token` is a fee-on-transfer or rebasing token, any solver filling the order pays the nominal amount but the beneficiary receives less than promised (fee taken in-flight by the token contract), yet:
- the gateway still credits the full nominal amount as "filled" (`_partialFills[commitment][outputToken] = amountFilled` using the pre-fee `fillAmount`), and
- releases/redeems the corresponding proportional (or full) escrowed input to the solver via `_withdraw`/`RedeemEscrow`, and
- the order can be marked `isFullyFilled` even though the beneficiary was shorted.

This is the same root-cause bug class as the GPT PoC: trusting a token's nominal transfer amount as the settled amount instead of verifying the actual balance change, allowing an attacker (here, any solver) to extract more value than they delivered.

### Impact Explanation
An intent creator (order placer) who requests an output denominated in a fee-on-transfer/deflationary/rebasing ERC-20 will always receive less than the promised `order.output.assets[i].amount`, while the solver still collects the full escrowed input value corresponding to the nominal (undelivered) amount. This is a direct value-extraction/theft vector against users placing orders whose output asset has any transfer-fee mechanic (a category of ERC-20 tokens that indisputably exists on EVM chains this gateway supports), and it can be exploited on every fill by every solver, not just a privileged or malicious one — it is a structural mispricing rather than an edge case. It results in permanent loss of user funds equal to the transfer fee percentage, with no reconciliation step (no `DustCollected`/refund on the output leg), unlike the input leg where actual receipts are always faithfully tracked.

### Likelihood Explanation
Likelihood is high for any deployment where a user places an order requesting a fee-on-transfer output token: every solver filling it — malicious or not — will trigger under-delivery, since the code path always uses nominal amounts on the output side with no balance verification. No special conditions or race are required; a single `fillOrder` call against such a token reveals the shortfall each time.

### Recommendation
Mirror the input-side defense in `placeOrder` on the output side: after each output-token `safeTransferFrom` to the beneficiary, measure `balanceOf(beneficiary)` before and after (or `balanceOf(order.output beneficiary)` deltas for the exact transferred amount), and use the actually-received amount to (a) determine whether the fill is complete for that leg (`_partialFills`), (b) compute the proportional escrow to release, and (c) emit any shortfall so subsequent partial fills or refunds can reconcile it — analogous to how `placeOrder` mutates `order.inputs[i].amount` to the measured delta before crediting escrow.

### Proof of Concept
1. User places a same-chain order via `IntentGatewayV2.placeOrder` requesting `outputAssets[0] = {token: FEE_TOKEN, amount: 1000e18}` with a 5% fee-on-transfer token as `FEE_TOKEN`.
2. A solver calls `fillOrder` with `outputs[0].amount = 1000e18` and approves the gateway for that amount.
3. `_fillSameChain` calls `IERC20(FEE_TOKEN).safeTransferFrom(solver, beneficiary, 1000e18)`; due to the 5% transfer fee, the beneficiary's balance only increases by 950e18.
4. The gateway nonetheless sets `_partialFills[commitment][FEE_TOKEN] = 1000e18 == totalRequired`, marks the order `isFullyFilled = true`, releases the *full* escrowed input to the solver via `_withdraw`, and emits `OrderFilled`.
5. Net effect: the beneficiary received 950e18 instead of the promised 1000e18, while the solver captured the full input escrow value corresponding to 1000e18 output — a 5% value extraction with no on-chain accounting of the shortfall (no `DustCollected` emitted, no partial-fill correction), reproducible on every fill of orders denominated in that output token.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L312-329)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L91-129)
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
        }

        // Orders carrying output calldata must be filled completely in a single fill.
        // The attached call is only executed on a full fill, so a partial fill would
        // leave the intended side effect unexecuted while releasing proportional escrow.
        if (order.output.call.length > 0 && !isFullyFilled) revert PartialFillNotAllowed();

        WithdrawalRequest memory body = WithdrawalRequest({
            commitment: commitment, tokens: escrowedInputs, beneficiary: bytes32(uint256(uint160(msg.sender)))
        });
        _withdraw(body, false, isFullyFilled);
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
