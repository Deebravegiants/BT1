# [M] _revokeRole doesn't remove account from roleMember set

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-04-backd
Published: 2022-04-27
Source: https://github.com/code-423n4/2022-04-backd-findings/issues/164
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-04-backd/blob/c856714a50437cb33240a5964b63687c9876275b/backd/contracts/access/RoleManager.sol#L155


# Vulnerability details

## Impact
The function doesn't remove the address from _roleMembers[role] set, which will mess up with the roleCount

## Proof of Concept

## Tools Used

## Recommended Mitigation Steps
```
_roles[role].members[account] = false;
_roleMembers[role].remove(account);
```
