# [M] `safeApprove()` function deprecated is used in multiple lines

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/32
Type: sherlock-finding

## Details
0xmuxyz

medium

# `safeApprove()` function deprecated is used in multiple lines

## Summary
- `safeApprove()` function deprecated is used in multiple lines.

## Vulnerability Detail
- `safeApprove()` function has been deprecated by OpenZeppelin team: https://github.com/OpenZeppelin/openzeppelin-contracts/pull/2268
   - However, `safeApprove()` deprecated is still used in the multiple lines in this repo.

## Impact
- Using this deprecated-function may lead to unexpected-behavior of smart contracts which this deprecated-function is used in the future.

## Code Snippet
- `safeApprove()` function deprecated is used in the following lines in this repo:
  - https://github.com/masaun/2022-11-dodo-masaun/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L44
  - https://github.com/masaun/2022-11-dodo-masaun/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L46

## Tool used
- Manual Review

## Recommendation
- Instead of using safeApprove() function, `safeIncreaseAllowance()` function and `safeDecreaseAllowance()` function should be used.
    https://docs.openzeppelin.com/contracts/4.x/api/token/erc20#SafeERC20-safeApprove-contract-IERC20-address-uint256-
