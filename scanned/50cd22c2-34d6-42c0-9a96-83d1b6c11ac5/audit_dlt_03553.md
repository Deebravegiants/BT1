# [M] Inconsistent balance when fee-on transfer tokens.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-yieldy
Published: 2022-06-26
Source: https://github.com/code-423n4/2022-06-yieldy-findings/issues/234
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-yieldy/blob/main/src/contracts/Staking.sol#:~:text=function%20transferToke(,%7D


# Vulnerability details

## Impact
There are ERC20 tokens that may make certain customizations to their ERC20 contracts.
One type of these tokens is deflationary tokens that charge a certain fee for every `transfer()` or `transferFrom()`.
## Proof of Concept
https://github.com/code-423n4/2022-06-yieldy/blob/main/src/contracts/Staking.sol#:~:text=Invalid%20address%22)%3B-,uint256%20totalTokeAmount%20%3D%20IERC20Upgradeable(TOKE_TOKEN).balanceOf(,)%3B,-%7D

When `IERC20Upgradeable(TOKE_TOKEN)` get set to `totalTokeAmount` it will be different once `safetransfer` have fees as some types of tokens may charge a certain fee for transfer and transferfrom.

It may be better to get the before balance then `safetransferfrom` then get the after balance to make sure no fees were added. 

## Tools Used
Manual Review
