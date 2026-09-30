# [H] H-02 | GLV Callbacks Do Not Validate Remaining Gas

## Summary
Severity: High
Contest weight: 0.2501
Dataset id: 21899
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the afterGlvDepositExecution, afterGlvDepositCancellation, afterGlvWithdrawalExecution, and afterGlvWithdrawalCancellation functions the validateGasLeftForCallback is not performed as it is in all other callbacks. As a result these callbacks may forward less than the expected callback gas limit and cause integrating systems to silently revert, leading to loss of funds in these systems. Specifically, in validation done in the respective _handleError functions is against the MIN_HANDLE_EXECUTION_ERROR_GAS which is configured as 1,200,000 and does not take into account cancellation's callback gas usage. Therefore this check can pass while gas provided by keeper is insufficient for the cancellation + callback gas which will lead to forwarding less than enough gas to the callback contract. Without this validation keepers will not correctly account for the gas necessary for these callbacks upon estimation and may on accident or on purpose cause loss of funds in integrators.

## Recommendation
Implement the validateGasLeftForCallback validation in the afterGlvDepositExecution, afterGlvDepositCancellation, afterGlvWithdrawalExecution, and afterGlvWithdrawalCancellation functions so keepers may adequately estimate gas and cannot accidentally or purposefully cause loss of funds in these systems.
