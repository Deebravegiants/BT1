# [M] M-01 | Funds Trapped On Ethereum

## Summary
Severity: Medium
Contest weight: 0.0639
Dataset id: 2135
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MultiHopComposerV1 contract uses an interface which returns a boolean value for the approve function, however USDT on Ethereum does not return a boolean from the approve function. This results in a revert upon approval which will cause the compose message to be un-executable, thereby trapping the USDT in the MultiHopComposerV1 contract.

## Recommendation
For MultiHopComposerV1 deployment on Ethereum mainnet use an IERC20 interface which does not include a boolean return value for the approve function.
