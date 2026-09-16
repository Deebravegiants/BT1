### Title
Partial-fill rounding lets the completing filler capture escrow rounding-dust owed to earlier fillers - ([File: evm/src/apps/intentsv2/IntrinsicIntents.sol])

### Summary
`_fillSameChain()` releases escrowed input tokens to each partial filler using floor-division proportional to the output amount they deliver: `escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired` [1](#0-0)  Whichever fill happens to bring `amountFilled` exactly to `totalRequired` instead receives the entire remaining escrow balance `_orders[commitment][token]` rather than its own proportional share [2](#0-1) . Because every non-final fill's release is floored down, any accumulated rounding remainder is not distributed proportionally — it is handed in full to whichever party lands the completing fill, regardless of how small that final output contribution is. This is the same rounding-favoritism bug class as the referenced Splits report ("all funds sent to the majority position while minority rounds to zero"), here manifesting as "all rounding dust goes to whoever completes the order, at the expense of earlier fillers."

### Finding Description
`fillOrder` → `_fillSameChain` is a public, unprivileged entry point that supports partial fills of an order's output assets, tracking cumulative progress in `_partialFills[commitment][outputToken]` [3](#0-2) . For every fill that does not complete the pair, the escrow released to that filler is computed via integer division and floored: `(order.inputs[i].amount * fillAmount) / totalRequired` [4](#0-3) . This systematically under-pays every non-final filler by up to 1 unit of the input token's smallest denomination per fill. The docs confirm this is the intended per-fill formula: `inputs[i].amount × fillAmount / totalRequired` [5](#0-4) .

Only on the fill that satisfies `amountFilled == totalRequired` does the contract instead release the *entire* remaining escrow balance for that token, not the proportional amount for that specific increment [2](#0-1) . The existing test suite explicitly documents and asserts this "final solver gets remaining balance including rounding dust" behavior [6](#0-5) [7](#0-6) .

The consequence: when an order's input token has few decimals relative to the output token's decimals (a GUSD/WBTC-style low-decimal input against an 18-decimal output, exactly the scenario flagged in the referenced report), and the order is filled via several independent partial fills (from different, unrelated solvers competing for pieces of the same order — a normal, expected usage pattern per the docs), every filler except the last is floored down by up to 1 wei of the input token. That entire accumulated shortfall is transferred — for free, with no proportional output requirement — to whichever party happens to submit the fill that completes the pair. Because `fillOrder` has no access control and any address can submit the completing fill for any remaining sliver of the output amount, an opportunistic actor can watch pending partial fills and snipe the completion with a minimal output contribution, collecting the full unclaimed remainder that was floor-rounded away from the genuine earlier fillers.

### Impact Explanation
This directly diverts funds that are contractually owed (proportionally) to earlier, legitimate partial fillers to an unrelated party who contributes comparatively negligible value on the completing fill. This is a concrete theft of escrowed user input tokens from other solvers, reachable by any address calling the public, unprivileged `fillOrder` function — no governance or privileged role is required. The magnitude scales with the number of partial fills and the input token's decimal precision, and is most severe for low-decimal input tokens (e.g., 2-decimal stablecoins) paired against high-decimal outputs, mirroring the exact "GUSD-style" conditions called out in the referenced report.

### Likelihood Explanation
Partial fills by multiple independent solvers on the same order are an explicitly supported, expected usage pattern (the docs advertise same-chain orders as fillable in arbitrary portions by any solver) [5](#0-4) . No coordination with the victim is required — the completing fill can be submitted by anyone at any time once `remaining` is nonzero, so an attacker only needs to monitor mempool/on-chain state for partially-filled orders with accumulated rounding dust and race to submit the final tiny completing fill.

### Recommendation
Track cumulative "amount that should have been released" using full precision (e.g. `mulDiv` against `amountFilled` rather than incremental `fillAmount`), and release `newCumulativeRelease - previousCumulativeRelease` on every fill (final or not), so any rounding remainder is deterministically resolved to whichever fill closes the gap in the same amount it is entitled to — not gifted wholesale to the last completer. Alternatively, require the final fill to receive only its own proportional share, and separately sweep any true residual dust to the protocol treasury (as is already done for surplus) instead of to an arbitrary solver.

### Proof of Concept
Using a low-decimal input token (2 decimals, analogous to GUSD) as `order.inputs[0]` and an 18-decimal output token as `order.output.assets[0]`:
1. Solver A (legitimate) submits a partial fill for a fraction of `totalRequired` designed to floor-round; A receives `floor(inputAmount * fillA / totalRequired)`, losing up to `1` unit of the 2-decimal input token versus the true proportional value.
2. Repeat with additional independent partial fills from other unrelated solvers, each losing up to 1 unit due to the same floor division at line 115 of `evm/src/apps/intentsv2/IntrinsicIntents.sol`.
3. An unrelated attacker monitors the order and submits the final completing fill for the remaining (potentially tiny) output amount; per lines 111-113, they receive `_orders[commitment][token]` — the ENTIRE remaining escrow, including every unit of dust floored away from A and the other solvers — despite having contributed comparatively negligible output value on this last fill.
4. Total escrow released across all fillers still equals `inputAmount` (nothing is permanently locked), but the distribution violates proportionality: the attacker's completing fill nets disproportionately more escrow per unit of output delivered than every prior filler, at those fillers' direct expense — the existing test `testPartialFill_RoundingDustReleasedToFinalSolver` in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol` (lines 1734-1841) demonstrates exactly this mechanic, framed as a "fix" that actually documents the reallocation of rounding dust to whichever party completes the order rather than proportionally to the fillers who generated the shortfall.

### Citations

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L53-78)
```text
    function _fillSameChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        bool isFullyFilled = true;

        TokenInfo[] memory escrowedInputs = new TokenInfo[](outputsLen);
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            uint256 alreadyFilled = _partialFills[commitment][outputToken];
            uint256 remaining = totalRequired - alreadyFilled;
            if (remaining == 0 || solverAmount == 0) {
                if (solverAmount == 0 && remaining > 0) isFullyFilled = false;
                continue;
            }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L111-117)
```text
            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L31-33)
```text
### Partial Fills

For same-chain orders, solvers can fill any portion of the output. The proportional share of escrowed inputs is released immediately (`inputs[i].amount × fillAmount / totalRequired`). The order is fully filled once all output pairs reach their target amounts.
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L1727-1741)
```text
    /*//////////////////////////////////////////////////////////////
                    ROUNDING DUST IN PARTIAL FILLS (Finding #4)
    //////////////////////////////////////////////////////////////*/

    /// @notice Verifies that rounding dust from integer division in partial fills
    /// is not permanently locked. The final solver completing the order should
    /// receive the full remaining escrow balance rather than a truncated amount.
    function testPartialFill_RoundingDustReleasedToFinalSolver() public {
        // Choose amounts that produce rounding truncation:
        // input = 100 USDC (100e6), output = 3 DAI (3e18)
        // Each of 3 solvers fills 1 DAI. Proportional release per fill:
        //   100e6 * 1e18 / 3e18 = 33333333 (truncated from 33333333.33...)
        // Without fix: 3 * 33333333 = 99999999, leaving 1 unit locked.
        // With fix: final solver gets remaining balance = 100e6 - 2*33333333 = 33333334
        uint256 inputAmount = 100 * 1e6; // 100 USDC
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L1830-1841)
```text
        // Final solver should receive the remaining balance (truncatedRelease + 1 rounding unit)
        uint256 expectedFinalRelease = inputAmount - (2 * truncatedRelease); // 33333334
        assertEq(
            usdc.balanceOf(solver3),
            solver3UsdcBefore + expectedFinalRelease,
            "Final solver should receive remaining escrow including rounding dust"
        );
        assertGt(expectedFinalRelease, truncatedRelease, "Final release should be larger due to rounding dust");

        // Gateway should have zero USDC — no dust locked
        assertEq(usdc.balanceOf(address(intentGateway)), 0, "Gateway should have zero USDC - no rounding dust locked");
    }
```
