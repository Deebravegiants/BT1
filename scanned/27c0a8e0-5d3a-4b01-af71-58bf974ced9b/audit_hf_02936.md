# [M] Large Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.0702
Dataset id: 16286
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The withdrawFunds() Function within the RunaAGI.sol file poses a significant centralization risk. This function permits the contract owner to withdraw the entire balance of funds to any specified address. This capability grants the owner excessive control over the contract’s funds, potentially leading to misuse or exploitation.

## Recommendation
Consider implementing a Timelock mechanism. This mechanism introduces a delay between the initiation of a withdrawal request and its execution, providing an opportunity for stakeholders to review and potentially intervene in case of any suspicious or unauthorized withdrawal attempts.
