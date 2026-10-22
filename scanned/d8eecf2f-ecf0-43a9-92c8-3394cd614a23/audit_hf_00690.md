# [M] M-11 | Insuﬃcient OdosRouter Calldata Validation

## Summary
Severity: Medium
Contest weight: 0.1386
Dataset id: 2241
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ZapSwap._validateOdosSwapAllData() tries to validate the whole amount of received sUSDC tokens is being spent by calling swapCompact. [OdosRouter.swapCompact()](https://github.com/odos-xyz/odos-router-v2/blob/21f4124510aa5c1045f9b3eb1ac2cdcacf235ddd/contracts/OdosRouterV2.sol#L121) supports two main formats for each token - input and output. Each of these tokens may be speciﬁed directly in the calldata or loading them by the odos router storage. The code in ZapSwap.validateOdosSwapAllData adjust the amountLengthPosition accordingly depending on which format is used for the input token. However, it assumes the output token will always use the second format where there is no token address in the calldata. This will result in a failed validation. One of the tokens' bytes will be checked instead of checking the byte showing whether there is input amount speciﬁed. This will either result in allowing not all tokens to be spent or reverting if that token byte is not 0.

## Recommendation
Consider both formats for both tokens.
