# [M] GLOBAL-1 | Payload Attack Enables Grieﬁng Of Keepers

## Summary
Severity: Medium
Contest weight: 0.0703
Dataset id: 19582
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _transferOutETHWithGasLimitFallbackToWeth and _transferOutETH functions in GMX V1 are used to transfer ether. Neither of these functions utilizes assembly to avoid copying return data into memory. This allows any contract interacting with GMX V1 to maliciously return a large amount of data, which will end up costing more gas than anticipated and could force the keepers to run a deﬁcit.

## Recommendation
Use a low-level call to avoid loading the return data into memory: assembly { success := call(gasLimit, receiver, amount, 0, 0, 0, 0) }.
