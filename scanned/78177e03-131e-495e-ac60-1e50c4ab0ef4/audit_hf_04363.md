# [H] H-01 | Valor Emitted Without Cap

## Summary
Severity: High
Contest weight: 0.1269
Dataset id: 21568
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The system uses two variables to calculate the valor emission, totalValorEmitted and maximumValorEmission, and performs a check to validate if the new emission and the total emitted will not surpass the max value. The issue is that totalValorEmitted state variable is never updated, so it's value is always 0. Therefore, the valor cap validations are non existent, and the system can emit valor indefinitely.

## Recommendation
Update the totalValorEmitted state variable, by adding the valorEmission in _getCurrentAccValorPreShareScaled: totalValorEmitted += valorEmission
