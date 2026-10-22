# [M] GMXL-3 | Withdrawals Fail When A Backing Token is Zero

## Summary
Severity: Medium
Contest weight: 0.1041
Dataset id: 20530
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The outputToken and secondaryOutputToken are always validated to be equal after the execution of
a withdrawal:
_outputTokenAddress.value == _secondaryOutputTokenAddress.value
However, the GMX SwapUtils.swap function does not alter the resulting token in the case that the
input into the swap is 0. An input of 0 can occur if the GMX market is one-sided at the point of
withdrawal execution e.g. market only has 1 ETH and no USDC deposited.
Another scenario this may occur in is if the amount being withdrawn is very small. This ultimately
means that the validation will fail and the tokens will be stuck in the unwrapper trader.

## Recommendation
Modify the check such that if the value of the withdrawal output amount is 0, then the
_outputTokenAddress and the _secondaryOutputTokenAddress do not have to match.
