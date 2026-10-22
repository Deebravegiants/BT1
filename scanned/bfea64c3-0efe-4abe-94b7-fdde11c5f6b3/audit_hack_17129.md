# [M] no checks for duplicate guages before addition

## Summary
Severity: Medium
Reporter: Delightful Felt Pangolin
Source: https://github.com/sherlock-audit/2023-11-convergence/blob/main/sherlock-cvg/contracts/Rewards/CvgRewards.sol#L129-L133
Type: audit-issue

## Details
# no checks for duplicate guages before addition

## Summary
the guages array isnt checked for duplicates  before adding new guage address
## Vulnerability Detail
the guages array can be made bloated with duplicates and the guageId array doesnt have a correct pointer to the guageAddress
## Impact
protocol insolvency 
## Code Snippet
https://github.com/sherlock-audit/2023-11-convergence/blob/main/sherlock-cvg/contracts/Rewards/CvgRewards.sol#L129-L133
## Tool used

Manual Review

## Recommendation
checks for duplicate address
