# [H] LP-2 | hedgerTotalLiq Errantly Counted As Debt

## Summary
Severity: High
Contest weight: 0.1794
Dataset id: 121
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The hedgerTotalLiq represents the present value of the GMX positions belonging to the protocol. This amount is an asset for liquidity providers in addition to the NAV amount held in the contract. This is in contrast to the other two variables in the numerator of the utilizationRatio, the utilizedCollateral is a loaned amount and MM is a margin maintenance amount. The hedgerTotalLiq is not an amount of the NAV that is being utilized, but rather an additional amount of value belonging to the LPs. Therefore including the hedgerTotalLiq in the numerator of the utilizationRatio misrepresents the ratio of assets being utilized in the IVXLP.

## Recommendation
Do not include the hedgerTotalLiq in the numerator of the utilizationRatio, instead consider factoring it into the NAV or including it in the denominator of the utilizationRatio.
