# [M] Oracle is not validated.

## Summary
Severity: Medium
Reporter: 0x2e
Source: https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/oracles/StableOracleDAI.sol#L48
Type: audit-issue

## Details
# Oracle is not validated.

## Summary

Oracle is not validated.

## Vulnerability Detail

Oracle is not validated. `latestRoundData()` may get stale.

## Impact

Get wrong price.

## Code Snippet

https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/oracles/StableOracleDAI.sol#L48
https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/oracles/StableOracleWBTC.sol#L23
https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/oracles/StableOracleWETH.sol#L23

## Tool used

Manual Review

## Recommendation

Check answeredInRound > roundID, price > 0, and timeStamp > 0.
