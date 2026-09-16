Confirmed: `_getOraclePrice` in `SimplexPaymaster.sol` reads `latestRoundData()` and only checks `answer <= 0` and staleness via `updatedAt`, but never validates `roundId`/`answeredInRound` or clamps `answer` against Chainlink's documented min/max aggregator bounds. [1](#0-0) 

### Title
Missing Chainlink round-completeness and min/max answer sanity checks in `_getOraclePrice` lets stale/limit-pinned feeds mis-price gas payments - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster._getOraclePrice()` consumes `AggregatorV3Interface.latestRoundData()` for both the native/USD and token/USD feeds used to price every ERC-4337 `UserOperation`'s gas payment. It validates only `answer > 0` and `block.timestamp - updatedAt <= maxOracleAge`, omitting the two checks Chainlink explicitly recommends: (1) an incomplete-round check (`answeredInRound >= roundId`), and (2) a sanity clamp of `answer` against the feed's `minAnswer`/`maxAnswer` circuit-breaker bounds.

### Finding Description
`_getOraclePrice` is:
```solidity
function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
    (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();
    if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
    if (block.timestamp - updatedAt > maxOracleAge) {
        revert StaleOraclePrice(address(oracle), updatedAt);
    }
    ...
}
``` [2](#0-1) 

This function feeds `_tokenPrice()`, which is called from `_fetchDetails` (the paymaster-facing pricing hook invoked during `validatePaymasterUserOp` for every unprivileged `UserOperation`) and from `swapAndDeposit`: [3](#0-2) [4](#0-3) [5](#0-4) 

Two Chainlink-recommended guards are missing:
1. **Incomplete-round check**: without comparing `answeredInRound` to `roundId`, a round that started but has not reached consensus can still be reported by `latestRoundData()` in some legacy/adapter feeds, allowing a carried-over stale answer to be accepted as fresh (it passes the `updatedAt` staleness check because `updatedAt` reflects a previous completed round, not the in-flight one).
2. **min/max answer clamp**: Chainlink aggregators enforce a `minAnswer`/`maxAnswer` circuit breaker at the aggregator level; when the real market price moves outside that range (e.g. a depeg or extreme volatility), the feed keeps returning the pinned `minAnswer`/`maxAnswer` value instead of reverting or clearly signalling staleness. `_getOraclePrice` treats this pinned value as a valid, positive, "fresh" price since `answer > 0` and `updatedAt` keeps advancing with each pinned round.

Both failure modes let attacker-observable but protocol-unvalidated Chainlink data drive `_tokenPrice()`, which directly computes how many ERC-20 token units are pulled from a `UserOperation` sender via `transferFrom`/`Permit2` in `_prefund`, and how much native asset `swapAndDeposit` swaps token surplus for.

### Impact Explanation
Any unprivileged actor submitting a `UserOperation` through this paymaster is priced using `_tokenPrice()`, which is fully dependent on the unvalidated `_getOraclePrice()` result. If either feed is pinned at `minAnswer`/`maxAnswer` (e.g., during a stablecoin depeg or a BNB/ETH flash crash/spike) or is stuck reporting a stale, unconsummated round, users can be systematically overcharged or undercharged in the fee token relative to the true native-gas cost, and `swapAndDeposit`'s governance-controlled slippage-bound swap (which reuses the same `_getOraclePrice`) can likewise execute against an incorrect reference price, causing token surplus to be swapped for the wrong amount of native asset. This is a fund-mispricing/loss vector reachable from a normal `UserOperation`, not an admin action.

### Likelihood Explanation
Likelihood is tied to real Chainlink aggregator failure modes (min/max pinning during extreme price moves, or adapter rounds that fail to reach consensus) which have occurred historically on live feeds; the paymaster's `maxOracleAge` staleness check does not detect either failure mode because `updatedAt` still advances with each pinned/incomplete round.

### Recommendation
In `_getOraclePrice`, additionally capture `roundId` and `answeredInRound` from `latestRoundData()` and revert if `answeredInRound < roundId`. Additionally, either query the underlying aggregator's `minAnswer`/`maxAnswer` (via `aggregator()`/`AggregatorInterface`) and revert if `answer` is at or near those bounds, or configure and enforce protocol-level sanity bounds per oracle (as is already done for `maxOracleAge`) and revert `InvalidOraclePrice` when the answer falls outside them.

### Proof of Concept
1. Governance registers a token with a Chainlink feed whose underlying aggregator has `minAnswer = X` (e.g., set during initial deployment years ago, now far below realistic prices for that asset).
2. Market price for the asset craters below `X` (or an incomplete round is in flight while the underlying value has moved sharply).
3. `latestRoundData()` returns `answer = X` (pinned) with a fresh `updatedAt` (or a stale-but-`answeredInRound`-mismatched round that still passes `updatedAt <= maxOracleAge`).
4. `_getOraclePrice` accepts this: `answer > 0` and `updatedAt` fresh, so no revert.
5. `_tokenPrice()` computes a `tokenPrice` based on the pinned/incomplete value rather than the true market price.
6. A submitted `UserOperation` is prefunded via `_prefund`, pulling an incorrect token amount from the sender based on the mispriced `tokenPrice`, or `swapAndDeposit` swaps at an incorrect reference price, both without any code path in `SimplexPaymaster.sol` detecting the underlying oracle malfunction.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L541-546)
```text
        TokenConfig memory cfg = tokenConfigs[tokenAddr];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(tokenAddr);
        if (!cfg.active) revert TokenNotActive(tokenAddr);

        tokenPrice = _tokenPrice(cfg);
        token = IERC20(tokenAddr);
```

**File:** evm/src/utils/SimplexPaymaster.sol (L653-658)
```text
    function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

        return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L660-676)
```text
    /// @dev Fetch a Chainlink price normalized to 8 decimals.
    ///      Reverts on stale or non-positive answers.
    function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
        (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();

        if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
        if (block.timestamp - updatedAt > maxOracleAge) {
            revert StaleOraclePrice(address(oracle), updatedAt);
        }

        if (oracleDecimals < 8) {
            return uint256(answer) * (10 ** (8 - oracleDecimals));
        } else if (oracleDecimals > 8) {
            return uint256(answer) / (10 ** (oracleDecimals - 8));
        }
        return uint256(answer);
    }
```
