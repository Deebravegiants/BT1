# [M] computePoolAddress() will not work on ZkSync

## Summary
Severity: Medium
Contest weight: 0.1391
Dataset id: 20348
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When borrowing or repaying a position a user can either use a custom router that swaps on Uniswap v3 as a fallback.
When using the Uniswap v3 as a fallback the _v3SwapExactInput() internal function is being called. This function uses computePoolAddress() to find the pool address to use. computePoolAddress() is also used during the uniswapV3SwapCallback() to make sure the msg.sender is a valid pool.
On ZkSync Era the create2 addresses are not computed the same way see here.
This will result in the swaps on Uniswapv3 to revert. If a user was able to open a position using a custom router but the custom router is removed later on by the liquidators could find themself not able to close the positions until a new router is whitelisted.
The borrower could be forced to pay collateral for a longer time as he won't be able to close his position.
Medium. Unlikely to happen but would result in short-term DOS and more fees paid by the borrower.

## Recommendation
Consider calling the Uniswap factory getter getPool() to get the address of the pool.
