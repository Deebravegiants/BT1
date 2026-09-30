# [M] M-07 | Governor Contract Does Not Conﬁgure Blast Points

## Summary
Severity: Medium
Contest weight: 0.0981
Dataset id: 20867
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The blast governor contract does not conﬁgure blast points, this will cause the contract to miss out on points that can later be used to receive an airdrop of tokens from blast. “Blast Points are distributed automatically every block to EOAs and smart contracts based on their balance of ETH, WETH, and USDB. Speciﬁcally, EOAs and smart contracts earn Points at a rate of 0.06504987 Points/Block/ETH (around 0.03252493376 Points/second/ETH).” Since the contract is meant to hold eth as it collects yields from other contracts, it will not be able to accrue points based on its eth balance.

## Recommendation
Add a call to blast points conﬁgure function to allow the governor contract's points to be harvested. Add this to constructor BlastPoints.conﬁgure();
