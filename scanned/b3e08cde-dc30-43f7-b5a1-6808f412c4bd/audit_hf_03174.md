# [M] Outstanding debt is not guaranteed to be cov-

## Summary
Severity: Medium
Contest weight: 0.1301
Dataset id: 17736
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The best-effort one-time English auction for borrower collateral is not economically efficient to drive auction bids towards reaching the total outstanding debt, which leads to loss of LP funds. When any lien against a borrower collateral is not paid within the lien duration, the underlying collateral is put up for auction where bids can come in at any price. The borrower is allowed to cancel the auction if the current bid is lower than the reserve price which is set to the total outstanding debt. The reserve price is not enforced anywhere else. If there are no bids, the liquidator will receive the collateral. This auction design of a best-effort one-time English auction is not economically efficient to drive auction bids towards reaching the total outstanding debt which effectively leads to loss of LP funds on unpaid liens.

## Recommendation
Consider alternative auction design mechanisms e.g. a Dutch auction where the auction starts at the reserve price to provide a higher payment possibility to the LPs.
