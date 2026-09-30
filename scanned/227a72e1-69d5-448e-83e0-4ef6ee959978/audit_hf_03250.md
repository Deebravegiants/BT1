# [M] GLOBAL-8 | Unintelligible Revert Reasons

## Summary
Severity: Medium
Contest weight: 0.0946
Dataset id: 17869
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In every catch (bytes memory _reason) case, the reason is parsed with string(abi.encode(_reason)) However, parsing the bytes reason like this results in unintelligible revert strings. The first 4 bytes of the _reason bytes represent the selector for the error that caused the revert, and the rest represent the data that accompanies the error. There ought to be a way (perhaps off-chain) to map from these 4 bytes to the error type and decode the data. Additionally, panic reverts will be caught in this case and should not be parsed.

## Recommendation
Consider an alternative approach to parsing the bytes revert reasons, and know that it is possible by chance for the 4 byte selector for two separate errors to be the same if they are not defined in the same contract.
