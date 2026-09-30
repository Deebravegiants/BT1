# [H] H-19 | Missing onlyFactory Check In SuperPool

## Summary
Severity: High
Contest weight: 0.1902
Dataset id: 2535
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
All pools exist within the singleton pool contract, with one singleton contract per SuperPool factory.
Developer comments indicate that SuperPools should only be deployed through the factory contract to ensure they all point to the same singleton pool implementation.
However, the constructor of the SuperPool lacks a check to confirm it is being called by the factory.
This opens the possibility for users to deploy a SuperPool that points to a malicious base pool. With multiple SuperPools containing the same asset, distinguishing between malicious SuperPools and regular ones becomes challenging for ordinary users.

## Recommendation
Implement an onlyFactory check to restrict SuperPool deployment to the factory only, preventing unauthorized users from deploying potentially harmful SuperPools.
