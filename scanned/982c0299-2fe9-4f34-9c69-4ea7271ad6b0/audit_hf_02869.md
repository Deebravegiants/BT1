# [M] Rewards for wrapping NFTs can be gamed

## Summary
Severity: Medium
Contest weight: 0.0841
Dataset id: 16144
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The prize structure for wrapping an NFT is restarted everyday. The first user to wrap his NFT will receive 0.1 ETH, the second 0.05 ETH, and all users after that will get 0.015 ETH. However, as this is restarted each day, users will be incentivized to wait for the next day and get the higher reward. This could lead to users intentionally waiting and not wrapping their NFTs, slowing the whole process (which is expected to take place for 1-2 weeks), or alternatively many users missing the period to wrap their NFTs.

## Recommendation
Consider implementing a reward structure that is not on a daily basis.
