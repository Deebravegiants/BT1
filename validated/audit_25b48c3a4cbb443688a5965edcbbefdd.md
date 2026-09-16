### Title
Fee-on-transfer output tokens let a solver "fill" an order without the beneficiary actually receiving the required amount, while the full escrowed input is still released - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
`_fillSameChain` and `_fillCrossChain` decide whether an order is "fully filled" (and thus release the entire escrowed input to the solver) purely from the nominal amounts specified in `options.outputs[i].amount` / `order.output.assets[i].amount`, and then move output tokens with a plain `safeTransferFrom`, without measuring the beneficiary's actual balance delta. This is the same root-cause class as the referenced report: a contract computes a "required/full" amount and treats a nominal transfer as proof the requirement was satisfied, without verifying the recipient actually received that amount — which silently breaks for fee-on-transfer (FOT) tokens.

### Finding Description
In `_fillCrossChain` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:164-220`), the solver's fill is validated only against the nominal `totalRequired`/`solverAmount`: [1](#0-0) 
The tokens are sent to `beneficiary` with `IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare)` — there is no `balanceOf(beneficiary)` check before/after, unlike `placeOrder` in `evm/src/apps/IntentGatewayV2.sol:260-329`, which explicitly snapshots balances and mutates `order.inputs[i].amount` to the *actually received* value specifically to handle FOT tokens.

Immediately after, the contract marks the order filled (`_filled[commitment] = msg.sender`, set at line 167) and dispatches `RedeemEscrow` carrying the **full, unmutated** `order.inputs` to the source chain: [2](#0-1) 
That message causes `_withdraw` on the source chain to release the entire escrowed input to the solver, regardless of whether the beneficiary actually received `totalRequired` of the output token.

The same pattern exists in the same-chain path, `_fillSameChain` (`evm/src/apps/intentsv2/IntrinsicIntents.sol:53-143`): `beneficiaryTotal` is computed from nominal `fillAmount`/`beneficiaryShare` and sent via `safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal)` at line 102, with no balance check. `isFullyFilled` and the escrow released via `_withdraw` (line 111-129) are driven entirely by the nominal `amountFilled == totalRequired` comparison, not by what the beneficiary actually holds afterward.

If the order's output token is a fee-on-transfer token, the beneficiary receives `beneficiaryTotal - fee`, strictly less than what the order promised, yet:
- the order is marked completely filled,
- the full (unreduced) escrowed input is delivered to the solver (cross-chain) or the full proportional/complete escrow is released (same-chain),
- no revert, no partial-fill fallback, and no way for the user to later reclaim the shortfall.

This mirrors the reported Blueberry issue precisely: the code that determines "the requirement has been met" operates on the requested amount, not the amount actually delivered, so the "full settlement" guarantee silently fails for fee-on-transfer tokens.

### Impact Explanation
This is a direct, quantifiable loss for the order's beneficiary: they receive less than the order's contractually specified output while the solver still collects 100% of the escrowed input value on the source chain (cross-chain path) or via `_withdraw`(same-chain path). Because `IntentGatewayV2`/`ExtrinsicIntents`/`IntrinsicIntents` are unprivileged, permissionless intent-settlement paths reachable by any user placing an order and any solver filling it, this satisfies "concrete theft ... of funds" for orders whose output asset is a deflationary/fee-on-transfer token. Severity is Medium, consistent with the source report, since it requires the order's output token to be FOT (not universally exploitable against arbitrary tokens), but it silently and permanently harms the beneficiary with no on-chain signal of the shortfall.

### Likelihood Explanation
Likelihood is limited to orders whose destination `output.assets[].token` is a fee-on-transfer/deflationary ERC20 (chosen by the order's `user` at `placeOrder` time). Given that the protocol elsewhere (`placeOrder`'s input handling, with dedicated `FeeOnTransferToken` tests in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`) explicitly designs for FOT compatibility, it is reasonable to expect users to place orders expecting outputs in such tokens, and any solver (malicious or not) filling with a FOT output token would trigger the shortfall without any special intent to exploit it — a solver providing exactly `totalRequired` in a 1%-fee token will always underpay the beneficiary by the fee while getting full escrow credit.

### Recommendation
Mirror the input-side pattern already used in `placeOrder`: measure `beneficiary`'s (and protocol treasury's) balance before and after each output transfer in `_fillSameChain` and `_fillCrossChain`, and use the actual received amount to determine whether `totalRequired` was met. If actual receipt is short of `totalRequired`, either revert the fill (do not mark it filled / do not release escrow) or reduce the released escrow proportionally to the amount actually delivered, so the beneficiary can never be left with less than promised while the full escrow is paid out.

### Proof of Concept
1. User places a cross-chain order with `order.output.assets[0].token` = a 1% fee-on-transfer token, `amount = 100`.
2. Solver calls `fillOrder` with `options.outputs[0].amount = 100` (matches `totalRequired`, passes the `solverAmount < totalRequired` check at `ExtrinsicIntents.sol:181`).
3. `safeTransferFrom(solver, beneficiary, 100)` actually delivers only 99 tokens to `beneficiary` due to the 1% fee; no check catches this.
4. `_filled[commitment] = solver` is already set; `RedeemEscrow` is dispatched with the full, unreduced `order.inputs`.
5. On the source chain, `_withdraw` releases the entirety of the escrowed input to the solver.
6. Result: beneficiary got 99 instead of 100 (1% permanently lost, no revert, no recourse), while the solver received 100% of escrow value as if the order were fully honored.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L178-196)
```text
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

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
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L207-212)
```text
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
```
