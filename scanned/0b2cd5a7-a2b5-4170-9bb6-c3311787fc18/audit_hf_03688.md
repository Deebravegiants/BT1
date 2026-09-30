# [M] voltGNS.compound is not called for

## Summary
Severity: Medium
Contest weight: 0.0812
Dataset id: 19783
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
compound is not called for voltGNS.withdraw and redeem. User lose funds because of that.
voltGNS.compound is harvesting rewards from gnsVault, then swap them into GNS and then stake them back to the vault. Because of this totalAssets is increasing and stakers earn more GNS. This function is called at the top of deposit and mint function, but it's not called inside withdraw and redeem. Because of that, users that are going to withdraw from voltGNS are losing some funds.
Lose of funds for withdrawers.

## Recommendation
Call compound in both withdraw and redeem functions.
