# [H] MJR-2 Strategy migration reverts after Maker liquidation

## Summary
Severity: High
Contest weight: 0.0365
Dataset id: 16483
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Unlikely, but possible situation when Maker collateral will be liquidated. In this case all operations with collateral will be reverted because the owner would be changed. After the liquidation you can't migrate to a new strategy because prepareMigration will be reverted for the above reasons. Strategy.sol#L450

## Recommendation
The Maker's contract does not provide any functionality for getting the collateral's owner by cdpId (for checking that the liquidation didn't happen). That's why you have to catch all exceptions of transferCdp call by using try/catch functionality in Solidity (0.6 and higher) and check the security modifier error.
