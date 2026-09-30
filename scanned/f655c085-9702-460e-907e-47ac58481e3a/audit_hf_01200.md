# [M] Solvers may receive less gas than they expect

## Summary
Severity: Medium
Contest weight: 0.1166
Dataset id: 5219
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A key change introduced in Atlas V1.6 is that the gas limit forwarded to solvers is now set as the minimum of solverOp.gas (the value set by the solver) and dConfig.solverGasLimit (the value from the DAppControl).
One consequence of this change is that if dConfig.solverGasLimit is lowered after a solver signs and submits their solverOp, the gas limit they ultimately receive will be lower than they expect. In a worst-case scenario, a DAppControl could intentionally lower the dConfig.solverGasLimit value to cause the solverOp to fail due to an out-of-gas error. This could grief the solver since an out-of-gas error would be treated as their fault.

## Recommendation
Consider adding a field to the userOp struct to commit to the expected dConfig.solverGasLimit from the DAppControl, similar to how bundlerSurchargeRate is included in the userOp. This approach would only add one new field and ensures that all solverOps are aware of the expected dConfig.solverGasLimit, since it contributes to the userOp hash.
