# [M] Unbounded loops in LiquidityMining

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

There are some methods that have unbounded loops and will fail when enough items exist in the arrays.


**code/contracts/LiquidityMining.sol:L83**
```solidity
for (uint256 i = 0; i < _teamsNumber; i++) {
```


**code/contracts/LiquidityMining.sol:L97**
```solidity
for (uint256 i = 0; i < _membersNumber; i++) {
```


**code/contracts/LiquidityMining.sol:L110**
```solidity
for (uint256 i = 0; i < _usersNumber; i++) {
```

These methods will fail when lots of items will be added to them.

#### Recommendation

Consider adding limits (from, to) when requesting the items.
