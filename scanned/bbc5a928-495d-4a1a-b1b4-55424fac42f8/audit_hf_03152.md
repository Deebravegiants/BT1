# [H] LIEN_TOKEN.ownerOf(i) should be LIEN_TOKEN.ownerOf(liensRemaining[i])

## Summary
Severity: High
Contest weight: 0.1266
Dataset id: 17694
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In endAuction(), the check for public vault owner is referred to the wrong lien token id. And the actual vault lien amount is not properly recorded. The lien token id should be queried is liensRemaining[i] instead of i. YIntercept will not be correctly recorded. The accounting for LienToken amounts will be wrong. Hence the totalAssets on book will be wrong, eventually the contract and users could lose fund due to the wrong accounting.

## Recommendation
Change LIEN_TOKEN.ownerOf(i) to LIEN_TOKEN.ownerOf(liensRemaining[i]).
