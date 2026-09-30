# [H] H-5 Incorrect rewards distribution

## Summary
Severity: High
Contest weight: 0.1120
Dataset id: 7071
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some of the rewards will be blocked on the contract if they were deposited to the empty gauge (when totalSupply == 0) LiquidityGauge.vy#L318 This happens because last_update will be updated nevertheless totalSupply is zero. This finding is classified as HIGH severity since the reward distributor will block some rewards on the contract without a possibility to retrieve them.

## Recommendation
We recommend updating last_update only if totalSupply > 0.
2.3 Medium
