# [M] M-01 | Insufficient Token Amounts Lead To Swap Error

## Summary
Severity: Medium
Contest weight: 0.1054
Dataset id: 22172
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When compounding rewards in _pairedLpTokenToPodLp, pairedLpTokens are swapped to pTKN via Uniswap's swapV2Single. However, if too little tokens are provided it may revert in Uniswap V2 with 'INSUFFICIENT_INPUT_AMOUNT' or INSUFFICIENT_OUTPUT_AMOUNT . This could be caused by a balance of 1 wei of pairedLpTokens. which after halving becomes 0 pTKNs. This small balance could be easily donated by an attacker looking to DOS the contract, or simply caused by leftover tokens from a previous transaction. As processing of rewards is called by every major flow, reverting could have serious implications such as preventing users from removing leverage and result in liquidations.

## Recommendation
Verify the balance of tokens before calling the swap function to avoid reverts.
