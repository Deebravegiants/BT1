## Title
Multiplication performed on the result of an already-truncated division in `VWAPOracle._recordSpread` compounds rounding error in the on-chain spread tracker - (File: `evm/src/utils/VWAPOracle.sol`)

### Summary
`VWAPOracle.recordSpread()` computes `spreadBps` via integer division and then re-multiplies that truncated result by the same volume figure to derive `weightedSpread`, mirroring the exact "multiplication on the result of a division" anti-pattern flagged in the source report for `SingleSidedLPVaultBase._calculateLPTokenValue`.

### Finding Description
`recordSpread` first computes the spread in basis points with a division: [1](#0-0) 

and then multiplies that already-truncated `spreadBps` back by `inputAmountNormalized` to obtain the value accumulated into cumulative storage: [2](#0-1) 

The correct order of operations would be to compute `weightedSpread = amountDiff * BPS_DENOMINATOR` directly (deferring the division on `inputAmountNormalized`) rather than dividing first (in `spreadBps`) and multiplying the rounded quotient again. As written, every call to `recordSpread` bakes in truncation from the first division before that value is scaled back up, so the recorded `weightedSpreadSum`/`totalVolume` — and therefore the value returned by `spread()` — diverges from the true volume-weighted average the contract is supposed to track. [3](#0-2) 

This function is invoked once per input/output pair on every order fill by `IntentGatewayV2`/`IntrinsicIntents`/`ExtrinsicIntents` (restricted only to `_intentGateway`, i.e. reachable from any unprivileged solver calling `fillOrder`), with `inputs`/`outputs` amounts fully attacker (solver)-controlled within the constraints of the order being filled: [4](#0-3) 

### Impact Explanation
`VWAPOracle` exists specifically to track how much spread fillers capture on same-token intents, and its interface documentation frames `spreadBps`/cumulative spread as the metric consumers rely on to detect fillers "capturing spread" from users. Because the truncation happens before the volume-weighting multiplication rather than after, the error compounds across every fill rather than being isolated to the final read — a solver who fills many small orders with amounts chosen to sit just below rounding boundaries can systematically bias the recorded average spread away from the true value, either masking spread capture (negative spread underreported) or skewing the on-chain metric that downstream governance/monitoring depends on. This is a data integrity/manipulation issue on a value that other on-chain or off-chain consumers may treat as authoritative for filler behavior, consistent with a Medium-severity precision-loss finding.

### Likelihood Explanation
`recordSpread` is called unconditionally on every fill of a same-token intent order, and its inputs (`inputs[]`, `outputs[]`) are the escrowed/filled token amounts that a solver directly controls when constructing a fill. No privileged role is required — any solver executing `fillOrder` on `IntentGatewayV2` triggers this path, making the flawed accounting reachable and repeatable at will.

### Recommendation
Reorder the arithmetic to multiply before dividing, computing the weighted spread directly from `amountDiff * BPS_DENOMINATOR` (or equivalently `(outputAmountNormalized - inputAmountNormalized) * BPS_DENOMINATOR`) without an intermediate division by `inputAmountNormalized`, and defer all division to the final `spread()` read (`weightedSpreadSum / totalVolume`) as it already does. Concretely:
```solidity
int256 amountDiff = int256(outputAmountNormalized) - int256(inputAmountNormalized);
int256 spreadBps = inputAmountNormalized > 0
    ? (amountDiff * int256(BPS_DENOMINATOR)) / int256(inputAmountNormalized)
    : int256(0);
// Weighted spread computed without re-multiplying the truncated quotient:
int256 weightedSpread = amountDiff * int256(BPS_DENOMINATOR);
```
(adjusting `_updateCumulativeSpread`/`spread()` divisor accordingly, or otherwise restructuring so only one division occurs per accounting cycle).

### Proof of Concept
For a fill where `inputAmountNormalized = 3` and `outputAmountNormalized = 4` (both normalized to 18 decimals, illustrative small units):
- `amountDiff = 1`
- `spreadBps = (1 * 10_000) / 3 = 3333` (truncated from `3333.33…`)
- `weightedSpread = 3333 * 3 = 9999` (should be `1 * 10_000 = 10_000` if multiplication preceded division)

The 1-unit-per-fill error is deterministic and repeats on every fill for every same-token pair tracked by the oracle, so it accumulates linearly with fill count into `weightedSpreadSum`/`totalVolume`, permanently skewing every future `spread()` read for that `(sourceChain, token)` pair.

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

**File:** evm/src/utils/VWAPOracle.sol (L203-207)
```text
            int256 spreadBps = 0;
            if (inputAmountNormalized > 0) {
                int256 amountDiff = int256(outputAmountNormalized) - int256(inputAmountNormalized);
                spreadBps = (amountDiff * int256(BPS_DENOMINATOR)) / int256(inputAmountNormalized);
            }
```

**File:** evm/src/utils/VWAPOracle.sol (L209-211)
```text
            // Update cumulative spread data for this token (weighted by volume)
            int256 weightedSpread = spreadBps * int256(inputAmountNormalized);
            _updateCumulativeSpread(_tokenSpreads[sourceChainHash][inputToken], weightedSpread, inputAmountNormalized);
```

**File:** sdk/packages/core/contracts/apps/IntentPriceOracle.sol (L42-54)
```text
    /**
     * @notice Records the spread for a filled order and computes weighted average
     * @param commitment The order commitment hash
     * @param sourceChain The source chain identifier (bytes format)
     * @param inputs The input tokens that were escrowed
     * @param outputs The output tokens provided by the filler (actual amounts)
     */
    function recordSpread(
        bytes32 commitment,
        bytes memory sourceChain,
        TokenInfo[] calldata inputs,
        TokenInfo[] calldata outputs
    ) external;
```
