# [C] Denial of Service on withdrawTokens()

## Summary
Severity: Critical
Contest weight: 0.5588
Dataset id: 14250
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The withdrawTokens() function withdraws locked user tokens from allocated guild contracts. This function fails to check whether a user tries to withdraw zero tokenAmount. If a user has no balance and withdraws zero tokens, totalMembers will reduce by one. This can be seen in the following excerpt from BaseERC20Guild.sol as indicated in the following snippet1:
```solidity
if (tokensLocked[msg.sender].amount == 0) totalMembers = totalMembers.sub(1);
```
A malicious user could launch a DoS attack against the system through repeatedly withdrawing zero tokens until totalMembers == 0. This would prevent other users from withdrawing tokens, due to the aforementioned check causing an Integer Overflow error.

## Recommendation
Add an extra check to make sure users withdraw non-zero tokenAmount. Also, if totalMembers is not essential to the protocol, it can be removed from to minimize complexity and avoid pitfalls.
