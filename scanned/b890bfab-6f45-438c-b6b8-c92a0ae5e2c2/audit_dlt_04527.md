# [M] Oracle data feed is not validated with `decimals()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-float-capital
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/18
Type: sherlock-finding

## Details
sorrynotsorry

medium

# Oracle data feed is not validated with `decimals()`

## Summary
Oracle data feed is not validated with `decimals()`.
## Vulnerability Detail
OracleManager calls the` getRoundData()` of ChainLink API in `validateAndReturnMissedEpochInformation` function with the provided `latestExecutedOracleRoundId` parameter.
However, the returned data is not validated by calling the `decimals()` function of Chainlink. Since Float Capital allows any token to be used in the project, there should be a validation of the data compared to the token decimals.
## Impact
Very large price differences
## Code Snippet
```solidity
  function validateAndReturnMissedEpochInformation(
    uint32 latestExecutedEpochIndex,
    uint80 latestExecutedOracleRoundId,
    uint80[] memory oracleRoundIdsToExecute
  ) public view returns (int256 previousPrice, int256[] memory missedEpochPriceUpdates) {
    uint256 lengthOfEpochsToExecute = oracleRoundIdsToExecute.length;

    if (lengthOfEpochsToExecute == 0) revert EmptyArrayOfIndexes();
    (, previousPrice, , , ) = chainlinkOracle.getRoundData(latestExecutedOracleRoundId);
    missedEpochPriceUpdates = new int256[](lengthOfEpochsToExecute);
    uint256 relevantEpochStartTimestampWithMEWT = ((uint256(latestExecutedEpochIndex) + 2) * EPOCH_LENGTH) +
      MINIMUM_EXECUTION_WAIT_THRESHOLD +
      initialEpochStartTimestamp;


    for (uint32 i = 0; i < lengthOfEpochsToExecute; i++) {
      (, int256 currentOraclePrice, uint256 currentOracleUpdateTimestamp, , ) = chainlinkOracle.getRoundData(oracleRoundIdsToExecute[i]);

      (, , uint256 previousOracleUpdateTimestamp, , ) = chainlinkOracle.getRoundData(oracleRoundIdsToExecute[i] - 1);


      if ((oracleRoundIdsToExecute[i] >> 64) > (latestExecutedOracleRoundId >> 64) && previousOracleUpdateTimestamp == 0) {
          latestExecutedOracleRoundId = (((latestExecutedOracleRoundId >> 64) + 1) << 64) | uint64(oracleRoundIdsToExecute[i] - 1);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/18_
