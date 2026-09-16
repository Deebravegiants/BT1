## Title
Same-chain partial fill can release zero escrowed input to the solver due to rounding, letting a fill transfer real output tokens for nothing in return - (File: `evm/src/apps/intentsv2/IntrinsicIntents.sol`)

### Summary
`IntrinsicIntents._fillSameChain` computes the escrow released to a solver for a non-completing partial fill as `(order.inputs[i].amount * fillAmount) / totalRequired`, a floor-division identical in structure to the Notional `StrategyUtils._convertStrategyTokensToBPTClaim` rounding bug. When `fillAmount` is small relative to `totalRequired`, this expression can round down to zero. The function proceeds anyway — it transfers `fillAmount` of real output tokens to the beneficiary and consumes `fillAmount` from `_partialFills[commitment][outputToken]`, but the solver's `escrowedAmount` (and therefore what `_withdraw` actually releases to them) is silently zero, with no revert.

### Finding Description
In `_fillSameChain` (`evm/src/apps/intentsv2/IntrinsicIntents.sol`): [1](#0-0) 

```solidity
uint256 fillAmount;
...
} else {
    fillAmount = solverAmount > remaining ? remaining : solverAmount;
}
...
uint256 escrowedAmount;
if (amountFilled == totalRequired) {
    escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
} else {
    escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
}
```

The final-completing case (`amountFilled == totalRequired`) is correctly handled by reading the exact remaining balance — this is the fix already applied for the "rounding dust" finding covered by `testPartialFill_RoundingDustReleasedToFinalSolver` [2](#0-1) . However, the non-completing (intermediate partial) branch still performs a plain floor division with no zero check, exactly mirroring the `Boosted3TokenPoolUtils._redeem` / `StrategyUtils._convertStrategyTokensToBPTClaim` pattern from the Sherlock report: `bptClaim` (here, `escrowedAmount`) can be `0`, and the function does not revert — it just proceeds to transfer the caller's real assets (`beneficiaryTotal` of output tokens, sent via `safeTransferFrom`/native transfer at lines 95-106) while crediting them with nothing from escrow.

Concretely: for an order with `totalRequired = 3e18` (e.g. 3 DAI, 18 decimals) and `order.inputs[i].amount = 100e6` (100 USDC, 6 decimals), any `fillAmount < 3e10` wei of DAI causes `escrowedAmount` to round to exactly `0`. The solver still pays `fillAmount` DAI to the beneficiary and still advances `_partialFills[commitment][outputToken]` by that amount, permanently consuming a slice of the order's remaining requirement, but receives zero USDC from escrow.

### Impact Explanation
A solver that fills a small remaining chunk of an order (a routine occurrence in automated partial-fill flows, where residual amounts shrink as an order nears completion) can deliver real assets to the order's beneficiary and receive nothing back from the escrow, while the order's fill-tracking state is still updated as if a legitimate value-for-value exchange occurred. This is a direct loss of funds for the party executing the fill, matching the accepted severity of the original report (loss of assets due to unchecked rounding-to-zero in an asset-release computation) rather than a purely cosmetic dust issue.

### Likelihood Explanation
Requires no privileged access — any address may call `fillOrder`/`_fillSameChain` for an existing order with attacker- or solver-chosen `outputs[i].amount`. The zero-release condition is trivially reachable by choosing (or, for automated solver strategies, unintentionally computing) a `fillAmount` below `totalRequired / order.inputs[i].amount`. Because same-chain fills explicitly support arbitrary partial fills with solver-supplied fill sizes, this path is reachable from ordinary transaction flow.

### Recommendation
Mirror the recommended fix from the referenced report: revert instead of silently proceeding when the computed `escrowedAmount` is zero for a non-completing partial fill, e.g.:
```solidity
} else {
    escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
    require(escrowedAmount > 0, "zero escrow release");
}
```
Alternatively, require a minimum `fillAmount` proportional to `totalRequired` so that intermediate partial fills can never round the released escrow to zero.

### Proof of Concept
1. Place an order with `inputs[0].amount = 100e6` (100 USDC) and `output.assets[0].amount = 3e18` (3 DAI), as in the existing rounding-dust test setup [3](#0-2) .
2. Call `fillOrder` with `outputs[0].amount = 1` wei of DAI (`fillAmount = 1`, `remaining = 3e18 > fillAmount`, so this is a non-completing partial fill).
3. `escrowedAmount = (100e6 * 1) / 3e18 = 0` — the solver transfers `1` wei of DAI to the beneficiary via `safeTransferFrom` (line 102) but `_withdraw` receives `amount = 0` for the USDC leg and releases nothing (the `if (amount == 0) continue;` guard in `_withdraw` at `IntentsBase.sol` line 459 [4](#0-3) ).
4. Assert the solver's USDC balance is unchanged while their DAI balance decreased by 1 wei, and `_partialFills[commitment][outputToken]` increased by 1 — demonstrating assets transferred for zero consideration.

### Citations

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L79-118)
```text
            uint256 fillAmount;

            uint256 beneficiaryShare = 0;
            uint256 protocolShare = 0;
            if (alreadyFilled == 0 && solverAmount > totalRequired) {
                fillAmount = totalRequired;
                (protocolShare, beneficiaryShare) =
                    _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);
            } else {
                fillAmount = solverAmount > remaining ? remaining : solverAmount;
            }

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L1734-1751)
```text
    function testPartialFill_RoundingDustReleasedToFinalSolver() public {
        // Choose amounts that produce rounding truncation:
        // input = 100 USDC (100e6), output = 3 DAI (3e18)
        // Each of 3 solvers fills 1 DAI. Proportional release per fill:
        //   100e6 * 1e18 / 3e18 = 33333333 (truncated from 33333333.33...)
        // Without fix: 3 * 33333333 = 99999999, leaving 1 unit locked.
        // With fix: final solver gets remaining balance = 100e6 - 2*33333333 = 33333334
        uint256 inputAmount = 100 * 1e6; // 100 USDC
        uint256 outputAmount = 3 * 1e18; // 3 DAI

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: outputAmount});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L455-464)
```text
        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
```
