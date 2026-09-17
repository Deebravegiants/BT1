# [H] lastUpdatedDay not initialized

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-marginswap
Published: 2021-04-04
Source: https://github.com/code-423n4/2021-04-marginswap-findings/issues/14
Type: code-finding

## Details
# Email address

mail@gpersoon.com


# Handle

gpersoon


# Eth address

gpersoon.eth


# Vulnerability details

The variable lastUpdatedDay in IncentiveDistribution.sol is not (properly) initialized.
This means the function updateDayTotals will end up in a very large loop which will lead to an out of gas error.
Even if the loop would end, the variable currentDailyDistribution would be updated very often.
Thus updateDayTotals cannot be performed 


# Impact

The entire IncentiveDistribution does not work.
If the loop would stop, the variable currentDailyDistribution is not accurate, resulting in a far lower incentive distribution than expected.


# Recommended mitigation steps

Initialize lastUpdatedDay with something like block.timestamp / (1 days)


# Proof of concept

uint256 lastUpdatedDay; # ==> lastUpdatedDay = 0

#When the function updateDayTotals is called:
uint256 public nowDay = block.timestamp / (1 days);  #==> ~ 18721
uint256 dayDiff = nowDay - lastUpdatedDay; #==> 18721-0 = 18721
        
for (uint256 i = 0; i < dayDiff; i++) {  # very long loop (18721) 
     currentDailyDistribution = ....
}
#will result in an out of gas error
