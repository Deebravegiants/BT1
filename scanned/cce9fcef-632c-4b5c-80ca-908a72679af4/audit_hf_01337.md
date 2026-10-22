# [M] A transfer that is not validated its result.

## Summary
Severity: Medium
Contest weight: 0.0693
Dataset id: 6667
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the transfer is made in the **withdraw()** function, it is not validated if the transfer was done correctly.

This could be a conflict since not being able to perform it would return a false and that case would not be handled, the most common is to revert.

## Recommendation
The recommendation is to wrap the transfer with a require, as is done in **MerkleDropFactory.sol** for example.

Malicious or otherwise bad tokens are considered acceptable risks for this contract as long as they cannot interfere with other trees.

[illuzen (FactoryDAO) resolved](https://github.com/code-423n4/2022-05-factorydao-findings/issues/87#issuecomment-1145529354):

<https://github.com/code-423n4/2022-05-factorydao/pull/3>
