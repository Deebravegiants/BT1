# [M] The function `MeritDutchAuction.mint` misses 2 important checks

## Summary
Severity: Medium
Reporter: SanketKogekar
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# The function `MeritDutchAuction.mint` misses 2 important checks

## Summary
The function misses to check if `nft` is not set to any address and amount to mint is greater than 0 (`nft != address(0)` and `amount > 0`)

## Vulnerability Detail
The protocol mentions that it will be deployed on ethereum mainnet where the transaction cost is high compared to other chains. The case in which amount is passed 0 to execute the function with no state changes and user will lose funds sent as gas and in the case where protocol owner (admin) fails to set nft address will cause revert in the first iteration of loop.

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Impact
User will lose funds, and txn could revert.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Manual Review

## Recommendation
Add checks: 

```solidity
require(nft != address(0), "nft is unassigned");
require(amount > 0, "Amount should be greater than 0")
```
