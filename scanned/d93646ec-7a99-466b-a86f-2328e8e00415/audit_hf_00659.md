# [M] M-07 | Native Funds Locked In Contract

## Summary
Severity: Medium
Contest weight: 0.0518
Dataset id: 2195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _lzSend function, the _refundAddress parameter is set to the contract's address, but the contract lacks functionality to withdraw or rescue these refunded ETH funds. When LayerZero returns excess fees to the contract address, they will be not be retrievable.

## Recommendation
Consider implementing a pull method for users to receive their refund. Or add a rescue function so that admin can recover the locked ETH.
