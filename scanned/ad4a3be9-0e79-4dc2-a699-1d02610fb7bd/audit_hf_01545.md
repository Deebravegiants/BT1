# [M] _crossTransfer(...) reverts for smart contracts that don't share the same address on different chains

## Summary
Severity: Medium
Contest weight: 0.0671
Dataset id: 8225
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_crossTransfer(...) has a beneficiary check such that the receiver of the funds in the destination chain must be the same as the previous beneficiary (most likely the msg.sender or the ConnextRouter). If the address is a smart contract, the address will probably be different on the different chain, which will make the transaction revert.

## Recommendation
Allow users to specify in a mapping the corresponding beneficiary in the destination chain, in a function addBeneficiaryToDestDomain(...), which would set beneficiary[msg.sender][destDomain] = newBeneficary;.
