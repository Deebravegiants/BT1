# [M] Frontrunning Proposal Execution

## Summary
Severity: Medium
Contest weight: 0.1566
Dataset id: 14278
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contracts PermissionRegistry.sol and ERC20Guild (BaseERC20Guild or any related implementation contracts) complement each other. These contracts provide a checking mechanism to ensure that each function call is permitted and
the amount of assets transferred is within specified limits. When a proposal is executed, the ERC20Guild contract calls
PermissionRegistry.setPermissionUsed() to register the asset transfer.
This mechanism can be disrupted by a malicious user who aims to prevent the proposal from executing. This is
done by frontrunning transaction on
ERC20Guild.endProposal() by calling
ERC20Guild.setPermissionUsed() with
valueTransferred equals to valueAllowed and other information that corresponds to the proposal.
As a result of this frontrunning, ERC20Guild.endProposal() will fail if the blockchain tries to execute the transaction
within the same block as the malicious ERC20Guild.setPermissionUsed().
The frontrunning action may keep going until timeForExecution passes. In this case, the proposal will execute with
ProposalState.Failed result.

## Recommendation
The issue can be mitigated by adding access control to PermissionRegistry.setPermissionUsed() such that it is only
callable by the respective permissioned owner.
