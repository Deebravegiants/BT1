# [H] No zero checks in cvg.sol constructor

## Summary
Severity: High
Reporter: Delightful Felt Pangolin
Source: https://github.com/sherlock-audit/2023-11-convergence/blob/main/sherlock-cvg/contracts/Token/Cvg.sol#L34-L38
Type: audit-issue

## Details
# No zero checks in cvg.sol constructor

## Summary
absence of zero address checks before assignments in the cvg.sol constructor 
## Vulnerability Detail
assignment  to state variables is made without checks for zero address 
## Impact
assignment to burn address
## Code Snippet
https://github.com/sherlock-audit/2023-11-convergence/blob/main/sherlock-cvg/contracts/Token/Cvg.sol#L34-L38
## Tool used

Manual Review

## Recommendation
zero checks should be used before assignments
