# [M] Users are missing out on Aave v3 rewards

## Summary
Severity: Medium
Contest weight: 0.0793
Dataset id: 3310
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Aave can hand out extra rewards See here Currently in StrategyManager there is no way to claim these rewards. This is in itself not a problem as a protocol can through an Aave gov vote get rights to claim on behalf of their contracts. But once that is done, there is no way for these to be redistributed back to the users staking. Hence a user is disincentivized from moving their staking position from Aave to Athena since they will be losing out on their rewards.

## Recommendation
Consider implementing a way to re-add the rewards from Aave to the users staking in Aave through StrategyManager.
