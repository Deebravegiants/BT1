# [C] attackers to drain the vault

## Summary
Severity: Critical
Contest weight: 0.1200
Dataset id: 10494
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
BasicVault::_redeem() is inconsistent as it burns newAmount, the value returned from the
hook, but pushes a request to the redeem queue with amount. As hook::reportRedeem()
will cap the amount to redeem to the current load, the last user to withdraw may specify a
huge amount to redeem, which will be capped to the remaining load, burning the capped
newAmount shares, but pushing a request with the huge amount.

## Recommendation
uint256 requestId = $v2.redeemQueue.push(_msgSender(), newAmount);
