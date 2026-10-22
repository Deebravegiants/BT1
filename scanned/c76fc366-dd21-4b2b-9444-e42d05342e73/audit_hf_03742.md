# [H] Adversary can lock every deposit forever by

## Summary
Severity: High
Contest weight: 0.2873
Dataset id: 19883
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DepositMangerV1 allows the caller to specify _expiration which specifies how long the deposit is locked. An adversary can specify a deposit with _expiration = type(uint256).max which will cause an overflow in the BountyCore#getLockedFunds subcall and permanently break refunds.
nager/Implementations/DepositManagerV1.sol#L54-L56
DepositManagerV1#fundBountyToken allows the depositor to specify an _expiration which is passed directly to BountyCore#receiveFunds.
plementations/BountyCore.sol#L47-L52
BountyCore stores the _expiration in the expiration mapping.
plementations/BountyCore.sol#L339-L349
When requesting a refund, getLockedFunds returns the amount of funds currently locked. The line to focus on is depositTime[depList[i]] + expiration[depList[i]]
An adversary can cause getLockedFunds to always revert by making a deposit in which depositTime[depList[i]] + expiration[depList[i]] > type(uint256).max causing an overflow. To exploit this the user would make a deposit with _expiration = type(uint256).max which will cause a guaranteed overflow. This causes DepositMangerV1#refundDeposit to always revert breaking all refunds.
Submitting as high risk because when combined with payout breaking methods it will result in all deposited tokens being stuck forever.
Adversary can permanently break refunds

## Recommendation
Add the following check to DepositMangerV1#fundBountyToken:
require(_expiration <= type(uint128).max)
