# [M] Chainlink price and L2 sequencer uptime feeds are not used with recommended validations and guardrails

## Summary
Severity: Medium
Contest weight: 0.2515
Dataset id: 19117
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[`ChainlinkPriceOracleV1`](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/external/oracles/ChainlinkPriceOracleV1.sol) is an implementation of [IPriceOracle](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/external/oracles/ChainlinkPriceOracleV1.sol#L38) which is used in [`Storage::fetchPrice`](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/lib/Storage.sol#L455-L456). The protocol currently validates [price cannot be zero](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/lib/Storage.sol#L457-L462), but there exist no checks for staleness and round incompleteness which could result in use of an incorrect non-zero price. `ChainlinkPriceOracleV1` currently uses the [deprecated](https://docs.chain.link/data-feeds/api-reference) `IChainlinkAggregator::latestAnswer` function instead of the recommended `IChainlinkAggregator::latestRoundData` function in conjunction with these additional validations.

L2 sequencer downtime validation is handled by calls to a contract conforming to the [IOracleSentinel interface](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/interfaces/IOracleSentinel.sol#L27-L28) in both [`OperationImpl::_verifyFinalState`](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/impl/OperationImpl.sol#L317) and [`LiquidateOrVaporizeImpl::liquidate`](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/impl/LiquidateOrVaporizeImpl.sol#L64). The contract on which [`getFlag`](https://arbiscan.io/address/0x3c14e07edd0dc67442fa96f1ec6999c57e810a83#code) is called simply returns the sequencer uptime status and nothing else.

When an L2 sequencer comes back online after a period of downtime and oracles update their prices, all price movements that occurred during downtime are applied at once. If these movements are significant, borrowers rush to save their positions, while liquidators rush to liquidate borrowers. Since liquidations are in the future intended to be handled by Chainlink Automation, without some grace period where liquidations are disallowed, borrowers are likely to suffer mass liquidations. This is unfair to borrowers, as they could not act on their positions even if they wanted to due to the L2 downtime.

1. Lack of staleness and round-incompleteness validation could result in the use of an incorrect non-zero price.
2. Lack of a sequencer downtime grace period could mean that borrow positions become immediately liquidatable once the sequencer is back up and running if there is a large price deviation in the intermediate time period.

## Recommendation
The Dolomite Margin protocol should correctly validate values returned by Chainlink data feeds and give borrowers a grace period to deposit additional collateral prior to allowing liquidations to resume after a period of L2 sequencer downtime.
