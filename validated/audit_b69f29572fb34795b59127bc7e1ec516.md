### Title
VWAPOracle's volume-weighted spread lets a filler manipulate the tracked price to fabricate a favorable historical spread - ([File: evm/src/utils/VWAPOracle.sol])

### Summary
`VWAPOracle` tracks a cumulative, volume-weighted average spread per `(sourceChain, token)` pair. `recordSpread` is called (only) by the `_intentGateway` and blindly trusts the `inputs`/`outputs` amounts it is handed, weighting each fill's spread contribution by that fill's own `inputAmountNormalized`. Whoever controls the amounts being recorded therefore controls both the "vote" (spread value) and its "voting power" (volume weight) in the same call, letting them push the cumulative VWAP toward an arbitrary extreme with a handful of self-dealt, artificially large fills — the same "vote for the extreme value to gain leverage over a weighted-average parameter" pattern described in the report.

### Finding Description
`VWAPOracle.recordSpread` computes, per token, `spreadBps = (output - input) / input * 10000` and folds it into a running weighted sum: [1](#0-0) 

`_updateCumulativeSpread` simply accumulates `weightedSpreadSum += spread*volume` and `totalVolume += volume` with no bound, decay, or per-fill cap: [2](#0-1) 

`spread()` (the oracle's externally-read output) is just `weightedSpreadSum / totalVolume`, i.e. the classic weighted-average-of-votes construction called out in the report: [3](#0-2) 

The access control on `recordSpread` restricts the caller to `_intentGateway`, but not the content of `inputs`/`outputs` — those are the raw order/fill amounts forwarded from `IntentGatewayV2`, which is data the order placer and the filler jointly control (the order's `inputs` are set by the placer, the `outputs` correspond to what the filler actually delivers). The interface doc for `recordSpread` itself notes `outputs` are "the actual amounts provided by the filler," i.e., attacker-influenced input: [4](#0-3) 

Because the weight of each fill's vote is the very same fill's `inputAmountNormalized` that the filler chose to set, a party that can create and fill same-token orders against themselves (self-fill, or collude placer+filler) can submit an arbitrarily large-volume, extreme-spread fill to overwhelm all prior "honest" votes in a single transaction — exactly the manipulation the "voting for max/min values increases voting power" bug class describes, except here the abuser also controls the weight, not just the direction, making it strictly easier than the classic governance case (which caps voting power at one's stake).

### Impact Explanation
The VWAPOracle spread is meant to be an oracle of realistic cross-chain swap spread for same-token intents; any downstream consumer (e.g., other IntentGateway logic that reads `spread()` to set pricing/slippage guards for its own users, or that gates order acceptance) would be fed a poisoned value. An attacker who can drive `spread()` to an artificial extreme (very positive or very negative bps) could cause downstream logic that consults the oracle to misprice fills — e.g. accepting orders that under-deliver relative to true market rates, or rejecting/mispricing otherwise-fair fills — enabling value extraction from real users interacting with whatever contract trusts `IIntentPriceOracle.spread()`.

Note however: per the SDK changelog found during review, `fillOrder` in the current EVM `IntentGatewayV2` no longer calls `recordSpread` at all (removed because "neither `order.inputs` nor `options.outputs` is validated against anything that costs the caller money"): [5](#0-4) 

This confirms the maintainers already identified that unvalidated `inputs`/`outputs` feeding the oracle is unsafe, and disconnected the EVM `IntentGatewayV2.fillOrder` path from it. I could not find any current call site (in the indexed portion of the repo) that still invokes `recordSpread` from a live, unprivileged-reachable dispatch path (the Tron `IntentGatewayV2.sol` I inspected also does not call `recordSpread`). Given the index size limits, I cannot rule out another still-wired caller elsewhere in the codebase, but based on available evidence the wiring that would make this reachable by an ordinary intent solver/order placer appears to have been removed.

### Likelihood Explanation
Low, given the available evidence: `VWAPOracle.recordSpread` is `restrict(_intentGateway)`-gated and the concrete `IntentGatewayV2.fillOrder` implementations located in the index (EVM and Tron) do not call it, so there is no confirmed unprivileged path from a solver/filler transaction into `recordSpread` today. If any deployment still wires an `IntentGatewayV2` fill path to `VWAPOracle.recordSpread` (or a similar pattern gets reintroduced elsewhere), the manipulation described above is trivially exploitable by any filler/placer able to construct same-token orders, since `recordSpread` itself performs no plausibility checks on the amounts.

### Recommendation
- Do not weight votes/spread contributions by attacker-controlled amounts alone; cap the influence of any single fill (e.g. clamp `weightedSpread`/`volume` per call, or use a decayed/windowed average with a max per-fill weight).
- Validate that recorded `inputs`/`outputs` correspond to amounts that actually cost the caller real value (e.g., tie to escrowed/settled amounts verified on-chain, not caller-supplied parameters), consistent with the rationale already used to drop the `recordSpread` call from `fillOrder`.
- If `VWAPOracle` is to be reintroduced as a price reference for any contract, require multiple independent fills from unrelated fillers before trusting the aggregate, and/or bound `spread()`'s influence on downstream logic (sanity min/max clamps), mirroring the report's own observation that hard parameter bounds mitigate (but don't eliminate) this class of issue.

### Proof of Concept
Given `recordSpread` is reachable (hypothetically, or in any future re-wiring):
1. Attacker places a same-token order on `IntentGatewayV2` with `inputs = 1,000,000 * 1e18` of token X and self-fills with `outputs` far outside fair value (e.g. `outputs = 1,100,000 * 1e18`, a +1000bps spread).
2. `recordSpread` is invoked with these attacker-chosen amounts: [6](#0-5) 
3. Because `weightedSpread = spreadBps * inputAmountNormalized`, and the attacker set `inputAmountNormalized` to a huge value, this single fill dwarfs `totalVolume`/`weightedSpreadSum` accumulated by all prior legitimate fills (demonstrated directly in the repo's own test `testVWAPWithExtremeVolumeDifferences`, showing a tiny honest fill's spread becomes "negligible" against one large fill): [7](#0-6) 
4. Subsequent calls to `spread(sourceChain, token)` return the attacker-skewed VWAP, which any downstream consumer of `IIntentPriceOracle.spread()` would treat as the market-representative spread.

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

**File:** evm/src/utils/VWAPOracle.sol (L170-216)
```text
    function recordSpread(
        bytes32 commitment,
        bytes memory sourceChain,
        TokenInfo[] calldata inputs,
        TokenInfo[] calldata outputs
    ) external restrict(_intentGateway) {
        // Validate inputs and outputs have the same length
        if (inputs.length != outputs.length || inputs.length == 0) {
            return;
        }

        bytes32 sourceChainHash = keccak256(sourceChain);
        uint256 tokensLen = inputs.length;
        for (uint256 i = 0; i < tokensLen; i++) {
            address inputToken = address(uint160(uint256(inputs[i].token)));
            address outputToken = address(uint160(uint256(outputs[i].token)));

            // Get decimals for input token from storage (remote chain)
            // Native tokens (address(0)) use 18 decimals
            uint8 inputDecimals = inputToken == address(0) ? 18 : _tokenDecimals[sourceChainHash][inputToken];
            if (inputDecimals == 0) continue; // Skip if decimals not configured

            // Get decimals for output token directly from contract (local chain)
            // Native tokens (address(0)) use 18 decimals
            uint8 outputDecimals = outputToken == address(0) ? 18 : IERC20Metadata(outputToken).decimals();

            // Normalize both amounts to 18 decimals for comparison
            uint256 inputAmountNormalized = _normalizeAmount(inputs[i].amount, inputDecimals);
            uint256 outputAmountNormalized = _normalizeAmount(outputs[i].amount, outputDecimals);

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

            // Emit event for each token
            emit SpreadRecorded(commitment, outputToken, spreadBps);
        }
    }
```

**File:** evm/src/utils/VWAPOracle.sol (L270-281)
```text
    /**
     * @notice Updates cumulative spread data
     * @param data Storage reference to the cumulative spread data
     * @param weightedSpread The weighted spread (spread * volume)
     * @param volume The volume for this fill
     */
    function _updateCumulativeSpread(CumulativeSpreadData storage data, int256 weightedSpread, uint256 volume) private {
        data.weightedSpreadSum += weightedSpread;
        data.totalVolume += volume;
        data.fillCount += 1;
        data.lastUpdate = block.timestamp;
    }
```

**File:** sdk/packages/core/contracts/apps/IntentPriceOracle.sol (L43-54)
```text
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

**File:** evm/tests/foundry/VWAPOracleTest.sol (L437-461)
```text
    function testVWAPWithExtremeVolumeDifferences() public {
        _initOracle();

        // One tiny fill and one massive fill
        // Fill 1: 1 token, +1000 bps (10%)
        TokenInfo[] memory inputs1 = new TokenInfo[](1);
        TokenInfo[] memory outputs1 = new TokenInfo[](1);
        inputs1[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1 * 1e18});
        outputs1[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 11 * 1e17}); // 1.1 tokens
        oracle.recordSpread(keccak256("order1"), sourceChain, inputs1, outputs1);

        // Fill 2: 1 million tokens, -10 bps
        TokenInfo[] memory inputs2 = new TokenInfo[](1);
        TokenInfo[] memory outputs2 = new TokenInfo[](1);
        inputs2[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1_000_000 * 1e18});
        outputs2[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 999_000 * 1e18});
        oracle.recordSpread(keccak256("order2"), sourceChain, inputs2, outputs2);

        int256 vwap = oracle.spread(sourceChain, address(dai));

        // VWAP: (1000*1 + -10*1000000) / 1000001 = (1000 - 10000000) / 1000001 ≈ -9.99 bps
        // Tiny fill's huge spread (+1000 bps) is negligible compared to large volume at -10 bps
        assertTrue(vwap < 0, "VWAP should be dominated by large volume fill");
        assertEq(vwap, -9, "VWAP should be approximately -10 bps");
    }
```
