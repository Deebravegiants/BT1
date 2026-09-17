# [M] Deprecated Chainlink oracle API

## Summary
Severity: Medium
Reporter: jasonxiale
Source: https://github.com/sherlock-audit/2023-05-Index/blob/main/index-coop-smart-contracts/contracts/adapters/AaveLeverageStrategyExtension.sol#L895-L897
Type: audit-issue

## Details
# Deprecated Chainlink oracle API

## Summary
Deprecated Chainlink oracle API. API might stop working. Prices could be outdated. Protocol might need to be redeployed or false prices might lead to users losing funds.

## Vulnerability Detail
https://github.com/sherlock-audit/2023-05-Index/blob/main/index-coop-smart-contracts/contracts/adapters/AaveLeverageStrategyExtension.sol#L895-L897

## Impact

The contracts use Chainlink’s deprecated API latestAnswer(). Such functions might suddenly stop working if Chainlink stopped supporting deprecated APIs.
Additionally, one cannot check if the returned price is fresh. The price might by stale (old historical price).

## Code Snippet

## Tool used

Manual Review

## Recommendation
Use the latestRoundData() function to get the price instead.
