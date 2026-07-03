Audit Report

## Title
`getRoundData` Returns Fabricated Historical Price by Mixing Historical ETH/USD with Current rsETH/ETH Rate — (`contracts/oracles/RSETHPriceFeed.sol`)

## Summary
`RSETHPriceFeed.getRoundData(_roundId)` computes its return value by multiplying the historical ETH/USD answer for `_roundId` (line 58) by the **current** `RS_ETH_ORACLE.rsETHPrice()` (line 60). Because `IRSETHOracle` exposes only `rsETHPrice()` with no round-based historical lookup, the returned `answer` is a synthetic value that never existed on-chain, violating the `AggregatorV3Interface` invariant. The confirmed impact is that the contract fails to deliver the historically correct price it promises.

## Finding Description
`IRSETHOracle` (lines 22–24) exposes only `rsETHPrice() external view returns (uint256)` — no historical query capability exists. In `getRoundData` (lines 53–61):

```solidity
// Line 58: correct — historical ETH/USD for _roundId
(roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);

// Line 60: incorrect — current rsETH/ETH rate applied to historical ETH/USD
answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
```

For any round other than the most recent, `rsETHPrice()` returns a rate that differs from the rate at `_roundId` by the staking yield accrued since then. The result is a price that never existed. No guards or staleness checks exist to prevent this. `latestRoundData` (lines 63–70) has the same structure but is correct by construction since both values are current.

No other contract within the LRT-rsETH codebase calls `getRoundData` on this feed; the feed is a standalone oracle contract intended for external integrators.

## Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The `RSETHPriceFeed` contract itself holds no funds and cannot directly cause theft or freezing within the LRT-rsETH protocol. The confirmed, in-scope impact is that the contract fails to fulfill the `AggregatorV3Interface` contract: `getRoundData` must return the price at the queried round, and it does not. Any caller relying on historical round data receives a fabricated answer. The Critical impact scenarios described in the submission (TWAP manipulation, liquidation freezing) are speculative — they require unspecified external protocols to gate fund release on historical round data from this feed, which is not demonstrated within this codebase and cannot be attributed to this repository alone.

## Likelihood Explanation
`getRoundData` is a public view function callable by any unprivileged address. The divergence between the returned value and the true historical price grows monotonically as rsETH accrues staking yield (~3–5% annualized). The bug is structural and triggered on every call with any non-latest `_roundId`.

## Recommendation
Since `IRSETHOracle` provides no historical rate lookup, `getRoundData` cannot be correctly implemented with the current oracle design. The most conservative fix is to revert unconditionally in `getRoundData` with a descriptive message (e.g., `"RSETHPriceFeed: historical round data not supported"`), preventing any caller from silently consuming fabricated data. Alternatively, maintain an on-chain `mapping(uint80 => uint256) public rsETHPriceAtRound` updated in `latestRoundData`, and use the stored snapshot in `getRoundData`.

## Proof of Concept
```solidity
// Mainnet fork test
// 1. Deploy RSETHPriceFeed with live ETH_TO_USD and RS_ETH_ORACLE addresses
// 2. Obtain oldRoundId from 30 days ago via ETH_TO_USD.latestRoundData() minus N rounds
// 3. (, int256 historicalEthUsd,,,) = ETH_TO_USD.getRoundData(oldRoundId);
// 4. uint256 currentRate = RS_ETH_ORACLE.rsETHPrice();
// 5. (, int256 feedAnswer,,,) = rsETHPriceFeed.getRoundData(oldRoundId);
// 6. assertEq(feedAnswer, int256(currentRate) * historicalEthUsd / 1e18); // fabricated
// 7. assertTrue(feedAnswer != trueHistoricalRsEthUsd);                    // never existed
// Delta ≈ 30-day rsETH yield on the ETH/USD price at that round
```