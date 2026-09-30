# [H] inconsistent risk premium validation in accounting allows future underflows or zero apr

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23411
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: Accounting::calculateRiskPremium computes risk = riskX + riskY * pow(tvlRatio,
riskK). Accounting::setRiskParameters checks that risk < 1e18 (i.e., less than 100%) immediately after
updating the parameters, using the current TVL. However, TVL can change later, so risk may become >= 1e18.
In Accounting::updateIndexes, the expression UD60x18.wrap(1e18) - risk will yield 0 if risk == 1e18
(making aprSrt1 zero) and will revert due to underflow if risk > 1e18. This creates an inconsistency between
the functions and can produce unintended zeros or reverts at runtime.
Impact:
• If risk > 1e18 after TVL changes, Accounting::updateIndexes reverts on underflow, blocking accounting
updates, tranche deposits/withdrawals, and NAV calculations.
• If risk == 1e18, aprSrt1 becomes zero, potentially setting senior APR (aprSrt) to low values, leading to
incorrect NAV splits and no yield for seniors.

## Recommendation
Recommended Mitigation: In Accounting::updateIndexes, cap risk or revert explicitly if risk >= 1e18.
