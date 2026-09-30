# [M] M-03 | Unnecessary Fees When Closing Short

## Summary
Severity: Medium
Contest weight: 0.0710
Dataset id: 22086
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When closing a short position in the _closePosition function, position.vEthAmount is swapped to vGas. Next, if position.borrowedVGas > tokenAmountVGas, then vEth is swapped back to vGas. Since tokens were swapped from vEth to vGas back to vEth the position closer had to pay extra fees for unnecessary swaps when they could just swap a lower amount of vETH initially and skipped the second swap.

## Recommendation
Consider first calculating the amount of vETH that needs to be swapped to vGas to close the position and then executing only a single swap.
