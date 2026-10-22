# [M] M-2 Incomplete Validation of _callData in

## Summary
Severity: Medium
Contest weight: 0.1097
Dataset id: 10436
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This issue has been identified in the proposeMajorityMetaVesTAmendment function of the MetaVesTController.sol#L570 contract.
The function does not check the length of the _callData parameter before processing, which could allow arbitrary or malformed data to be sent to the function. This lack of validation increases the risk of passing incorrect data that might lead to unintended behavior or errors. Proper validation would help ensure that only well-formed data is used in the proposal.
The issue is classified as Medium severity because improper handling of data could lead to errors in contract execution, impacting the reliability of the voting process.

## Recommendation
We recommend adding a validation check to ensure that the length of _callData is exactly 68 bytes to match the expected data format, preventing arbitrary or incorrect data from being processed.
