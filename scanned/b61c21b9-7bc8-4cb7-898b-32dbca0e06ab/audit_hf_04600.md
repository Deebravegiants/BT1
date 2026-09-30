# [M] M-34 | VotingPool Pods Priced Equally

## Summary
Severity: Medium
Contest weight: 0.0922
Dataset id: 22205
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, all pods are priced equally in the VotingPool contract (assuming the conversion factor is 1:1). This means users can stake cheap pods and receive the same amount of voting tokens they would have received with more expensive pods. For example, a pod with DAI as underlying token and a pod with WETH as underlying token would both be priced equally if their conversion factors are the same. There may also be a situation where the pod with DAI token has its conversion factor higher - this will lead to the DAI pod minting more voting tokens than the WETH one.

## Recommendation
Either implement another pricing mechanism or make sure to only use pods with close price.
