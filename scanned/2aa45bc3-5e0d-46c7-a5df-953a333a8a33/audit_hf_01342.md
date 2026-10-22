# [M] M-11 ChainlinkOracle integration problems

## Summary
Severity: Medium
Contest weight: 0.1874
Dataset id: 6742
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are several shortcomings in the current implementation of the interaction with Chainlink.
1. ChainlinkOracle.isTokenSupported() returns true if a Chainlink feed exists, but it does not consider the case when it has been abandoned (not updated for a long time):
function isTokenSupported(...) external view override returns (bool) {
...
try _feedRegistry.getFeed(...) returns (IAggregatorV2V3) {
return true;
} catch Error(string memory) {
try _feedRegistry.getFeed(...) returns (IAggregatorV2V3) {
return true;
ChainlinkOracle.sol#L52-L56
2. ChainlinkOracle._getPrice() uses the deprecated answeredInRound, see https://docs.chain.link/data-feeds/api-reference#latestrounddata
function _getPrice(
...
require(answeredInRound >= roundID, "stale price");
ChainlinkOracle.sol#L83
3. ChainlinkOracle._getPrice() doesn't check for stale prices.
Each feed has a heartbeat, and for each call to latestRoundData() the equation updatedAt < block.timestamp - heartbeat must be checked, see https://ethereum.stackexchange.com/questions/133890/chainlink-latestrounddata-security-fresh-data-check-usage.
4. ChainlinkOracle.getUSDPrice() has a check for price_ != 0 which should actually be price_ > 0 since it is int256 and could hypothetically be negative:
function _getPrice
...
require(price_ != 0, "negative price");
ChainlinkOracle.sol#L82

## Recommendation
Recommendations are as follows:
1. Add a check for abandoned pools in isTokenSupported().
2. Remove the deprecated answeredInRound check.
3. Implement checks for stale prices.
4. Ensure the price_ > 0.
