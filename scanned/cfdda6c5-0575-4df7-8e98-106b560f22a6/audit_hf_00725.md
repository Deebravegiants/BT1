# [H] H-06 | Liquidations Errantly Adjust Funding Correction

## Summary
Severity: High
Contest weight: 0.1862
Dataset id: 2276
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When liquidating positions with the liquidatePosition function, the debtCorrection is updated to account for the position’s size decrease. However the funding which has accrued over the period from the time range [ﬂagPosition, liquidatePosition] is accounted for in the debt correction update. As the liquidated position will not settle the funding received or paid to its margin, this debtCorrection adjustment for the funding realized is unnecessary and perturbs the reportedDebt accounting of the market.

## Proof of Concept
https://docs.google.com/spreadsheets/d/1gpxbpGPHWarm0unXLMHenZkKbiYb5wYIDYdibc6CWbA/edit?usp=sharing

## Recommendation
Consider adding a parameter to updateDebtCorrection function that would allow the totalPositionPnl to be ignored from the result. In the case of liquidations post-ﬂagging, neither the price PnL or the funding PnL is relevant.
