# [M] `TwabLib::getTwabBetween` can return innacurate balances if `_startTime` and `_endTime` aren't safely bounded

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-pooltogether
Published: 2023-07-14
Source: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/464
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/4bc8a12b857856828c018510b5500d722b79ca3a/src/PrizePool.sol#L920, https://github.com/GenerationSoftware/pt-v5-twab-controller/blob/0145eeac23301ee5338c659422dd6d69234f5d50/src/libraries/TwabLib.sol#L281, https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/4bc8a12b857856828c018510b5500d722b79ca3a/src/PrizePool.sol#L429


# Vulnerability details

## M-01 `TwabLib::getTwabBetween` can return innacurate balances if `_startTime` and `_endTime` aren't safely bounded

## Vulnerability details
Here's the documentation of the get `TwabLib::getTwabBetween` function :

```solidity
File: twab-controller\src\libraries\TwabLib.sol

278:   /**
279:    * @notice Looks up a users TWAB for a time range.
280:    * @dev If the timestamps in the range are not exact matches of observations, the balance is extrapolated using the previous observation.
281:    * @dev Ensure timestamps are safe using isTimeRangeSafe.
282:    * @param _observations The circular buffer of observations
283:    * @param _accountDetails The account details to query with
284:    * @param _startTime The start of the time range
285:    * @param _endTime The end of the time range
286:    * @return twab The TWAB for the time range
287:    */
288:   function getTwabBetween(  //@audit - M01: dev comment (isTimeRangeSafe) doesn't seems to be followed in PrizePool calling it
289:     uint32 PERIOD_OFFSET,
290:     ObservationLib.Observation[MAX_CARDINALITY] storage _observations,
291:     AccountDetails memory _accountDetails,
292:     uint32 _startTime,
293:     uint32 _endTime
294:   ) internal view returns (uint256) {
```

`TwabLib::getTwabBetween` function get called in `PrizePool::_getVaultUserBalanceAndTotalSupplyTwab`, which itself get called by `PrizePool::claimPrize` returning twab for a specified time-range, which finally is called by `PrizePool::isWinner` in `PrizePool::claimPrize`.

The thing is, as well explained by [the documentation](https://v4.docs.pooltogether.com/protocol/next/design/twab-controller/#sample-loss-of-historic-information), values from balance history isn't guaranteed to be accurate the if timestamp at which it is queried time do not fall between :
- (or at) the newest observation in a period

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/464_
