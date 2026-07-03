Audit Report

## Title
`RSETHPriceFeed.getRoundData()` Applies Current rsETH/ETH Rate to Historical ETH/USD Round Data, Producing Incorrect rsETH/USD Price - (File: contracts/oracles/RSETHPriceFeed.sol)

## Summary
`RSETHPriceFeed.getRoundData(_roundId)` fetches a historical ETH/USD price from Chainlink but unconditionally multiplies it by the **current** `RS_ETH_ORACLE.rsETHPrice()`, which is the live rsETH/ETH rate stored in `LRTOracle`. Because `rsETHPrice` monotonically increases over time as staking rewards accrue, any call to `getRoundData` with a non-latest round ID returns a fabricated rsETH/USD price that never existed on-chain. The contract implements `AggregatorV3Interface` and is deployed as a Chainlink-compatible feed, so downstream integrators relying on historical round data receive silently incorrect answers.

## Finding Description
In `contracts/oracles/RSETHPriceFeed.sol` at lines 53–61:

```solidity
function getRoundData(uint80 _roundId)
    external
    view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

- `ETH_TO_USD.getRoundData(_roundId)` returns the ETH/USD price **at the time of that historical Chainlink round**.
- `RS_ETH_ORACLE.rsETHPrice()` reads `LRTOracle.rsETHPrice`, a storage variable updated by `updateRSETHPrice()` that reflects the **current** rsETH/ETH exchange rate.
- No historical mapping of rsETH/ETH rates by round ID or timestamp exists anywhere in the contract or in `LRTOracle`.

The result is a synthetic price combining a past ETH/USD value with a present rsETH/ETH multiplier — a combination that never existed. The `updatedAt` and `answeredInRound` fields returned are those of the historical ETH/USD round, so the timestamp metadata signals an old price while the rsETH component is current. There are no guards or reverts in `getRoundData` to prevent this misuse.

By contrast, `latestRoundData()` (lines 63–70) is correct because both the ETH/USD price and the rsETH/ETH rate are contemporaneous at the time of the call.

## Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

`RSETHPriceFeed` is explicitly designed as a Chainlink `AggregatorV3Interface` drop-in (deployed at `0x4B9C66c2C0d3706AabC6d00D2a6ffD2B68A4E383` for Morph per the README). External protocols integrating this feed and calling `getRoundData` for staleness validation or historical price checks receive a fabricated rsETH/USD answer. The LRT-rsETH core protocol does not call `getRoundData` internally, so no direct fund loss occurs within the core contracts. The impact falls on downstream consumers of the feed, which is the contract's intended use case.

## Likelihood Explanation
**Medium.** The function is public and requires no privileges. Any protocol integrating `RSETHPriceFeed` as a Chainlink-compatible oracle — a standard integration pattern — and calling `getRoundData` with any non-latest round ID will silently receive an incorrect answer. No special conditions, timing, or attacker capability is required beyond making a standard view call.

## Recommendation
Since `LRTOracle` does not store historical rsETH/ETH rates keyed by round ID or timestamp, the correct fix is to have `getRoundData` revert with an explicit `NotSupported()` error rather than silently returning a fabricated answer. If historical rsETH/ETH rates are desired in the future, a mapping from Chainlink round ID (or block timestamp) to rsETH/ETH rate should be maintained and populated on each `updateRSETHPrice()` call. The `latestRoundData()` path is correct and does not need to change.

## Proof of Concept
1. At time T₀, `LRTOracle.rsETHPrice` = 1.05e18, ETH/USD Chainlink round R₀ answer = 2000e8. True rsETH/USD at R₀ = $2100.
2. Time passes; staking rewards accrue. At T₁, `LRTOracle.rsETHPrice` = 1.10e18, ETH/USD round R₁ answer = 2100e8.
3. Any caller invokes `RSETHPriceFeed.getRoundData(R₀)`.
4. The function executes: `answer = int256(1.10e18) * 2000e8 / 1e18 = 2200e8` — i.e., $2200.
5. The correct historical answer is $2100. The feed overstates by ~4.8%.
6. A lending protocol using this for a liquidation boundary or historical price continuity check operates on incorrect data.

Foundry fork test plan: fork mainnet, deploy `RSETHPriceFeed` pointing to the live ETH/USD Chainlink feed and `LRTOracle`, advance time to allow `rsETHPrice` to increase, then call `getRoundData` with a round ID from before the price increase and assert that the returned `answer` differs from `ETH_USD_historical * rsETH_rate_at_that_time / 1e18`.