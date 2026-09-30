# [M] GLOBAL-3 | FeedIds Must Be Set For Every Token

## Summary
Severity: Medium
Contest weight: 0.0710
Dataset id: 19264
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Deposits, withdrawals and orders may use swap paths including any token supported on the GMX V2 platform. Therefore every supported token must be assigned a valid functioning feedId, otherwise deposits, withdrawals and orders may be unable to be executed using the Chainlink keeper or may become cancelled unexpectedly.

## Recommendation
Ensure that every token on the GMX V2 platform is supported by a valid feedId. Additionally, implement validation in the checkLog function such that if a feedId is not configured for a token that is necessary for the action, the action is not executed by the Chainlink keeper and is instead executed by the default keeper.
