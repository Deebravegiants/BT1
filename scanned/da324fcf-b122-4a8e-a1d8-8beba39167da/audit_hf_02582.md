# [H] Incorrect quoteWETH() implementation (out-of-scope)

## Summary
Severity: High
Contest weight: 0.7486
Dataset id: 13951
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
UniswapPoolHelper.quoteWETH() is used to calculate the WBNB (denoted as WETH) required for LP-ing into the WBNB-RDNT pool on BSC. There are 2 issues with its implementation:
neededWeth is derived from the wrong reserve
```solidity
uint256 weth = lpToken.token0() != address(rdntAddr) ? reserve0 : reserve1;
uint256 rdnt = lpToken.token0() == address(rdntAddr) ? reserve0 : reserve1;
uint256 lpTokenSupply = lpToken.totalSupply();
uint256 neededWeth = (rdnt * lpAmount) / lpTokenSupply;
```
The neededWeth should be using weth instead of rdnt.
Required amounts are derived from pool amounts before swap, not after
Doing 1-sided liquidity is akin to swapping half of the amount for the other token, then adding liquidity with the remaining half and swapped amounts.
The implementation uses the pool reserves before the swap to calculate the amounts needed, but it should use the altered reserves from the swap where weth increases and rdnt decreases.

## Recommendation
The suggested implementation is below.
```solidity
uint256 neededRdnt = (lpAmount * rdnt) / (lpAmount + lpTokenSupply);
uint256 neededRdntInWeth = router.getAmountIn(neededRdnt, weth, rdnt);
uint256 neededWeth = (weth - neededRdntInWeth) * lpAmount / lpTokenSupply;
return neededWeth + neededRdntInWeth;
```
