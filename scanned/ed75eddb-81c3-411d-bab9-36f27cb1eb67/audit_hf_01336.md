# [M] Codeup::claimCodeupERC20() may revert whenever the weth balance is very low

## Summary
Severity: Medium
Contest weight: 0.0834
Dataset id: 6642
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
UP-M01 up::claimCodeupERC20() may revert whenever the weth balance is very low up::claimCodeupERC20() adds liquidity to the Uniswap pool whenever the weth balance is bigger than 1. However, an amount bigger than 1 may still lead to reverts if it is low upERC20, trying to swap an amount of 0 and reverting. If it is bigger than 2, but still low, it may swap upERC20, reverting when adding liquidity due to not providing enough liquidity to mint a single share. A poc is available to confirm the finding.

## Recommendation
Instead of setting 1, a slightly bigger dust amount could be use to ensure it does not revert.
