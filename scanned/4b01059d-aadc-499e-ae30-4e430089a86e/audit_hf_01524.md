# [H] solverMetaTryCatch() assumes there is no pre-existing ETH in contract

## Summary
Severity: High
Contest weight: 0.8555
Dataset id: 8051
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
solverMetaTryCatch()
requires ExecutionEnvironment's balance to be the same as solverOp.value:
require(address(this).balance == solverOp.value, "ERR-CE05 IncorrectValue");
```
However, someone can frontrun this transaction and send some ETH to ExecutionEnvironment making its balance non-zero. This leads to the solverMetaTryCatch() call reverting, since the call is sent with an ETH amount equal to solverOp.value. This makes address(this).balance > solverOp.value. Since the error would be treated as SolverOutcome.EVMError in the _solverOpWrapper(), the solver would be forced to pay the gas costs for this revert.

## Recommendation
Refactor the function as follows:
• Update ExecutionEnvironment.sol#L152 as:
```solidity
- require(address(this).balance == solverOp.value, "ERR-CE05 IncorrectValue");
+ require(msg.value == solverOp.value, "ERR-CE05 IncorrectValue");
```
• Update startBalance initialization:
```solidity
- startBalance = 0; // address(this).balance - solverOp.value;
+ startBalance = address(this).balance - msg.value;
```
