# [M] using `latestRoundData()` and turn int to uint but does not check if `answer > 0`

## Summary
Severity: Medium
Reporter: BugHunter101
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L582
Type: audit-issue

## Details
# using `latestRoundData()` and turn int to uint but does not check if `answer > 0`

## Summary

Using `latestRoundData()` and turn int to uint but does not check if `answer > 0`, it will cause the result is wrong

## Vulnerability Detail
This could lead to stale prices according to the Chainlink documentation:
https://docs.chain.link/data-feeds/price-feeds/historical-data
Related report:
https://github.com/code-423n4/2021-05-fairside-findings/issues/70

And all the contract have the same problem 
such Vault.vy:
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L582

TrailingStopDex.vy:
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L238

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L245C1-L245C1

## Impact

it will cause the result is wrong

This could lead to stale prices according to the Chainlink documentation:
https://docs.chain.link/data-feeds/price-feeds/historical-data
Related report:
https://github.com/code-423n4/2021-05-fairside-findings/issues/70

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L238

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L245C1-L245C1


https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L582

## Tool used

Manual Review

## Recommendation

Please check `latestRoundData()` return value such like :
https://github.com/sherlock-audit/2023-02-blueberry-judging/issues/94
