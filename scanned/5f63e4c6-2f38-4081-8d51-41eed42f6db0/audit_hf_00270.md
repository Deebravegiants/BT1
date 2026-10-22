# [H] wrong minting amount

## Summary
Severity: High
Contest weight: 0.0792
Dataset id: 1382
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
uint256 proxy = (baseBalance * ONE) / _redeemRate;

should be:
    
    uint256 proxy = (amount * ONE) / _redeemRate;

Should be a balanceBefore and balanceAfter calculation with the diff being wrapped.

Valid `high`. The issue description can be more comprehensive though.

## Recommendation
No recommendation
