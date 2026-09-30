# [M] ChainlinkOracleWrapper - latestRoundData might return stale results

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The oracle wrapper calls out to a chainlink oracle receiving the `latestRoundData()`. It then checks freshness by verifying that the answer is indeed for the last known round. The returned `updatedAt` timestamp is not checked.

If there is a problem with chainlink starting a new round and finding consensus on the new value for the oracle (e.g. chainlink nodes abandon the oracle, chain congestion, vulnerability/attacks on the chainlink system) consumers of this contract may continue using outdated stale data (if oracles are unable to submit no new round is started)

#### Examples


**code/contracts/oracle/ChainlinkOracleWrapper.sol:L49-L58**
```solidity
/// @notice read the oracle price
/// @return oracle price
/// @return true if price is valid
function read() external view override returns (Decimal.D256 memory, bool) {
    (uint80 roundId, int256 price,,, uint80 answeredInRound) = chainlinkOracle.latestRoundData();
    bool valid = !paused() && price > 0 && answeredInRound == roundId;

    Decimal.D256 memory value = Decimal.from(uint256(price)).div(oracleDecimalsNormalizer);
    return (value, valid);
}
```


**code/contracts/oracle/ChainlinkOracleWrapper.sol:L42-L47**
```solidity
/// @notice determine if read value is stale
/// @return true if read value is stale
function isOutdated() external view override returns (bool) {
    (uint80 roundId,,,, uint80 answeredInRound) = chainlinkOracle.latestRoundData();
    return answeredInRound != roundId;
}
```

#### Recommendation

Consider checking the oracle responses `updatedAt`  value after calling out to `chainlinkOracle.latestRoundData()` verifying that the result is within an allowed margin of freshness.
