# [M] WadRayMath rounding behavior may lead to reward overestimation that could impact user withdrawals

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/110
Type: sherlock-finding

## Details
TurnipBoy

medium

# WadRayMath rounding behavior may lead to reward overestimation that could impact user withdrawals

## Summary

WadRayMath#wadMul implements a rounding behavior instead of truncation which is typical in solidity. When rounding up the contract will overestimate the users rewards. The compounding effect of this rounding can lead to users being unable to withdraw rewards as the sum of committed rewards will be greater than the amount of rewards available.

## Vulnerability Detail

    function wadMul(uint256 a, uint256 b) internal pure returns (uint256) {
        return (halfWAD + a * b) / WAD;
    }

The WadRayMath library implements rounding in all of its functions, instead of truncation. In wadMul this behavior is caused by the addition of halfWAD to the product of a and b. We can walk through an example of this behavior. Using a WAD of 1e18 would be cumbersome, so I will give an example using a WAD of 1e2. The number of decimals is different but the principle is the same:

a = 115 (1.15e2)
b = 105 (1.05e2)

WAD = 100 (1e2)
halfWAD = WAD / 2 = 100 / 2 = 50 (0.5e2)

a * b = 12075 (1.2075e4)

a * b + halfWAD = 12125 (1.2125e4)

12125 / 100 = 121 (1.21e2)

Here we see our result has been rounded up. Without the addition of halfWAD the result would have been 120 compared to the return value of 121.

        return (curInflationIndex - startInflationIndex).wadMul(effectiveStakeAmount).wadMul(inflationIndex);

In Comptroller when calculating the rewards owed the user are calculated using wadMul, meaning that user rewards will be rounded rather than truncated. This is problematic as it may lead to it over committing rewards. We can ignore the nitty gritty of the math and use an abstraction to visualize the problem in a neater fashion:

Assume there are a total of 10 rewards to be distributed between user A and user B. Assume that user A's stake results in an allocation of 6.5 and user B's stake results in an allocation of 3.5. Under truncation rules, users A and B would be entitled to 6 and 3 respectively. This brings the total owed to 9. 1 token is lost but both users are able to claim their share. Under rounding rules, users A and B would be entitled to 7 and 4 respectively. This brings the total owed to 11. It is now impossible for both users to withdraw their claim as there are only 10 tokens to be distributed. 


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/110_
