# [M] `FeeBuyback` does not utilize OpenZeppelin's SafeERC20 library, even though the rest of the codebase does

## Summary
Severity: Medium
Reporter: pashov
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L71
Type: audit-issue

## Details
# `FeeBuyback` does not utilize OpenZeppelin's SafeERC20 library, even though the rest of the codebase does

## Summary
Both `StakingModule` and `SimplePlugin` utilize SafeERC20, but `FeeBuyback` which actually should work with many ERC20 tokens does not

## Vulnerability Detail
We have the following code in `FeeBuyback`
```solidity
      IERC20(token).transferFrom(_safe, address(this), amount);
      IERC20(token).approve(_aggregator, amount);
```
Both `transferFrom` and `approve` methods from ERC20 should return a `boolean` showing if the function call completed successfully, but this is not checked here. Since there are tokens that either do not revert but return `false` on failed transfer, or ones that do not actually return a boolean on `transferFrom`, it is best to use OpenZeppelin SafeERC20 which handles those cases.

## Impact
The impact of this can be unexpected failures or silent failures from `transferFrom` or `approve` ERC20 calls

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L71
## Tool used

Manual Review

## Recommendation
Use OpenZeppelin's SafeERC20 library wherever you do ERC20 external calls
