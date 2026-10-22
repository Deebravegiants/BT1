# [M] Call to `swapExactTokensForETH` in `liquidateDai`

## Summary
Severity: Medium
Contest weight: 0.1104
Dataset id: 362
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`liquidateDai()` calls Uniswap’s `swapExactTokensForETH` to swap Dai to ETH. This will work if `msg.sender` (i.e., the FSD contract) has already given the router an allowance amount that is at least as much as the input token Dai.

Given that there is no prior approval, the call to UniswapV2 router for swapping will fail. This is because `msg.sender` has not approved UniswapV2 with an allowance for the tokens that are attempting to be swapped.

The impact is that, while working with the Dai stablecoin, `updateCostShareRequest()` will fail and revert.

Recommend adding FSD approval to UniswapV2 with an allowance for the tokens that are attempting to be swapped.

Fixed in [PR#19](https://github.com/fairside-core/2021-05-fairside/pull/19).

## Recommendation
No recommendation
