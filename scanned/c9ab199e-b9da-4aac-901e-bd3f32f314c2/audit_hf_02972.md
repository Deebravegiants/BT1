# [H] MJR-1 Incorrect use of a library function

## Summary
Severity: High
Contest weight: 0.0366
Dataset id: 16488
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the lines BaseWrapper.sol#L117 BaseWrapper.sol#L198 use the safeApprove() function from the SafeERC20 library. But before giving permission for a certain amount of tokens, you first need to zero this value. Now the safeApprove() function is called only once with a specific value. After the first call, everything will work, but after the second call, the function will be blocked.

## Recommendation
It is necessary to make a correct call to the safeApprove() function: token.safeApprove(addressValue, 0); token.safeApprove(addressValue, amount);
