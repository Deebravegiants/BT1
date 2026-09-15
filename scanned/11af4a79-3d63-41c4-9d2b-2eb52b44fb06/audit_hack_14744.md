# [M] The _etherPrice function retrieves the asset price from the Chainlink aggregator using the latestRoundData function, but it does not check whether the returned value represents outdated data.

## Summary
Severity: Medium
Reporter: Strong Ebony Cormorant
Source: https://github.com/sherlock-audit/2023-07-perennial/blob/main/root/contracts/attribute/Kept.sol#L61-L64
Type: audit-issue

## Details
# The _etherPrice function retrieves the asset price from the Chainlink aggregator using the latestRoundData function, but it does not check whether the returned value represents outdated data.
The _etherPrice function retrieves the asset price from the Chainlink aggregator using the latestRoundData function, but it does not check whether the returned value represents outdated data.

## Vulnerability Detail
The _etherPrice function retrieves the asset price from the Chainlink aggregator using the latestRoundData function, but it does not check whether the returned value represents outdated data.

## Impact
The price represents outdated data.

## Code Snippet
https://github.com/sherlock-audit/2023-07-perennial/blob/main/root/contracts/attribute/Kept.sol#L61-L64

## Tool used

Manual Review

## Recommendation
Add timestamp check
