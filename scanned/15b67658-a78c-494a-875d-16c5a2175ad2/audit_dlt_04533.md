# [M] Lack of function to update the chainlink oracle address if the chainlink price is deprecated.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-float-capital
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/6
Type: sherlock-finding

## Details
ctf_sec

medium

# Lack of function to update the chainlink oracle address if the chainlink price is deprecated.

## Summary

Lack of function to update the chainlink oracle address.

## Vulnerability Detail

In the current implementation, once the chainlink oracle price feed address is set in OracleManager.sol,

the oracle address cannot be updated.

```solidity
  constructor(
    address _chainlinkOracle,
    uint256 epochLength,
    uint256 minimumExecutionWaitThreshold
  ) {
    chainlinkOracle = AggregatorV3Interface(_chainlinkOracle);
    MINIMUM_EXECUTION_WAIT_THRESHOLD = minimumExecutionWaitThreshold;
    EPOCH_LENGTH = epochLength;

    // NOTE: along with the getCurrentEpochIndex function this assignment gives an initial epoch index of 1,
    //         and this is set at the time of deployment of this contract
    //         i.e. calling getCurrentEpochIndex() at the end of this constructor will give a value of 1.
    initialEpochStartTimestamp = getEpochStartTimestamp() - epochLength;
  }
```

While the assumption is that the chainlink oracle will always be reliable and deliver up-to-date price feed, this might not be the case.

## Impact

Let us say, We use the chainlink price feed for ETH / USD

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/6_
