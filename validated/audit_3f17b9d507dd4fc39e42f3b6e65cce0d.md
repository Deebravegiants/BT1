### Title
VWAPOracle spread accumulator can be poisoned by self-filled intent orders, corrupting the price feed consumed for pricing later orders - (File: evm/src/utils/VWAPOracle.sol)

### Summary
`VWAPOracle.recordSpread` is invoked once per filled order by `IntentGatewayV2` and updates a cumulative, volume-weighted "spread" for a `(sourceChain, token)` pair. The inputs to this calculation are exactly the order's `inputs` (escrowed by the *user* who placed the order) and `outputs` (provided by the *solver* who filled it) — values that are entirely user/solver-controlled and are never validated against any independent market price. This mirrors the reported class of bug: a value that should reflect real market price is instead derived from unvalidated, attacker-influenceable caller data, and that value is later trusted downstream to price/size other users' orders without further slippage adjustment.

### Finding Description
`VWAPOracle.recordSpread` is access-restricted only by `restrict(_intentGateway)`, i.e. it can only be called by the `IntentGatewayV2` contract: [1](#0-0) 

However, the *content* of `inputs`/`outputs` that feeds the spread calculation is not something the gateway independently verifies against a market price — it is simply the order's escrowed `inputs` (chosen by whoever places the order) and the `outputs` a solver actually delivered when filling it (constrained only to be `>= required`, with no upper bound): [2](#0-1) 

Because both `placeOrder` and `fillOrder` are permissionless, an attacker (or two colluding addresses) can:
1. Place a same-token, cross-chain intent order with a token amount and a deliberately extreme requested output (e.g., requesting far more output than the input is worth).
2. Immediately fill their own order as the "solver", supplying the inflated `outputs` amount that satisfies their own inflated request.
3. This drives `IntentGatewayV2` to call `recordSpread(commitment, sourceChain, inputs, outputs)` with these contrived numbers, which get folded into the weighted average via `_updateCumulativeSpread`: [3](#0-2) 

Repeating this (each fill adds `spreadBps * volume` to `weightedSpreadSum` and `volume` to `totalVolume`) skews `spread()`'s output over time in either direction, since `spread()` is a straight running average with no staleness window, outlier rejection, or minimum-liquidity/volume gate: [4](#0-3) 

This is structurally the same flaw as the original report: a function reachable by any unprivileged actor (`execute_dca_order` calling `_calc_min_amount_out` with attacker-supplied pool path; here, `fillOrder`/`placeOrder` feeding `recordSpread` with attacker-supplied amounts) computes a "price" signal from data the caller fully controls, with no sanity check against a trusted, hard-to-manipulate source (e.g., a real TWAP/Chainlink oracle, minimum liquidity/volume threshold).

### Impact Explanation
Per the SDK/indexer documentation, this on-chain VWAP/spread data feeds "indexed-rate" quoting used to size the `inputs`/`output.assets` of *other* users' intent orders, and the docs explicitly state no further slippage adjustment is applied on top of it: [5](#0-4) 

If the underlying spread accumulator can be skewed by an attacker's self-fills, subsequent legitimate users relying on this indexed rate to size their orders would place orders priced against a manipulated baseline. A solver who is aware of (or has caused) the skew can then fill those orders at the "fair-looking" but actually unfavorable rate, capturing the difference at the victim's expense — analogous to the DCA report's "user is wrecked" scenario where an attacker-controlled pricing input is unknowingly trusted to protect the user's trade.

### Likelihood Explanation
Both `placeOrder` and `fillOrder` are unprivileged, callable by any address, and same-chain same-token orders settle atomically in a single transaction, so an attacker can self-fill contrived orders cheaply and repeatedly to bias the cumulative average — no special access or governance compromise is required. The only cost is gas plus whatever notional is used per manipulation order, which can be kept small and repeated, while `spread()` has no volume floor guarding against low-liquidity skew.

### Recommendation
- Do not treat `VWAPOracle.spread()` as an unconditionally trustworthy price signal for pricing new orders without independent bounds (e.g., compare against a real DEX/Chainlink price and reject if divergence exceeds a threshold).
- Add safeguards to `recordSpread`/`spread()`: minimum cumulative volume before the spread is considered valid, decay/staleness windows, and/or per-fill spread caps to bound the influence of any single (or self-dealing) fill.
- Consider requiring solver and order-placer to be distinct, unaffiliated addresses for spread-eligible fills, or excluding same-block/self-fill patterns from spread accounting.
- On the SDK/indexer side, apply an explicit slippage/sanity check on top of the indexed rate rather than using it as-is with "no further adjustment."

### Proof of Concept
Not independently verified end-to-end against the SDK/indexer consumer of `spread()` (that code lives outside the on-chain `evm/` contracts and was not directly inspected in this pass), so the downstream fund-loss path is inferred from the documented behavior in `docs/content/developers/sdk/api/intent-gateway.mdx` rather than from a directly traced call site in the indexer/SDK source. The on-chain manipulation primitive itself, however, is fully demonstrated by:
1. `IntentGatewayV2.placeOrder` — user escrows `inputs` (any user-chosen split/amount).
2. `IntentGatewayV2.fillOrder` — solver (can be the same attacker) supplies `outputs >= required` with no upper bound, then the gateway calls `VWAPOracle.recordSpread(commitment, sourceChain, inputs, outputs)`.
3. `VWAPOracle._updateCumulativeSpread` accumulates `spreadBps * volume` unconditionally into `weightedSpreadSum`/`totalVolume`, directly moving `spread()`'s return value: [6](#0-5) 
Given the documented downstream reliance on this spread for pricing (and no independent verification cited anywhere in the reviewed code), this is flagged as a valid analog of the reported bug class rather than a fully proven exploit chain.

### Citations

**File:** evm/src/utils/VWAPOracle.sol (L138-147)
```text
    /**
     * @inheritdoc IIntentPriceOracle
     */
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

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L41-46)
```text
### Fill Flow

The solver calls `fillOrder(order, options)` on the **destination chain**. The function verifies the order hasn't expired (`order.deadline >= block.number`), confirms execution is on the correct chain, and checks the order hasn't already been filled. The solver must provide output amounts greater than or equal to the order's required amounts — any amount below the required amount reverts with `InvalidInput()`.

If the solver provides more tokens than required, the excess (surplus) is split according to `surplusShareBps`. If the order includes calldata, 100% of surplus goes to the protocol to prevent manipulation.

```

**File:** docs/content/developers/sdk/api/intent-gateway.mdx (L230-234)
```text
The result includes `amountIn`, `amountOut`, and strategy-specific quote metadata. Indexed-rate metadata contains the source and destination chains, base and quote symbols, the buy or sell rate used, its update time, and the source-chain protocol fee.

`amountIn` and `amountOut` already account for the IntentGateway protocol fee that the gateway deducts from order inputs. Exact-input quotes price the swap against the post-fee input, so `amountOut` is the snapshot-priced output; exact-output quotes return the gross `amountIn` required to produce the requested `amountOut`. Use the returned amounts directly as the order's `inputs` and `output.assets`—no further fee or slippage adjustment is required.

For exact-input quotes, the SDK deducts the gateway fee before applying the directional rate. For exact-output quotes, it calculates the required net input from that rate and then grosses the input up for the gateway fee. Token decimals are read from SDK chain configuration. A missing indexer, missing directional rate, or invalid rate throws an explicit error.
```
