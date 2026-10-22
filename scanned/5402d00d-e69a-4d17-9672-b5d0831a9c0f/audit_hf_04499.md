# [C] C-04 | Uniswap Pool Creation DoS

## Summary
Severity: Critical
Contest weight: 0.1351
Dataset id: 22062
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Uniswap pool creation is done with three variables (gasToken address, ethToken address, and feeRate). These variables are all predictable even before creation of speciﬁed tokens. Hence it is possible to frontrun pool creations happening in Epoch.sol/createValid(), which will lead to revert in epoch creation.

## Proof of Concept
https://gist.github.com/GuardianAudits/b2bfd0e2770b0f80c002c959f1e95072

## Recommendation
Use CREATE2 to deploy the virtual tokens with a conﬁgurable salt so that pool creation cannot be permanently DoS, additionally be sure to use a private rpc to avoid being frontran to DoS individual epoch creations.
