# [M] A transfer that is not validated its result.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-factorydao
Published: 2022-05-07
Source: https://github.com/code-423n4/2022-05-factorydao-findings/issues/87
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-factorydao/blob/db415804c06143d8af6880bc4cda7222e5463c0e/contracts/MerkleVesting.sol#L173


# Vulnerability details

## Impact
When the transfer is made in the **withdraw()** function, it is not validated if the transfer was done correctly.
This could be a conflict since not being able to perform it would return a false and that case would not be handled, the most common is to revert.


## Recommended Mitigation Steps
The recommendation is to wrap the transfer with a require, as is done in **MerkleDropFactory.sol** for example.
