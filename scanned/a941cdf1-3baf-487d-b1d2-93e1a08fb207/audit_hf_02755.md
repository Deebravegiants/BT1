# [M] Users can pool SHEEP to reduce sheepDog fee

## Summary
Severity: Medium
Contest weight: 0.0709
Dataset id: 15112
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Rent for protecting SHEEP by depositing them into the sheepDog contract is charged as 10 wGAS per user per day regardless of how many SHEEP is deposited. A group of users can pool their sheep in a contract, let sheepDog protect all of them and only pay 10wGAS per day for all users combined. It's also far cheaper for a user holding a large amount of sheep compared to one that holds a smaller amount.

## Recommendation
Although this could be regarded as part of the gamiﬁcation, consider charging a fee per SHEEP per day rather than per user.
