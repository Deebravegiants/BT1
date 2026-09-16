### Title
Premature rounding in VWAPOracle's weighted-spread accumulation corrupts the on-chain price-spread statistic - (File: evm/src/utils/VWAPOracle.sol)

### Summary
`VWAPOracle.recordSpread()` computes a per-fill spread in basis points using integer division, and then **re-multiplies that already-truncated value** by the fill's volume to obtain the "weighted spread" it accumulates. This is the same root-cause class as the reported Notional bug: an intermediate division is performed before a multiplication that should have been applied to the un-rounded quantity, corrupting the resulting fixed-point statistic.

### Finding Description
In `recordSpread()`:
```solidity
// evm/src/utils/VWAPOracle.sol:200-211
int256 spreadBps = 0;
if (inputAmountNormalized > 0) {
    int256 amountDiff = int256(outputAmountNormalized) - int256(inputAmountNormalized);
    spreadBps = (amountDiff * int256(BPS_DENOMINATOR)) / int256(inputAmountNormalized);
}

int256 weightedSpread = spreadBps * int256(inputAmountNormalized);
_updateCumulativeSpread(_tokenSpreads[sourceChainHash][inputToken], weightedSpread, inputAmountNormalized);
``` [1](#0-0) 

Mathematically, `weightedSpread` should equal `amountDiff * BPS_DENOMINATOR` exactly — the `inputAmountNormalized` divisor and the volume multiplier cancel algebraically. However, the code first *divides* `amountDiff * BPS_DENOMINATOR` by `inputAmountNormalized` (truncating toward zero, discarding a fraction of up to `inputAmountNormalized - 1` in the numerator), and only afterward multiplies that already-rounded `spreadBps` back by `inputAmountNormalized`. This reproduces exactly the "division-before-multiplication" pattern from the reference report: an operation that should be pure multiplication (no rounding at all) is forced through an unnecessary intermediate division, injecting rounding error into every fill.

The corrupted `weightedSpread` is accumulated into `CumulativeSpreadData.weightedSpreadSum`, and later divided by `totalVolume` in `spread()`:
```solidity
// evm/src/utils/VWAPOracle.sol:141-147
function spread(bytes memory sourceChain, address token) external view returns (int256) {
    ...
    return data.weightedSpreadSum / int256(data.totalVolume);
}
``` [2](#0-1) 

Because the per-fill rounding error scales with each fill's `spreadBps` truncation (which any solver fully controls by choosing `outputs[i].amount`/`inputs[i].amount` in the order it fills), a solver filling many small orders can systematically bias the accumulated `spreadBps` reading away from the true volume-weighted average, since integer division always truncates toward zero (i.e. it biases the reported spread favorably for whichever sign the solver targets).

`recordSpread` is invoked by `IntentGatewayV2` (the caller is restricted to `_intentGateway`) during order settlement using the actual `inputs`/`outputs` amounts of a filled order — a path directly reachable by any unprivileged intent solver simply by filling orders, with no special privileges required.

### Impact Explanation
`VWAPOracle` implements `IIntentPriceOracle`, the on-chain price/spread oracle feeding `IntentGatewayV2`'s `priceOracle` parameter. A corrupted, solver-biased spread statistic undermines the integrity of this on-chain price-tracking mechanism — any downstream logic relying on `spread()` for slippage/price-manipulation detection would receive drift that a solver can influence by choosing fill sizes, understating or overstating how much spread it has been capturing from users over time.

### Likelihood Explanation
The path is trivially reachable: it fires unconditionally on every order settlement through `IntentGatewayV2`, and the bias is fully within an unprivileged solver's control (order sizing on each fill it submits). No special permissions, race conditions, or unusual configuration are required — only that a `priceOracle`/`VWAPOracle` deployment is wired up and consulted.

### Recommendation
Compute the weighted spread contribution directly from the un-rounded numerator, deferring all division to the final `spread()` read:
```solidity
int256 weightedSpread = 0;
if (inputAmountNormalized > 0) {
    int256 amountDiff = int256(outputAmountNormalized) - int256(inputAmountNormalized);
    // No intermediate division — this is the exact per-fill numerator contribution.
    weightedSpread = amountDiff * int256(BPS_DENOMINATOR);
}
_updateCumulativeSpread(_tokenSpreads[sourceChainHash][inputToken], weightedSpread, inputAmountNormalized);
```
If a per-fill `spreadBps` value is still needed for the `SpreadRecorded` event, compute it separately for display/logging only, and never feed the rounded value back into the accumulator.

### Proof of Concept
1. A solver fills an order where `inputAmountNormalized = 3` (in 18-decimal normalized units) and `outputAmountNormalized = 4`, so `amountDiff = 1`.
2. `spreadBps = (1 * 10_000) / 3 = 3333` (true value is `3333.33...`, truncated).
3. `weightedSpread = 3333 * 3 = 9999`, whereas the mathematically correct contribution is `amountDiff * BPS_DENOMINATOR = 1 * 10_000 = 10_000`.
4. This 1-unit-per-fill deficit (scaled by `BPS_DENOMINATOR/inputAmountNormalized` truncation) accumulates over every fill processed by the oracle, and a solver choosing `inputAmountNormalized` values that maximize this truncation (e.g., picking amounts just above a power-of-ten boundary) can deliberately skew the reported `spread()` for a `(sourceChain, token)` pair away from the true volume-weighted average, without needing any privileged role — only ordinary participation as an intent solver filling orders through `IntentGatewayV2`.

Note: I was not able to fully trace every downstream consumer of `VWAPOracle.spread()` within the indexed context (e.g., exact `priceOracle` gating logic in `IntentGatewayV2` at fill time) to quantify the maximum extractable value from this bias; a Devin session with full repo access would be needed to confirm the precise downstream severity ceiling.

### Citations

**File:** evm/src/utils/VWAPOracle.sol (L141-147)
```text
    function spread(bytes memory sourceChain, address token) external view returns (int256) {
        bytes32 chainHash = keccak256(sourceChain);
        CumulativeSpreadData memory data = _tokenSpreads[chainHash][token];
        if (data.totalVolume == 0) return 0;

        return data.weightedSpreadSum / int256(data.totalVolume);
    }
```

**File:** evm/src/utils/VWAPOracle.sol (L200-211)
```text
            // Calculate spread for this token: (output - input) / input * 10000
            // Positive spread = filler provided more tokens (good for user)
            // Negative spread = filler provided fewer tokens (filler captured spread)
            int256 spreadBps = 0;
            if (inputAmountNormalized > 0) {
                int256 amountDiff = int256(outputAmountNormalized) - int256(inputAmountNormalized);
                spreadBps = (amountDiff * int256(BPS_DENOMINATOR)) / int256(inputAmountNormalized);
            }

            // Update cumulative spread data for this token (weighted by volume)
            int256 weightedSpread = spreadBps * int256(inputAmountNormalized);
            _updateCumulativeSpread(_tokenSpreads[sourceChainHash][inputToken], weightedSpread, inputAmountNormalized);
```
