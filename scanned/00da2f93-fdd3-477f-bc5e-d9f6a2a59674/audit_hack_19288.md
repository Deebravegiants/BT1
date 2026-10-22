# [M] Incorrect input of parameters for the `StakingRewardsManager.sol: recoverERC20` function call

## Summary
Severity: Medium
Reporter: Ambitious Opaque Peacock
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Incorrect input of parameters for the `StakingRewardsManager.sol: recoverERC20` function call

## Summary 
The `recoverERC20` function in `StakingRewardsManager.sol` takes 3 parameters as input in this exact order: `IERC20 tokenAddress`, `uint256 tokenAmount` `address to`.
However `recoverERC20FromStaking` calls `recoverERC20 ` with misplaced parameters: `staking.recoverERC20(to, tokenAddress, tokenAmount);`


## Vulnerability Detail

## Impact

## Code Snippet
```solidity
function recoverERC20(
        IERC20 tokenAddress,
        uint256 tokenAmount,
        address to
    ) external onlyRole(SUPPORT_ROLE) {
        //move funds
        tokenAddress.safeTransfer(to, tokenAmount);
    }
```
```solidity
function recoverERC20FromStaking(
        StakingRewards staking,
        IERC20 tokenAddress,
        uint256 tokenAmount,
        address to
    ) external onlyRole(SUPPORT_ROLE) {
        // grab the tokens from the staking contract
        staking.recoverERC20(to, tokenAddress, tokenAmount);
    }
```
## Tool used

Manual Review

## Recommendation
```diff
-        *staking.recoverERC20(to, tokenAddress, tokenAmount);
+        *staking.recoverERC20(tokenAddress, tokenAmount, to);
```
