# [H] zero address check absent when minting

## Summary
Severity: High
Reporter: Delightful Felt Pangolin
Source: https://github.com/sherlock-audit/2023-11-convergence/blob/main/sherlock-cvg/contracts/Token/CvgSDT.sol#L39-L43
Type: audit-issue

## Details
# zero address check absent when minting

## Summary
minting into an address without zero checks
## Vulnerability Detail
minting directly into an address  without zero address checks 
## Impact
burn address can be used to burn all minted token by attackers
## Code Snippet
https://github.com/sherlock-audit/2023-11-convergence/blob/main/sherlock-cvg/contracts/Token/CvgSDT.sol#L39-L43
## Tool used

Manual Review

## Recommendation
zero checks before minting
