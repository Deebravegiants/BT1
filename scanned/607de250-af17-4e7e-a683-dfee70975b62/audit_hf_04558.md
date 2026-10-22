# [H] H-04 | Loss Of Rewards Due Two Step Swap Failure

## Summary
Severity: High
Contest weight: 0.1241
Dataset id: 22161
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When compounding rewards in _processRewardsToPodLp, some rewards may require a two-step process to swap to the paired LP token. However in _swapV2, only a single swap is performed. Therefore, if a second swap is required, it will not be performed and the intermediate token received will remain in the contract. These rewards will not be compounded and users will lose potential yield. An identical error was found in Zapper.sol.

## Recommendation
Perform a second swap for tokens which require a two-step process.
