# [M] Insufficient oracle validation

## Summary
Severity: Medium
Contest weight: 0.5512
Dataset id: 2824
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AirPuffHandler::getLatestData function calls the Chainlink price feed aggregator's
latestRoundData method, but it does no validation on it - the answer is not checked if it is actually a
positive number and also the timestamp or answeredInRound property is not checked if it isn't too old.
```solidity
(, /* uint80 roundID */ int answer /*uint startedAt*/ /*uint
timeStamp*/ /*uint80 answeredInRound*/, , , ) = AggregatorV3Interface(
chainlinkOracle[_token]
).latestRoundData(); //in 1e8
uint256 decimalPrice;
if (_token == swapHandlerAddresses.wstETH) {
    decimalPrice = uint256(answer);
} else {
    decimalPrice = uint256(answer) * 1e10;
    return decimalPrice;
}
```
This means the contract can operate with old and stale price and lead to significant errors.

## Recommendation
Consider validating the data feed:
```solidity
require(answeredInRound >= roundID, "Stale price");
require(timestamp != 0, "Round not complete");
require(answer > 0, "Chainlink answer reporting 0");
```
