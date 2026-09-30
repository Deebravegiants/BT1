# [H] H-06 | Gas Validation Does Not Account For Callback Gas

## Summary
Severity: High
Contest weight: 0.2665
Dataset id: 21413
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When keeper performing the actions, if for any reason executions are failed, it is caught in their respective _handleError functions. These functions before checking the reason for execution error and handling the cancellation logic, calls gasUtils' validateExecutionErrorGas function to check if execution trace can be followed till the end with current gasLeft. The problem is, the variable that is checked against gasLeft is MIN_HANDLE_EXECUTION_ERROR_GAS and it is configured as 1.200.000 and did not take into account cancellation's callback gas usage. So this check can pass while gas provided by keeper can be fully used in the concurrent process and that can lead to forwarding less than enough gas to callback contracts which would create unexpected silent reverts for systems integrating with GMX V2, which in many cases could cause a loss of funds or protocol disruption for those integrators. The same situation also applies to getExecutionGas() and it's corresponding variable: MIN_HANDLE_EXECUTION_ERROR_GAS_TO_FORWARD which is configured as 1.000.000 Additionally REFUND_EXECUTON_FEE_GAS_LIMIT also is not accounted which should be accounted similarly.

## Recommendation
When checking gas to see if it would be enough to handle executions, take into account the gas usage for callbacks.
