# [M] Need more checks for Chainlink price feed

## Summary
Severity: Medium
Reporter: ni8mare
Source: https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/Vault.vy#L576
Type: audit-issue

## Details
# Need more checks for Chainlink price feed

## Summary
Chainlink's `latestRoundData` function returns a set of variables that need to be validated, in order to avoid wrong prices.

## Vulnerability Detail
As the summary suggests, `latestRoundData` function returns a set of variables that need to be validated, in order to avoid wrong prices. For example, there is no check to see that the price of the token s greater than 0 or there are no minPrice/maxPrice checks on the token price - https://solodit.xyz/issues/6663.

## Impact
Incorrect data could be used by the project due to insufficient checks on the price feed return values.

## Code Snippet
https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/Vault.vy#L576

## Tool used

Manual Review

## Recommendation

Please use the following checks to ensure safety:

```solidity
require(price > 0, "Negative Oracle Price");
require(block.timestamp - updatedAt <= outdated , "ChainLinkOracle: outdated.");
require(price < maxPrice, "Upper price bound breached");
require(price > minPrice, "Lower price bound breached");
require(answeredInRound >= roundID, "round not complete");
```
