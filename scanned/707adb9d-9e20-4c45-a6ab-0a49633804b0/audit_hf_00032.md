# [M] DIEM-10 | Liquidation Bonus Comes From The Protocol

## Summary
Severity: Medium
Contest weight: 0.0655
Dataset id: 108
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the liquidate() function when a user’s portfolio is liquidated, a liqBonus is given to the msg.sender who initiates the liquidation. However the liqBonus is subtracted from the pnl amount which is to be transferred to the IVXLP contract. Instead the liqBonus ought to be deducted from the user’s remaining portfolio amount if there are leftovers.

## Recommendation
Deduct the liqBonus from the user’s remaining margin amount if it is sufficient rather than deducting it from the amount that the IVXLP contract will receive.
