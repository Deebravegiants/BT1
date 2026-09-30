# [C] C-03 | shiftGasLimitKey Returns Incorrect Gas Limit Key

## Summary
Severity: Critical
Contest weight: 0.1592
Dataset id: 21423
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Keys.sol file, the shiftGasLimitKey function returns the WITHDRAWAL_GAS_LIMIT key instead of the SHIFT_GAS_LIMIT key. Therefore the estimated execution fee for shift actions will be significantly smaller than it ought to be, as a shift includes not only a withdrawal but a deposit action as well. This will lead to the protocol keeper being unexpectedly drained of the native token, potentially stopping execution on the exchange for a period of time. The gas draining can occur due to regular exchange usage or can be easily leveraged by an attacker to maliciously drain the keeper.

## Recommendation
Return the SHIFT_GAS_LIMIT key in the shiftGasLimitKey function.
