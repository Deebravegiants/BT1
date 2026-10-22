# [H] MJR-1 Possible blocking of the contract

## Summary
Severity: High
Contest weight: 0.0393
Dataset id: 9557
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the line DepositSecurityModule.sol#L123 initializes the owner variable without checking the new value of the variable. If the value of the variable is equal to zero, then the following functions will stop working: setOwner(), setNodeOperatorsRegistry(), setPauseIntentValidityPeriodBlocks(), setMaxDeposits(), setMinDepositBlockDistance(), setGuardianQuorum(), addGuardian(), addGuardians(), removeGuardian(), unpauseDeposits().

## Recommendation
It is necessary to add a check for the value of the newValue variable to zero before initializing the owner variable.
