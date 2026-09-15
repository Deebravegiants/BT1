# [M] Rounding by division can make pricePerShare lower than expected

## Summary
Severity: Medium
Reporter: 8olidity
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L219
Type: audit-issue

## Details
# Rounding by division can make pricePerShare lower than expected

## Summary
Rounding by division can make pricePerShare lower than expected
## Vulnerability Detail
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L219
## Impact
Divisions in EVM are rounded down, which means when the fraction price is close to 1 (e.g. 0.999) it would effectively be zero, when it's close to 2 (1.999) it would be rounded to 1 - loosing close to 50% of the intended price.
## Code Snippet
```solidity
        if (shares <= 0) {
            pricePerShare = 0;
        } else if (claimTokenSupply > 0) {
            pricePerShare = (pricePerShare * shares) / claimTokenSupply;
        }
```
## Tool used
vscode
Manual Review

## Recommendation
Solution : make sure (pricePerShare * shares)  = pricePerShare  * claimTokenSupply
