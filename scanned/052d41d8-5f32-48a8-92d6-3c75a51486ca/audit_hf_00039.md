# [M] LP-5 | First Depositor Inflation Attack

## Summary
Severity: Medium
Contest weight: 0.0923
Dataset id: 115
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The IVXLP vault is susceptible to the first deposit inflation attack. 1) Bob calls addLiquidity with 1 wei and then the queue is processed. 2) Bob observes Alice's addLiquidity call in the mempool for 100 tokens and frontruns it by transferring 100 tokens directly to the vault to inflate the NAV. 3) Once the queue is processed, Alice will mint 0 shares but Bob's 1 share is now worth the entire balance of the vault. Although this is less likely because only the queue contract can call mint and burn, the epoch duration is variable and it is a potential risk.

## Recommendation
Consider creating “dead” shares by burning some shares on the first deposit or tracking LP balance internally.
