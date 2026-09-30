# [H] Restriction on User Withdrawals

## Summary
Severity: High
Contest weight: 0.2168
Dataset id: 14675
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract Account is used to store the balance ERC20 Tokens that users have deposited in the markets.
These user balances are updated as users make trades. A user who makes a profit from these trades would then
withdraw their profits and/or deposited balance via the function withdraw().
On
line
[138]
of
the
function
withdraw()
the
users
deposited
balance
is
updated
as
such
userBalance.deposited = userBalance.deposited.sub(amount);.
The variable userBalance.deposited is only increased when a user makes a deposit and decreased when a
user withdraws. Since this function uses SafeMath and deposited is of type uint256 the function will revert
if a user attempts to withdraw more than the total balance they have deposited.
The implications are that a user will be unable to withdraw profits, their withdrawals are limited to the amount
they have deposited.

## Recommendation
We recommend removing the field deposited from the type AccountBalance and remove the instances
where it is used.
Tracer Protocol
