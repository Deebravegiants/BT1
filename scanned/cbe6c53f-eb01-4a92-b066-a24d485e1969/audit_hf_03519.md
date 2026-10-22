# [M] GLOBAL-1 | Execution Gas Validated Too Early

## Summary
Severity: Medium
Contest weight: 0.1148
Dataset id: 19229
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Based on the startingGas and the estimatedGasLimit, the execution gas is validated to ensure the startingGas is greater than the estimatedGasLimit and some variable, additional gas for execution. After calling GasUtils.validateExecutionGas(dataStore, startingGas, estimatedGasLimit), the gas for execution is presumed to be enough for execution of the order as it has been validated. However, uint256 executionGas = GasUtils.getExecutionGas(dataStore, startingGas) is called right afterwards which reduces the startingGas by the gas needed for error handling. The amount of gas validated for execution is different than the amount given for execution, which may now be insufficient.

## Recommendation
Consider making the gas validation more restrictive by calling validateExecutionGas() on the result of getExecutionGas() or ensure the minAdditionalGasForExecution is large enough to cover the gas forwarded to handle the execution error.
