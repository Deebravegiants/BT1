# [M] M-10 | Market Updates Invalidate Previous Positions

## Summary
Severity: Medium
Contest weight: 0.0644
Dataset id: 22066
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
updateValid() allows the owner to change the Uniswap v3 NonFungiblePositionManager. However, changing this will invalidate the tokenID's of all previous positions, among other problems. Additionally, an update to uniswapSwapRouter will freeze previous positions as the tokens are approved to the old and not the new router.

## Recommendation
Consider storing the variables such as the uniswapPositionManager, uniswapSwapRouter and optimisticOracle as part of the epoch parameters so that changes to market parameters only apply to future epochs.
