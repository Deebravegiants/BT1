# [M] 6.3 Inconsistent Access Control

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected


The access control for FraxLocker.execute is onlyGovernanceOrDepositor. The function
basically allows to call any arbitrary contract and function. The function
FraxLocker.claimFXSRewards has the following access control onlyGovernanceOrAcc. As
execute can replicate the behavior of claimFXSRewards the access control is inconsistent because
claimFXSRewards can be replicated by execute. Ultimately, giving the Depositor the same power
as Acc in this case.

This is only a theoretical problem in the current implementation due to another issue.

Code corrected

The updated code protects the function execute with the modifier onlyGovernance, which restricts
the access to only the governance address.
