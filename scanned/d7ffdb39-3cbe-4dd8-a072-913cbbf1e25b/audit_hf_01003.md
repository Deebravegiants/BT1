# [C] Front-end owner can steal all bets balance

## Summary
Severity: Critical
Contest weight: 0.0592
Dataset id: 3364
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Azuro protocol allows any front-end owner to add his address in each bet placed through his UI. In SuperExpress , this address will be able to withdraw a fee amount that is taken from each bet, some small percentage. The problem is that the withdrawFrontFee method, from where this happens, is flawed - it can be called multiple times in a loop until there is no more bet token balance in the contract.
The flaw is that even though the method does this:
round.frontRewarded[msg.sender] = true;
which is an attempt at stopping the front-end owner from claiming his rewards again, this is not checked anywhere. The _viewFrontFee method should account for already claimed "front" rewards, but it doesn't.

## Recommendation
In _viewFrontFee check if round.frontRewarded[msg.sender] == true and if it is just return 0.
