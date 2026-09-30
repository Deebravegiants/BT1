# [M] commonFunds can be burned by anyone

## Summary
Severity: Medium
Contest weight: 0.1467
Dataset id: 5108
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Drips protocol allows users to request updates to the ownership of a repo through the requestUpdateOwner() function. This will trigger a call through Gelato, which will result in a fee being charged to the contract. This fee can be paid from two different sources:
1. The users' deposited funds.
2. The commonFunds.
The protocol will ﬁrst use the users deposited funds, and if there are none, the common funds are used.
if (userFundsUsed >= amount) {
    userFundsUsed = amount;
} else {
    require(commonFunds() >= amount - userFundsUsed, "Not enough funds");
}
if (userFundsUsed != 0) {
    _gelatoStorage().userFunds[payer] -= userFundsUsed;
    _gelatoStorage().userFundsTotal -= userFundsUsed;
}
Address.sendValue(gelatoFeeCollector, amount);
The problem is that there is no restriction on requesting these callbacks from Gelato. So a malicious user could generate countless callbacks which would drain the whole commonFunds without any guards in place to stop him.

## Recommendation
We recommend only allowing updates through trusted identity (e.g. a whitelist) to prevent malicious actors from burning the commonFunds every time new ones get deposited.
