# [C] C-03 | Utilization Rate Manipulated Through Deposits

## Summary
Severity: Critical
Contest weight: 0.1915
Dataset id: 22073
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Utilization rate is calculated in GlobalPerpsMarket.sol by lockedCredit.divDecimal(delegatedCollateralValue). The issue lies with lockedCredit which is taken from minimumCredit which includes deposited sUSD collateral. Intuitively, this deposited collateral should be excluded as it is not part of the market's positions. By including it, an attacker can deposit collateral into the market to increase the utilization rate and result in higher interest charged to all traders.

## Proof of Concept
https://github.com/GuardianAudits/perps-v3-2/blob/4bf0a52d1211a1a0615ef56a815c8e5e298018ea/markets/perps-market/test/integration/guardian/pocs/POC_incorrectUtilizationRate.test.ts

## Recommendation
Exclude deposited sUSD from minimum credit when calculating the utilization rate.
