# [M] M-02 | initializeMarket Can Be Front Run

## Summary
Severity: Medium
Contest weight: 0.0675
Dataset id: 22085
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The owner of a market is set with the initializeMarket function, which is called after deploying the system and can be called by anyone. This allows an attacker to take over the market by calling the function before the protocol calls it. A malicious owner would be able to configure malicious Uniswap contracts to steal user funds. This also acts as a griefer attack as the protocol needs to pay gas for re-deploying the system.

## Recommendation
Set the owner of the system at deployment.
