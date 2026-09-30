# [H] H-01 | Incorrect stethAmount Used

## Summary
Severity: High
Contest weight: 0.1214
Dataset id: 4043
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _lidoEthToBrktETH function the return value from the submit function is used as the stEth amount gained from the submit call. However the return value represents the amount of stEth shares, not the amount of stEth which were gained from the submit call. As a result a significant portion of stEth will be left in the router contract and the user will not receive brktEth for this amount.

## Recommendation
Use the difference between the stEth balance before and after calling the submit function to wrap in the wstEth contract.
