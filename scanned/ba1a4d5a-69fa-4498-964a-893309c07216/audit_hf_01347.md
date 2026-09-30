# [M] M-7 Reentrancy in GovernanceProxy._executeChange()

## Summary
Severity: Medium
Contest weight: 0.3871
Dataset id: 6775
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Check-Effect-Interaction pattern is violated in the GovernanceProxy.executeChange() function:
```solidity
function _executeChange...
...
for(uint256 i; i < change.calls.length; i++) {
    change.calls[i].target.functionCall(change.calls[i].data);
}
...
_endChange(change, index, Status.Executed);
```
GovernanceProxy.sol#L168-L172
Change is marked as completed only after all the change.calls.
If there is a call in the change.calls list to a contract with a hacker's hook (for example, an ERC-777 token), this could allow a malicious actor to repeatedly invoke executeChange() for this list of calls, leading to unforeseen consequences.

## Recommendation
Move _endChange() before the calls to adhere to the Check-Effect-Interaction pattern.
